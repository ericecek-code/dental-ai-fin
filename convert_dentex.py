#!/usr/bin/env python3
"""
Convert DENTEX dataset from COCO format to YOLO format.
DENTEX uses hierarchical annotations: categories_3 = diagnoses (4 classes)
"""

import json
import zipfile
from pathlib import Path
import shutil

# Paths
DATASET_ROOT = Path("datasets/dentex")
DENTEX_DIR = DATASET_ROOT / "DENTEX"
IMAGES_DIR = DATASET_ROOT / "images"
LABELS_DIR = DATASET_ROOT / "labels"

# Create directory structure
for split in ["train", "val", "test"]:
    (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)


def extract_zip(zip_path, extract_to):
    """Extract zip file."""
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)
    print(f"  Extracted to {extract_to}")


def convert_coco_to_yolo(coco_ann, img_width, img_height):
    """Convert COCO bbox [x, y, w, h] to YOLO [x_center, y_center, w, h] normalized."""
    x, y, w, h = coco_ann['bbox']
    x_center = (x + w / 2) / img_width
    y_center = (y + h / 2) / img_height
    w_norm = w / img_width
    h_norm = h / img_height
    return x_center, y_center, w_norm, h_norm


def process_split(split_name, zip_file, json_file=None):
    """Process a dataset split."""
    print(f"\n=== Processing {split_name} ===")
    
    # Extract images
    extract_dir = DENTEX_DIR / split_name
    if not extract_dir.exists():
        extract_zip(zip_file, extract_dir)
    
    # Find images
    image_files = list(extract_dir.rglob("*.png")) + list(extract_dir.rglob("*.jpg"))
    print(f"Found {len(image_files)} images")
    
    # Load annotations if JSON provided
    annotations = {}
    if json_file and json_file.exists():
        with open(json_file) as f:
            data = json.load(f)
        
        # Build image_id -> annotations mapping
        for ann in data['annotations']:
            img_id = ann['image_id']
            if img_id not in annotations:
                annotations[img_id] = []
            annotations[img_id].append(ann)
        
        # Build image_id -> image_info mapping
        img_info = {img['id']: img for img in data['images']}
        
        # Copy images and create labels
        for img_id, anns in annotations.items():
            if img_id not in img_info:
                continue
            
            info = img_info[img_id]
            src_img = extract_dir / info['file_name']
            if not src_img.exists():
                # Try finding in subdirectories
                found = list(extract_dir.rglob(info['file_name']))
                if found:
                    src_img = found[0]
            
            if not src_img.exists():
                print(f"  Warning: Image not found: {info['file_name']}")
                continue
            
            # Copy image
            dst_img = IMAGES_DIR / split_name / info['file_name']
            shutil.copy2(src_img, dst_img)
            
            # Create label file
            label_path = LABELS_DIR / split_name / (Path(info['file_name']).stem + ".txt")
            with open(label_path, 'w') as f:
                for ann in anns:
                    # Use category_id_3 (diagnosis: 0=Impacted, 1=Caries, 2=Periapical, 3=Deep Caries)
                    class_id = ann['category_id_3']
                    xc, yc, w, h = convert_coco_to_yolo(ann, info['width'], info['height'])
                    f.write(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
            
            print(f"  {info['file_name']}: {len(anns)} annotations")
    
    else:
        # No annotations - just copy images (e.g., test set without labels)
        for img_file in image_files:
            dst_img = IMAGES_DIR / split_name / img_file.name
            shutil.copy2(img_file, dst_img)
        print(f"  Copied {len(image_files)} images without annotations")


def main():
    print("Converting DENTEX dataset to YOLO format...")
    
    # Process validation (has annotations in validation_triple.json)
    process_split(
        "val",
        DENTEX_DIR / "validation_data.zip",
        DENTEX_DIR / "validation_triple.json"
    )
    
    # Process test (has annotations in test_triple.json if exists, otherwise just images)
    test_json = DENTEX_DIR / "test_triple.json"
    if test_json.exists():
        process_split("test", DENTEX_DIR / "test_data.zip", test_json)
    else:
        process_split("test", DENTEX_DIR / "test_data.zip")
    
    # Process training (training_data.zip - large, may take time)
    train_json = DENTEX_DIR / "training_triple.json"
    if train_json.exists():
        process_split("train", DENTEX_DIR / "training_data.zip", train_json)
    else:
        print("\nTraining annotations not found yet. Checking training_data.zip...")
        # Just extract and copy images for now
        process_split("train", DENTEX_DIR / "training_data.zip")
    
    print("\n=== Conversion complete ===")
    for split in ["train", "val", "test"]:
        img_count = len(list((IMAGES_DIR / split).glob("*")))
        lbl_count = len(list((LABELS_DIR / split).glob("*.txt")))
        print(f"  {split}: {img_count} images, {lbl_count} label files")


if __name__ == "__main__":
    main()