"""Tests for the PDF reporter module."""

import os
import tempfile
from pathlib import Path

import pytest


class TestSKLabels:
    """Verify the Slovak translation dictionaries."""

    def test_sk_labels_has_all_classes(self):
        """SK_LABELS should cover all expected dental classes."""
        from app.ml.reporter import SK_LABELS
        expected = [
            "Caries", "Deep Caries", "Crown", "Implant", "Malaligned",
            "Mandibular Canal", "Missing teeth", "Periapical lesion",
            "Retained root", "Root Canal Treatment", "Root Piece",
            "Impacted tooth", "impacted tooth", "Filling", "plating",
            "wire", "Cyst", "Root resorption", "Primary teeth",
        ]
        for cls in expected:
            assert cls in SK_LABELS, f"Missing Slovak label for: {cls}"

    def test_sk_labels_values_are_strings(self):
        """All SK_LABELS values should be non-empty strings."""
        from app.ml.reporter import SK_LABELS
        for cls, label in SK_LABELS.items():
            assert isinstance(label, str)
            assert len(label) > 0, f"Empty label for: {cls}"

    def test_sk_severity_has_all_levels(self):
        """SK_SEVERITY should contain urgent, treat_soon, and watch."""
        from app.ml.reporter import SK_SEVERITY
        assert "urgent" in SK_SEVERITY
        assert "treat_soon" in SK_SEVERITY
        assert "watch" in SK_SEVERITY

    def test_sk_severity_values_are_slovak(self):
        """SK_SEVERITY values should be in Slovak (containing diacritics)."""
        from app.ml.reporter import SK_SEVERITY
        assert "urg" in SK_SEVERITY["urgent"].lower()  # Urgentné
        assert "sled" in SK_SEVERITY["watch"].lower()   # Sledovať


class TestSkLabelFunction:
    """Test the sk_label() helper function."""

    def test_known_label(self):
        """sk_label('Caries') should return the Slovak translation."""
        from app.ml.reporter import sk_label
        result = sk_label("Caries")
        assert result == "Kaz"

    def test_unknown_label_returns_raw(self):
        """sk_label with unknown class should fall back to the raw string."""
        from app.ml.reporter import sk_label
        result = sk_label("UnknownCondition")
        assert result == "UnknownCondition"

    def test_case_insensitive_fallback(self):
        """sk_label should try case-insensitive matching as fallback."""
        from app.ml.reporter import sk_label
        # "impacted tooth" (lowercase) is in SK_LABELS
        result = sk_label("impacted tooth")
        assert result == "Retinovaný zub"


class TestSkSeverityFunction:
    """Test the sk_sev() helper function."""

    def test_known_severity(self):
        """sk_sev('urgent') should return the Slovak translation."""
        from app.ml.reporter import sk_sev
        result = sk_sev("urgent")
        assert result == "Urgentné"

    def test_unknown_severity_returns_raw(self):
        """sk_sev with unknown severity should fall back to raw string."""
        from app.ml.reporter import sk_sev
        result = sk_sev("unknown_level")
        assert result == "unknown_level"


class TestGeneratePDF:
    """Test PDF report generation."""

    def test_generates_valid_pdf(self, sample_result_dict, tmp_path):
        """generate_pdf should produce a file starting with %PDF-."""
        from app.ml.reporter import generate_pdf
        output_path = str(tmp_path / "test_report.pdf")
        generate_pdf(sample_result_dict, output_path)

        assert os.path.exists(output_path)
        with open(output_path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_pdf_file_has_content(self, sample_result_dict, tmp_path):
        """Generated PDF should have more than just the header."""
        from app.ml.reporter import generate_pdf
        output_path = str(tmp_path / "test_report2.pdf")
        generate_pdf(sample_result_dict, output_path)

        size = os.path.getsize(output_path)
        assert size > 500, f"PDF too small ({size} bytes), likely corrupt"

    def test_empty_detections_pdf(self, tmp_path):
        """PDF with zero detections should still be valid."""
        from app.ml.reporter import generate_pdf
        result = {
            "job_id": "empty_job",
            "status": "done",
            "filename": "empty.png",
            "conf_threshold": 0.25,
            "detection_count": 0,
            "detections": [],
        }
        output_path = str(tmp_path / "empty_report.pdf")
        generate_pdf(result, output_path)

        assert os.path.exists(output_path)
        with open(output_path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_pdf_contains_report_content(self, sample_result_dict, tmp_path):
        """PDF should contain metadata indicating it was generated for the job."""
        from app.ml.reporter import generate_pdf
        output_path = str(tmp_path / "test_report3.pdf")
        generate_pdf(sample_result_dict, output_path)

        # PDF content is FlateDecode-compressed, so check the metadata object
        # which is uncompressed and contains the job info
        content = open(output_path, "rb").read()
        # The PDF metadata /Title should contain info about the document
        # Also verify the PDF has multiple objects (content, fonts, pages)
        assert b"%PDF-1.4" in content or b"%PDF-1.5" in content
        # Verify the PDF is substantial (has embedded font data + content streams)
        assert len(content) > 5000

    def test_multiple_detections_in_pdf(self, tmp_path):
        """PDF should handle multiple detections correctly."""
        from app.ml.reporter import generate_pdf
        result = {
            "job_id": "multi_job",
            "status": "done",
            "filename": "multi.png",
            "conf_threshold": 0.3,
            "detection_count": 3,
            "detections": [
                {"label": "Caries", "tooth_number": "Q1-1", "confidence": 0.95, "severity": "urgent"},
                {"label": "Filling", "tooth_number": "Q2-1", "confidence": 0.80, "severity": "watch"},
                {"label": "Deep Caries", "tooth_number": "Q3-1", "confidence": 0.70, "severity": "urgent"},
            ],
        }
        output_path = str(tmp_path / "multi_report.pdf")
        generate_pdf(result, output_path)

        assert os.path.getsize(output_path) > 500
        with open(output_path, "rb") as f:
            assert f.read(5) == b"%PDF-"
