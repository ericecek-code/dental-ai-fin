import requests, os, json

API = "http://127.0.0.1:8000"
test_dir = r"C:\Users\PC1\Desktop\dental-ai\benchmark_test"
CLASS_NAMES = {0: "caries", 1: "periapical_lesion", 2: "impacted_tooth"}
THRESHOLDS = [0.01, 0.05, 0.15, 0.25]

all_results = {}
for conf in THRESHOLDS:
    threshold_results = []
    for fname in sorted(os.listdir(test_dir)):
        if not fname.endswith(".jpg"):
            continue
        txt_path = os.path.join(test_dir, fname.replace(".jpg", ".txt"))
        gt_classes = set()
        gt_count = 0
        if os.path.exists(txt_path):
            with open(txt_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        gt_classes.add(CLASS_NAMES.get(cls_id, "unknown"))
                        gt_count += 1

        img_path = os.path.join(test_dir, fname)
        try:
            with open(img_path, "rb") as f:
                r = requests.post(API + "/analyze/?conf=" + str(conf), files={"file": (fname, f, "image/jpeg")}, timeout=60)
            data = r.json()
            det_count = data.get("detection_count", 0)
            by_class = data.get("by_class", {})
            yolo_classes = set()
            for k, v in by_class.items():
                cnt = v if isinstance(v, int) else (v.get("count", 0) if isinstance(v, dict) else 0)
                if cnt > 0:
                    yolo_classes.add(k.lower().replace(" ", "_"))
            found = gt_classes.intersection(yolo_classes)
            missed = gt_classes.difference(yolo_classes)
        except Exception as e:
            det_count = 0
            found = set()
            missed = gt_classes

        threshold_results.append({
            "image": fname, "gt_count": gt_count, "det_count": det_count,
            "gt_classes": sorted(gt_classes), "found": sorted(found), "missed": sorted(missed)
        })

    total_gt = sum(r["gt_count"] for r in threshold_results)
    total_det = sum(r["det_count"] for r in threshold_results)
    unique_gt = set()
    for r in threshold_results:
        unique_gt.update(r["gt_classes"])

    per_class = {}
    for cls in sorted(unique_gt):
        gt_in = sum(1 for r in threshold_results if cls in r["gt_classes"])
        tp = sum(1 for r in threshold_results if cls in r["found"])
        per_class[cls] = {"gt": gt_in, "recall": tp, "pct": tp * 100 // max(gt_in, 1)}

    all_results[str(conf)] = {
        "threshold": conf,
        "images": len(threshold_results),
        "total_gt": total_gt,
        "total_detections": total_det,
        "per_class": per_class,
        "avg_dets_per_image": total_det // max(len(threshold_results), 1),
    }
    print("conf=" + str(conf) + ": dets=" + str(total_det) + " avg=" + str(total_det // max(len(threshold_results), 1)) + "/img")
    for cls, info in per_class.items():
        print("  " + cls + ": " + str(info["recall"]) + "/" + str(info["gt"]) + " (" + str(info["pct"]) + "%)")

# Find optimal threshold
best_conf = 0.05
best_score = 0
for conf, data in all_results.items():
    total_recall = sum(v["recall"] for v in data["per_class"].values())
    total_gt = sum(v["gt"] for v in data["per_class"].values())
    avg_dets = data["avg_dets_per_image"]
    score = total_recall * 100 // max(total_gt, 1) - (avg_dets // 20)
    if score > best_score:
        best_score = score
        best_conf = float(conf)

print("")
print("BEST THRESHOLD: " + str(best_conf) + " (score=" + str(best_score) + ")")
print(json.dumps(all_results, indent=2))
