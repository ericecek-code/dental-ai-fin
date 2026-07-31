from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
import json
import cv2

from app.core.config import settings
from app.ml.reporter import generate_pdf
from app.ml.heatmap import HeatmapGenerator
from app.ml.database import export_json, export_csv

router = APIRouter(prefix="/results", tags=["results"])

REPORT_DIR = Path("/tmp/dental-ai/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("/tmp/dental-ai/outputs")


def _verify_token(job_id: str, token: str | None) -> dict:
    """Over access token pre daný job. Vráti result dict."""
    data = export_json(job_id)
    if not data:
        job_file = OUTPUT_DIR / f"{job_id}.json"
        if job_file.exists():
            try:
                data = json.loads(job_file.read_text())
            except Exception:
                pass
    if not data:
        raise HTTPException(404, "Analysis not found")

    # Ak je API_TOKEN nastavený, over access_token
    if settings.api_token and settings.api_token != "replace-with-generated-token":
        expected = data.get("access_token")
        if expected and token != expected:
            raise HTTPException(403, "Invalid or missing access token")

    return data


def _check_file_access(job_id: str, token: str | None, suffix: str) -> Path:
    """Over prístup k súboru (image endpoints — len existence + token)."""
    file_path = OUTPUT_DIR / f"{job_id}{suffix}"
    if not file_path.exists():
        raise HTTPException(404, f"File not found")

    # Token check len ak je API_TOKEN nastavený
    if settings.api_token and settings.api_token != "replace-with-generated-token":
        # Over či job existuje a token sedí
        job_file = OUTPUT_DIR / f"{job_id}.json"
        if job_file.exists():
            try:
                data = json.loads(job_file.read_text())
                expected = data.get("access_token")
                if expected and token != expected:
                    raise HTTPException(403, "Invalid or missing access token")
            except HTTPException:
                raise
            except Exception:
                pass

    return file_path


@router.get("/{job_id}")
def get_results(job_id: str, token: str | None = Query(default=None)):
    """Return the detection result JSON for a given job."""
    return _verify_token(job_id, token)


@router.get("/{job_id}/original")
def get_original(job_id: str, token: str | None = Query(default=None)):
    """Return the enhanced PNG WITHOUT detection boxes."""
    path = _check_file_access(job_id, token, "_enhanced.png")
    return FileResponse(str(path), media_type="image/png")


@router.get("/{job_id}/overlay")
def get_overlay(job_id: str, token: str | None = Query(default=None)):
    """Return the enhanced PNG with detections drawn (if any)."""
    path = _check_file_access(job_id, token, "_overlay.png")
    return FileResponse(str(path), media_type="image/png")


# ---------------------------------------------------------------------------
# Enhancement image endpoints (CLAHE, pseudocolor, heatmap)
# ---------------------------------------------------------------------------

@router.get("/{job_id}/enhanced")
async def get_enhanced(job_id: str, token: str | None = Query(default=None)):
    """Return CLAHE-enhanced image as a PNG."""
    try:
        path = _check_file_access(job_id, token, "_enhanced.png")
        return FileResponse(str(path), media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced image failed: {e}")


@router.get("/{job_id}/pseudocolor")
async def get_pseudocolor(job_id: str, colormap: str = "bone", token: str | None = Query(default=None)):
    """Return pseudocolor-enhanced version as a PNG image."""
    try:
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

        _, buffer = cv2.imencode('.png', colored)
        tmp_path = OUTPUT_DIR / f"{job_id}_pseudocolor_{colormap}.png"
        tmp_path.write_bytes(buffer.tobytes())
        return FileResponse(str(tmp_path), media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pseudocolor failed: {e}")


@router.get("/{job_id}/heatmap")
async def get_heatmap(job_id: str, token: str | None = Query(default=None)):
    """Return Grad-CAM heatmap overlay as a PNG image."""
    try:
        data = _verify_token(job_id, token)
        detections = data.get("detections", [])

        enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
        image = cv2.imread(str(enhanced_path))
        if image is None:
            raise HTTPException(404, "Image not found")

        from app.ml.heatmap import HeatmapGenerator
        heatmap = HeatmapGenerator.generate(detections, image.shape)
        overlay = HeatmapGenerator.overlay(image, heatmap, alpha=0.45)

        _, buffer = cv2.imencode('.png', overlay)
        tmp_path = OUTPUT_DIR / f"{job_id}_heatmap.png"
        tmp_path.write_bytes(buffer.tobytes())
        return FileResponse(str(tmp_path), media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap failed: {e}")


@router.get("/{job_id}/report")
def get_report(job_id: str, token: str | None = Query(default=None)):
    data = _verify_token(job_id, token)
    output_path = REPORT_DIR / f"{job_id}.pdf"
    generate_pdf(data, str(output_path))
    return FileResponse(str(output_path), media_type="application/pdf")


# ---------------------------------------------------------------------------
# Export / measurement endpoints
# ---------------------------------------------------------------------------

@router.get("/{job_id}/json")
def get_json_export(job_id: str, token: str | None = Query(default=None)):
    """Export analysis as JSON from database."""
    data = export_json(job_id)
    if not data:
        return _verify_token(job_id, token)
    return data


@router.get("/{job_id}/csv")
def get_csv_export(job_id: str, token: str | None = Query(default=None)):
    """Export detections as CSV."""
    _verify_token(job_id, token)
    csv = export_csv(job_id)
    if not csv:
        raise HTTPException(404, "Analysis not found")
    return PlainTextResponse(csv, media_type="text/csv")


@router.get("/{job_id}/measurements")
def get_measurements(job_id: str, token: str | None = Query(default=None)):
    """Vráti iba merania (mm) pre danú analýzu."""
    data = _verify_token(job_id, token)
    return {
        "job_id": job_id,
        "measurements": data.get("measurements", []),
        "health_score": data.get("health_score", 0),
    }
