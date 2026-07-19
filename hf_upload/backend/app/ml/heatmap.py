"""Heatmap generator for dental caries detection.

Uses a confidence-weighted spatial heatmap approach rather than Grad-CAM
(which is unreliable with YOLO's complex architecture). Each detection
creates a Gaussian blob centered on the bbox, weighted by confidence.
This produces a smooth, clinically useful heatmap showing where the model
focused its detections.
"""
import numpy as np
import cv2


class HeatmapGenerator:
    """Generate confidence-weighted spatial heatmaps from detections."""

    @staticmethod
    def generate(detections: list, image_shape: tuple) -> np.ndarray:
        """Create a heatmap from a list of detections.

        Args:
            detections: list of dicts with 'bbox', 'confidence', 'class_id'
            image_shape: (height, width) of the target image

        Returns:
            Heatmap as float32 array in [0, 1] range
        """
        h, w = image_shape[:2]
        heatmap = np.zeros((h, w), dtype=np.float32)

        for det in detections:
            bbox = det.get("bbox", [])
            conf = det.get("confidence", 0.5)
            if len(bbox) < 4:
                continue

            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            bw = (x2 - x1)
            bh = (y2 - y1)

            # Gaussian sigma proportional to bbox size
            sigma_x = max(bw * 0.6, 10)
            sigma_y = max(bh * 0.6, 10)

            # Create gaussian blob
            y_range = np.arange(max(0, int(cy - 3 * sigma_y)),
                                min(h, int(cy + 3 * sigma_y)))
            x_range = np.arange(max(0, int(cx - 3 * sigma_x)),
                                min(w, int(cx + 3 * sigma_x)))

            if len(y_range) == 0 or len(x_range) == 0:
                continue

            xx, yy = np.meshgrid(x_range, y_range)
            gaussian = np.exp(-(((xx - cx) ** 2) / (2 * sigma_x ** 2) +
                                ((yy - cy) ** 2) / (2 * sigma_y ** 2)))

            # Weight by confidence
            gaussian *= conf

            heatmap[np.ix_(y_range, x_range)] += gaussian

        # Normalize to [0, 1]
        max_val = heatmap.max()
        if max_val > 0:
            heatmap /= max_val

        return heatmap

    @staticmethod
    def apply_colormap(heatmap: np.ndarray,
                       colormap: int = cv2.COLORMAP_INFERNO) -> np.ndarray:
        """Apply a colormap to the heatmap, returning a BGR image."""
        heatmap_uint8 = (heatmap * 255).astype(np.uint8)
        return cv2.applyColorMap(heatmap_uint8, colormap)

    @staticmethod
    def overlay(image: np.ndarray, heatmap: np.ndarray,
                alpha: float = 0.4) -> np.ndarray:
        """Overlay heatmap on the original image with alpha blending."""
        colored = HeatmapGenerator.apply_colormap(heatmap)
        # Resize if needed
        if colored.shape[:2] != image.shape[:2]:
            colored = cv2.resize(colored, (image.shape[1], image.shape[0]))
        return cv2.addWeighted(image, 1 - alpha, colored, alpha, 0)
