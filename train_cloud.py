#!/usr/bin/env python3
"""
Universal Cloud Training Script for Dental AI
Works on: Kaggle, Colab, RunPod, Local GPU, CPU

Usage:
    python train_cloud.py                    # Auto-detect environment
    python train_cloud.py --config config.yaml  # Custom config
    python train_cloud.py --model yolov8m --epochs 50  # Override args
"""

import os
import sys
import argparse
import yaml
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# ============================================================
# 🔧 ENVIRONMENT DETECTION
# ============================================================

def detect_environment() -> Dict[str, Any]:
    """Detect the current runtime environment."""
    env = {
        "platform": "unknown",
        "gpu_available": False,
        "gpu_type": "unknown",
        "drive_mounted": False,
        "kaggle_available": False,
        "colab_available": False,
        "hf_token": os.environ.get("HF_TOKEN", ""),
        "kaggle_username": os.environ.get("KAGGLE_USERNAME", ""),
        "kaggle_key": os.environ.get("KAGGLE_KEY", ""),
    }
    
    # Check for Kaggle
    if os.environ.get("KAGGLE_KERNEL_RUN_TYPE") or os.path.exists("/kaggle"):
        env["platform"] = "kaggle"
        env["gpu_available"] = True
        env["kaggle_available"] = True
        try:
            import torch
            if torch.cuda.is_available():
                env["gpu_type"] = torch.cuda.get_device_name(0)
        except:
            pass
    
    # Check for Colab
    elif "COLAB_GPU" in os.environ or os.path.exists("/content"):
        env["platform"] = "colab"
        env["colab_available"] = True
        env["gpu_available"] = True
        try:
            import torch
            if torch.cuda.is_available():
                env["gpu_type"] = torch.cuda.get_device_name(0)
        except:
            pass
        # Check for Drive mount
        if os.path.exists("/content/drive"):
            env["drive_mounted"] = True
    
    # Check for RunPod
    elif os.environ.get("RUNPOD_POD_ID"):
        env["platform"] = "runpod"
        env["gpu_available"] = True
        try:
            import torch
            if torch.cuda.is_available():
                env["gpu_type"] = torch.cuda.get_device_name(0)
        except:
            pass
    
    # Local
    else:
        env["platform"] = "local"
        try:
            import torch
            if torch.cuda.is_available():
                env["gpu_available"] = True
                env["gpu_type"] = torch.cuda.get_device_name(0)
        except:
            pass
    
    return env


# ============================================================
# ⚙️ CONFIGURATION MANAGEMENT
# ============================================================

DEFAULT_CONFIG = {
    "model": "yolov8x.pt",
    "data": "datasets/dentex/data.yaml",
    "epochs": 100,
    "imgsz": 1280,
    "batch": 16,
    "device": 0,
    "project": "runs/detect",
    "name": "dentex_v1",
    "patience": 20,
    "lr0": 0.01,
    "cos_lr": True,
    "close_mosaic": 10,
    "workers": 4,
    "amp": True,
    "save": True,
    "save_period": 10,
    "cache": False,
    "verbose": True,
    # Cloud-specific
    "upload_hf": False,
    "hf_repo": "ericecek/dental-ai-models",
    "export_onnx": True,
    # Data
    "download_data": True,
    "dataset": "dentex",
    "dataset_source": "kaggle",
}

def load_config(config_path: Optional[str] = None, overrides: Dict = None) -> Dict:
    """Load configuration from YAML file with optional overrides."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            file_config = yaml.safe_load(f)
            if file_config:
                config.update(file_config)
    
    if overrides:
        config.update(overrides)
    
    return config


def save_config(config: Dict, path: str):
    """Save configuration to YAML file."""
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


# ============================================================
# 📥 DATA MANAGEMENT
# ============================================================

def download_kaggle_dataset(dataset_slug: str, output_dir: str) -> str:
    """Download dataset from Kaggle."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        username = os.environ.get("KAGGLE_USERNAME")
        key = os.environ.get("KAGGLE_KEY")
        
        if not username or not key:
            raise ValueError("KAGGLE_USERNAME and KAGGLE_KEY environment variables required")
        
        api = KaggleApi()
        api.authenticate()
        
        print(f"📥 Downloading {dataset_slug}...")
        api.dataset_download_files(dataset_slug, path=output_dir, unzip=True)
        print(f"✅ Dataset downloaded to {output_dir}")
        return output_dir
    except Exception as e:
        print(f"❌ Failed to download dataset: {e}")
        raise


