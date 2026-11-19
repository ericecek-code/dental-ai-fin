# Kaggle Training Instructions for Agent

## Goal
Train YOLOv8 model on dental X-ray dataset for detecting dental conditions.

## Dataset
- **Name:** Mega Dental Dataset
- **Local path:** `C:\Users\PC1\Desktop\dental-ai\mega-dataset`
- **Zip file:** `C:\Users\PC1\Desktop\dental-ai\mega-dataset.zip` (741 MB)
- **Kaggle dataset:** `eriksmite/mega-dataset-dental` (already uploaded)
- **Classes:** 5 (Caries, Crown, Filling, Implant, Periapical-lesion)
- **Images:** 7,228 train / 1,840 valid / 1,103 test

## Kaggle Account
- **Username:** eriksmite
- **API key location:** `C:\Users\PC1\.kaggle\kaggle.json`

## Important: Known Errors and Solutions

### Error 1: Read-only file system
```
OSError: [Errno 30] Read-only file system: '/kaggle/input/.../data.yaml'
```
**Cause:** `/kaggle/input/` directory is read-only on Kaggle.
**Solution:** Copy dataset to `/kaggle/working/` before modifying:
```python
import shutil
shutil.copytree("/kaggle/input/mega-dataset-dental/mega-dataset", "/kaggle/working/dataset")
DATASET_PATH = "/kaggle/working/dataset"
```

### Error 2: Dataset path issues
```
FileNotFoundError: '/kaggle/input/mega-dataset-dental/data.yaml' does not exist
```
**Cause:** Dataset is nested: actual path is `/kaggle/input/mega-dataset-dental/mega-dataset/data.yaml`
**Solution:** Use correct nested path:
```python
DATASET_PATH = "/kaggle/input/mega-dataset-dental/mega-dataset"
```

### Error 3: CUDA compatibility (Tesla P100)
```
CUDA error: no kernel image is available for execution on the device
```
**Cause:** Tesla P100 (CUDA 6.0) is not compatible with current PyTorch on Kaggle (requires CUDA 7.0-12.0).
**Solution:** Use Google Colab with T4 GPU instead, or use local GPU (GTX 1080 Ti).

### Error 4: nbformat is null
```
Error converting value {null} to type 'System.Int32'. Path 'nbformat'
```
**Cause:** Notebook JSON format is invalid.
**Solution:** Create notebook using nbformat library:
```python
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
# Add cells...
nbf.write(nb, "notebook.ipynb")
```

## Recommended Training Configuration

### For Kaggle (if CUDA issue resolved):
```python
CONFIG = {
    "model": "yolov8m.pt",
    "data": "/kaggle/working/dataset/data.yaml",
    "epochs": 60,
    "imgsz": 640,
    "batch": 16,
    "device": 0,
    "workers": 4,
    "amp": True,
    "mosaic": 1.0,
    "flipud": 0.0,
    "fliplr": 0.5,
    "mixup": 0.1,
    "copy_paste": 0.1,
}
```

### For Google Colab (recommended):
Same config but use:
```python
DATASET_PATH = "/content/mega-dataset"
# Upload mega-dataset.zip and unzip
!unzip -q /content/mega-dataset.zip -d /content/
```

## Complete Working Notebook Code

