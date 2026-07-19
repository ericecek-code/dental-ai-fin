"""Test that the backend can import and model loads."""
import sys
print(f"Python {sys.version}")
print(f"CWD: {__import__('os').getcwd()}")
print(f"sys.path[0:3]: {sys.path[:3]}")

try:
    from app.ml.detector import Detector
    print("[OK] Detector imported")
    d = Detector(model_path="weights/yolov8x_dental.pt")
    d.load()
    print(f"[OK] Model loaded, classes: {list(d.model.names.values())[:5]}")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback; traceback.print_exc()
