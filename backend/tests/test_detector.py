"""Tests for the ML Detector module (COLOR_MAP, color_for, Detector class).

These tests verify the pure-logic parts of the detector without loading
any YOLO weights or requiring a GPU.
"""

import pytest
import numpy as np


# ---------------------------------------------------------------------------
# COLOR_MAP tests
# ---------------------------------------------------------------------------
class TestColorMap:
    """Verify the COLOR_MAP dictionary covers all expected dental classes."""

    EXPECTED_CLASSES = [
        "Caries", "Deep Caries", "Crown", "Implant", "Malaligned",
        "Mandibular Canal", "Missing teeth", "Periapical lesion",
        "Retained root", "Root Canal Treatment", "Root Piece",
        "impacted tooth", "Impacted tooth", "Filling", "plating",
        "wire", "Cyst", "Root resorption", "Primary teeth",
    ]

    def test_color_map_has_19_entries(self):
        """COLOR_MAP should have exactly 19 entries."""
        from app.ml.detector import COLOR_MAP
        assert len(COLOR_MAP) == 19

    def test_all_expected_classes_present(self):
        """Every expected class name should be a key in COLOR_MAP."""
        from app.ml.detector import COLOR_MAP
        for cls in self.EXPECTED_CLASSES:
            assert cls in COLOR_MAP, f"Missing class: {cls}"

    def test_each_entry_has_required_keys(self):
        """Every COLOR_MAP entry should have 'bgr', 'severity', and 'label'."""
        from app.ml.detector import COLOR_MAP
        for cls, info in COLOR_MAP.items():
            assert "bgr" in info, f"{cls} missing 'bgr'"
            assert "severity" in info, f"{cls} missing 'severity'"
            assert "label" in info, f"{cls} missing 'label'"

    def test_bgr_values_are_3_tuples(self):
        """Each 'bgr' value should be a tuple/list of exactly 3 integers."""
        from app.ml.detector import COLOR_MAP
        for cls, info in COLOR_MAP.items():
            bgr = info["bgr"]
            assert len(bgr) == 3, f"{cls} bgr has wrong length"
            for v in bgr:
                assert isinstance(v, int), f"{cls} bgr value not int"

    def test_severity_values_are_valid(self):
        """Severity should be one of: urgent, treat_soon, watch."""
        from app.ml.detector import COLOR_MAP
        valid = {"urgent", "treat_soon", "watch"}
        for cls, info in COLOR_MAP.items():
            assert info["severity"] in valid, \
                f"{cls} has invalid severity: {info['severity']}"

    def test_all_severities_represented(self):
        """All three severity levels should appear at least once."""
        from app.ml.detector import COLOR_MAP
        severities = {info["severity"] for info in COLOR_MAP.values()}
        assert severities == {"urgent", "treat_soon", "watch"}

    def test_urgent_classes_are_critical(self):
        """Classes with 'urgent' severity should include Caries, Deep Caries, Periapical lesion."""
        from app.ml.detector import COLOR_MAP
        urgent = {cls for cls, info in COLOR_MAP.items() if info["severity"] == "urgent"}
        assert "Caries" in urgent
        assert "Deep Caries" in urgent
        assert "Periapical lesion" in urgent

    def test_label_matches_key(self):
        """The 'label' value should match the dictionary key (with proper casing)."""
        from app.ml.detector import COLOR_MAP
        # Most labels match their key exactly; check a few
        assert COLOR_MAP["Caries"]["label"] == "Caries"
        assert COLOR_MAP["Filling"]["label"] == "Filling"
        assert COLOR_MAP["Cyst"]["label"] == "Cyst"


