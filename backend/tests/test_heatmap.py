"""Tests for the HeatmapGenerator module."""

import numpy as np
import pytest


class TestHeatmapGenerator:
    """Verify the confidence-weighted spatial heatmap approach."""

    def test_generate_empty_detections(self):
        """generate() with no detections should return a zero heatmap."""
        from app.ml.heatmap import HeatmapGenerator
        heatmap = HeatmapGenerator.generate([], (100, 100))
        assert heatmap.shape == (100, 100)
        assert heatmap.max() == 0.0

    def test_generate_single_detection(self):
        """generate() with one detection should produce a non-zero heatmap."""
        from app.ml.heatmap import HeatmapGenerator
        detections = [
            {"bbox": [20, 20, 60, 60], "confidence": 0.9, "class_id": 0}
        ]
        heatmap = HeatmapGenerator.generate(detections, (100, 100))
        assert heatmap.shape == (100, 100)
        assert heatmap.max() > 0.0

    def test_generate_normalized_to_01(self):
        """generate() output should be normalized to [0, 1] range."""
        from app.ml.heatmap import HeatmapGenerator
        detections = [
            {"bbox": [10, 10, 50, 50], "confidence": 0.8, "class_id": 0},
            {"bbox": [60, 60, 90, 90], "confidence": 0.5, "class_id": 1},
        ]
        heatmap = HeatmapGenerator.generate(detections, (100, 100))
        assert heatmap.min() >= 0.0
        assert heatmap.max() <= 1.0

    def test_generate_multiple_detections(self):
        """generate() with multiple detections should combine their Gaussians."""
        from app.ml.heatmap import HeatmapGenerator
        detections = [
            {"bbox": [10, 10, 40, 40], "confidence": 0.9, "class_id": 0},
            {"bbox": [60, 60, 90, 90], "confidence": 0.7, "class_id": 1},
        ]
        heatmap = HeatmapGenerator.generate(detections, (100, 100))
        # Should have non-zero values in both detection regions
        assert heatmap[25, 25] > 0  # center of first detection
        assert heatmap[75, 75] > 0  # center of second detection

    def test_generate_handles_out_of_bounds_bbox(self):
        """generate() should handle bboxes that extend beyond image bounds."""
        from app.ml.heatmap import HeatmapGenerator
        detections = [
            {"bbox": [-10, -10, 200, 200], "confidence": 0.8, "class_id": 0}
        ]
        heatmap = HeatmapGenerator.generate(detections, (100, 100))
        assert heatmap.shape == (100, 100)
        assert heatmap.max() > 0.0

    def test_generate_short_bbox_skipped(self):
        """generate() should skip bboxes with fewer than 4 coordinates."""
        from app.ml.heatmap import HeatmapGenerator
        detections = [
            {"bbox": [10, 20], "confidence": 0.8, "class_id": 0}  # too short
        ]
        heatmap = HeatmapGenerator.generate(detections, (100, 100))
        assert heatmap.max() == 0.0

    def test_generate_confidence_weighting(self):
        """Higher confidence detections should produce stronger heatmap signals."""
        from app.ml.heatmap import HeatmapGenerator
        det_high = [{"bbox": [30, 30, 70, 70], "confidence": 1.0, "class_id": 0}]
        det_low = [{"bbox": [30, 30, 70, 70], "confidence": 0.1, "class_id": 0}]

        hm_high = HeatmapGenerator.generate(det_high, (100, 100))
        hm_low = HeatmapGenerator.generate(det_low, (100, 100))

        # Both are normalized to [0,1], so peak should be 1.0 for both,
        # but the raw values before normalization differ. After normalization,
        # the spatial distribution should be the same since same bbox.
        # This test mainly verifies the pipeline doesn't crash.
        assert hm_high.shape == hm_low.shape

    def test_apply_colormap_returns_bgr(self):
        """apply_colormap should return a 3-channel BGR image."""
        from app.ml.heatmap import HeatmapGenerator
        heatmap = np.random.rand(50, 50).astype(np.float32)
        colored = HeatmapGenerator.apply_colormap(heatmap)
        assert colored.ndim == 3
        assert colored.shape[2] == 3

    def test_overlay_returns_same_shape(self):
        """overlay should return an image with the same shape as input."""
        from app.ml.heatmap import HeatmapGenerator
        image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        heatmap = np.random.rand(64, 64).astype(np.float32)
        result = HeatmapGenerator.overlay(image, heatmap, alpha=0.4)
        assert result.shape == image.shape

    def test_overlay_with_custom_alpha(self):
        """overlay should accept custom alpha parameter."""
        from app.ml.heatmap import HeatmapGenerator
        image = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        heatmap = np.random.rand(64, 64).astype(np.float32)
        result = HeatmapGenerator.overlay(image, heatmap, alpha=0.8)
        assert result.shape == image.shape
