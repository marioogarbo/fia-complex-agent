import os
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

load_dotenv(override=True)

# Define the base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = os.path.join(BASE_DIR)

# Database URI for session management
USE_IN_MEMORY_SESSION = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"
SESSION_SERVICE_URI = os.getenv("DATABASE_URL", USE_IN_MEMORY_SESSION)

# Example allowed origins for CORS
ALLOWED_ORIGINS = ["*"]

# Create FastAPI app
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=True,
)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    )