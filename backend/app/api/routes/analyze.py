import os
# Patch DFLoss before any ultralytics import
import app.ml._dfloss_compat  # noqa: F401

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
import uuid
import shutil
import json
import secrets
import cv2
import numpy as np

from app.core.config import settings
from app.ml.preprocessor import ImageEnhancer
from app.ml.detector import Detector
from app.ml.measurements import DentalMeasurement
from app.ml.database import save_analysis

router = APIRouter(prefix="/analyze", tags=["analyze"])

UPLOAD_DIR = Path("/tmp/dental-ai/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path("/tmp/dental-ai/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".dcm"}
ALLOWED_CONTENT_TYPES = {
    "image/png", "image/jpeg", "image/tiff", "image/x-tiff",
    "application/dicom",
}

enhancer = ImageEnhancer()
detector = Detector(model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "weights", "yolov8x_dental.pt"))
measurer = DentalMeasurement()


def _patch_torch_weights_only() -> None:
    try:
        import torch
        try:
            from ultralytics.nn.tasks import DetectionModel
            torch.serialization.add_safe_globals([DetectionModel])
        except Exception:
            pass
        _orig_load = torch.load

        def _patched_load(*args, **kwargs):
            kwargs.setdefault("weights_only", False)
            return _orig_load(*args, **kwargs)

        torch.load = _patched_load
    except Exception:
        pass


_patch_torch_weights_only()


# ---------------------------------------------------------------------------
# Severity / color scheme  (matches frontend)
# ---------------------------------------------------------------------------
_SEVERITY_COLORS = {
    "urgent":     (0, 0, 255),      # red
    "treat_soon": (0, 140, 255),    # orange
    "watch":      (0, 255, 255),    # yellow
}


def _severity_color(severity: str) -> tuple:
    """Return BGR color tuple for a given severity level."""
    return _SEVERITY_COLORS.get(severity, (127, 255, 0))


def _rounded_rect(image: np.ndarray, pt1: tuple, pt2: tuple,
                  color: tuple, thickness: int = 2,
                  radius: int = 8, fill_color: tuple | None = None,
                  fill_alpha: float = 0.25) -> np.ndarray:
    out = image
    x1, y1 = pt1
    x2, y2 = pt2

    if fill_color is not None and fill_alpha > 0:
        overlay = out.copy()
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), fill_color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), fill_color, -1)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, fill_color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, fill_color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, fill_color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, fill_color, -1)
        cv2.addWeighted(overlay, fill_alpha, out, 1 - fill_alpha, 0, out)

    cv2.line(out, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
    cv2.line(out, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
    cv2.line(out, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
    cv2.line(out, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
    cv2.ellipse(out, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
    cv2.ellipse(out, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
    cv2.ellipse(out, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
    cv2.ellipse(out, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

    return out


def _draw_boxes(image: np.ndarray, detections):
    out = image.copy()
    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) < 4:
            continue
        x1, y1, x2, y2 = [int(v) for v in bbox[:4]]
        x1, y1 = max(x1, 0), max(y1, 0)
        x2, y2 = min(x2, out.shape[1]), min(y2, out.shape[0])

        severity = det.get("severity", "watch")
        bgr = _severity_color(severity)
        fill_bgr = bgr

        _rounded_rect(out, (x1, y1), (x2, y2),
                      color=bgr, thickness=2, radius=8,
                      fill_color=fill_bgr, fill_alpha=0.18)

        label = det.get("label", "")
        confidence = det.get("confidence", 0.0)
        tooth = det.get("tooth_number", "")
        text = f"{label} {confidence:.2f}"
        if tooth:
            text += f" [{tooth}]"

        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.45
        (tw, th), baseline = cv2.getTextSize(text, font, scale, 1)
        ty = max(y1 - 6, th + 6)
        cv2.rectangle(out, (x1, ty - th - baseline), (x1 + tw + 4, ty + baseline + 2), bgr, -1)
        cv2.putText(out, text, (x1 + 2, ty), font, scale, (0, 0, 0), 1, cv2.LINE_AA)
    return out


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/")
async def analyze_xray(
    file: UploadFile = File(...),
    conf: float = Query(default=0.05),
    token: str | None = Query(default=None),
):
    # --- Auth: ak je API_TOKEN nastavený, vyžaduj ho ---
    if settings.api_token and settings.api_token != "replace-with-generated-token":
        if token != settings.api_token:
            raise HTTPException(status_code=403, detail="Invalid or missing API token")

    # --- Validácia typu súboru (extension) ---
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # --- Validácia content_type (ak je nastavený) ---
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    # --- Filename sanitácia: iba basename, žiadne path traversal ---
    safe_filename = Path(file.filename).name

    job_id = uuid.uuid4().hex
    upload_path = UPLOAD_DIR / f"{job_id}{suffix}"

    try:
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # --- Upload size limit ---
        file_size_mb = upload_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.upload_max_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {file_size_mb:.1f} MB (max {settings.upload_max_size_mb} MB)",
            )

        # --- Empty file check ---
        if upload_path.stat().st_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        # --- Image decode validation (magic bytes + OpenCV) ---
        image = cv2.imdecode(np.fromfile(str(upload_path), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Unreadable image or invalid image data")

        enhanced = enhancer.enhance(image)["enhanced"]
        enhanced_path = OUTPUT_DIR / f"{job_id}_enhanced.png"
        cv2.imwrite(str(enhanced_path), enhanced)

        # --- Confidence clamp ---
        conf = max(0.005, min(conf, 0.95))

        try:
            detections = detector.predict(enhanced, conf=conf)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Detection failed: {e}")

        overlay = _draw_boxes(enhanced, detections)
        overlay_path = OUTPUT_DIR / f"{job_id}_overlay.png"
        cv2.imwrite(str(overlay_path), overlay)

        by_class: dict = {}
        for det in detections:
            c = det.get("label", "?")
            d = by_class.setdefault(c, {"count": 0, "max_conf": 0.0, "severity": det.get("severity")})
            d["count"] += 1
            d["max_conf"] = max(d["max_conf"], det.get("confidence", 0.0))

        # --- Measurements (mm) ---
        measurements = measurer.measure_cej_to_bone_crest(enhanced, detections)

        # --- Health score (simple heuristic) ---
        urgent = sum(1 for d in detections if d.get("severity") == "urgent")
        treat = sum(1 for d in detections if d.get("severity") == "treat_soon")
        total = len(detections) or 1
        health_score = max(0.0, 1.0 - (urgent * 0.3 + treat * 0.15) / total)

        # --- Access token pre results ---
        access_token = secrets.token_urlsafe(16)

        result = {
            "job_id": job_id,
            "access_token": access_token,
            "status": "done",
            "filename": safe_filename,
            "conf_threshold": conf,
            "enhanced_image_path": str(enhanced_path),
            "overlay_path": str(overlay_path),
            "detection_count": len(detections),
            "by_class": by_class,
            "detections": detections,
            "measurements": measurements,
            "health_score": round(health_score, 2),
        }

        json_path = OUTPUT_DIR / f"{job_id}.json"
        json_path.write_text(json.dumps(result, indent=2))

        # --- Persist to SQLite ---
        try:
            save_analysis(job_id, result)
        except Exception:
            pass  # non-critical

        return result

    except HTTPException:
        # --- Cleanup pri chybe (neodstraňuj úspešné joby) ---
        if upload_path.exists() and not OUTPUT_DIR.exists():
            upload_path.unlink(missing_ok=True)
        raise
    except Exception:
        # --- Cleanup pri neočakávanej chybe ---
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Internal analysis error")
