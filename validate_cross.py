"""Cross-validate: v2 model on v3 dataset + v3 model on v2 dataset (CPU only)."""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

# Patch torch.load for compatibility
import torch
_orig = torch.load
def _patched(*a, **kw):
    kw.setdefault("weights_only", False)
    return _orig(*a, **kw)
torch.load = _patched

from ultralytics import YOLO

ROOT = Path(r"C:\Users\PC1\Desktop\dental-ai")

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

results = {}

# --- Test 1: v2 best.pt on v3 dataset ---
log("=== TEST 1: v2 model → v3 dataset (CPU) ===")
try:
    model_v2 = YOLO(str(ROOT / "runs/detect/train_v2/weights/best.pt"))
    t0 = time.time()
    r = model_v2.val(
        data=str(ROOT / "combined-dataset/data.yaml"),
        device="cpu",
        batch=1,
        imgsz=640,
        workers=0,
    )
    elapsed = time.time() - t0
    results["v2_on_v3"] = {
        "mAP50": round(float(r.box.map50), 4),
        "mAP50_95": round(float(r.box.map), 4),
        "precision": round(float(r.box.mp), 4),
        "recall": round(float(r.box.mr), 4),
        "time_sec": round(elapsed, 1),
    }
    log(f"  mAP50={results['v2_on_v3']['mAP50']:.4f}  "
        f"mAP50-95={results['v2_on_v3']['mAP50_95']:.4f}  "
        f"P={results['v2_on_v3']['precision']:.4f}  "
        f"R={results['v2_on_v3']['recall']:.4f}  "
        f"({elapsed:.0f}s)")
except Exception as e:
    log(f"  ERROR: {e}")
    results["v2_on_v3"] = {"error": str(e)}

# --- Test 2: v3 best.pt on v2 dataset ---
log("=== TEST 2: v3 model → v2 dataset (CPU) ===")
try:
    model_v3 = YOLO(str(ROOT / "runs/detect/train_v3/weights/best.pt"))
    t0 = time.time()
    r = model_v3.val(
        data=str(ROOT / "restorative-ai-bbox/data.yaml"),
        device="cpu",
        batch=1,
        imgsz=1280,
        workers=0,
    )
    elapsed = time.time() - t0
    results["v3_on_v2"] = {
        "mAP50": round(float(r.box.map50), 4),
        "mAP50_95": round(float(r.box.map), 4),
        "precision": round(float(r.box.mp), 4),
        "recall": round(float(r.box.mr), 4),
        "time_sec": round(elapsed, 1),
    }
    log(f"  mAP50={results['v3_on_v2']['mAP50']:.4f}  "
        f"mAP50-95={results['v3_on_v2']['mAP50_95']:.4f}  "
        f"P={results['v3_on_v2']['precision']:.4f}  "
        f"R={results['v3_on_v2']['recall']:.4f}  "
        f"({elapsed:.0f}s)")
except Exception as e:
    log(f"  ERROR: {e}")
    results["v3_on_v2"] = {"error": str(e)}

# --- Summary ---
log("=== VÝSLEDKY ===")
print(json.dumps(results, indent=2))
