import requests, os, json

API = "http://127.0.0.1:8000"
test_dir = r"C:\Users\PC1\Desktop\dental-ai\benchmark_test"
CLASS_NAMES = {0: "caries", 1: "periapical_lesion", 2: "impacted_tooth"}

results = []
for fname in sorted(os.listdir(test_dir)):
    if not fname.endswith(".jpg"):
        continue

    txt_file = fname.replace(".jpg", ".txt")
    txt_path = os.path.join(test_dir, txt_file)
    gt_boxes = []
    gt_classes = set()
    if os.path.exists(txt_path):
        with open(txt_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    cls_id = int(parts[0])
                    cls_name = CLASS_NAMES.get(cls_id, "class_" + str(cls_id))
                    gt_classes.add(cls_name)
                    gt_boxes.append({"class": cls_name})

    img_path = os.path.join(test_dir, fname)

    # YOLO
    yolo_count = 0
    yolo_classes_found = set()
    try:
        with open(img_path, "rb") as f:
            r = requests.post(API + "/analyze/?conf=0.05", files={"file": (fname, f, "image/jpeg")}, timeout=60)
        yolo_data = r.json()
        yolo_count = yolo_data.get("detection_count", 0)
        by_class = yolo_data.get("by_class", {})
        for k, v in by_class.items():
            cnt = 0
            if isinstance(v, int):
                cnt = v
            elif isinstance(v, dict):
                cnt = v.get("count", 0)
            if cnt > 0:
                yolo_classes_found.add(k.lower().replace(" ", "_"))
    except Exception as e:
        print("YOLO error:", fname, str(e))

    # Gemini
    gemini_detections = []
    gemini_classes = set()
    try:
        with open(img_path, "rb") as f:
            r2 = requests.post(API + "/vision/analyze", files={"file": (fname, f, "image/jpeg")}, timeout=120)
        gemini_data = r2.json()
        gemini_detections = gemini_data.get("gemini_detections", [])
        for d in gemini_detections:
            lbl = d.get("label", "").lower().replace(" ", "_")
            gemini_classes.add(lbl)
    except Exception as e:
        print("Gemini error:", fname, str(e))

    yolo_found = gt_classes.intersection(yolo_classes_found)
    yolo_missed = gt_classes.difference(yolo_classes_found)
    yolo_extra = yolo_classes_found.difference(gt_classes)
    gemini_found = gt_classes.intersection(gemini_classes)
    gemini_missed = gt_classes.difference(gemini_classes)
    gemini_extra = gemini_classes.difference(gt_classes)

    result = {
        "image": fname,
        "gt_count": len(gt_boxes),
        "gt_classes": sorted(gt_classes),
        "yolo_count": yolo_count,
        "yolo_classes": sorted(yolo_classes_found),
        "yolo_found": sorted(yolo_found),
        "yolo_missed": sorted(yolo_missed),
        "yolo_extra": sorted(yolo_extra),
        "gemini_count": len(gemini_detections),
        "gemini_classes": sorted(gemini_classes),
        "gemini_found": sorted(gemini_found),
        "gemini_missed": sorted(gemini_missed),
        "gemini_extra": sorted(gemini_extra),
    }
    results.append(result)

    gt_str = str(sorted(gt_classes))
    yf_str = str(sorted(yolo_found))
    ym_str = str(sorted(yolo_missed))
    gf_str = str(sorted(gemini_found))
    gm_str = str(sorted(gemini_missed))
    line = fname
    line += " | GT=" + gt_str
    line += " | YOLO=" + str(yolo_count) + " found=" + yf_str + " miss=" + ym_str
    line += " | Gemini=" + str(len(gemini_detections)) + " found=" + gf_str + " miss=" + gm_str
    print(line)

# Summary
all_gt = set()
for r in results:
    all_gt.update(r["gt_classes"])

print("")
print("=" * 70)
print("BENCHMARK SUMMARY: " + str(len(results)) + " images")
print("Dataset 1: liodon-ai/dental-panoramic-xray-yolo (10 OPG panoramic)")
print("Dataset 2: reza362/dental-xray-caries (5 intraoral)")
print("GT classes: " + str(sorted(all_gt)))
print("=" * 70)

for cls in sorted(all_gt):
    total = sum(1 for r in results if cls in r["gt_classes"])
    yolo_tp = sum(1 for r in results if cls in r["gt_classes"] and cls in r["yolo_found"])
    gemini_tp = sum(1 for r in results if cls in r["gt_classes"] and cls in r["gemini_found"])
    yr = yolo_tp * 100 // max(total, 1)
    gr = gemini_tp * 100 // max(total, 1)
    print(cls + ": GT=" + str(total) + " | YOLO=" + str(yolo_tp) + "/" + str(total) + " (" + str(yr) + "%) | Gemini=" + str(gemini_tp) + "/" + str(total) + " (" + str(gr) + "%)")

print("")
# Save full results
with open(os.path.join(test_dir, "benchmark_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("Results saved to benchmark_results.json")
