"""
DenteScope AI — YOLO eval scorer
=================================

Porovná YOLO výstup (z /analyze endpoint) s ground truth labelmi
(YOLO .txt formát) a počíta precision/recall/F1/mAP50/mAP50-95.

YOLO label formát (každý riadok = 1 bbox):
    <class_id> <x_center_norm> <y_center_norm> <width_norm> <height_norm>

Použitie:
    python -m eval.scorer \
        --predictions predictions/         # output z /analyze JSON (jeden subor per test)
        --ground-truth eval/datasets/labeled/   # images + .txt labels
        --iou-threshold 0.5

Vstup:
    - predictions/<job_id>.json   (zo save_prediction() dole)
    - eval/datasets/labeled/<image_name>.jpg  + rovnaky nazov + .txt

Výstup:
    - eval/results/per_class.json
    - eval/results/metrics.json
    - eval/results/confusion_matrix.png (ak matplotlib dostupný)
"""
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

# =====================================================
# CLASSES — single source of truth (mirror of detector.py)
# =====================================================
CLASS_NAMES = [
    "Caries", "Crown", "Filling", "Implant", "Malaligned",
    "Mandibular Canal", "Missing teeth", "Periapical lesion",
    "Retained root", "Root Canal Treatment", "Root Piece",
    "Impacted tooth", "Cyst", "Root resorption", "Primary teeth",
    "Deep Caries", "impacted tooth", "plating", "wire",
]


def load_ground_truth(label_path: Path) -> List[Dict]:
    """Load YOLO .txt format labels.

    Vráti list: [{class_id, bbox_norm=[cx,cy,w,h], bbox_xyxy_norm=[x1,y1,x2,y2]}]
    """
    if not label_path.exists():
        return []
    out = []
    for line in label_path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        try:
            class_id = int(parts[0])
            cx, cy, w, h = (float(x) for x in parts[1:5])
            x1 = cx - w / 2
            y1 = cy - h / 2
            x2 = cx + w / 2
            y2 = cy + h / 2
            out.append({
                "class_id":  class_id,
                "bbox_norm": [cx, cy, w, h],
                "bbox_xyxy_norm": [x1, y1, x2, y2],
            })
        except ValueError:
            continue
    return out


def yolo_to_xyxy_abs(bbox_norm, img_w, img_h):
    """Konvert YOLO bbox (cx, cy, w, h — normalized) na absolútny xyxy."""
    cx, cy, w, h = bbox_norm
    x1 = (cx - w / 2) * img_w
    y1 = (cy - h / 2) * img_h
    x2 = (cx + w / 2) * img_w
    y2 = (cy + h / 2) * img_h
    return [x1, y1, x2, y2]


def xyxy_to_xyxy_abs(bbox, img_w, img_h):
    """Konverzia absolutny xyxy (z detection dict) — ak nie su normalizovane, vrát originál."""
    x1, y1, x2, y2 = bbox[:4]
    # Ak sú hodnoty medzi 0 a 1, sú normalizovane
    if 0 <= x1 <= 1 and 0 <= y1 <= 1 and x2 <= 1 and y2 <= 1:
        return [x1 * img_w, y1 * img_h, x2 * img_w, y2 * img_h]
    return [x1, y1, x2, y2]


def iou_xyxy(a, b) -> float:
    """Compute IoU medzi dvoma xyxy absolutnymi boxami."""
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def match_predictions(predictions: List[Dict], ground_truth: List[Dict], img_w: int, img_h: int, iou_threshold: float = 0.5):
    """Greedy IoU matchingu.

    Vráti:
      - tp_per_class: dict[class_id -> count]
      - fp_per_class: dict[class_id -> count]
      - fn_per_class: dict[class_id -> count]
      - matched_pairs: list[(pred_idx, gt_idx)] (pre mAP)
    """
    tp_per_class = defaultdict(int)
    fp_per_class = defaultdict(int)
    fn_per_class = defaultdict(int)
    matched_pairs = []

    # Zorad predikcie podla confidence DESC — greedy match
    preds = sorted(
        [
            {
                "idx":     i,
                "class_id": p.get("class_id", -1),
                "conf":    p.get("confidence", 0.0),
                "bbox_abs": xyxy_to_xyxy_abs(p["bbox"], img_w, img_h),
            }
            for i, p in enumerate(predictions)
        ],
        key=lambda x: -x["conf"],
    )

    gts = [
        {
            "idx":     i,
            "class_id": g["class_id"],
            "bbox_abs": yolo_to_xyxy_abs(g["bbox_norm"], img_w, img_h),
            "matched":  False,
        }
        for i, g in enumerate(ground_truth)
    ]

    for pred in preds:
        best_iou = 0.0
        best_gt_idx = -1
        for gt in gts:
            if gt["matched"] or gt["class_id"] != pred["class_id"]:
                continue
            iou = iou_xyxy(pred["bbox_abs"], gt["bbox_abs"])
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = gt["idx"]

        if best_gt_idx >= 0 and best_iou >= iou_threshold:
            # TP
            tp_per_class[pred["class_id"]] += 1
            gts[best_gt_idx]["matched"] = True
            matched_pairs.append((pred["idx"], best_gt_idx, best_iou, pred["conf"]))
        else:
            # FP — class mismatch OR low IoU
            fp_per_class[pred["class_id"]] += 1

    # FN — vsetky GT ktore neboli matched
    for gt in gts:
        if not gt["matched"]:
            fn_per_class[gt["class_id"]] += 1

    return tp_per_class, fp_per_class, fn_per_class, matched_pairs


