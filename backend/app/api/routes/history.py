"""
History router – zobrazuje históriu analýz a umožňuje export.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.ml.database import get_history, export_json, export_csv

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def list_history(limit: int = 50):
    """Vráti zoznam posledných analýz."""
    return get_history(limit)


@router.get("/{job_id}/json")
def get_json(job_id: str):
    """Export analýzy ako JSON."""
    data = export_json(job_id)
    if not data:
        raise HTTPException(404, "Analysis not found")
    return data


@router.get("/{job_id}/csv")
def get_csv(job_id: str):
    """Export detekcií ako CSV."""
    csv = export_csv(job_id)
    if not csv:
        raise HTTPException(404, "Analysis not found")
    return PlainTextResponse(csv, media_type="text/csv")


@router.get("/{job_id}/measurements")
def get_measurements(job_id: str):
    """Vráti iba merania pre danú analýzu."""
    data = export_json(job_id)
    if not data:
        raise HTTPException(404, "Analysis not found")
    return {
        "job_id": job_id,
        "measurements": data.get("measurements", []),
        "health_score": data.get("health_score", 0),
    }
