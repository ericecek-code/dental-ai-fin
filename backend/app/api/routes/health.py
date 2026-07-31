from fastapi import APIRouter
from pathlib import Path
import os

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Health check endpoint pre monitoring a load balancery."""
    # Check if model is loaded
    model_loaded = False
    try:
        weights_dir = Path(__file__).parent.parent.parent / "weights"
        model_loaded = any(weights_dir.glob("*.pt"))
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": "0.1.0",
        "model_loaded": model_loaded,
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
    }
