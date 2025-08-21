# CCHUB Microservice Workshop - Part 2: Building a Scalable & Resilient Ecosystem

Welcome back to the second and final session of our microservices workshop! Today, August 21, 2025, we move from theory to practice. We will take the concepts from Part 1 and build out a fully containerized, polyglot microservices ecosystem. 🚀

Our goal is to implement the services we've designed, tackle the challenges of a distributed system, and integrate modern AI capabilities. Let's get building!

## Today's Architecture: A Polyglot Ecosystem

We are bringing our architecture to life using docker-compose. This setup simulates a real-world production environment where multiple independent services work together. Each service is designed for a specific purpose and can be developed, deployed, and scaled independently.

Here's a breakdown of the services defined in our docker-compose.yml file:

#### Core Infrastructure

- `db` **(PostgreSQL 🐘)**: Our relational database. For this workshop, multiple services will connect to it. In a more mature architecture, you would likely adopt a database-per-service pattern.

- `rabbitmq` **(RabbitMQ 🐇)**: The message broker. This is the backbone of our event-driven architecture. It allows our services to communicate asynchronously, decoupling them and improving resilience. If one service is down, messages can queue up and be processed later.

#### Application Services

- `django` & `celery_worker` **(Python/Django 🐍)**: Our original monolith is now just another service. The django container runs the web server, and the celery_worker handles background tasks (like publishing messages to RabbitMQ) off the main request thread.

- `api-service` **(Python/FastAPI ⚡)**: A new, high-performance microservice built with FastAPI. This could be used to expose a fast, modern API for a mobile client or a single-page application, separate from the original Django monolith.

- `email-service` **(Node.js ✉️)**: A dedicated service whose only job is to send emails. This demonstrates the polyglot nature of microservices—we're using the right tool (or language) for the job. It will listen for events from RabbitMQ and act on them.

- `go-service` **(Go 🤖)**: Our AI-powered microservice. Written in Go for performance, this service integrates with Google's AI Platform (Vertex AI) to provide intelligent features. It can process data and use Gemini to generate text or analyze information, then call back to other services to update them.

### Prerequisites

Before you begin, please ensure you have the following installed and configured:

1. Git: For version control.

2. Docker & Docker Compose: To build and run our containerized services.

3. A Google Cloud Platform (GCP) Account: The `go-service` requires access to Google's AI services. You will need a GCP project with billing enabled to proceed.

### 🛠️ Setup and Configuration

Follow these steps carefully to get the project running.

**Step 1: Clone the Repository**
If you haven't already, clone the project repository to your local machine.

```
# Clone the repository

git clone <your-repository-url>
cd <repository-directory>
```

**Step 2: Configure the Email Service**
The email-service needs credentials to send emails.

1. Create a .env file in the project root by copying the example:

   `cp .env.example .env`

2. Open the new .env file and fill in the details for your email provider (e.g., SendGrid, Mailgun).

**Step 3: Configure the AI Service (Go)**

This is the most critical setup step. The go-service needs credentials to authenticate with Google Cloud.

1. **Select or Create a GCP Project:** Go to the [Google Cloud Console](https://console.cloud.google.com) and select an existing project or create a new one.

2. **Enable the Vertex AI API:**

   - In the console, navigate to "APIs & Services" > "Library".

   - Search for "Vertex AI API" and click **Enable**.

3. **Create a Service Account:**

   - Navigate to "IAM & Admin" > "Service Accounts".

   - Click "**+ CREATE SERVICE ACCOUNT**".

   - Give it a name (e.g., cchub-microservice-account) and a description.

   - Click **"CREATE AND CONTINUE"**.

     In the "Grant this service account access to project" step, add the **"Vertex AI User"** role. This gives it permission to interact with Vertex AI models like Gemini.

     Click **"CONTINUE"**, then **"DONE"**.

4. **Create and Download a JSON Key:**

   - Find your newly created service account in the list.

   - Click on the three-dot menu under "Actions" and select **"Manage keys"**.

   - Click **"ADD KEY"** > **"Create new key"**.

   - Choose JSON as the key type and click **"CREATE"**.

   - A JSON file will be downloaded to your computer. **Rename this file to** `gcp-credentials.json` and place it in the root directory of this project.

5. **Update** `docker-compose.yml`:

   - Open the `docker-compose.yml` file.

   - Find the `go-service` definition.

   - Fill in the `environment` variables with your specific GCP details:

```
        environment:
          - GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json
          - GCP_PROJECT_ID=your-gcp-project-id-here # 👈 UPDATE THIS
          - GCP_LOCATION=us-central1 # 👈 UPDATE THIS (or your preferred location)
          # - GEMINI_API_KEY=... # This is an alternative to a service account
          - GIN_MODE=release
          - DJANGO_CALLBACK_URL_FORMAT=http://django:8000/todos/api/%d/complete/
```

# ▶️ Running the Project

Once all configuration is complete, you can start the entire microservices ecosystem with two commands.

1. **Build the Docker Images:**
   This command builds the images for all our custom services based on their Dockerfiles.

   `docker-compose build`

2. **Start all Services:**
   This command starts all services in detached mode `(-d)`, so they run in the background.

   `docker-compose up -d`

You should see output indicating that all containers are starting up. To check the status and logs:

- **See all running containers:** docker-compose ps

- **View logs for a specific service (e.g., Django):** docker-compose logs -f django

- **Stop all services**: docker-compose down

# 🌐 Exploring the System

With everything running, you can now interact with the different parts of our distributed application:

- **Django Web App:** Open your browser to `http://localhost:8000`

- **FastAPI Service Docs:** Check out the API docs at `http://localhost:8001/docs`

- **RabbitMQ Management UI:** Monitor queues and messages at `http://localhost:15672` (Login with guest/guest)

Try creating a new "To-Do" item in the Django app. Watch the logs and the RabbitMQ dashboard to see how an event is published and consumed by the `email-service` and the `go-service `to trigger actions across the system.

Enjoy the hands-on experience!
