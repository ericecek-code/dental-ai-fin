#!/usr/bin/env python3
"""
Consolidate multiple dental datasets into combined-dataset-v2
with proper train/val/test splits and class balancing.
"""
import shutil
from pathlib import Path
import random
import yaml

ROOT = Path(r"C:\Users\PC1\Desktop\dental-ai")
OUT = ROOT / "combined-dataset-v2"

# Class mapping: all datasets use same 5 classes
# 0: Caries, 1: Crown, 2: Filling, 3: Implant, 4: Periapical-lesion
CLASS_NAMES = ["Caries", "Crown", "Filling", "Implant", "Periapical-lesion"]

# Source datasets with their label directories
SOURCES = {
    "mega-dataset": {
        "train_img": "mega-dataset/train/images",
        "train_lbl": "mega-dataset/train/labels",
        "val_img": "mega-dataset/valid/images",
        "val_lbl": "mega-dataset/valid/labels",
        "test_img": "mega-dataset/test/images",
        "test_lbl": "mega-dataset/test/labels",
    },
    "combined-dataset": {
        "train_img": "combined-dataset/train/images",
        "train_lbl": "combined-dataset/train/labels",
        "val_img": "combined-dataset/val/images",
        "val_lbl": "combined-dataset/val/labels",
        "test_img": "combined-dataset/test/images",
        "test_lbl": "combined-dataset/test/labels",
    },
    "restorative-ai-bbox": {
        "train_img": "restorative-ai-bbox/train/images",
        "train_lbl": "restorative-ai-bbox/train/labels",
        "val_img": "restorative-ai-bbox/valid/images",
        "val_lbl": "restorative-ai-bbox/valid/labels",
        "test_img": "restorative-ai-bbox/test/images",
        "test_lbl": "restorative-ai-bbox/test/labels",
    },
    "test_caries_only": {
        "val_img": "verified_models/test_caries_only/val/images",
        "val_lbl": "verified_models/test_caries_only/val/labels",
    },
    "test_matched": {
        "val_img": "verified_models/test_matched/val/images",
        "val_lbl": "verified_models/test_matched/val/labels",
    },
    "restorative-ai-1": {
        # Different class mapping! Need to remap
        "train_img": "restorative-ai-1/train/images",
        "train_lbl": "restorative-ai-1/train/labels",
        "val_img": "restorative-ai-1/valid/images",
        "val_lbl": "restorative-ai-1/valid/labels",
        "test_img": "restorative-ai-1/test/images",
        "test_lbl": "restorative-ai-1/test/labels",
        "class_map": {0: 1, 1: 2, 2: 0, 3: 3, 4: 4, 5: 4}  # their 0=Crown, 1=Filling, 2=Caries, 3=Implant, 4=Periapical, 5=Periapical
    },
    "Dental-X-ray-1": {
        # Different classes: 0=Cavity, 1=Crown, 2=Filling, 3=Implant
        "train_img": "Dental-X-ray-1/train/images",
        "train_lbl": "Dental-X-ray-1/train/labels",
        "val_img": "Dental-X-ray-1/valid/images",
        "val_lbl": "Dental-X-ray-1/valid/labels",
        "test_img": "Dental-X-ray-1/test/images",
        "test_lbl": "Dental-X-ray-1/test/labels",
        "class_map": {0: 0, 1: 1, 2: 2, 3: 3}  # Cavity->Caries, Crown, Filling, Implant
    },
}

def copy_split(src_img_dir, src_lbl_dir, dst_img_dir, dst_lbl_dir, class_map=None, prefix=""):
    """Copy images and labels with optional class remapping."""
    src_img = ROOT / src_img_dir
    src_lbl = ROOT / src_lbl_dir
    dst_img = OUT / dst_img_dir
    dst_lbl = OUT / dst_lbl_dir
    
    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)
    
    if not src_img.exists():
        print(f"  ⚠️  Missing: {src_img}")
        return 0
    
    count = 0
    for img_file in src_img.glob("*.jpg"):
        lbl_file = src_lbl / (img_file.stem + ".txt")
        if not lbl_file.exists():
            continue
        
        # Read and remap labels
        lines = lbl_file.read_text().strip().splitlines()
        new_lines = []
        for line in lines:
            parts = line.split()
            cls = int(parts[0])
            if class_map and cls in class_map:
                cls = class_map[cls]
            if cls >= 5:  # skip classes we don't use
                continue
            parts[0] = str(cls)
            new_lines.append(" ".join(parts))
        
        if not new_lines:
            continue
        
        # Write new label
        new_name = f"{prefix}{img_file.name}"
        (dst_lbl / (img_file.stem + f"_{prefix}.txt")).write_text("\n".join(new_lines))
        shutil.copy2(img_file, dst_img / new_name)
        count += 1
    
    return count

def main():
    print("🔄 Consolidating datasets into combined-dataset-v2...")
    
    # Clean output
    if OUT.exists():
        shutil.rmtree(OUT)
    
    # Create directory structure
    for split in ["train", "val", "test"]:
        (OUT / split / "images").mkdir(parents=True, exist_ok=True)
        (OUT / split / "labels").mkdir(parents=True, exist_ok=True)
    
    stats = {"train": 0, "val": 0, "test": 0}
    class_counts = {"train": {}, "val": {}, "test": {}}
    
    for ds_name, paths in SOURCES.items():
        print(f"\n📦 Processing {ds_name}...")
        class_map = paths.get("class_map")
        
        # Train
        if "train_img" in paths:
            n = copy_split(
                paths["train_img"], paths["train_lbl"],
                "train/images", "train/labels",
                class_map, prefix=f"{ds_name}_"
            )
            stats["train"] += n
            print(f"  Train: +{n} images")
        
        # Val
        if "val_img" in paths:
            n = copy_split(
                paths["val_img"], paths["val_lbl"],
                "val/images", "val/labels",
                class_map, prefix=f"{ds_name}_"
            )
            stats["val"] += n
            print(f"  Val: +{n} images")
        
        # Test
        if "test_img" in paths:
            n = copy_split(
                paths["test_img"], paths["test_lbl"],
                "test/images", "test/labels",
                class_map, prefix=f"{ds_name}_"
            )
            stats["test"] += n
            print(f"  Test: +{n} images")
    
    # Count classes
    for split in ["train", "val", "test"]:
        lbl_dir = OUT / split / "labels"
        for lbl_file in lbl_dir.glob("*.txt"):
            for line in lbl_file.read_text().strip().splitlines():
                cls = int(line.split()[0])
                class_counts[split][cls] = class_counts[split].get(cls, 0) + 1
    
    # Print summary
    print("\n📊 Final Statistics:")
    for split in ["train", "val", "test"]:
        print(f"\n  {split.upper()} ({stats[split]} images):")
        for cls in range(5):
            cnt = class_counts[split].get(cls, 0)
            print(f"    {CLASS_NAMES[cls]}: {cnt}")
    
    # Write data.yaml
    data_yaml = {
        "path": str(OUT),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "nc": 5,
        "names": CLASS_NAMES
    }
    (OUT / "data.yaml").write_text(yaml.dump(data_yaml, sort_keys=False))
    print(f"\n✅ Done! Output: {OUT}")
    print(f"   data.yaml written to {OUT / 'data.yaml'}")

if __name__ == "__main__":
    main()