def convert_dentex_to_yolo(dataset_path: str, output_dir: str) -> Dict[str, int]:
    """Convert DENTEX dataset from COCO to YOLO format."""
    import json
    import shutil
    from pathlib import Path
    
    SRC_DIR = Path(dataset_path) / "training_data" / "training_data" / "quadrant-enumeration-disease"
    VAL_DIR = Path(dataset_path) / "validation_data" / "validation_data" / "quadrant_enumeration_disease"
    YOLO_DIR = Path(output_dir) / "dentex_yolo"
    
    for split in ["train", "val"]:
        (YOLO_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (YOLO_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)
    
    def convert_coco_to_yolo(coco_ann, img_width, img_height):
        x, y, w, h = coco_ann['bbox']
        return (x + w/2) / img_width, (y + h/2) / img_height, w / img_width, h / img_height
    
    def process_split(split_name, json_file, src_img_dir):
        with open(json_file) as f:
            data = json.load(f)
        
        annotations = {}
        for ann in data['annotations']:
            img_id = ann['image_id']
            annotations.setdefault(img_id, []).append(ann)
        
        img_info = {img['id']: img for img in data['images']}
        
        count = 0
        for img_id, ann_list in annotations.items():
            if img_id not in img_info:
                continue
            info = img_info[img_id]
            src_img = Path(src_img_dir) / info['file_name']
            if not src_img.exists():
                continue
            
            dst_img = Path(output_dir) / "dentex_yolo" / "images" / split_name / info['file_name']
            dst_img.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_img, dst_img)
            
            label_path = Path(output_dir) / "dentex_yolo" / "labels" / split_name / (Path(info['file_name']).stem + ".txt")
            label_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(label_path, 'w') as f:
                for ann in ann_list:
                    class_id = ann['category_id_3']
                    xc, yc, w, h = (ann['bbox'][0] + ann['bbox'][2]/2) / info['width'], \
                                   (ann['bbox'][1] + ann['bbox'][3]/2) / info['height'], \
                                   ann['bbox'][2] / info['width'], ann['bbox'][3] / info['height']
                    f.write(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
            count += 1
        return count
    
    # Process training
    train_json = Path(dataset_path) / "training_data" / "training_data" / "quadrant-enumeration-disease" / "train_quadrant_enumeration_disease.json"
    train_img_src = Path(dataset_path) / "training_data" / "training_data" / "quadrant-enumeration-disease" / "xrays"
    train_count = process_split("train", str(train_json), str(train_img_src))
    
    # Validation
    val_img_src = Path(dataset_path) / "validation_data" / "validation_data" / "quadrant_enumeration_disease" / "xrays"
    val_img_dst = Path(output_dir) / "dentex_yolo" / "images" / "val"
    val_img_dst.mkdir(parents=True, exist_ok=True)
    val_count = 0
    for img_file in Path(val_img_src).glob("*.png"):
        shutil.copy2(img_file, val_img_dst / img_file.name)
        val_count += 1
    
    return {"train": train_count, "val": val_count}


def create_data_yaml(yolo_dir: str, output_path: str):
    """Create data.yaml for YOLO training."""
    yaml_content = f"""# DENTEX Dataset - YOLO Configuration
# Classes: 4 diagnoses from DENTEX categories_3
# 0: Impacted
# 1: Caries
# 2: Periapical Lesion
# 3: Deep Caries

path: {yolo_dir}
train: images/train
val: images/val

names:
  0: Impacted
  1: Caries
  2: Periapical Lesion
  3: Deep Caries

nc: 4
"""
    with open(output_path, 'w') as f:
        f.write(yaml_content)
    print(f"✅ data.yaml created at: {output_path}")


# ============================================================
# 🏋️ TRAINING
# ============================================================

def train_model(config: Dict, env: Dict) -> Dict:
    """Train YOLO model."""
    from ultralytics import YOLO
    
    model = YOLO(config["model"])
    
    print(f"🚀 Starting training on {env['platform']} ({env['gpu_type']})")
    print(f"Model: {config['model']}, Epochs: {config['epochs']}, Batch: {config['batch']}, imgsz: {config['imgsz']}")
    
    results = model.train(
        data=config["data"],
        epochs=config["epochs"],
        imgsz=config["imgsz"],
        batch=config["batch"],
        device=config["device"],
        project=config["project"],
        name=config["name"],
        patience=config["patience"],
        lr0=config["lr0"],
        cos_lr=config["cos_lr"],
        close_mosaic=config["close_mosaic"],
        workers=config["workers"],
        amp=config["amp"],
        save=config["save"],
        save_period=config["save_period"],
        cache=config["cache"],
        verbose=config["verbose"],
    )
    
    return {
        "model": model,
        "results": results,
    }


def validate_model(model, config: Dict) -> Dict:
    """Validate trained model."""
    metrics = model.val(
        data=config["data"],
        split="val",
        imgsz=config["imgsz"],
        batch=config["batch"]
    )
    
    class_names = ["Impacted", "Caries", "Periapical Lesion", "Deep Caries"]
    results = {
        "mAP50": float(metrics.box.map50),
        "mAP50-95": float(metrics.box.map),
        "precision": float(metrics.box.mp),
        "recall": float(metrics.box.mr),
        "per_class": {}
    }
    
    for i, (ap50, rec) in enumerate(zip(metrics.box.ap50, metrics.box.recall)):
        results["per_class"][i] = {
            "name": ["Impacted", "Caries", "Periapical Lesion", "Deep Caries"][i],
            "AP50": float(ap50),
            "Recall": float(rec)
        }
    
    return results


def export_model(model, config: Dict, output_dir: str):
    """Export model to ONNX and other formats."""
    if not config.get("export_onnx", True):
        return
    
    print("📦 Exporting to ONNX...")
    onnx_path = model.export(format="onnx", imgsz=config["imgsz"], simplify=True)
    print(f"✅ ONNX model: {onnx_path}")
    
    # Copy to output dir
    onnx_file = Path(onnx_path)
    if onnx_file.exists():
        shutil.copy2(onnx_file, Path(output_dir) / "best.onnx")
        print(f"✅ ONNX copied to {output_dir}/best.onnx")


def upload_to_huggingface(model_path: str, repo_id: str, token: str):
    """Upload model to HuggingFace Hub."""
    try:
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo="yolov8x_dental.pt",
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"✅ Uploaded to HuggingFace: {repo_id}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")


