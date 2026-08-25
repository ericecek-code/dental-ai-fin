#!/usr/bin/env python3
"""Resume YOLOv8x training from last checkpoint."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parent
DATA_YAML = REPO_ROOT / "combined-dataset" / "data.yaml"
OUTPUT_DIR = REPO_ROOT / "runs" / "detect" / "train_v3"
BEST_PT = OUTPUT_DIR / "weights" / "best.pt"
LAST_PT = OUTPUT_DIR / "weights" / "last.pt"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)


def main() -> int:
    log("Resuming YOLOv8x training from last.pt...")

    if not LAST_PT.exists():
        log(f"ERROR: {LAST_PT} not found")
        return 1

    model = YOLO(str(LAST_PT))

    try:
        results = model.train(
            data=str(DATA_YAML),
            epochs=200,
            imgsz=1280,
            batch=2,
            patience=30,
            optimizer="AdamW",
            lr0=0.001,
            lrf=0.01,
            device="0",
            workers=4,
            project=str(REPO_ROOT / "runs" / "detect"),
            name="train_v3",
            exist_ok=True,
            resume=True,
        )
    except Exception as e:
        log(f"ERROR: {e}")
        return 1

    log("Training complete.")

    # Final validation
    try:
        val_model = YOLO(str(BEST_PT))
        val_results = val_model.val(data=str(DATA_YAML), device="0")
        metrics = {
            "mAP50": float(val_results.box.map50),
            "mAP50_95": float(val_results.box.map),
            "precision": float(val_results.box.mp),
            "recall": float(val_results.box.mr),
        }
        log(f"Final metrics: {json.dumps(metrics, indent=2)}")
    except Exception as e:
        log(f"Validation error: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
