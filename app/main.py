from fastapi import FastAPI
from sqlalchemy import text

from app.db.database import engine

app = FastAPI(
    title="CareerCopilot AI API",
    version="1.0.0"
)

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

@app.get("/db-health")
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