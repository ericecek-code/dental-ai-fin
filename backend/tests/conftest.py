"""Shared pytest fixtures for the Dental AI backend test suite.

Provides test client, sample images, mock detector, and temp directories
so individual test modules stay clean and focused.
"""

import io
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Make sure the backend package is importable from the tests directory.
# ---------------------------------------------------------------------------
_backend_root = str(Path(__file__).resolve().parent.parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)


# ---------------------------------------------------------------------------
# FastAPI TestClient
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def client():
    """Return a FastAPI TestClient wired to the app.

    The heavy YOLO imports are patched so no GPU or model weights are needed.
    """
    # Patch ultralytics before importing the app (module-level imports)
    _mock_ultralytics()
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


def _mock_ultralytics():
    """Install a fake ultralytics module so that detector / analyze imports
    succeed without the real ultralytics package or model weights."""
    if "ultralytics" in sys.modules:
        return  # already loaded (real or mock)
    mock_mod = MagicMock()
    mock_yolo_cls = MagicMock()
    mock_mod.YOLO = mock_yolo_cls
    sys.modules["ultralytics"] = mock_mod
    sys.modules["ultralytics.nn"] = MagicMock()
    sys.modules["ultralytics.nn.tasks"] = MagicMock()
    sys.modules["ultralytics.utils"] = MagicMock()
    sys.modules["ultralytics.utils.loss"] = MagicMock()

    # Also patch torch if not present
    if "torch" not in sys.modules:
        torch_mock = MagicMock()
        sys.modules["torch"] = torch_mock
        sys.modules["torch.nn"] = MagicMock()
        sys.modules["torch.nn.functional"] = MagicMock()
        sys.modules["torch.serialization"] = MagicMock()


# ---------------------------------------------------------------------------
# Sample image fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_png_bytes():
    """Return raw PNG bytes for a small 64×64 test image."""
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[:] = (100, 150, 200)  # BGR colour
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


@pytest.fixture
def sample_jpg_bytes():
    """Return raw JPEG bytes for a small 64×64 test image."""
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[:] = (80, 120, 180)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


@pytest.fixture
def sample_image_array():
    """Return a 64×64×3 BGR numpy array (valid dental-xray-like image)."""
    img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    return img


@pytest.fixture
def large_image_bytes():
    """Return PNG bytes for a 2048×2048 image (useful for upscale tests)."""
    img = np.random.randint(0, 255, (2048, 2048, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


@pytest.fixture
def tiny_image_bytes():
    """Return PNG bytes for a 32×32 image (triggers upscale path)."""
    img = np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


# ---------------------------------------------------------------------------
# Mock detector fixture
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_detector():
    """Return a MagicMock Detector with predict() returning sample detections."""
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
        },
        {
            "label": "Filling",
            "raw_label": "Filling",
            "confidence": 0.65,
            "bbox": [100.0, 50.0, 180.0, 130.0],
            "severity": "watch",
            "color_bgr": [220, 230, 240],
            "class_id": 13,
            "tooth_number": "Q2-1",
        },
    ]
    return det


# ---------------------------------------------------------------------------
# Temp directories
# ---------------------------------------------------------------------------
@pytest.fixture
def tmp_upload_dir(tmp_path):
    """Provide a temporary upload directory."""
    d = tmp_path / "uploads"
    d.mkdir()
    return d


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Provide a temporary output directory pre-populated with sample files."""
    d = tmp_path / "outputs"
    d.mkdir()
    return d


@pytest.fixture
def tmp_report_dir(tmp_path):
    """Provide a temporary report directory."""
    d = tmp_path / "reports"
    d.mkdir()
    return d


@pytest.fixture
def sample_result_dict():
    """Return a realistic result dict matching the /analyze response shape."""
    return {
        "job_id": "abc123",
        "status": "done",
        "filename": "test_xray.png",
        "conf_threshold": 0.25,
        "enhanced_image_path": "/tmp/dental-ai/outputs/abc123_enhanced.png",
        "overlay_path": "/tmp/dental-ai/outputs/abc123_overlay.png",
        "detection_count": 2,
        "by_class": {
            "Caries": {"count": 1, "max_conf": 0.92, "severity": "urgent"},
            "Filling": {"count": 1, "max_conf": 0.65, "severity": "watch"},
        },
        "detections": [
            {
                "label": "Caries",
                "raw_label": "Caries",
                "confidence": 0.92,
                "bbox": [10.0, 20.0, 80.0, 90.0],
                "severity": "urgent",
                "color_bgr": [0, 215, 255],
                "class_id": 0,
                "tooth_number": "Q1-1",
            },
            {
                "label": "Filling",
                "raw_label": "Filling",
                "confidence": 0.65,
                "bbox": [100.0, 50.0, 180.0, 130.0],
                "severity": "watch",
                "color_bgr": [220, 230, 240],
                "class_id": 13,
                "tooth_number": "Q2-1",
            },
        ],
    }
