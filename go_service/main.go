package main

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	vertexai "cloud.google.com/go/aiplatform/apiv1"
	"github.com/gin-gonic/gin"
	"github.com/google/generative-ai-go/genai"
	"github.com/joho/godotenv"
	"google.golang.org/api/option"
	vertexaipb "google.golang.org/genproto/googleapis/cloud/aiplatform/v1"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/protobuf/types/known/structpb"
	_ "modernc.org/sqlite"
)

var (
	gcpProjectID = os.Getenv("GCP_PROJECT_ID")
	gcpLocation  = os.Getenv("GCP_LOCATION")
	db           *sql.DB
)

type TodoPayload struct {
	TodoID      int       `json:"todo_id"`
	Title       string    `json:"title"`
	Description string    `json:"description"`
	SendAt      time.Time `json:"remind_at"`
	Latitude    float64   `json:"latitude"`
	Longitude   float64   `json:"longitude"`
}

type GeminiResponse struct {
	Notes       string `json:"notes"`
	ImagePrompt string `json:"image_prompt"`
}

type DjangoCallbackPayload struct {
	Notes string `json:"notes"`
	Image string `json:"image"` // Base64 encoded image string
}

type LogData struct {
	TodoID      int
	Title       string
	Description string
	RemindAt    time.Time
	Weather     string
	Notes       string
	ImagePrompt string
	Status      string // "SUCCESSFUL" or "FAILED"
}

var DJANGO_CALLBACK_URL = os.Getenv("DJANGO_CALLBACK_URL_FORMAT")

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Println("Note: Could not load .env file, relying on OS environment variables.")
	}
	gcpProjectID := os.Getenv("GCP_PROJECT_ID")
	gcpLocation := os.Getenv("GCP_LOCATION")

	if gcpProjectID == "" || gcpLocation == "" || os.Getenv("GEMINI_API_KEY") == "" {
		log.Fatal("FATAL: Environment variables GEMINI_API_KEY, GCP_PROJECT_ID, and GCP_LOCATION must be set.")
	}

	db, err = sql.Open("sqlite", "./db.sqlite3")
	if err != nil {
		log.Fatalf("FATAL: Failed to open database: %v", err)
	}
	defer db.Close()

	if err = db.Ping(); err != nil {
		log.Fatalf("FATAL: Failed to connect to database: %v", err)
	}

	if err := initDB(); err != nil {
		log.Fatalf("FATAL: Failed to initialize database schema: %v", err)
	}

	log.Println("Successfully connected to SQLite database.")

	router := gin.Default()
	router.POST("/generate-notes", handleGenerateNotes)
	log.Println("Go service starting on :8080")
	router.Run(":8080")
}

func handleGenerateNotes(c *gin.Context) {
	var payload TodoPayload
	if err := c.ShouldBindJSON(&payload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusAccepted, gin.H{"status": "processing started"})
	go processTodo(payload)
}

func processTodo(payload TodoPayload) {
	log.Printf("Processing Todo ID: %d", payload.TodoID)
	ctx := context.Background()

	logData := LogData{
		TodoID:      payload.TodoID,
		Title:       payload.Title,
		Description: payload.Description,
		RemindAt:    payload.SendAt,
		Status:      "SUCCESSFUL",
	}

	defer func() {
		log.Printf("INFO [ID %d]: Writing final log entry with status: %s", logData.TodoID, logData.Status)
		if err := writeLogEntry(logData); err != nil {
			log.Printf("CRITICAL [ID %d]: FAILED TO WRITE LOG: %v", logData.TodoID, err)
		}
	}()

	dateStr := payload.SendAt.Format("2006-01-02")
	weatherURL := fmt.Sprintf("https://api.open-meteo.com/v1/forecast?latitude=%f&longitude=%f&daily=weather_code,temperature_2m_max&timezone=auto&start_date=%s&end_date=%s",
		payload.Latitude, payload.Longitude, dateStr, dateStr)
	resp, err := http.Get(weatherURL)
	if err != nil {
		log.Printf("ERROR [ID %d]: Failed to fetch weather: %v", payload.TodoID, err)
		logData.Status = "FAILED"
		return
	}
	defer resp.Body.Close()
	weatherBytes, _ := io.ReadAll(resp.Body)
	logData.Weather = string(weatherBytes)
	log.Printf("INFO [ID %d]: Fetched weather data.", payload.TodoID)

	geminiAPIKey := os.Getenv("GEMINI_API_KEY")
	client, err := genai.NewClient(ctx, option.WithAPIKey(geminiAPIKey))
	if err != nil {
		log.Printf("ERROR [ID %d]: Failed to create Gemini client: %v", payload.TodoID, err)
		logData.Status = "FAILED"
		return
	}
	defer client.Close()
	model := client.GenerativeModel("gemini-2.5-flash")
	prompt := fmt.Sprintf(
		`Based on the following reminder, generate content in a valid JSON format.
		Do not include the markdown backticks in your response.
		
		Reminder Title: %s
		Description: %s
		Date: %s
		Weather Forecast Data: %s

		JSON format to use:
		{
		  "notes": "A short, helpful note for the user about the reminder, incorporating the weather if relevant.",
		  "image_prompt": "A highly detailed, vivid, realistic like and creative prompt for an image generation AI like Imagen. Describe the scene and style. The prompt MUST NOT include sexual content and children. The style must be safe for all audiences. The prompt must be in English."
		}
		
		Generate the JSON now.`,
		payload.Title, payload.Description, dateStr, logData.Weather)
	respGen, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		log.Printf("ERROR [ID %d]: Failed to generate content from Gemini: %v", payload.TodoID, err)
		logData.Status = "FAILED"
		return
	}
	geminiRespText := extractContent(respGen)
	var geminiData GeminiResponse
	if err := json.Unmarshal([]byte(geminiRespText), &geminiData); err != nil {
		log.Printf("ERROR [ID %d]: Failed to parse JSON from Gemini: %v. Response was: %s", payload.TodoID, err, geminiRespText)
		logData.Status = "FAILED"
		return
	}
	logData.Notes = geminiData.Notes
	logData.ImagePrompt = geminiData.ImagePrompt
	log.Printf("INFO [ID %d]: Successfully parsed Gemini response.", payload.TodoID)

	log.Printf("INFO [ID %d]: Generating image with prompt: %s", payload.TodoID, logData.ImagePrompt)
	imageBase64, err := generateImageWithImagen(ctx, logData.ImagePrompt)
	if err != nil {
		log.Printf("ERROR [ID %d]: Failed to generate image with Imagen: %v", payload.TodoID, err)
		logData.Status = "FAILED"
		return
	}
	log.Printf("INFO [ID %d]: Successfully generated image with Imagen.", payload.TodoID)

	callbackPayload := DjangoCallbackPayload{
		Notes: logData.Notes,
		Image: imageBase64,
	}
	jsonPayload, _ := json.Marshal(callbackPayload)
	djangoURL := fmt.Sprintf(DJANGO_CALLBACK_URL, payload.TodoID)
	req, _ := http.NewRequest("PATCH", djangoURL, bytes.NewBuffer(jsonPayload))
	req.Header.Set("Content-Type", "application/json")
	httpClient := &http.Client{Timeout: time.Second * 15}
	_, err = httpClient.Do(req)
	if err != nil {
		log.Printf("ERROR [ID %d]: Failed to send callback to Django: %v", payload.TodoID, err)
		logData.Status = "FAILED"
		return
	}

	log.Printf("SUCCESS [ID %d]: Process completed and callback sent.", logData.TodoID)
}

