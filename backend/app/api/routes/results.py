from pathlib import Path
import json

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse

from app.core.config import settings
from app.ml.reporter import generate_pdf

try:  # app.ml.database is the single source of truth for persisted analyses
    from app.ml.database import export_csv, export_json
except ImportError:  # pragma: no cover - DB module optional
    export_csv = None
    export_json = None

router = APIRouter(prefix="/results", tags=["results"])

REPORT_DIR = settings.data_path / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = settings.data_path / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = settings.data_path / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# PNG výstupy z analýzy majú ~2,5 MB. Pre prehliadač ich servírujeme ako JPEG
# (q=90) a držíme na disku, aby druhý a ďalší request nič neprekódoval.
JPEG_QUALITY = 90
CACHE_HEADERS = {"Cache-Control": "public, max-age=86400, immutable"}


def _load_result(job_id: str) -> dict:
    """Load a result from SQLite, falling back to the job JSON file."""
    data = export_json(job_id) if export_json else None
    if not data:
        job_file = OUTPUT_DIR / f"{job_id}.json"
        if job_file.exists():
            try:
                data = json.loads(job_file.read_text(encoding="utf-8"))
            except Exception:
                data = None
    if not data:
        raise HTTPException(404, "Analysis not found")
    return data


def _check_file_access(job_id: str, token: str | None, suffix: str) -> Path:
    """Return the output file for a job, or 404.

    API access is enforced by AuthMiddleware (X-API-Key / Bearer). Per-job
    tokens are no longer required so every endpoint behaves the same way.
    """
    file_path = OUTPUT_DIR / f"{job_id}{suffix}"
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    return file_path


def _cache_path(cache_key: str) -> Path:
    return CACHE_DIR / f"{cache_key}.jpg"


def _jpeg_response(image: np.ndarray, cache_key: str) -> FileResponse:
    """Zakóduje obrázok do JPEG (raz) a vráti ho s dlhou cache hlavičkou."""
    cache = _cache_path(cache_key)
    if not cache.exists():
        ok, buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        )
        if not ok:
            raise HTTPException(500, "Image encoding failed")
        cache.write_bytes(buffer.tobytes())
    return FileResponse(str(cache), media_type="image/jpeg", headers=CACHE_HEADERS)


def _file_jpeg_response(source: Path, cache_key: str) -> FileResponse:
    """Serve a stored PNG as cached JPEG (transcode only when stale)."""
    cache = _cache_path(cache_key)
    if not cache.exists() or cache.stat().st_mtime < source.stat().st_mtime:
        image = cv2.imread(str(source))
        if image is None:
            raise HTTPException(404, "Image unreadable")
        return _jpeg_response(image, cache_key)
    return FileResponse(str(cache), media_type="image/jpeg", headers=CACHE_HEADERS)


@router.get("/{job_id}")
def get_results(job_id: str, token: str | None = Query(default=None)):
    """Return the detection result JSON for a given job."""
    return _load_result(job_id)


@router.get("/{job_id}/original")
def get_original(job_id: str, token: str | None = Query(default=None)):
    """Return the enhanced scan WITHOUT detection boxes (JPEG)."""
    path = _check_file_access(job_id, token, "_enhanced.png")
    return _file_jpeg_response(path, f"{job_id}_original")


@router.get("/{job_id}/overlay")
def get_overlay(job_id: str, token: str | None = Query(default=None)):
    """Return the enhanced scan with detections drawn (JPEG)."""
    path = _check_file_access(job_id, token, "_overlay.png")
    return _file_jpeg_response(path, f"{job_id}_overlay")


# ---------------------------------------------------------------------------
# Enhancement image endpoints (CLAHE, pseudocolor, heatmap)
# ---------------------------------------------------------------------------

@router.get("/{job_id}/enhanced")
def get_enhanced(job_id: str, token: str | None = Query(default=None)):
    """Return the CLAHE-enhanced scan (JPEG)."""
    path = _check_file_access(job_id, token, "_enhanced.png")
    return _file_jpeg_response(path, f"{job_id}_enhanced")


