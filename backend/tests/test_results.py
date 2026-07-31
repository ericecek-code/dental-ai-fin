"""Tests for the /results endpoints."""

import io
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import cv2
import numpy as np
import pytest


class TestGetResults:
    """Verify GET /results/{job_id} returns detection JSON."""

    def test_unknown_job_returns_unknown_status(self, client):
        """GET /results/{nonexistent_id} should return status: unknown."""
        response = client.get("/results/nonexistent123")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unknown"
        assert data["detections"] == []

    def test_get_results_returns_json(self, client):
        """GET /results/{id} should return JSON content type."""
        response = client.get("/results/some_id")
        assert "application/json" in response.headers["content-type"]


class TestGetOriginal:
    """Verify GET /results/{job_id}/original returns an enhanced PNG image."""

    def test_original_not_found_returns_404(self, client):
        """GET /results/{id}/original with nonexistent job returns 404."""
        response = client.get("/results/nonexistent/original")
        assert response.status_code == 404

    def test_original_returns_png_when_exists(self, client, tmp_output_dir):
        """GET /results/{id}/original returns PNG image when file exists."""
        # Create a fake enhanced image file
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_orig_001"
        img_path = tmp_output_dir / f"{job_id}_enhanced.png"
        cv2.imwrite(str(img_path), img)

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/original")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        # Verify the returned bytes are a valid PNG
        assert response.content[:4] == b'\x89PNG'


class TestGetOverlay:
    """Verify GET /results/{job_id}/overlay returns an overlay PNG image."""

    def test_overlay_not_found_returns_404(self, client):
        """GET /results/{id}/overlay with nonexistent job returns 404."""
        response = client.get("/results/nonexistent/overlay")
        assert response.status_code == 404

    def test_overlay_returns_png_when_exists(self, client, tmp_output_dir):
        """GET /results/{id}/overlay returns PNG when file exists."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_overlay_001"
        img_path = tmp_output_dir / f"{job_id}_overlay.png"
        cv2.imwrite(str(img_path), img)

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/overlay")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


class TestGetEnhanced:
    """Verify GET /results/{job_id}/enhanced returns an enhanced PNG image."""

    def test_enhanced_not_found_returns_404(self, client):
        """GET /results/{id}/enhanced with nonexistent job returns 404."""
        response = client.get("/results/nonexistent/enhanced")
        assert response.status_code == 404

    def test_enhanced_returns_png_when_exists(self, client, tmp_output_dir):
        """GET /results/{id}/enhanced returns PNG when file exists."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_enh_001"
        img_path = tmp_output_dir / f"{job_id}_enhanced.png"
        cv2.imwrite(str(img_path), img)

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/enhanced")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


class TestGetPseudocolor:
    """Verify GET /results/{job_id}/pseudocolor applies color mapping."""

    def test_pseudocolor_not_found_returns_404(self, client):
        """GET /results/{id}/pseudocolor with nonexistent job returns 404."""
        response = client.get("/results/nonexistent/pseudocolor")
        assert response.status_code == 404

    def test_pseudocolor_returns_png_when_exists(self, client, tmp_output_dir):
        """GET /results/{id}/pseudocolor returns a colored PNG."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_pseudo_001"
        img_path = tmp_output_dir / f"{job_id}_enhanced.png"
        cv2.imwrite(str(img_path), img)

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/pseudocolor?colormap=bone")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_pseudocolor_invalid_colormap_defaults(self, client, tmp_output_dir):
        """GET /results/{id}/pseudocolor with unknown colormap defaults to bone."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_pseudo_002"
        img_path = tmp_output_dir / f"{job_id}_enhanced.png"
        cv2.imwrite(str(img_path), img)

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/pseudocolor?colormap=invalid")
        assert response.status_code == 200


class TestGetHeatmap:
    """Verify GET /results/{job_id}/heatmap generates a heatmap overlay."""

    def test_heatmap_not_found_returns_404(self, client):
        """GET /results/{id}/heatmap with nonexistent job returns 404."""
        response = client.get("/results/nonexistent/heatmap")
        assert response.status_code == 404

    def test_heatmap_returns_png_when_exists(self, client, tmp_output_dir):
        """GET /results/{id}/heatmap returns PNG when job files exist."""
        img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        job_id = "test_heatmap_001"

        # Write enhanced image
        img_path = tmp_output_dir / f"{job_id}_enhanced.png"
        cv2.imwrite(str(img_path), img)

        # Write result JSON with detections
        result = {
            "job_id": job_id,
            "detections": [
                {"bbox": [10, 10, 50, 50], "confidence": 0.9, "class_id": 0}
            ],
        }
        json_path = tmp_output_dir / f"{job_id}.json"
        json_path.write_text(json.dumps(result))

        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/heatmap")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


class TestGetReport:
    """Verify GET /results/{job_id}/report generates a PDF report."""

    def test_report_generates_pdf(self, client, tmp_output_dir):
        """GET /results/{id}/report should return a PDF file."""
        job_id = "test_report_001"
        # Write a minimal result JSON
        result = {
            "job_id": job_id,
            "status": "done",
            "filename": "test.png",
            "conf_threshold": 0.25,
            "detection_count": 1,
            "detections": [
                {
                    "label": "Caries",
                    "tooth_number": "Q1-1",
                    "confidence": 0.92,
                    "severity": "urgent",
                }
            ],
        }
        json_path = tmp_output_dir / f"{job_id}.json"
        json_path.write_text(json.dumps(result))

        # Patch the directories
        with patch("app.api.routes.results.OUTPUT_DIR", tmp_output_dir), \
             patch("app.api.routes.results.REPORT_DIR", tmp_output_dir):
            response = client.get(f"/results/{job_id}/report")
        assert response.status_code == 200
        # Verify it starts with PDF magic bytes
        assert response.content[:5] == b'%PDF-'
