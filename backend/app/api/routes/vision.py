"""Gemini Vision + Compare API routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import cv2
import numpy as np
import time

router = APIRouter(tags=["vision"])


@router.post("/vision/analyze")
async def vision_analyze(file: UploadFile = File(...)):
    """Gemini Vision analyzes the X-ray independently."""
    from app.ml.gemini_vision import analyze_xray_with_gemini

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".dcm"}:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Unreadable image")

    result = analyze_xray_with_gemini(image)
    return {
        "gemini_detections": result["gemini_detections"],
        "gemini_raw_text": result["gemini_raw_text"],
        "overall_assessment": result["overall_assessment"],
        "success": result["success"],
        "error": result.get("error"),
        "processing_time_ms": result["processing_time_ms"],
    }


@router.post("/analyze/compare")
async def analyze_compare(file: UploadFile = File(...), conf: float = 0.05):
    """Run BOTH YOLO and Gemini, return side-by-side matched results."""
    from app.ml.gemini_vision import analyze_xray_with_gemini, match_yolo_gemini
    from app.ml.detector import Detector
    from app.ml.preprocessor import ImageEnhancer

    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".dcm"}:
        raise HTTPException(400, "Invalid file type")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(400, "Unreadable image")

    enhancer = ImageEnhancer()
    detector = Detector(model_path="weights/yolov8x_dental.pt")

    start = time.time()

    # YOLO detection
    enhanced = enhancer.enhance(image)
    yolo_result = detector.detect(enhanced, conf_threshold=conf)
    yolo_detections = yolo_result.get("detections", [])

    # Gemini detection
    gemini_result = analyze_xray_with_gemini(image)

    # Match results
    comparison = match_yolo_gemini(yolo_detections, gemini_result.get("gemini_detections", []))

    total_ms = round((time.time() - start) * 1000, 1)

    return {
        "yolo": {
            "detections": yolo_detections,
            "count": len(yolo_detections),
        },
        "gemini": {
            "detections": gemini_result.get("gemini_detections", []),
            "raw_text": gemini_result.get("gemini_raw_text", ""),
            "overall_assessment": gemini_result.get("overall_assessment", ""),
            "success": gemini_result.get("success", False),
            "error": gemini_result.get("error"),
            "count": len(gemini_result.get("gemini_detections", [])),
        },
        "comparison": comparison,
        "processing_time_ms": total_ms,
    }
