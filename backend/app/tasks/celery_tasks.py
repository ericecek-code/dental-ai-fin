from celery import Celery
from app.ml.preprocessor import ImageEnhancer
from app.ml.detector import Detector
import numpy as np
import cv2

celery_app = Celery(
    "dental-ai",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

enhancer = ImageEnhancer()
detector = Detector(model_path="../weights/yolov8x_dental.pt")


@celery_app.task(bind=True)
def analyze_xray_task(self, image_bytes: bytes):
    self.update_state(state="PROGRESS", meta={"step": "preprocessing"})
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    enhanced = enhancer.enhance(image)["enhanced"]

    self.update_state(state="PROGRESS", meta={"step": "detection"})
    detections = detector.predict(enhanced)

    return {"status": "done", "detections": detections}
