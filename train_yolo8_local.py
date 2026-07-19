#!/usr/bin/env python3
"""YOLOv8 local training for dental AI."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parent
DATA_YAML = REPO_ROOT / "data_dental.yaml"
OUTPUT_DIR = REPO_ROOT / "runs" / "detect" / "train"


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] {msg}", flush=True)


def main() -> int:
    if not DATA_YAML.exists():
        log(f"ERROR: data_dental.yaml not found at {DATA_YAML}")
        return 1

    log("Starting YOLOv8m dental training.")
    log(f"Data YAML: {DATA_YAML}")
    log(f"Output:    {OUTPUT_DIR}")

    try:
        model = YOLO("yolov8m.pt")
    except Exception as e:
        log(f"ERROR loading YOLOv8m: {e}")
        return 1

    try:
        results = model.train(
            data=str(DATA_YAML),
            epochs=50,
            imgsz=640,
            batch=8,
            patience=10,
            optimizer="AdamW",
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
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
            mixup=0.0,
            copy_paste=0.0,
            device="0",
            workers=4,
            project=str(REPO_ROOT / "runs" / "detect"),
            name="train",
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

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": "yolov8m",
        "epochs": 50,
        "imgsz": 640,
        "batch": 8,
        "dataset": str(DATA_YAML),
        "train_images": 100,
        "val_images": 20,
        "best_pt": str(best_pt),
        "best_pt_exists": best_pt.exists(),
        "metrics": metrics,
    }

    results_file = REPO_ROOT / "training_results.json"
    results_file.write_text(json.dumps(output, indent=2), encoding="utf-8")
    log(f"Results saved to {results_file}")

    log("Training complete.")
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
