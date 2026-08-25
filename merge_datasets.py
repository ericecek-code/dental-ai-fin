#!/usr/bin/env python3
"""
Merge dental datasets for YOLOv8 training.
Sources:
1. oral-disease (Kaggle) - 8,616 images, 5 classes (calculus, cancer, caries, gingivitis, ulcer)
2. dental_yolo_v8-420 (Roboflow) - 3,802 images, 38 classes (polygon annotations → bbox)
3. combined-dataset (our) - 969 images, 5 classes
4. restorative-ai-bbox (our) - 849 images, 5 classes

Target: 5 unified classes
  0: Caries
  1: Crown
  2: Filling  
  3: Implant
  4: Periapical-lesion
"""

import os
import shutil
import random
from pathlib import Path
from collections import Counter, defaultdict

# === CONFIGURATION ===
ROOT = Path("C:/Users/PC1/Desktop/dental-ai")
OUTPUT = ROOT / "mega-dataset"
RANDOM_SEED = 42
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# === CLASS MAPPING ===
# Target classes (our 5 classes)
TARGET_CLASSES = {
    0: "Caries",
    1: "Crown", 
    2: "Filling",
    3: "Implant",
    4: "Periapical-lesion"
}

# oral-disease mapping: oral_classes → our classes
ORAL_DISEASE_MAP = {
    0: None,      # calculus → skip (not in our classes)
    1: None,      # cancer → skip
    2: 0,         # caries → Caries
    3: None,      # gingivitis → skip
    4: 4,         # ulcer → Periapical-lesion (closest match)
}

# dental_yolo_v8-420 mapping (38 classes → our 5 classes)
# Based on typical dental YOLO dataset classes
DENTAL_YOLO_MAP = {
    # Caries-related
    0: 0,    # cavity → Caries
    1: 0,    # caries → Caries
    # Crown-related  
    6: 1,    # crown → Crown
    7: 1,    # porcelain_crown → Crown
    # Filling-related
    3: 2,    # filling → Filling
    4: 2,    # composite → Filling
    # Implant-related
    11: 3,   # implant → Implant
    # Periapical-related
    13: 4,   # periapical → Periapical-lesion
    14: 4,   # periapical_lesion → Periapical-lesion
}

# Our datasets (already correct format)
OUR_DATASETS = ["combined-dataset", "restorative-ai-bbox"]


def polygon_to_bbox(coords):
    """Convert polygon coordinates to bounding box [cx, cy, w, h]"""
    if len(coords) < 6:  # Need at least 3 points (x,y pairs)
        return None
    
    xs = coords[0::2]
    ys = coords[1::2]
    
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    
    cx = (x_min + x_max) / 2
    cy = (y_min + y_max) / 2
    w = x_max - x_min
    h = y_max - y_min
    
    return cx, cy, w, h


def convert_polygon_label(label_line, class_map):
    """Convert polygon annotation to bbox with class mapping"""
    parts = label_line.strip().split()
    if len(parts) < 7:  # class + at least 3 points (6 coords)
        return None
    
    try:
        orig_class = int(parts[0])
    except ValueError:
        return None
    
    if orig_class not in class_map:
        return None
    
    new_class = class_map[orig_class]
    if new_class is None:
        return None
    
    coords = [float(x) for x in parts[1:]]
    bbox = polygon_to_bbox(coords)
    
    if bbox is None:
        return None
    
    cx, cy, w, h = bbox
    # Clamp values to [0, 1]
    cx = max(0, min(1, cx))
    cy = max(0, min(1, cy))
    w = max(0, min(1, w))
    h = max(0, min(1, h))
    
    return f"{new_class} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def process_oral_disease(output_dir):
    """Process oral-disease dataset"""
    src = ROOT / "kaggle_datasets" / "oral-disease" / "oral_dataset"
    stats = Counter()
    
    for split in ["train", "valid", "test"]:
        img_src = src / split / "images"
        lbl_src = src / split / "labels"
        img_dst = output_dir / split / "images"
        lbl_dst = output_dir / split / "labels"
        img_dst.mkdir(parents=True, exist_ok=True)
        lbl_dst.mkdir(parents=True, exist_ok=True)
        
        for lbl_file in lbl_src.glob("*.txt"):
            lines = lbl_file.read_text().strip().split("\n")
            new_lines = []
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                try:
                    orig_class = int(parts[0])
                except ValueError:
                    continue
                
                if orig_class in ORAL_DISEASE_MAP and ORAL_DISEASE_MAP[orig_class] is not None:
                    new_class = ORAL_DISEASE_MAP[orig_class]
                    new_lines.append(f"{new_class} {' '.join(parts[1:])}")
                    stats[new_class] += 1
            
            if new_lines:
                img_file = img_src / lbl_file.name.replace(".txt", ".jpg")
                if not img_file.exists():
                    img_file = img_src / lbl_file.name.replace(".txt", ".png")
                if img_file.exists():
                    shutil.copy2(img_file, img_dst / img_file.name)
                    (lbl_dst / lbl_file.name).write_text("\n".join(new_lines))
    
    return stats


