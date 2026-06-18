from fastapi import FastAPI
from sqlalchemy import text
from app.routers.auth import router as auth_router

from app.db.database import engine

app = FastAPI(
    title="CareerCopilot AI API",
    version="1.0.0"
)
app.include_router(auth_router)

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