func writeLogEntry(logData LogData) error {
	sqlStmt := `
	INSERT INTO logs_goservicelogs (todo, title, description, remind_at, weather_status, notes, image_prompt, status)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?);
	`
	_, err := db.Exec(sqlStmt,
		logData.TodoID,
		logData.Title,
		logData.Description,
		logData.RemindAt,
		logData.Weather,
		logData.Notes,
		logData.ImagePrompt,
		logData.Status,
	)
	if err != nil {
		return fmt.Errorf("failed to insert log entry: %w", err)
	}
	return nil
}

func generateImageWithImagen(ctx context.Context, prompt string) (string, error) {
	endpoint := fmt.Sprintf("%s-aiplatform.googleapis.com:443", gcpLocation)
	clientOptions := []option.ClientOption{
		option.WithEndpoint(endpoint),
		option.WithGRPCDialOption(grpc.WithTimeout(90 * time.Second)),
		option.WithGRPCDialOption(grpc.WithKeepaliveParams(keepalive.ClientParameters{
			Time:    30 * time.Second,
			Timeout: 15 * time.Second,
		})),
	}

	client, err := vertexai.NewPredictionClient(ctx, clientOptions...)

	if err != nil {
		return "", fmt.Errorf("error creating prediction client for endpoint %s: %w", endpoint, err)
	}
	defer client.Close()

	instance, err := structToValue(map[string]interface{}{
		"prompt":           prompt,
		"number_of_images": 1,
		"sample_steps":     20,
		"aspect_ratio":     "1:1",
	})
	if err != nil {
		return "", fmt.Errorf("error creating instance value: %w", err)
	}

	req := &vertexaipb.PredictRequest{
		Endpoint:  fmt.Sprintf("projects/%s/locations/%s/publishers/google/models/imagegeneration@006", gcpProjectID, gcpLocation),
		Instances: []*structpb.Value{instance},
	}

	resp, err := client.Predict(ctx, req)
	if err != nil {
		return "", fmt.Errorf("error from prediction api: %w", err)
	}

	if len(resp.Predictions) == 0 {
		return "", fmt.Errorf("no predictions returned")
	}

	prediction := resp.Predictions[0].GetStructValue().AsMap()
	imageBase64, ok := prediction["bytesBase64Encoded"].(string)
	if !ok {
		return "", fmt.Errorf("could not find or parse bytesBase64Encoded field from response")
	}

	return imageBase64, nil
}

func extractContent(resp *genai.GenerateContentResponse) string {
	var b strings.Builder
	for _, cand := range resp.Candidates {
		if cand.Content != nil {
			for _, part := range cand.Content.Parts {
				if txt, ok := part.(genai.Text); ok {
					b.WriteString(string(txt))
				}
			}
		}
	}
	rawText := b.String()
	cleanText := strings.TrimSpace(rawText)
	cleanText = strings.TrimPrefix(cleanText, "```json")
	cleanText = strings.TrimSuffix(cleanText, "```")
	return strings.TrimSpace(cleanText)
}

func structToValue(v interface{}) (*structpb.Value, error) {
	b, err := json.Marshal(v)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal struct to JSON: %w", err)
	}
	val := &structpb.Value{}
	if err := val.UnmarshalJSON(b); err != nil {
		return nil, fmt.Errorf("failed to unmarshal JSON to protobuf Value: %w", err)
	}
	return val, nil
}

func initDB() error {
	sqlStmt := `
    CREATE TABLE IF NOT EXISTS logs_goservicelogs (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        todo INTEGER,
        title TEXT,
        description TEXT,
        remind_at DATETIME,
        weather_status TEXT,
        notes TEXT,
        image_prompt TEXT,
        status TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    `
	_, err := db.Exec(sqlStmt)
	if err != nil {
		return fmt.Errorf("failed to create table: %w", err)
	}
	log.Println("Database table 'logs_goservicelogs' is ready.")
	return nil
}