# ============================================================
# 🎯 MAIN ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Universal Cloud Training for Dental AI")
    parser.add_argument("--config", type=str, help="Path to config YAML")
    parser.add_argument("--model", type=str, help="Model to train (yolov8x.pt, yolov8m.pt, etc.)")
    parser.add_argument("--epochs", type=int, help="Number of epochs")
    parser.add_argument("--batch", type=int, help="Batch size")
    parser.add_argument("--imgsz", type=int, help="Image size")
    parser.add_argument("--batch", type=int, help="Batch size")
    parser.add_argument("--epochs", type=int, help="Number of epochs")
    parser.add_argument("--imgsz", type=int, help="Image size")
    parser.add_argument("--batch", type=int, help="Batch size")
    parser.add_argument("--model", type=str, help="Model variant (yolov8x.pt, yolov8m.pt, yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=None, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=None, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=None, help="Image size")
    parser.add_argument("--data", type=str, default=None, help="Data YAML path")
    parser.add_argument("--project", type=str, default=None, help="Project directory")
    parser.add_argument("--name", type=str, default=None, help="Run name")
    parser.add_argument("--device", type=int, default=0, help="GPU device index")
    parser.add_argument("--epochs", type=int, help="Number of epochs")
    parser.add_argument("--batch", type=int, help="Batch size")
    parser.add_argument("--imgsz", type=int, help="Image size")
    parser.add_argument("--model", type=str, help="Model to train")
    parser.add_argument("--data", type=str, help="Data YAML path")
    parser.add_argument("--project", type=str, help="Project directory")
    parser.add_argument("--name", type=str, help="Run name")
    parser.add_argument("--device", type=int, default=0, help="GPU device")
    parser.add_argument("--epochs", type=int, help="Epochs")
    parser.add_argument("--batch", type=int, help="Batch size")
    parser.add_argument("--imgsz", type=int, help="Image size")
    parser.add_argument("--upload-hf", action="store_true", help="Upload to HuggingFace")
    parser.add_argument("--hf-repo", type=str, help="HF repo ID")
    parser.add_argument("--hf-token", type=str, help="HF token")
    parser.add_argument("--download-data", action="store_true", help="Download dataset")
    parser.add_argument("--dataset", type=str, default="dentex", help="Dataset name")
    parser.add_argument("--no-train", action="store_true", help="Only prepare data, don't train")
    parser.add_argument("--export-only", action="store_true", help="Only export existing model")
    parser.add_argument("--model-path", type=str, help="Path to model for export")
    
    args = parser.parse_args()
    
    # Detect environment
    env = detect_environment()
    print(f"🖥️  Environment: {env['platform']} | GPU: {env['gpu_type']} | Available: {env['gpu_available']}")
    
    # Build config
    overrides = {k: v for k, v in vars(args).items() if v is not None}
    config = load_config(args.config, overrides)
    
    # Set defaults based on environment
    if env["platform"] == "colab":
        config.setdefault("project", "/content/drive/MyDrive/dental-ai/runs/detect")
    elif env["platform"] == "kaggle":
        config.setdefault("project", "/kaggle/working/runs/detect")
    
    print(f"📋 Config: {config['model']} | epochs={config['epochs']} | batch={config['batch']} | imgsz={config['imgsz']}")
    
    # Download data if needed
    if config.get("download_data") and config.get("dataset") == "dentex":
        dataset_dir = "datasets/kaggle_dentex"
        if not os.path.exists("datasets/kaggle_dentex/training_data"):
            print("📥 Downloading DENTEX dataset...")
            download_kaggle_dataset("truthisneverlinear/dentex-challenge-2023", "datasets")
        
        # Convert to YOLO
        if not os.path.exists("datasets/kaggle_dentex/dentex_yolo/data.yaml"):
            print("🔄 Converting dataset to YOLO format...")
            stats = convert_dentex_to_yolo("datasets/kaggle_dentex", "datasets/kaggle_dentex")
            create_data_yaml("datasets/kaggle_dentex/dentex_yolo", "datasets/kaggle_dentex/dentex_yolo/data.yaml")
            print(f"✅ Dataset converted: {stats}")
        
        config["data"] = "datasets/kaggle_dentex/dentex_yolo/data.yaml"
    
    # Export only mode
    if args.export_only:
        if not args.model_path:
            print("❌ --model-path required for export-only mode")
            return
        from ultralytics import YOLO
        model = YOLO(args.model_path)
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        model.export(format="onnx", imgsz=config["imgsz"], simplify=True)
        # Copy to output
        for f in Path(".").rglob("*.onnx"):
            shutil.copy2(f, f"exports/{f.name}")
        print(f"✅ Exported to exports/")
        return
    
    if args.no_train:
        print("✅ Data preparation complete. Run without --no-train to start training.")
        return
    
    # Train
    if not os.path.exists(config["data"]):
        print(f"❌ Data config not found: {config['data']}")
        print("Run with --download-data first")
        return
    
    # Train
    train_result = train_model(config, detect_environment())
    model = train_result["model"]
    
    # Validate
    metrics = validate_model(model, config)
    print(f"\n📊 Results:")
    print(f"  mAP50: {metrics['mAP50']:.4f}")
    print(f"  mAP50-95: {metrics['mAP50-95']:.4f}")
    for cls_id, cls_metrics in metrics["per_class"].items():
        print(f"  {cls_metrics['name']}: AP50={cls_metrics['AP50']:.4f}, Recall={cls_metrics['Recall']:.4f}")
    
    # Check targets
    if metrics['mAP50'] >= 0.50:
        print("✅ mAP50 target (≥0.50) PASSED")
    else:
        print("❌ mAP50 target (≥0.50) FAILED")
    
    if metrics["per_class"][1]["Recall"] >= 0.65:
        print("✅ Caries Recall target (≥0.65) PASSED")
    else:
        print("❌ Caries Recall target (≥0.65) FAILED")
    
    # Export
    output_dir = "exports"
    os.makedirs(output_dir, exist_ok=True)
    export_model(train_result["model"], config, output_dir)
    
    # Upload to HF
    if config.get("upload_hf") and config.get("hf_token"):
        best_model = f"{config['project']}/{config['name']}/weights/best.pt"
        if os.path.exists(best_model):
            upload_to_huggingface(best_model, config["hf_repo"], config["hf_token"])
    
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()