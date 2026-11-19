"""YOLO detector — tenká vrstva nad ultralytics + kanonická taxonómia."""

# IMPORTANT: patch BEFORE any ultralytics import
from . import _dfloss_compat  # noqa: F401  – triggers monkey-patch

import logging
import os
from typing import Dict, List

import numpy as np

from .taxonomy import CLASSES as COLOR_MAP
from .taxonomy import DEFAULT

logger = logging.getLogger(__name__)


def color_for(class_name: str) -> Dict[str, object]:
    """Vráti taxonomický záznam pre triedu; neznámu triedu zaloguje."""
    info = COLOR_MAP.get(class_name)
    if info is None:
        logger.warning("Neznáma trieda modelu: %r – používam DEFAULT", class_name)
        return DEFAULT
    return info


class Detector:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self._quadrant_counters = {1: 0, 2: 0, 3: 0, 4: 0}

    def load(self):
        os.environ.setdefault("YOLO_VERBOSE", "False")
        from ultralytics import YOLO

        self.model = YOLO(self.model_path)

    def assign_tooth_number(self, bbox, image_shape) -> str:
        """Približné zaradenie nálezu do kvadrantu (NIE FDI číslo).

        Vracia "Q<kvadrant>-<poradie>" podľa stredu bounding boxu. Skutočné FDI
        číslo vyžaduje registráciu chrupu, ktorú model neposkytuje.
        """
        if not bbox or len(bbox) < 4 or not image_shape or len(image_shape) < 2:
            return "?"
        h, w = image_shape[:2]
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        if cx < w / 2:
            q = 1 if cy < h / 2 else 3
        else:
            q = 2 if cy < h / 2 else 4
        self._quadrant_counters[q] += 1
        return f"Q{q}-{self._quadrant_counters[q]}"

    def predict(self, image: np.ndarray, conf: float = 0.25) -> List[Dict]:
        if self.model is None:
            self.load()
        self._quadrant_counters = {1: 0, 2: 0, 3: 0, 4: 0}
        results = self.model.predict(source=image, conf=conf, verbose=False)
        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            raw_label = results[0].names[cls_id]
            info = color_for(raw_label)
            bbox = box.xyxy[0].tolist()
            detections.append(
                {
                    "label": info["label"],
                    "label_sk": info["label_sk"],
                    "raw_label": raw_label,
                    "confidence": float(box.conf[0]),
                    "bbox": bbox,
                    "severity": info["severity"],
                    "severity_sk": info["severity_sk"],
                    "color_bgr": list(info["bgr"]),
                    "class_id": cls_id,
                    "tooth_number": self.assign_tooth_number(bbox, image.shape),
                }
            )
        return detections
