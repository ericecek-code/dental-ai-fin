"""YOLO detector with DFLoss compat patch."""

# IMPORTANT: patch BEFORE any ultralytics import
from . import _dfloss_compat  # noqa: F401  – triggers monkey-patch

from typing import Dict, List
import os
import numpy as np

COLOR_MAP: Dict[str, Dict[str, object]] = {
    "Caries":                  {"bgr": (0, 215, 255), "severity": "urgent",     "label": "Caries"},
    "Deep Caries":             {"bgr": (0,   0, 255), "severity": "urgent",     "label": "Deep Caries"},
    "Crown":                   {"bgr": (209, 206,  0), "severity": "watch",      "label": "Crown"},
    "Implant":                 {"bgr": (180, 130,  0), "severity": "watch",      "label": "Implant"},
    "Malaligned":              {"bgr": (160,  80,  60), "severity": "watch",      "label": "Malaligned"},
    "Mandibular Canal":        {"bgr": (255, 200, 180), "severity": "watch",      "label": "Mandibular Canal"},
    "Missing teeth":           {"bgr": (160,  50,  60), "severity": "treat_soon", "label": "Missing teeth"},
    "Periapical lesion":       {"bgr": (140,  20, 211), "severity": "urgent",     "label": "Periapical lesion"},
    "Retained root":           {"bgr": (40,  60, 130), "severity": "treat_soon", "label": "Retained root"},
    "Root Canal Treatment":    {"bgr": (60, 140, 220), "severity": "watch",      "label": "Root Canal Treatment"},
    "Root Piece":              {"bgr": (40,  40, 100), "severity": "treat_soon", "label": "Root Piece"},
    "impacted tooth":          {"bgr": (200, 100,  20), "severity": "treat_soon", "label": "Impacted tooth"},
    "Impacted tooth":          {"bgr": (200, 100,  20), "severity": "treat_soon", "label": "Impacted tooth"},
    "Filling":                 {"bgr": (220, 230, 240), "severity": "watch",      "label": "Filling"},
    "plating":                 {"bgr": (180, 180, 140), "severity": "watch",      "label": "Plating"},
    "wire":                    {"bgr": (200, 200, 200), "severity": "watch",      "label": "Wire"},
    "Cyst":                    {"bgr": (40,  20, 130), "severity": "treat_soon", "label": "Cyst"},
    "Root resorption":         {"bgr": (130,  40,  60), "severity": "treat_soon", "label": "Root resorption"},
    "Primary teeth":           {"bgr": (200, 220, 240), "severity": "watch",      "label": "Primary teeth"},
}

DEFAULT = {"bgr": (127, 255, 0), "severity": "watch", "label": "Unknown"}


def color_for(class_name: str):
    return COLOR_MAP.get(class_name, DEFAULT)


class Detector:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self._quadrant_counters = {1: 0, 2: 0, 3: 0, 4: 0}

    def _patch_torch_weights_only(self) -> None:
        try:
            import torch
            try:
                from ultralytics.nn.tasks import DetectionModel
                torch.serialization.add_safe_globals([DetectionModel])
            except Exception:
                pass
            _orig = torch.load

            def _patched(*args, **kwargs):
                kwargs.setdefault("weights_only", False)
                return _orig(*args, **kwargs)

            torch.load = _patched
        except Exception:
            pass

    def load(self):
        self._patch_torch_weights_only()
        os.environ.setdefault("YOLO_VERBOSE", "False")
        from ultralytics import YOLO
        self.model = YOLO(self.model_path)

    def assign_tooth_number(self, bbox, image_shape) -> str:
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
            tooth_number = self.assign_tooth_number(bbox, image.shape)
            detections.append({
                "label": info["label"],
                "raw_label": raw_label,
                "confidence": float(box.conf[0]),
                "bbox": bbox,
                "severity": info["severity"],
                "color_bgr": list(info["bgr"]),
                "class_id": cls_id,
                "tooth_number": tooth_number,
            })
        return detections
