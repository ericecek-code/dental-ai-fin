"""Tests for /analyze/compare (YOLO + Gemini comparison endpoint)."""

from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest


def _png_bytes() -> bytes:
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[:] = (120, 140, 160)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


class TestCompareEndpoint:
    def test_compare_uses_predict_and_enhanced_image(self, client):
        """Regression: vision.py must call Detector.predict, not .detect()."""
        detections = [
            {
                "label": "Caries",
                "label_sk": "Kaz",
                "confidence": 0.9,
                "bbox": [1, 1, 10, 10],
                "severity": "urgent",
            }
        ]
        fake_detector = MagicMock()
        fake_detector.predict.return_value = detections

        gemini_result = {
            "gemini_detections": [],
            "gemini_raw_text": "",
            "overall_assessment": "",
            "success": False,
            "error": "no key",
            "processing_time_ms": 1,
        }

        with patch("app.ml.detector.Detector", return_value=fake_detector), patch(
            "app.ml.gemini_vision.analyze_xray_with_gemini",
            return_value=gemini_result,
        ):
            response = client.post(
                "/analyze/compare",
                files={"file": ("xray.png", _png_bytes(), "image/png")},
            )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["yolo"]["count"] == 1
        fake_detector.predict.assert_called_once()
        # first positional arg must be an image array, not the enhance() dict
        image_arg = fake_detector.predict.call_args[0][0]
        assert isinstance(image_arg, np.ndarray)

    def test_compare_rejects_unreadable_file(self, client):
        response = client.post(
            "/analyze/compare",
            files={"file": ("broken.png", b"not-an-image", "image/png")},
        )
        assert response.status_code == 400
