from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Simple liveness check.
    Confirms the API is running and returns basic app metadata.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }