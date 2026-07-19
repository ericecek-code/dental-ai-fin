"""
Empiricka evaluacia: spusti YOLO model na vsetkych test obrazkoch,
zozbieraj confidence po triedach, vypis priemery a distribucie.

NIE JE to skutocna 'precision/recall' (potrebovali by sme ground truth labely),
ale ukaze nam empiricke rozlozenie confidence -> odhad kvality modelu.
"""
import sys, os, glob
from pathlib import Path
import numpy as np
import cv2
import json

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.ml.detector import Detector  # noqa: E402

WEIGHTS = Path("C:/Users/PC1/Desktop/dental-ai/backend/weights/yolov8x_dental.pt")
TEST_DIR = Path("C:/Users/PC1/Desktop/dental-ai/test_images")
OUT_PATH = Path("C:/Users/PC1/Desktop/dental-ai/test_images/eval_report.json")


def main():
    det = Detector(model_path=str(WEIGHTS))
    det.load()

    images = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG"):
        images.extend(sorted(glob.glob(str(TEST_DIR / ext))))
    print(f"Najdenych {len(images)} test obrazkov")

    by_class_conf = {}      # nazov_triedy -> zoznam confidences
    by_class_count = {}     # nazov_triedy -> pocet detekcii (across images)
    total_dets_per_image = []
    image_results = []

    for img_path in images:
        img = cv2.imread(img_path)
        if img is None:
            print(f"  Skip (unreadable): {Path(img_path).name}")
            continue
        try:
            dets = det.predict(img, conf=0.01)  # nizky threshold pre evaluaciu
        except Exception as e:
            print(f"  Skip (err): {Path(img_path).name}: {e}")
            continue

        total_dets_per_image.append(len(dets))
        image_results.append({
            "image": Path(img_path).name,
            "detections": len(dets),
            "max_conf": max([d["confidence"] for d in dets], default=0.0),
        })
        for d in dets:
            cls = d.get("label", "?")
            by_class_conf.setdefault(cls, []).append(d["confidence"])
            by_class_count[cls] = by_class_count.get(cls, 0) + 1

    print()
    print("=" * 70)
    print(f"CELKOVY OBRAZ (pri conf threshold 0.01):")
    print(f"  Počet obrázkov: {len(image_results)}")
    print(f"  Počet detekcií: {sum(by_class_count.values())}")
    print(f"  Priemerný počet detekcií/obrázok: {np.mean(total_dets_per_image):.2f}")
    print(f"  Min/Max detekcií: {min(total_dets_per_image)}/{max(total_dets_per_image)}")
    print()
    print("=" * 70)
    print(f"{'Trieda':<22} | {'Počet':>6} | {'Avg conf':>10} | {'Max':>6} | {'P50':>6} | {'P90':>6} | {'StdDev':>7}")
    print("-" * 70)
    rows = []
    for cls in sorted(by_class_conf.keys(), key=lambda c: -by_class_count.get(c, 0)):
        confs = np.array(by_class_conf[cls])
        n = len(confs)
        rows.append({
            "class":    cls,
            "count":    int(n),
            "avg_conf": float(np.mean(confs)),
            "max":      float(np.max(confs)),
            "p50":      float(np.median(confs)),
            "p90":      float(np.percentile(confs, 90)),
            "std":      float(np.std(confs)),
            "below_50pct":   int(np.sum(confs < 0.50)),
            "above_70pct":   int(np.sum(confs >= 0.70)),
            "above_85pct":   int(np.sum(confs >= 0.85)),
        })
        print(f"{cls:<22} | {n:>6} | {np.mean(confs)*100:>9.1f}% | {np.max(confs)*100:>5.1f}% "
              f"| {np.median(confs)*100:>5.1f}% | {np.percentile(confs, 90)*100:>5.1f}% "
              f"| {np.std(confs)*100:>6.1f}%")

    print()
    print("=" * 70)
    print(f"PRAG SPOLAHLIVOSTI - interpretacia pre klinicke pouzitie:")
    print(f"  Ak hladas 'len iste detekcie':")
    print(f"    conf >= 0.85  -> velmi vysoka istota (opatmne na over-detekciu)")
    print(f"    conf 0.50-0.85 -> strede istota (zvycajne spolahlive)")
    print(f"    conf 0.20-0.50 -> nizka istota (kontrola zubara)")
    print(f"    conf < 0.20    -> pozadie, false-positive")
    print()
    print(f"Podiel detekcii s vysokou istotou (>= 0.85): "
          f"{sum(r['above_85pct'] for r in rows)}/"
          f"{sum(r['count'] for r in rows)} "
          f"({sum(r['above_85pct'] for r in rows) / max(1, sum(r['count'] for r in rows)) * 100:.1f}%)")

    OUT_PATH.write_text(json.dumps({
        "generated": str(Path(__file__).name),
        "weights": str(WEIGHTS),
        "images_tested": len(image_results),
        "total_detections": sum(by_class_count.values()),
        "per_image": image_results,
        "per_class": rows,
    }, indent=2))
    print()
    print(f"Detailny report ulozeny: {OUT_PATH}")


if __name__ == "__main__":
    main()