# ---------------------------------------------------------------------------
# color_for tests
# ---------------------------------------------------------------------------
class TestColorFor:
    """Verify the color_for() lookup function."""

    def test_known_class_returns_info(self):
        """color_for('Caries') should return the Caries COLOR_MAP entry."""
        from app.ml.detector import color_for
        info = color_for("Caries")
        assert info["severity"] == "urgent"
        assert info["label"] == "Caries"

    def test_unknown_class_returns_default(self):
        """color_for with unknown class should return DEFAULT dict."""
        from app.ml.detector import color_for, DEFAULT
        info = color_for("NonexistentCondition")
        assert info == DEFAULT

    def test_default_has_watch_severity(self):
        """DEFAULT entry should have severity 'watch'."""
        from app.ml.detector import DEFAULT
        assert DEFAULT["severity"] == "watch"

    def test_default_has_unknown_label(self):
        """DEFAULT entry should have label 'Unknown'."""
        from app.ml.detector import DEFAULT
        assert DEFAULT["label"] == "Unknown"

    def test_all_color_map_classes_accessible(self):
        """Every class in COLOR_MAP should be accessible via color_for()."""
        from app.ml.detector import COLOR_MAP, color_for
        for cls, expected in COLOR_MAP.items():
            result = color_for(cls)
            assert result == expected


# ---------------------------------------------------------------------------
# Detector class tests (without loading model)
# ---------------------------------------------------------------------------
class TestDetectorClass:
    """Test Detector initialization and tooth-number assignment logic."""

    def test_init_stores_model_path(self):
        """Detector.__init__ should store the model_path attribute."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.model_path == "/fake/weights.pt"

    def test_init_model_is_none(self):
        """Detector.model should be None until load() is called."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.model is None

    def test_init_quadrant_counters(self):
        """Detector should initialize quadrant counters to zero."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det._quadrant_counters == {1: 0, 2: 0, 3: 0, 4: 0}

    def test_assign_tooth_number_q1(self):
        """bbox center in top-left quadrant → Q1."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        bbox = [10.0, 10.0, 50.0, 50.0]  # center ~(30, 30) in 200×200
        tooth = det.assign_tooth_number(bbox, (200, 200))
        assert tooth.startswith("Q1-")

    def test_assign_tooth_number_q2(self):
        """bbox center in top-right quadrant → Q2."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        bbox = [150.0, 10.0, 190.0, 50.0]  # center ~(170, 30) in 200×200
        tooth = det.assign_tooth_number(bbox, (200, 200))
        assert tooth.startswith("Q2-")

    def test_assign_tooth_number_q3(self):
        """bbox center in bottom-left quadrant → Q3."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        bbox = [10.0, 150.0, 50.0, 190.0]  # center ~(30, 170) in 200×200
        tooth = det.assign_tooth_number(bbox, (200, 200))
        assert tooth.startswith("Q3-")

    def test_assign_tooth_number_q4(self):
        """bbox center in bottom-right quadrant → Q4."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        bbox = [150.0, 150.0, 190.0, 190.0]  # center ~(170, 170) in 200×200
        tooth = det.assign_tooth_number(bbox, (200, 200))
        assert tooth.startswith("Q4-")

    def test_assign_tooth_number_increments(self):
        """Multiple calls in the same quadrant should increment the counter."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        t1 = det.assign_tooth_number([10, 10, 50, 50], (200, 200))
        t2 = det.assign_tooth_number([20, 20, 60, 60], (200, 200))
        assert t1 == "Q1-1"
        assert t2 == "Q1-2"

    def test_assign_tooth_number_empty_bbox(self):
        """Empty bbox should return '?'."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.assign_tooth_number([], (200, 200)) == "?"

    def test_assign_tooth_number_short_bbox(self):
        """bbox with < 4 elements should return '?'."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.assign_tooth_number([10, 20], (200, 200)) == "?"

    def test_assign_tooth_number_empty_shape(self):
        """Empty image_shape should return '?'."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.assign_tooth_number([10, 20, 50, 60], []) == "?"

    def test_assign_tooth_number_short_shape(self):
        """image_shape with < 2 dims should return '?'."""
        from app.ml.detector import Detector
        det = Detector("/fake/weights.pt")
        assert det.assign_tooth_number([10, 20, 50, 60], (200,)) == "?"
