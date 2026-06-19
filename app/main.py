from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.routers.auth import router as auth_router
from app.routers.resume import router as resume_router

from app.db.database import engine

app = FastAPI(
    title="CareerCopilot AI API",
    version="1.0.0"
)

# Configure CORS Middleware to allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://careercopilot-ai-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)

@app.get("/")
def root():
    return {
        "message": "CareerCopilot AI API Running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.get("/health/db")
def db_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as e:
        return {
            "database": "failed",
            "error": str(e)
        }