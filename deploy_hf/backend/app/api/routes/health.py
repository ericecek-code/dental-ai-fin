from fastapi import APIRouter
from pathlib import Path

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "healthy"}
