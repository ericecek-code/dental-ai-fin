#!/usr/bin/env python3
"""YOLOv8x training on combined dataset - imgsz=1280, 200 epochs."""

import json
import os
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


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)


def main() -> int:
    if not DATA_YAML.exists():
        log(f"ERROR: data.yaml not found at {DATA_YAML}")
        return 1

    log("Starting YOLOv8x training on COMBINED dataset (imgsz=1280, 200 epochs).")
    log(f"Data YAML: {DATA_YAML}")
    log(f"Output:    {OUTPUT_DIR}")

    try:
        model = YOLO("yolov8x.pt")
    except Exception as e:
        log(f"ERROR loading YOLOv8x: {e}")
        return 1

    try:
        results = model.train(
            data=str(DATA_YAML),
            epochs=200,
            imgsz=1280,
            batch=2,  # 1280 needs very small batch on 11GB VRAM
            patience=30,
            optimizer="AdamW",
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=5,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.1,
            copy_paste=0.1,
            device="0",
            workers=4,
            project=str(REPO_ROOT / "runs" / "detect"),
            name="train_v3",
            exist_ok=True,
            pretrained=True,
            verbose=True,
            seed=42,
        )
    except Exception as e:
        log(f"ERROR during training: {e}")
        return 1

    best_pt = OUTPUT_DIR / "weights" / "best.pt"
    last_pt = OUTPUT_DIR / "weights" / "last.pt"

    log(f"Best weights: {best_pt} (exists={best_pt.exists()})")
    log(f"Last weights: {last_pt} (exists={last_pt.exists()})")

    # Run validation
    metrics = {}
    try:
        val_model = YOLO(str(best_pt))
        val_results = val_model.val(data=str(DATA_YAML), device="0")
        metrics = {
            "mAP50": float(val_results.box.map50),
            "mAP50_95": float(val_results.box.map),
            "precision": float(val_results.box.mp),
            "recall": float(val_results.box.mr),
            "fitness": float(val_results.fitness) if hasattr(val_results, "fitness") else None,
        }
        log(f"Validation metrics: {json.dumps(metrics, indent=2)}")
    except Exception as e:
        log(f"WARNING: Validation failed: {e}")

    # Run on test set
    test_metrics = {}
    try:
        test_model = YOLO(str(best_pt))
        test_results = test_model.val(data=str(DATA_YAML), device="0", split="test")
        test_metrics = {
            "mAP50": float(test_results.box.map50),
            "mAP50_95": float(test_results.box.map),
            "precision": float(test_results.box.mp),
            "recall": float(test_results.box.mr),
        }
        log(f"Test metrics: {json.dumps(test_metrics, indent=2)}")
    except Exception as e:
        log(f"WARNING: Test validation failed: {e}")

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "yolov8x",
        "epochs": 200,
        "imgsz": 1280,
        "batch": 2,
        "dataset": str(DATA_YAML),
        "train_images": 694,
        "val_images": 148,
        "test_images": 127,
        "best_pt": str(best_pt),
        "best_pt_exists": best_pt.exists(),
        "val_metrics": metrics,
        "test_metrics": test_metrics,
    }

    results_file = REPO_ROOT / "training_results_v3.json"
    results_file.write_text(json.dumps(output, indent=2), encoding="utf-8")
    log(f"Results saved to {results_file}")

    log("Training complete.")
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
