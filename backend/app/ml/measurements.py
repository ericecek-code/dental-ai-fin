"""
Dental Measurement Module – mm-based measurements on dental X-rays.

Meria vzdialenosti na RTG snímkach v milimetroch.
Kľúčové meranie: CEJ (Cemento-Enamel Junction) → kosťový hrebeň.
"""

from typing import Dict, List, Optional
import numpy as np


class DentalMeasurement:
    """Measures distances on dental X-rays in millimeters."""

    def __init__(self, pixels_per_mm: Optional[float] = None):
        # If pixels_per_mm is None, try to calibrate from image
        self.pixels_per_mm = pixels_per_mm

    def calibrate_from_image(self, image: np.ndarray) -> float:
        """Auto-calibrate using image dimensions.

        For dental X-rays: typical resolution is 300 DPI = ~11.8 px/mm.
        Standard dental film is ~30 mm wide.
        """
        h, w = image.shape[:2]
        # Typical dental X-ray width in pixels: 800–3000
        if 800 < w < 3000:
            estimated_mm = 30.0  # standard dental film width
            return w / estimated_mm
        return 11.8  # fallback: 300 DPI

    def measure_distance(
        self,
        image: np.ndarray,
        point1: tuple,
        point2: tuple,
    ) -> Dict:
        """Measure distance between two points in mm.

        Returns: {pixels, mm, point1, point2}
        """
        if self.pixels_per_mm is None:
            self.pixels_per_mm = self.calibrate_from_image(image)

        x1, y1 = point1
        x2, y2 = point2
        pixels = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        mm = pixels / self.pixels_per_mm

        return {
            "pixels": round(float(pixels), 1),
            "mm": round(float(mm), 1),
            "point1": list(point1),
            "point2": list(point2),
        }

    def measure_cej_to_bone_crest(
        self,
        image: np.ndarray,
        detections: List[Dict],
    ) -> List[Dict]:
        """Measure CEJ (Cemento-Enamel Junction) to bone crest distance.

        This is a key periodontal measurement.
        Returns list of measurements per tooth.
        """
        measurements: List[Dict] = []

        for det in detections:
            if not det.get("tooth_number"):
                continue

            bbox = det.get("bbox", [])
            if not bbox or len(bbox) < 4:
                continue

            x1, y1, x2, y2 = bbox
            # Approximate CEJ at 1/3 from top of tooth
            cej_y = y1 + (y2 - y1) * 0.33
            # Approximate bone crest at 2/3 from top
            crest_y = y1 + (y2 - y1) * 0.67
            cx = (x1 + x2) / 2

            dist = self.measure_distance(image, (cx, cej_y), (cx, crest_y))
            dist["tooth_number"] = det["tooth_number"]
            dist["label"] = det.get("label", "")
            dist["type"] = "CEJ-Bone Crest"

            # Clinical significance – Slovak notes
            mm_val = dist["mm"]
            if mm_val < 2.0:
                dist["status"] = "normal"
                dist["note"] = "Normálna výška kosti"
            elif mm_val < 3.5:
                dist["status"] = "mild"
                dist["note"] = "Mierna resorpcia kosti"
            elif mm_val < 5.0:
                dist["status"] = "moderate"
                dist["note"] = "Stredná resorpcia kosti"
            else:
                dist["status"] = "severe"
                dist["note"] = "Závažná resorpcia kosti"

            measurements.append(dist)

        return measurements
