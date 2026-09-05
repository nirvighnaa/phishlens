from fastapi import FastAPI

app = FastAPI(
    title="PhishLens API",
    description="AI-assisted phishing URL detection and analysis platform.",
    version="0.1.0",
)


@app.get("/api/health")
def health_check():
    """
    Simple liveness check.
    Returns a fixed status so we can confirm the server is running
    before any real business logic exists.
    """
    return {"status": "ok", "service": "PhishLens API"}