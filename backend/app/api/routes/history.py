"""
History router — zoznam analýz.

Exporty (/json, /csv, /measurements) zostavaju len v /results/{job_id}/...,
aby existoval jeden zdroj pravdy.
"""

from fastapi import APIRouter

from app.ml.database import get_history

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def list_history(limit: int = 50):
    """Vrati zoznam poslednych analyz."""
    return get_history(limit)
