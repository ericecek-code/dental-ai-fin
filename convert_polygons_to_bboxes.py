#!/usr/bin/env python3
"""Convert polygon/segmentation labels to YOLO bounding box format."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DATASET_DIR = REPO_ROOT / "restorative-ai-1"

# Class mapping from restorative-ai to our 5 target classes
# restorative-ai classes: 0=amalgam, 1=canal treatment, 2=caries, 3=composite, 
#                         4=crown, 5=implant, 6=implant_crown, 7=periapical lesion, 8=residual_root
# Target classes: 0=Caries, 1=Crown, 2=Filling, 3=Implant, 4=Periapical-lesion
CLASS_MAP = {
    0: 2,   # amalgam -> Filling
    1: None, # canal treatment -> skip
    2: 0,   # caries -> Caries
    3: 2,   # composite -> Filling
    4: 1,   # crown -> Crown
    5: 3,   # implant -> Implant
    6: 3,   # implant_crown -> Implant (closest)
    7: 4,   # periapical lesion -> Periapical-lesion
    8: None, # residual_root -> skip
}

TARGET_CLASSES = ["Caries", "Crown", "Filling", "Implant", "Periapical-lesion"]


def polygon_to_bbox(coords):
    """Convert polygon coordinates to bounding box [x_center, y_center, w, h]."""
    xs = coords[0::2]
    ys = coords[1::2]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2
    width = x_max - x_min
    height = y_max - y_min
    return x_center, y_center, width, height


def convert_label_file(input_path, output_path):
    """Convert a single label file from polygon to bbox format."""
    lines = input_path.read_text(encoding="utf-8").strip().split("\n")
    output_lines = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 3:
            continue
        class_id = int(parts[0])
        coords = [float(x) for x in parts[1:]]
        
        # Map to target class
        if class_id not in CLASS_MAP or CLASS_MAP[class_id] is None:
            continue
        
        target_class = CLASS_MAP[class_id]
        x_center, y_center, w, h = polygon_to_bbox(coords)
        
        # Clamp values to [0, 1]
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        w = max(0, min(1, w))
        h = max(0, min(1, h))
        
        output_lines.append(f"{target_class} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(output_lines), encoding="utf-8")
    return len(output_lines)


def main():
    output_dir = REPO_ROOT / "restorative-ai-bbox"
    total_objects = 0
    total_files = 0
    
    for split in ["train", "valid", "test"]:
        labels_dir = DATASET_DIR / split / "labels"
        images_dir = DATASET_DIR / split / "images"
        out_labels = output_dir / split / "labels"
        out_images = output_dir / split / "images"
        
        if not labels_dir.exists():
            continue
        
        # Copy images (symlink or copy)
        out_images.mkdir(parents=True, exist_ok=True)
        for img in images_dir.glob("*"):
            if img.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
                dst = out_images / img.name
                if not dst.exists():
                    dst.symlink_to(img.resolve()) if os.name != "nt" else None
                    if os.name == "nt":
                        import shutil
                        shutil.copy2(str(img), str(dst))
        
        # Convert labels
        for label_file in labels_dir.glob("*.txt"):
            out_file = out_labels / label_file.name
            n = convert_label_file(label_file, out_file)
            total_objects += n
            total_files += 1
    
    # Create data.yaml for the bbox dataset
    data_yaml = output_dir / "data.yaml"
    data_yaml.write_text(f"""path: {str(output_dir).replace(chr(92), '/')}
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
""", encoding="utf-8")
    
    print(f"Converted {total_files} label files, {total_objects} objects total")
    print(f"Output: {output_dir}")
    print(f"data.yaml: {data_yaml}")
    
    # Count per-split
    for split in ["train", "valid", "test"]:
        n_images = len(list((output_dir / split / "images").glob("*"))) if (output_dir / split / "images").exists() else 0
        n_labels = len(list((output_dir / split / "labels").glob("*.txt"))) if (output_dir / split / "labels").exists() else 0
        print(f"  {split}: {n_images} images, {n_labels} labels")


if __name__ == "__main__":
    main()
