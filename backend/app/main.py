from fastapi import FastAPI

from app.api.routes import health
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-assisted phishing URL detection and analysis platform.",
    version=settings.APP_VERSION,
)

app.include_router(health.router, prefix="/api", tags=["Health"])