def process_dental_yolo(output_dir):
    """Process dental_yolo_v8-420 dataset (polygon → bbox)"""
    src = ROOT / "dental_yolo_v8-420"
    stats = Counter()
    skipped = 0
    
    for split in ["train", "valid", "test"]:
        img_src = src / split / "images"
        lbl_src = src / split / "labels"
        img_dst = output_dir / split / "images"
        lbl_dst = output_dir / split / "labels"
        img_dst.mkdir(parents=True, exist_ok=True)
        lbl_dst.mkdir(parents=True, exist_ok=True)
        
        if not lbl_src.exists():
            continue
            
        for lbl_file in lbl_src.glob("*.txt"):
            lines = lbl_file.read_text().strip().split("\n")
            new_lines = []
            
            for line in lines:
                converted = convert_polygon_label(line, DENTAL_YOLO_MAP)
                if converted:
                    new_lines.append(converted)
                    orig_class = int(line.strip().split()[0])
                    if orig_class in DENTAL_YOLO_MAP and DENTAL_YOLO_MAP[orig_class] is not None:
                        stats[DENTAL_YOLO_MAP[orig_class]] += 1
                else:
                    skipped += 1
            
            if new_lines:
                # Copy image
                img_file = img_src / lbl_file.name.replace(".txt", ".jpg")
                if not img_file.exists():
                    img_file = img_src / lbl_file.name.replace(".txt", ".png")
                if img_file.exists():
                    shutil.copy2(img_file, img_dst / img_file.name)
                    (lbl_dst / lbl_file.name).write_text("\n".join(new_lines))
    
    print(f"  Skipped {skipped} polygon annotations (class not mapped)")
    return stats


def process_our_datasets(output_dir):
    """Process our existing datasets"""
    stats = Counter()
    
    for dataset_name in OUR_DATASETS:
        src = ROOT / dataset_name
        if not src.exists():
            print(f"  Warning: {dataset_name} not found, skipping")
            continue
        
        for split in ["train", "val", "test"]:
            # Map val → valid for consistency
            out_split = "valid" if split == "val" else split
            
            img_src = src / split / "images"
            lbl_src = src / split / "labels"
            img_dst = output_dir / out_split / "images"
            lbl_dst = output_dir / out_split / "labels"
            img_dst.mkdir(parents=True, exist_ok=True)
            lbl_dst.mkdir(parents=True, exist_ok=True)
            
            if not img_src.exists():
                continue
            
            for lbl_file in lbl_src.glob("*.txt"):
                lines = lbl_file.read_text().strip().split("\n")
                new_lines = []
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    try:
                        cls = int(parts[0])
                    except ValueError:
                        continue
                    
                    # Our classes are already 0-4
                    if 0 <= cls <= 4:
                        new_lines.append(line.strip())
                        stats[cls] += 1
                
                if new_lines:
                    img_file = img_src / lbl_file.name.replace(".txt", ".jpg")
                    if not img_file.exists():
                        img_file = img_src / lbl_file.name.replace(".txt", ".png")
                    if img_file.exists():
                        # Add prefix to avoid filename collisions
                        prefixed_name = f"{dataset_name}_{img_file.name}"
                        shutil.copy2(img_file, img_dst / prefixed_name)
                        (lbl_dst / lbl_file.name).write_text("\n".join(new_lines))
    
    return stats


def create_data_yaml(output_dir, total_stats):
    """Create data.yaml configuration"""
    yaml_content = f"""path: {str(output_dir).replace(chr(92), '/')}
train: train/images
val: valid/images
test: test/images

nc: 5
names:
  0: Caries
  1: Crown
  2: Filling
  3: Implant
  4: Periapical-lesion

# Dataset statistics
# Total images: {sum(total_stats.values())}
# Caries: {total_stats.get(0, 0)}
# Crown: {total_stats.get(1, 0)}
# Filling: {total_stats.get(2, 0)}
# Implant: {total_stats.get(3, 0)}
# Periapical-lesion: {total_stats.get(4, 0)}
"""
    (output_dir / "data.yaml").write_text(yaml_content)
    return yaml_content


def main():
    print("=" * 60)
    print("MERGING DENTAL DATASETS")
    print("=" * 60)
    
    # Create output directory
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    total_stats = Counter()
    
    # 1. Process oral-disease (biggest dataset)
    print("\n[1/3] Processing oral-disease (8,616 images)...")
    stats = process_oral_disease(OUTPUT)
    total_stats.update(stats)
    print(f"  Added: {dict(stats)}")
    
    # 2. Process dental_yolo_v8-420 (polygon → bbox)
    print("\n[2/3] Processing dental_yolo_v8-420 (3,802 images, polygon→bbox)...")
    stats = process_dental_yolo(OUTPUT)
    total_stats.update(stats)
    print(f"  Added: {dict(stats)}")
    
    # 3. Process our datasets
    print("\n[3/3] Processing our datasets (1,818 images)...")
    stats = process_our_datasets(OUTPUT)
    total_stats.update(stats)
    print(f"  Added: {dict(stats)}")
    
    # Create data.yaml
    print("\n[CONFIG] Creating data.yaml...")
    yaml_content = create_data_yaml(OUTPUT, total_stats)
    
    # Count final images
    print("\n" + "=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)
    
    for split in ["train", "valid", "test"]:
        img_dir = OUTPUT / split / "images"
        if img_dir.exists():
            count = len(list(img_dir.glob("*.jpg"))) + len(list(img_dir.glob("*.png")))
            print(f"  {split}: {count} images")
    
    print(f"\nClass distribution:")
    for cls_id, cls_name in TARGET_CLASSES.items():
        count = total_stats.get(cls_id, 0)
        print(f"  {cls_id}: {cls_name} = {count}")
    
    print(f"\nOutput: {OUTPUT}")
    print(f"Config: {OUTPUT / 'data.yaml'}")


if __name__ == "__main__":
    main()