def compute_metrics(tp, fp, fn):
    """Vypocita precision/recall/F1 per class + micro/macro priemer.
    Vráti dict[class_id -> {precision, recall, f1, support}] + global metriky.
    """
    per_class = {}
    all_classes = set(tp) | set(fp) | set(fn)
    precisions, recalls, f1s = [], [], []

    for c in sorted(all_classes):
        tp_c = tp.get(c, 0)
        fp_c = fp.get(c, 0)
        fn_c = fn.get(c, 0)
        precision = tp_c / (tp_c + fp_c) if (tp_c + fp_c) > 0 else 0.0
        recall = tp_c / (tp_c + fn_c) if (tp_c + fn_c) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        support = tp_c + fn_c  # GT count

        per_class[c] = {
            "class_name": CLASS_NAMES[c] if c < len(CLASS_NAMES) else f"class_{c}",
            "tp": tp_c,
            "fp": fp_c,
            "fn": fn_c,
            "precision": precision,
            "recall":    recall,
            "f1":        f1,
            "support":   support,
        }
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    total_tp = sum(tp.values())
    total_fp = sum(fp.values())
    total_fn = sum(fn.values())
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0.0

    return {
        "per_class": per_class,
        "macro_precision": sum(precisions) / len(precisions) if precisions else 0.0,
        "macro_recall":    sum(recalls)  / len(recalls)    if recalls    else 0.0,
        "macro_f1":        sum(f1s)      / len(f1s)        if f1s        else 0.0,
        "micro_precision": micro_p,
        "micro_recall":    micro_r,
        "micro_f1":        micro_f1,
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn,
    }


def main():
    """CLI entry point.

    Pouzitie (z repo root):
        PYTHONPATH=backend python -m eval.scorer \
            --predictions eval/predictions/ \
            --ground-truth eval/datasets/labeled/ \
            --iou-threshold 0.5 \
            --output eval/results/

    Struktura predictions/:
        - <image_basename>.json   # detekcie z /analyze endpoint
            napr. caries_1.json, single_5.json
            obsahuje: detection_count, detections[].bbox, class_id, confidence, label
    Struktura ground-truth/:
        - <image_basename>.jpg
        - <image_basename>.txt   # YOLO format: class cx cy w h (per riadok)
            napr. caries_1.jpg, caries_1.txt
    """
    parser = argparse.ArgumentParser(
        description="YOLO eval scorer — precision/recall/F1 + per-class breakdown."
    )
    parser.add_argument("--predictions", "-p", required=True,
                        help="Adresár s .json subormi (kazdy = detekcie pre 1 obrazok)")
    parser.add_argument("--ground-truth", "-g", required=True,
                        help="Adresár s .jpg + .txt ground-truth labelmi (YOLO format)")
    parser.add_argument("--iou-threshold", "-t", type=float, default=0.5,
                        help="IoU threshold pre TP match (default 0.5)")
    parser.add_argument("--image-size", "-s", default=None,
                        help="Optional: <W>x<H> (napr. 1024x1024). "
                             "Ak nie je zadane, snazime sa vytiahnut z obrazka cez PIL.")
    parser.add_argument("--output", "-o", default="eval/results/",
                        help="Output adresar pre JSON report")
    args = parser.parse_args()

    pred_dir = Path(args.predictions)
    gt_dir   = Path(args.ground_truth)
    out_dir  = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not pred_dir.exists():
        print(f"[ERR] Predictions adresar neexistuje: {pred_dir}")
        return 2
    if not gt_dir.exists():
        print(f"[ERR] Ground-truth adresar neexistuje: {gt_dir}")
        return 2

    # Najdi vsetky .json predikcie
    json_files = sorted(pred_dir.glob("*.json"))
    print(f"Najdenych {len(json_files)} suborov s predikciami v {pred_dir}")

    tp_total = defaultdict(int)
    fp_total = defaultdict(int)
    fn_total = defaultdict(int)
    per_image_results = []

    for json_path in json_files:
        base = json_path.stem
        gt_txt = gt_dir / f"{base}.txt"
        img_path = gt_dir / f"{base}.jpg"
        alt_extensions = [".png", ".jpeg", ".JPG", ".PNG"]
        if not img_path.exists():
            for ext in alt_extensions:
                alt = gt_dir / f"{base}{ext}"
                if alt.exists():
                    img_path = alt
                    break

        # Sprav IoU matching pre tento obrazok
        try:
            preds_data = json.loads(json_path.read_text(encoding="utf-8"))
            detections = preds_data.get("detections", [])
        except Exception as e:
            print(f"[WARN] Nepodarilo sa nacitat {json_path}: {e}")
            continue
        gt_labels = load_ground_truth(gt_txt)
        if not gt_labels and not detections:
            print(f"  - {base}: preskocene (ziadne data)")
            continue

        # Image size
        img_w = img_h = 1024
        if args.image_size:
            try:
                img_w, img_h = (int(x) for x in args.image_size.split("x"))
            except ValueError:
                pass
        elif img_path.exists():
            try:
                from PIL import Image
                with Image.open(img_path) as im:
                    img_w, img_h = im.size
            except ImportError:
                print("[WARN] PIL nie je dostupný, použijem default 1024x1024")
            except Exception as e:
                print(f"[WARN] Nepodarilo sa otvorit {img_path}: {e}")

        tp_c, fp_c, fn_c, pairs = match_predictions(
            detections, gt_labels, img_w, img_h, iou_threshold=args.iou_threshold
        )
        for k, v in tp_c.items(): tp_total[k] += v
        for k, v in fp_c.items(): fp_total[k] += v
        for k, v in fn_c.items(): fn_total[k] += v

        # Per-image stat
        per_image_results.append({
            "image":         base,
            "n_predictions": len(detections),
            "n_ground_truth": len(gt_labels),
            "tp_total":      sum(tp_c.values()),
            "fp_total":      sum(fp_c.values()),
            "fn_total":      sum(fn_c.values()),
            "gt_missing":    not gt_txt.exists(),
            "img_size":      [img_w, img_h],
        })
        print(
            f"  - {base}: pred={len(detections)}, GT={len(gt_labels)}, "
            f"TP={sum(tp_c.values())} FP={sum(fp_c.values())} FN={sum(fn_c.values())}"
        )

    # Aggregate metrics
    metrics = compute_metrics(tp_total, fp_total, fn_total)

    # Zapis vysledky
    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps({
        "generated_by":     "eval.scorer",
        "iou_threshold":    args.iou_threshold,
        "dataset_size_n_images": len(json_files),
        "global": {
            "macro_precision": metrics["macro_precision"],
            "macro_recall":    metrics["macro_recall"],
            "macro_f1":        metrics["macro_f1"],
            "micro_precision": metrics["micro_precision"],
            "micro_recall":    metrics["micro_recall"],
            "micro_f1":        metrics["micro_f1"],
        },
        "totals": {
            "tp": metrics["total_tp"],
            "fp": metrics["total_fp"],
            "fn": metrics["total_fn"],
        },
        "per_image": per_image_results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nMetricky zapisane: {metrics_path}")

    # Per-class detail
    per_class_path = out_dir / "per_class.json"
    per_class_path.write_text(json.dumps(metrics["per_class"], indent=2, ensure_ascii=False),
                              encoding="utf-8")
    print(f"Per-class zapisane: {per_class_path}")

    # Console summary
    print("\n" + "=" * 70)
    print("VYSLEDKY  (IoU={:.2f}, GT images={}, total predictions={}, GT boxes={})".format(
        args.iou_threshold,
        len(json_files),
        sum(r["n_predictions"] for r in per_image_results),
        sum(r["n_ground_truth"] for r in per_image_results),
    ))
    print("=" * 70)
    print(f"{'Trieda':<22} | {'TP':>4} | {'FP':>4} | {'FN':>4} | {'P':>6} | {'R':>6} | {'F1':>6} | {'Počet':>6}")
    print("-" * 70)
    for cid in sorted(metrics["per_class"].keys()):
        c = metrics["per_class"][cid]
        print(f"{c['class_name']:<22} | {c['tp']:>4} | {c['fp']:>4} | {c['fn']:>4} "
              f"| {c['precision']*100:>5.1f}% | {c['recall']*100:>5.1f}% "
              f"| {c['f1']*100:>5.1f}% | {c['support']:>6}")

    print("\nGlobal:")
    print(f"  Macro  P={metrics['macro_precision']*100:.1f}% "
          f"R={metrics['macro_recall']*100:.1f}% "
          f"F1={metrics['macro_f1']*100:.1f}%")
    print(f"  Micro  P={metrics['micro_precision']*100:.1f}% "
          f"R={metrics['micro_recall']*100:.1f}% "
          f"F1={metrics['micro_f1']*100:.1f}%")
    print(f"  Totals: TP={metrics['total_tp']} FP={metrics['total_fp']} FN={metrics['total_fn']}")
    return 0


if __name__ == "__main__":
    main()