```python
# Install dependencies
!pip install -q ultralytics pyyaml

# Import libraries
import os
import torch
from pathlib import Path
import yaml
import shutil
import time
from ultralytics import YOLO

# Check GPU
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")

# Dataset path (adjust for platform)
# Kaggle: DATASET_PATH = "/kaggle/input/mega-dataset-dental/mega-dataset"
# Colab:  DATASET_PATH = "/content/mega-dataset"
DATASET_PATH = "/kaggle/input/mega-dataset-dental/mega-dataset"

# Fix data.yaml (copy to working directory first on Kaggle)
yaml_path = f"{DATASET_PATH}/data.yaml"
if os.path.exists(yaml_path):
    with open(yaml_path) as f:
        config = yaml.safe_load(f)
    config['path'] = DATASET_PATH
    with open(yaml_path, 'w') as f:
        yaml.dump(config, f)
    print(f"✅ Fixed data.yaml: {config.get('nc')} classes")
else:
    print(f"❌ data.yaml not found at {yaml_path}")

# Training configuration
CONFIG = {
    "model": "yolov8m.pt",
    "data": f"{DATASET_PATH}/data.yaml",
    "epochs": 60,
    "imgsz": 640,
    "batch": 16,
    "device": 0,
    "project": "/kaggle/working/runs/detect",
    "name": "dental_5class_v1",
    "patience": 15,
    "lr0": 0.001,
    "lrf": 0.01,
    "optimizer": "AdamW",
    "momentum": 0.937,
    "weight_decay": 0.0005,
    "warmup_epochs": 3,
    "box": 7.5,
    "cls": 0.5,
    "dfl": 1.5,
    "cos_lr": True,
    "close_mosaic": 10,
    "workers": 4,
    "amp": True,
    "save": True,
    "save_period": 10,
    "verbose": True,
    "seed": 42,
    "mosaic": 1.0,
    "mixup": 0.1,
    "copy_paste": 0.1,
    "hsv_h": 0.015,
    "hsv_s": 0.7,
    "hsv_v": 0.4,
    "fliplr": 0.5,
}

# Start training
print("🚀 Starting training...")
model = YOLO(CONFIG["model"])
start_time = time.time()
results = model.train(**CONFIG)
elapsed = time.time() - start_time
print(f"\n✅ Training completed in {elapsed/3600:.1f} hours")

# Validation
metrics = model.val(data=CONFIG["data"], split="test")
print(f"\n📊 RESULTS:")
print(f"mAP50: {metrics.box.map50:.4f}")
print(f"mAP50-95: {metrics.box.map:.4f}")
print(f"Precision: {metrics.box.mp:.4f}")
print(f"Recall: {metrics.box.mr:.4f}")

# Per-class results
print("\nPer-class mAP50:")
for cls_id, cls_name in model.names.items():
    if cls_id in metrics.box.ap_class_index:
        idx = list(metrics.box.ap_class_index).index(cls_id)
        ap50 = metrics.box.ap50[idx]
        print(f"  {cls_name}: {ap50:.4f}")

# Save model
OUTPUT_DIR = "/kaggle/working/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
shutil.copy2(f"/kaggle/working/runs/detect/{CONFIG['name']}/weights/best.pt", f"{OUTPUT_DIR}/best.pt")
print(f"\n✅ Model saved to: {OUTPUT_DIR}/best.pt")
```

## Expected Results

| Metric | Expected Value |
|--------|----------------|
| mAP50 | 0.65-0.75 |
| mAP50-95 | 0.45-0.55 |
| Precision | 0.70-0.80 |
| Recall | 0.60-0.70 |

## Alternative: Local Training (GTX 1080 Ti)

If Kaggle CUDA issue persists, use local training:
```bash
python train.py
```

Training script is at: `C:\Users\PC1\Desktop\dental-ai\train.py`
Expected time: ~2 hours on GTX 1080 Ti

## Files Location

```
C:\Users\PC1\Desktop\dental-ai\
├── mega-dataset\              # Dataset folder
├── mega-dataset.zip           # 741 MB zip file
├── train.py                   # Local training script
├── dental_ai_1080ti.ipynb     # Jupyter notebook
└── KAGGLE_INSTRUCTIONS_FOR_AGENT.md  # This file
```

## Summary of Issues

1. **Kaggle CUDA incompatibility** - Tesla P100 not supported by PyTorch
2. **Read-only filesystem** - Cannot modify files in `/kaggle/input/`
3. **Nested dataset path** - Dataset is at `/kaggle/input/mega-dataset-dental/mega-dataset/`
4. **Notebook format issues** - Must use nbformat library for proper format

## Recommended Action

1. Try Google Colab first (T4 GPU works)
2. If Kaggle is required, resolve CUDA issue or use CPU training
3. Use local GTX 1080 Ti as fallback
