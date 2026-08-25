#!/usr/bin/env python3
"""
Convert DENTEX dataset from COCO format to YOLO format.
DENTEX uses hierarchical annotations: categories_3 = diagnoses (4 classes)
"""

import json
import shutil
from pathlib import Path

# Paths
DATASET_ROOT = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex")
SRC_DIR = DATASET_ROOT / "training_data" / "training_data" / "quadrant-enumeration-disease"
IMAGES_DIR = DATASET_ROOT / "images"
LABELS_DIR = DATASET_ROOT / "labels"

# Create directory structure
for split in ["train", "val"]:
    (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)


def convert_coco_to_yolo(coco_ann, img_width, img_height):
    """Convert COCO bbox [x, y, w, h] to YOLO [x_center, y_center, w, h] normalized."""
    x, y, w, h = coco_ann['bbox']
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height
    w_norm = w / img_width
    h_norm = h / img_height
    return x_center, y_center, w_norm, h_norm


def process_split(split_name, json_file):
    """Process a dataset split."""
    print(f"\n=== Processing {split_name} ===")
    
    with open(json_file) as f:
        data = json.load(f)
    
    # Build image_id -> annotations mapping
    annotations = {}
    for ann in data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations:
            annotations[img_id] = []
        annotations[img_id].append(ann)
    
    # Build image_id -> image_info mapping
    img_info = {img['id']: img for img in data['images']}
    
    src_img_dir = Path(json_file).parent.parent / "xrays"
    
    count = 0
    for img_id, ann_list in annotations.items():
        if img_id not in img_info:
            continue
        
        info = img_info[img_id]
        src_img = src_img_dir / info['file_name']
        if not src_img.exists():
            print(f"  Warning: Image not found: {info['file_name']}")
            continue
        
        # Copy image
        dst_img = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex/images") / split_name / info['file_name']
        shutil.copy2(src_img, dst_img)
        
        # Create label file
        label_path = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex/labels") / split_name / (Path(info['file_name']).stem + ".txt")
        with open(label_path, 'w') as f:
            for ann in ann_list:
                # Use category_id_3 (diagnosis: 0=Impacted, 1=Caries, 2=Periapical, 3=Deep Caries)
                class_id = ann['category_id_3']
                xc, yc, w, h = convert_coco_to_yolo(ann, info['width'], info['height'])
                f.write(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
        
        count += 1
        if count % 100 == 0:
            print(f"  Processed {count}...")
    
    print(f"  Done: {count} images")
    return count


def main():
    print("Converting DENTEX dataset to YOLO format...")
    
    # Process training
    train_json = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex/training_data/training_data/quadrant-enumeration-disease/train_quadrant_enumeration_disease.json")
    train_count = process_split("train", train_json)
    
    # For validation, we only have images without annotations
    # Copy validation images
    val_img_src = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex/validation_data/validation_data/quadrant_enumeration_disease/xrays")
    val_img_dst = Path("/c/Users/PC1/Desktop/dental-ai/datasets/kaggle_dentex/images/val")
    val_img_dst.mkdir(parents=True, exist_ok=True)
    
    val_count = 0
    for img_file in val_img_src.glob("*.png"):
        shutil.copy2(img_file, val_img_dst / img_file.name)
        val_count += 1
    print(f"\nValidation: {val_count} images (no annotations)")
    
    print(f"\n=== Conversion complete ===")
    print(f"Train: {train_count} images + labels")
    print(f"Val: {val_count} images (no labels)")


if __name__ == "__main__":
    main()