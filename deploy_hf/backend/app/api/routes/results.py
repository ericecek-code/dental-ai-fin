from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import json
import cv2

from app.ml.reporter import generate_pdf
from app.ml.heatmap import HeatmapGenerator

router = APIRouter(prefix="/results", tags=["results"])

REPORT_DIR = Path("/tmp/dental-ai/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("/tmp/dental-ai/outputs")


@router.get("/{job_id}")
def get_results(job_id: str):
    """Return the detection result JSON for a given job."""
    job_file = OUTPUT_DIR / f"{job_id}.json"
    if job_file.exists():
        try:
            return json.loads(job_file.read_text())
        except Exception:
            pass
    return {"job_id": job_id, "status": "unknown", "detections": []}


@router.get("/{job_id}/original")
def get_original(job_id: str):
    """Return the enhanced PNG WITHOUT detection boxes."""
    enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
    if not enhanced_path.exists():
        raise HTTPException(status_code=404, detail="Original not found")
    return FileResponse(str(enhanced_path), media_type="image/png")


@router.get("/{job_id}/overlay")
def get_overlay(job_id: str):
    """Return the enhanced PNG with detections drawn (if any)."""
    overlay_path = OUTPUT_DIR / f"{job_id}_overlay.png"
    if not overlay_path.exists():
        raise HTTPException(status_code=404, detail="Overlay not found")
    return FileResponse(str(overlay_path), media_type="image/png")


# ---------------------------------------------------------------------------
# Enhancement image endpoints (CLAHE, pseudocolor, heatmap)
# ---------------------------------------------------------------------------

@router.get("/{job_id}/enhanced")
async def get_enhanced(job_id: str):
    """Return CLAHE-enhanced image as a PNG."""
    try:
        enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
        if not enhanced_path.exists():
            raise HTTPException(404, "Image not found")
        return FileResponse(str(enhanced_path), media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced image failed: {e}")


@router.get("/{job_id}/pseudocolor")
async def get_pseudocolor(job_id: str, colormap: str = "bone"):
    """Return pseudocolor-enhanced version as a PNG image."""
    try:
        enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
        if not enhanced_path.exists():
            raise HTTPException(404, "Image not found")
        image = cv2.imread(str(enhanced_path))
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
async def get_heatmap(job_id: str):
    """Return Grad-CAM heatmap overlay as a PNG image."""
    try:
        json_path = OUTPUT_DIR / f"{job_id}.json"
        if not json_path.exists():
            raise HTTPException(404, "Job not found")
        result = json.loads(json_path.read_text())
        detections = result.get("detections", [])

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
def get_report(job_id: str):
    output_path = REPORT_DIR / f"{job_id}.pdf"
    result = get_results(job_id)
    generate_pdf(result, str(output_path))
    return FileResponse(str(output_path), media_type="application/pdf")