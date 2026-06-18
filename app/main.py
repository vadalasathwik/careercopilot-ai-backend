from fastapi import FastAPI

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