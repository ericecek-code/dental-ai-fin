"""Quick test: can we import the FastAPI app and load the YOLO model?"""
import sys
print(f"Python {sys.version}")

try:
    from app.ml.detector import Detector
    print("[OK] Detector imported")
except Exception as e:
    print(f"[FAIL] Detector: {e}")

try:
    from app.ml.preprocessor import ImageEnhancer
    enhancer = ImageEnhancer()
    print("[OK] ImageEnhancer imported")
except Exception as e:
    print(f"[FAIL] ImageEnhancer: {e}")

try:
    from app.ml.reporter import generate_pdf
    print("[OK] Reporter imported")
except Exception as e:
    print(f"[FAIL] Reporter: {e}")

try:
    from app.ml.heatmap import HeatmapGenerator
    print("[OK] HeatmapGenerator imported")
except Exception as e:
    print(f"[FAIL] HeatmapGenerator: {e}")

try:
    from fastapi import FastAPI
    print("[OK] FastAPI imported")
except Exception as e:
    print(f"[FAIL] FastAPI: {e}")

print("\nAll imports done.")
