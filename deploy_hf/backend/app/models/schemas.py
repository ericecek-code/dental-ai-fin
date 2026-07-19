from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Detection(BaseModel):
    label: str
    confidence: float
    bbox: list[float]
    severity: Optional[str] = None
    tooth_number: Optional[str] = None
    raw_label: Optional[str] = None
    color_bgr: Optional[list[int]] = None
    class_id: Optional[int] = None

class AnalyzeResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    result_url: Optional[str] = None
