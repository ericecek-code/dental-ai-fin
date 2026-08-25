#!/usr/bin/env python3
"""Benchmark comparison: baseline vs improved dental model."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from ultralytics import YOLO
except Exception as exc:
    print(f"Missing ultralytics: {exc}")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent
BENCH_DIR = REPO_ROOT / "benchmark_test"
BASELINE = REPO_ROOT / "backend" / "weights" / "yolov8x_dental.pt"
CANDIDATE = REPO_ROOT / "runs" / "detect" / "train" / "weights" / "best.pt"
RESULTS_DIR = REPO_ROOT / "benchmark_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def log(msg: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)


def find_images() -> list[Path]:
    if not BENCH_DIR.exists():
        return []
    out = []
    for p in BENCH_DIR.iterdir():
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            out.append(p)
    return sorted(out)


def infer(model_path: Path, images: list[Path], conf: float = 0.25) -> float:
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    model = YOLO(str(model_path))
    total = 0.0
    count = 0
    for img in images:
        try:
            res = model.predict(source=str(img), conf=conf, verbose=False)
            total += float(len(res[0].boxes)) if res else 0.0
            count += 1
        except Exception as exc:
            log(f"Inference error {img.name}: {exc}")
    return total / max(count, 1)


def main() -> int:
    images = find_images()
    if not images:
        log("No benchmark images found under benchmark_test/")
        return 1

    log(f"Benchmark images: {len(images)}")
    log(f"Baseline model: {BASELINE}")
    log(f"Candidate model: {CANDIDATE}")

    baseline_avg = infer(BASELINE, images)
    candidate_avg = infer(CANDIDATE, images)
    delta = candidate_avg - baseline_avg

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "images": len(images),
        "baseline_avg_detections": baseline_avg,
        "candidate_avg_detections": candidate_avg,
        "delta": delta,
    }

    out = RESULTS_DIR / "benchmark_comparison.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log(f"Results: {json.dumps(summary)}")
    log(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
