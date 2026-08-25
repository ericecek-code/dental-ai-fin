#!/usr/bin/env python3
"""Combine restorative-ai-bbox and original dental dataset into one."""

import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
COMBINED_DIR = REPO_ROOT / "combined-dataset"

# Source datasets
RESTORATIVE_DIR = REPO_ROOT / "restorative-ai-bbox"
ORIGINAL_DIR = Path(r"C:\Users\PC1\Documents\dental-caries-detector\data")

CLASS_NAMES = ["Caries", "Crown", "Filling", "Implant", "Periapical-lesion"]


def copy_with_rename(src_dir, dst_dir, prefix):
    """Copy files from src to dst, prefixing filenames to avoid conflicts."""
    count = 0
    if not src_dir.exists():
        return 0
    for f in src_dir.iterdir():
        if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.txt'}:
            new_name = f"{prefix}_{f.name}"
            dst = dst_dir / new_name
            if not dst.exists():
                shutil.copy2(str(f), str(dst))
                count += 1
    return count


def main():
    # Create directory structure
    for split in ["train", "val", "test"]:
        (COMBINED_DIR / split / "images").mkdir(parents=True, exist_ok=True)
        (COMBINED_DIR / split / "labels").mkdir(parents=True, exist_ok=True)

    total_images = 0
    total_labels = 0

    # 1. Copy restorative-ai-bbox (already converted to bbox format)
    print("Copying restorative-ai-bbox...")
    for split, rest_split in [("train", "train"), ("val", "valid"), ("test", "test")]:
        src_images = RESTORATIVE_DIR / rest_split / "images"
        src_labels = RESTORATIVE_DIR / rest_split / "labels"
        dst_images = COMBINED_DIR / split / "images"
        dst_labels = COMBINED_DIR / split / "labels"

        n_img = copy_with_rename(src_images, dst_images, "resto")
        n_lbl = copy_with_rename(src_labels, dst_labels, "resto")
        total_images += n_img
        total_labels += n_lbl
        print(f"  {split}: {n_img} images, {n_lbl} labels")

    # 2. Copy original dental dataset
    print("Copying original dental dataset...")
    # Original has images and labels in same dir (train/images/*.png + train/images/*.txt)
    for split, orig_split in [("train", "train"), ("val", "val")]:
        src_dir = ORIGINAL_DIR / orig_split / "images"
        dst_images = COMBINED_DIR / split / "images"
        dst_labels = COMBINED_DIR / split / "labels"

        if not src_dir.exists():
            print(f"  WARNING: {src_dir} not found, skipping")
            continue

        n_img = 0
        n_lbl = 0
        for f in src_dir.iterdir():
            if f.is_file():
                if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}:
                    new_name = f"orig_{f.name}"
                    dst = dst_images / new_name
                    if not dst.exists():
                        shutil.copy2(str(f), str(dst))
                        n_img += 1
                elif f.suffix.lower() == '.txt':
                    new_name = f"orig_{f.name}"
                    dst = dst_labels / new_name
                    if not dst.exists():
                        shutil.copy2(str(f), str(dst))
                        n_lbl += 1

        total_images += n_img
        total_labels += n_lbl
        print(f"  {split}: {n_img} images, {n_lbl} labels")

    # Create data.yaml
    data_yaml = COMBINED_DIR / "data.yaml"
    data_yaml.write_text(f"""path: {str(COMBINED_DIR).replace(chr(92), '/')}
train: train/images
val: val/images
test: test/images
nc: 5
names:
  0: Caries
  1: Crown
  2: Filling
  3: Implant
  4: Periapical-lesion
""", encoding="utf-8")

    print(f"\nCombined dataset created at: {COMBINED_DIR}")
    print(f"Total: {total_images} images, {total_labels} labels")
    print(f"data.yaml: {data_yaml}")

    # Final counts
    for split in ["train", "val", "test"]:
        n_img = len(list((COMBINED_DIR / split / "images").glob("*")))
        n_lbl = len(list((COMBINED_DIR / split / "labels").glob("*.txt")))
        print(f"  {split}: {n_img} images, {n_lbl} labels")


if __name__ == "__main__":
    main()
