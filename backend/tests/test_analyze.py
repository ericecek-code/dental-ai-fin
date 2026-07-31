"""Tests for the POST /analyze endpoint.

All tests mock the YOLO detector and image enhancer so no GPU or real
model weights are required.
"""

import io
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import cv2
import numpy as np
import pytest


def _mock_enhancer():
    """Return a MagicMock enhancer whose enhance() returns a plausible dict."""
    enh = MagicMock()
    fake_enhanced = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    enh.enhance.return_value = {
        "original": fake_enhanced,
        "enhanced": fake_enhanced,
        "enhancement_metrics": {"psnr": 0.0, "ssim": 0.0, "contrast_improvement": 0.0},
    }
    return enh


def _mock_detector():
    """Return a MagicMock detector whose predict() returns sample detections."""
    det = MagicMock()
    det.predict.return_value = [
        {
            "label": "Caries",
            "raw_label": "Caries",
            "confidence": 0.92,
            "bbox": [10.0, 20.0, 80.0, 90.0],
            "severity": "urgent",
            "color_bgr": [0, 215, 255],
            "class_id": 0,
            "tooth_number": "Q1-1",
        }
    ]
    return det


class TestAnalyzeEndpoint:
    """Verify POST /analyze accepts images and returns detection results."""

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_valid_png(self, client, sample_png_bytes):
        """POST /analyze with a valid PNG should return 200 and job_id."""
        response = client.post(
            "/analyze/",
            files={"file": ("test.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "done"

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_valid_jpeg(self, client, sample_jpg_bytes):
        """POST /analyze with a valid JPEG should return 200."""
        response = client.post(
            "/analyze/",
            files={"file": ("xray.jpg", io.BytesIO(sample_jpg_bytes), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_returns_detection_count(self, client, sample_png_bytes):
        """Response should include detection_count matching detections list."""
        response = client.post(
            "/analyze/",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert data["detection_count"] == len(data["detections"])

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_returns_detections_list(self, client, sample_png_bytes):
        """Response should include a 'detections' list."""
        response = client.post(
            "/analyze/",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert isinstance(data["detections"], list)
        assert len(data["detections"]) > 0
        det = data["detections"][0]
        assert "label" in det
        assert "confidence" in det
        assert "bbox" in det
        assert "severity" in det

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_no_file_returns_422(self, client):
        """POST /analyze with no file should return 422 (missing required param)."""
        response = client.post("/analyze/")
        assert response.status_code == 422

    def test_analyze_invalid_extension_returns_400(self, client):
        """POST /analyze with a .txt file should return 400."""
        response = client.post(
            "/analyze/",
            files={"file": ("readme.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid file type" in data["detail"]

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_sets_conf_threshold(self, client, sample_png_bytes):
        """Response should include conf_threshold from the request."""
        response = client.post(
            "/analyze/?conf=0.5",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert data["conf_threshold"] == 0.5

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_clamps_conf_below_min(self, client, sample_png_bytes):
        """Confidence below 0.005 should be clamped to 0.005."""
        response = client.post(
            "/analyze/?conf=0.001",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert data["conf_threshold"] == 0.005

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_clamps_conf_above_max(self, client, sample_png_bytes):
        """Confidence above 0.95 should be clamped to 0.95."""
        response = client.post(
            "/analyze/?conf=1.5",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert data["conf_threshold"] == 0.95

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_by_class_populated(self, client, sample_png_bytes):
        """by_class dict should contain the detected classes."""
        response = client.post(
            "/analyze/",
            files={"file": ("img.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert "Caries" in data["by_class"]
        assert data["by_class"]["Caries"]["count"] == 1

    @patch("app.api.routes.analyze.detector", _mock_detector())
    @patch("app.api.routes.analyze.enhancer", _mock_enhancer())
    def test_analyze_preserves_filename(self, client, sample_png_bytes):
        """Response should echo back the original filename."""
        response = client.post(
            "/analyze/",
            files={"file": ("patient_42.png", io.BytesIO(sample_png_bytes), "image/png")},
        )
        data = response.json()
        assert data["filename"] == "patient_42.png"


class TestAnalyzeHelperFunctions:
    """Test the internal helper functions in the analyze module."""

    def test_severity_color_urgent(self):
        """_severity_color('urgent') should return red BGR tuple."""
        from app.api.routes.analyze import _severity_color
        assert _severity_color("urgent") == (0, 0, 255)

    def test_severity_color_treat_soon(self):
        """_severity_color('treat_soon') should return orange BGR tuple."""
        from app.api.routes.analyze import _severity_color
        assert _severity_color("treat_soon") == (0, 140, 255)

    def test_severity_color_watch(self):
        """_severity_color('watch') should return yellow BGR tuple."""
        from app.api.routes.analyze import _severity_color
        assert _severity_color("watch") == (0, 255, 255)

    def test_severity_color_unknown(self):
        """_severity_color with unknown severity returns default color."""
        from app.api.routes.analyze import _severity_color
        assert _severity_color("unknown") == (127, 255, 0)

    def test_draw_boxes_returns_same_shape(self):
        """_draw_boxes should return an image with the same shape as input."""
        from app.api.routes.analyze import _draw_boxes
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        detections = [
            {"bbox": [10, 10, 50, 50], "severity": "urgent",
             "label": "Caries", "confidence": 0.9, "tooth_number": "Q1-1"},
        ]
        result = _draw_boxes(img, detections)
        assert result.shape == img.shape

    def test_draw_boxes_empty_detections(self):
        """_draw_boxes with no detections returns a copy of the image."""
        from app.api.routes.analyze import _draw_boxes
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        result = _draw_boxes(img, [])
        assert result.shape == img.shape

    def test_draw_boxes_clamps_bbox_to_image(self):
        """_draw_boxes should clamp out-of-bounds bboxes without error."""
        from app.api.routes.analyze import _draw_boxes
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        detections = [
            {"bbox": [-10, -10, 200, 200], "severity": "watch",
             "label": "Filling", "confidence": 0.5, "tooth_number": ""},
        ]
        result = _draw_boxes(img, detections)
        assert result.shape == img.shape
