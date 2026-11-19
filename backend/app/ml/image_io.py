"""Načítanie vstupných snímok — JPEG/PNG/TIFF aj DICOM (.dcm).

`cv2.imdecode` DICOM nevie; preto sa robí fallback cez pydicom. Ak pydicom
nie je nainštalovaný, DICOM vráti None a volajúci vráti 400 – nie 500.
"""

import io
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _dicom_to_bgr(data: bytes) -> np.ndarray | None:
    try:
        import pydicom  # type: ignore
    except ImportError:
        logger.warning("DICOM súbor prišiel, ale pydicom nie je nainštalovaný")
        return None

    try:
        dataset = pydicom.dcmread(io.BytesIO(data))
        pixels = dataset.pixel_array.astype(np.float32)

        # Aplikuj rescale (CT/MR modality)
        slope = float(getattr(dataset, "RescaleSlope", 1.0))
        intercept = float(getattr(dataset, "RescaleIntercept", 0.0))
        pixels = pixels * slope + intercept

        # Normalizuj na 0–255
        lo, hi = float(pixels.min()), float(pixels.max())
        if hi > lo:
            pixels = (pixels - lo) / (hi - lo) * 255.0
        pixels = pixels.clip(0, 255).astype(np.uint8)

        if pixels.ndim == 2:
            return cv2.cvtColor(pixels, cv2.COLOR_GRAY2BGR)
        return pixels
    except Exception as exc:  # pragma: no cover - závisí od konkrétneho súboru
        logger.warning("DICOM dekódovanie zlyhalo: %s", exc)
        return None


def decode_image_bytes(data: bytes) -> np.ndarray | None:
    """Vráti BGR numpy array alebo None, ak sa obrázok nedá prečítať."""
    if not data:
        return None

    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is not None:
        return image

    # Fallback: DICOM
    return _dicom_to_bgr(data)


def decode_image_file(path: str) -> np.ndarray | None:
    """Načíta obrázok z disku (vrátane DICOM) ako BGR numpy array."""
    try:
        with open(path, "rb") as handle:
            return decode_image_bytes(handle.read())
    except OSError:
        return None