@router.get("/{job_id}/pseudocolor")
def get_pseudocolor(
    job_id: str,
    colormap: str = "bone",
    token: str | None = Query(default=None),
):
    """Return pseudocolor-enhanced version as a JPEG (cached per colormap)."""
    cache_key = f"{job_id}_pseudocolor_{colormap}"
    cache = _cache_path(cache_key)
    if cache.exists():
        return FileResponse(str(cache), media_type="image/jpeg", headers=CACHE_HEADERS)

    path = _check_file_access(job_id, token, "_enhanced.png")
    image = cv2.imread(str(path))
    if image is None:
        raise HTTPException(404, "Image unreadable")

    cmap_map = {
        "bone": cv2.COLORMAP_BONE,
        "inferno": cv2.COLORMAP_INFERNO,
        "jet": cv2.COLORMAP_JET,
        "magma": cv2.COLORMAP_MAGMA,
        "turbo": cv2.COLORMAP_TURBO,
    }
    cmap = cmap_map.get(colormap, cv2.COLORMAP_BONE)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    colored = cv2.applyColorMap(gray, cmap)
    return _jpeg_response(colored, cache_key)


@router.get("/{job_id}/heatmap")
def get_heatmap(job_id: str, token: str | None = Query(default=None)):
    """Return a confidence-weighted heatmap overlay as a JPEG (cached)."""
    cache_key = f"{job_id}_heatmap"
    cache = _cache_path(cache_key)
    if cache.exists():
        return FileResponse(str(cache), media_type="image/jpeg", headers=CACHE_HEADERS)

    from app.ml.heatmap import HeatmapGenerator

    data = _load_result(job_id)
    detections = data.get("detections", [])

    enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
    image = cv2.imread(str(enhanced_path))
    if image is None:
        raise HTTPException(404, "Image not found")

    heatmap = HeatmapGenerator.generate(detections, image.shape)
    overlay = HeatmapGenerator.overlay(image, heatmap, alpha=0.45)
    return _jpeg_response(overlay, cache_key)


@router.get("/{job_id}/report")
def get_report(job_id: str, token: str | None = Query(default=None)):
    """Generate (and return) a PDF report for the job."""
    data = _load_result(job_id)
    output_path = REPORT_DIR / f"{job_id}.pdf"

    # Overlay musíme odovzdať explicitne: SQLite záznam neuchováva cesty
    # k obrázkom, takže bez tohto by report vyšiel bez snímky.
    overlay = OUTPUT_DIR / f"{job_id}_overlay.png"
    if not overlay.exists():
        overlay = OUTPUT_DIR / f"{job_id}_enhanced.png"

    generate_pdf(
        data,
        str(output_path),
        image_path=str(overlay) if overlay.exists() else None,
        measurements=data.get("measurements"),
        patient_id=data.get("patient_id"),
        xray_type=data.get("xray_type", "panoramic"),
    )
    return FileResponse(str(output_path), media_type="application/pdf")


# ---------------------------------------------------------------------------
# Export / measurement endpoints
# ---------------------------------------------------------------------------

@router.get("/{job_id}/json")
def get_json_export(job_id: str, token: str | None = Query(default=None)):
    """Export analysis as JSON from database."""
    data = export_json(job_id) if export_json else None
    if not data:
        data = _load_result(job_id)
    return data


@router.get("/{job_id}/csv")
def get_csv_export(job_id: str, token: str | None = Query(default=None)):
    """Export detections as CSV."""
    _load_result(job_id)
    csv = export_csv(job_id) if export_csv else None
    if not csv:
        raise HTTPException(404, "Analysis not found")
    return PlainTextResponse(csv, media_type="text/csv")


@router.get("/{job_id}/measurements")
def get_measurements(job_id: str, token: str | None = Query(default=None)):
    """Return only the millimeter measurements for an analysis."""
    data = _load_result(job_id)
    return {
        "job_id": job_id,
        "measurements": data.get("measurements", []),
        "health_score": data.get("health_score", 0),
    }
