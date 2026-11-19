import sys

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Health check endpoint pre monitoring a load balancery."""
    weights = settings.weights_path
    return {
        "status": "healthy",
        "version": settings.version,
        "model_loaded": weights.exists(),
        "model_path": str(weights),
        "python_version": (
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ),
    }
