from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from v1.main import app as v1_app
from v2.main import app as v2_app

app = FastAPI(title="Main App - API Version Selector")

app.mount("/v1", v1_app)
app.mount("/v2", v2_app)


# --- Root Endpoint ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """
    Provides a landing page with links to the API version documentation.
    """
    return """
    <html>
        <head>
            <title>API Version Selector</title>
            <style>
                body { font-family: sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .container { text-align: center; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                a { display: inline-block; text-decoration: none; background-color: #007BFF; color: white; padding: 10px 20px; margin: 10px; border-radius: 5px; transition: background-color 0.3s; }
                a:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>API Documentation</h1>
                <p>Please choose a version to view the documentation:</p>
                <a href="/v1/redoc">Version 1 Docs (ReDoc)</a>
                <a href="/v2/redoc">Version 2 Docs (ReDoc)</a>
            </div>
        </body>
    </html>
    """
