"""Tests for Pydantic schemas (Detection, AnalyzeResponse)."""

import pytest
from datetime import datetime


class TestDetectionSchema:
    """Verify the Detection Pydantic model."""

    def test_valid_detection(self):
        """A Detection with all required fields should parse correctly."""
        from app.models.schemas import Detection
        det = Detection(
            label="Caries",
            confidence=0.92,
            bbox=[10.0, 20.0, 80.0, 90.0],
        )
        assert det.label == "Caries"
        assert det.confidence == 0.92
        assert det.bbox == [10.0, 20.0, 80.0, 90.0]

    def test_detection_with_optional_fields(self):
        """A Detection with all optional fields should parse correctly."""
        from app.models.schemas import Detection
        det = Detection(
            label="Filling",
            confidence=0.65,
            bbox=[100.0, 50.0, 180.0, 130.0],
            severity="watch",
            tooth_number="Q2-1",
            raw_label="Filling",
            color_bgr=[220, 230, 240],
            class_id=13,
        )
        assert det.severity == "watch"
        assert det.tooth_number == "Q2-1"
        assert det.raw_label == "Filling"
        assert det.color_bgr == [220, 230, 240]
        assert det.class_id == 13

    def test_detection_optional_fields_default_none(self):
        """Optional fields should default to None when omitted."""
        from app.models.schemas import Detection
        det = Detection(label="Caries", confidence=0.9, bbox=[0, 0, 10, 10])
        assert det.severity is None
        assert det.tooth_number is None
        assert det.raw_label is None
        assert det.color_bgr is None
        assert det.class_id is None

    def test_detection_missing_label_raises(self):
        """Detection without required 'label' field should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import Detection
        with pytest.raises(ValidationError):
            Detection(confidence=0.9, bbox=[0, 0, 10, 10])

    def test_detection_missing_confidence_raises(self):
        """Detection without required 'confidence' field should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import Detection
        with pytest.raises(ValidationError):
            Detection(label="Caries", bbox=[0, 0, 10, 10])

    def test_detection_missing_bbox_raises(self):
        """Detection without required 'bbox' field should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import Detection
        with pytest.raises(ValidationError):
            Detection(label="Caries", confidence=0.9)

    def test_detection_json_serialization(self):
        """Detection should serialize to JSON correctly."""
        from app.models.schemas import Detection
        det = Detection(label="Caries", confidence=0.9, bbox=[0, 0, 10, 10])
        j = det.model_dump()
        assert j["label"] == "Caries"
        assert j["confidence"] == 0.9
        assert j["bbox"] == [0, 0, 10, 10]

    def test_detection_from_dict(self):
        """Detection should be constructable from a dictionary."""
        from app.models.schemas import Detection
        data = {"label": "Cyst", "confidence": 0.85, "bbox": [5, 5, 50, 50]}
        det = Detection(**data)
        assert det.label == "Cyst"
        assert det.confidence == 0.85


class TestAnalyzeResponseSchema:
    """Verify the AnalyzeResponse Pydantic model."""

    def test_valid_analyze_response(self):
        """AnalyzeResponse with all required fields should parse correctly."""
        from app.models.schemas import AnalyzeResponse
        resp = AnalyzeResponse(
            job_id="abc123",
            status="done",
            created_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        assert resp.job_id == "abc123"
        assert resp.status == "done"
        assert resp.created_at.year == 2026

    def test_analyze_response_optional_result_url(self):
        """result_url should default to None."""
        from app.models.schemas import AnalyzeResponse
        resp = AnalyzeResponse(
            job_id="abc",
            status="pending",
            created_at=datetime.now(),
        )
        assert resp.result_url is None

    def test_analyze_response_with_result_url(self):
        """result_url should be settable."""
        from app.models.schemas import AnalyzeResponse
        resp = AnalyzeResponse(
            job_id="abc",
            status="done",
            created_at=datetime.now(),
            result_url="/results/abc/report",
        )
        assert resp.result_url == "/results/abc/report"

    def test_analyze_response_missing_job_id_raises(self):
        """AnalyzeResponse without job_id should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import AnalyzeResponse
        with pytest.raises(ValidationError):
            AnalyzeResponse(status="done", created_at=datetime.now())

    def test_analyze_response_missing_status_raises(self):
        """AnalyzeResponse without status should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import AnalyzeResponse
        with pytest.raises(ValidationError):
            AnalyzeResponse(job_id="abc", created_at=datetime.now())

    def test_analyze_response_missing_created_at_raises(self):
        """AnalyzeResponse without created_at should raise ValidationError."""
        from pydantic import ValidationError
        from app.models.schemas import AnalyzeResponse
        with pytest.raises(ValidationError):
            AnalyzeResponse(job_id="abc", status="done")

    def test_analyze_response_json_serialization(self):
        """AnalyzeResponse should serialize to JSON correctly."""
        from app.models.schemas import AnalyzeResponse
        now = datetime(2026, 7, 15, 10, 30, 0)
        resp = AnalyzeResponse(job_id="xyz", status="done", created_at=now)
        j = resp.model_dump()
        assert j["job_id"] == "xyz"
        assert j["status"] == "done"
        assert "created_at" in j

    def test_analyze_response_from_dict(self):
        """AnalyzeResponse should be constructable from a dictionary."""
        from app.models.schemas import AnalyzeResponse
        data = {
            "job_id": "test123",
            "status": "processing",
            "created_at": datetime.now().isoformat(),
        }
        resp = AnalyzeResponse(**data)
        assert resp.job_id == "test123"
        assert resp.status == "processing"
