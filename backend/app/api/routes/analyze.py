import json
import logging
import secrets
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

# Patch DFLoss before any ultralytics import
import app.ml._dfloss_compat  # noqa: F401

from app.core.config import settings
from app.ml.anonymize import anonymize_upload
from app.ml.image_io import decode_image_file
from app.ml.preprocessor import ImageEnhancer
from app.ml.detector import Detector
from app.ml.measurements import DentalMeasurement
from app.ml.database import save_analysis
from app.ml.scoring import health_score_fraction

router = APIRouter(prefix="/analyze", tags=["analyze"])

logger = logging.getLogger(__name__)

UPLOAD_DIR = settings.data_path / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = settings.data_path / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".dcm"}
ALLOWED_CONTENT_TYPES = {
    "image/png", "image/jpeg", "image/tiff", "image/x-tiff",
    "application/dicom",
}

enhancer = ImageEnhancer()
detector = Detector(model_path=str(settings.weights_path))
measurer = DentalMeasurement()


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

        bgr = tuple(det.get("color_bgr") or _severity_color(det.get("severity", "watch")))
        fill_bgr = bgr

        _rounded_rect(out, (x1, y1), (x2, y2),
                      color=bgr, thickness=2, radius=8,
                      fill_color=fill_bgr, fill_alpha=0.18)

        label = det.get("label_sk") or det.get("label", "")
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

@router.post("", include_in_schema=False)
@router.post("/")
async def analyze_xray(
    file: UploadFile = File(...),
    conf: float = Query(default=settings.default_confidence),
    anonymize: bool = Query(default=True),
):
    # Auth rieši AuthMiddleware cez X-API-Key / Bearer hlavičku (ak je API_TOKEN nastavený).

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
        # --- Upload size limit (streaming, aby sa disk nezaplnil pred kontrolou) ---
        max_bytes = settings.upload_max_size_mb * 1024 * 1024
        written = 0
        with upload_path.open("wb") as buffer:
            while chunk := file.file.read(1024 * 1024):
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large (max {settings.upload_max_size_mb} MB)",
                    )
                buffer.write(chunk)

        # --- Empty file check ---
        if written == 0:
            raise HTTPException(status_code=400, detail="Empty file")

        # --- Odstránenie osobných údajov (pred akýmkoľvek spracovaním) ---
        privacy: dict = {"anonymized": False}
        if anonymize:
            anon = anonymize_upload(upload_path.read_bytes(), suffix)
            if anon.ok:
                upload_path.unlink(missing_ok=True)
                suffix = anon.suffix
                upload_path = UPLOAD_DIR / f"{job_id}{suffix}"
                upload_path.write_bytes(anon.data)
                # Názov súboru často obsahuje meno pacienta -> nahradíme ID úlohy
                safe_filename = f"{job_id}{suffix}"
                privacy = {"anonymized": True, "removed": anon.removed}
            else:
                privacy = {"anonymized": False, "reason": "anonymization_failed"}

        # --- Image decode validation (OpenCV, s fallbackom na DICOM) ---
        image = decode_image_file(str(upload_path))
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

        # --- Health score (jedna implementácia: app.ml.scoring) ---
        health_score = health_score_fraction(detections)

        # --- Access token pre results ---
        # Per-job token sa už nevyžaduje (ochranu rieši API_TOKEN); pole zostáva
        # pre spätnú kompatibilitu klientov, ktorí ho čítajú.
        access_token = secrets.token_urlsafe(16)

        result = {
            "job_id": job_id,
            "access_token": access_token,
            "status": "done",
            "filename": safe_filename,
            "privacy": privacy,
            "conf_threshold": conf,
            "detection_count": len(detections),
            "by_class": by_class,
            "detections": detections,
            "measurements": measurements,
            "health_score": round(health_score, 2),
        }

        json_path = OUTPUT_DIR / f"{job_id}.json"
        json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

        # --- Persist to SQLite ---
        try:
            save_analysis(job_id, result)
        except Exception:
            pass  # non-critical

        # --- Vymazanie obrázkov z disku po analýze (ochrana súkromia) ---
        # Snímka sa nesmie zostať uložená ani po vygenerovaní PDF.
        for p in (enhanced_path, overlay_path):
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass

        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail="Internal analysis error")
    finally:
        # Surový upload (aj s metadátami) nesmie zostať na disku.
        try:
            upload_path.unlink(missing_ok=True)
        except OSError:
            pass
