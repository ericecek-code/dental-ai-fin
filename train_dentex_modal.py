# Modal training script for DENTEX dataset - FIXED VERSION
# Run: modal run train_dentex_modal.py

import modal

app = modal.App("dental-ai-dentex-training")

# Use modal's base image with CUDA support, add system deps for OpenCV
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(["libgl1-mesa-glx", "libglib2.0-0", "libsm6", "libxext6", "libxrender-dev", "libgomp1"])
    .pip_install([
        "ultralytics==8.4.114",
        "opencv-python-headless",
        "pyyaml",
        "tqdm",
    ])
)

dataset_volume = modal.Volume.from_name("dentex-dataset")
output_volume = modal.Volume.from_name("dentex-output", create_if_missing=True)

@app.function(
    image=image,
    gpu="A10G",
    volumes={
        "/dentex": dataset_volume,
        "/output": output_volume,
    },
    timeout=7200,
)
def train_dentex():
    import os
    from ultralytics import YOLO
    
    # CRITICAL: Change to the dataset directory so ultralytics finds images/val relative to CWD
    os.chdir("/dentex")
    
    # DEBUG: Check what's actually mounted
    print("=== DEBUG: Checking mount points ===")
    for root, dirs, files in os.walk("/dentex"):
        level = root.replace("/dentex", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:
            print(f"{' ' * 2 * (level + 1)}{file}")
        if len(files) > 5:
            print(f"{' ' * 2 * (level + 1)}... and {len(files) - 5} more files")
    
    print("=== DEBUG: Current working directory ===")
    print(f"CWD: {os.getcwd()}")
    print(f"Contents: {os.listdir('.')}")
    
    print("=== DEBUG: Checking images directory ===")
    if os.path.exists("images"):
        print(f"images exists")
        print(f"Contents: {os.listdir('images')}")
    else:
        print("images DOES NOT EXIST")
    
    print("=== DEBUG: Checking labels directory ===")
    if os.path.exists("labels"):
        print(f"labels exists")
        print(f"Contents: {os.listdir('labels')}")
    else:
        print("labels DOES NOT EXIST")
    
    print("=== DEBUG: Checking data.yaml ===")
    if os.path.exists("data.yaml"):
        print("data.yaml exists")
        with open("data.yaml") as f:
            print(f.read())
    else:
        print("data.yaml DOES NOT EXIST")
    
    # Verify dataset exists
    for split in ["train", "val"]:
        img_dir = f"images/{split}"
        lbl_dir = f"labels/{split}"
        img_count = len([f for f in os.listdir(img_dir) if f.endswith(('.png', '.jpg'))])
        lbl_count = len([f for f in os.listdir(lbl_dir) if f.endswith('.txt')])
        print(f"{split}: {img_count} images, {lbl_count} labels")
    
    # Load model
    model = YOLO("yolov8x.pt")
    
    # Train
    print("Starting training...")
    results = model.train(
        data="data.yaml",
        epochs=100,
        imgsz=1280,
        batch=16,
        device=0,
        project="/output/runs/detect",
        name="dentex_v1",
        patience=20,
        lr0=0.01,
        cos_lr=True,
        close_mosaic=10,
        workers=4,
        amp=True,
        save=True,
        save_period=10,
    )
    
    # Validate
    print("Running validation...")
    metrics = model.val(data="data.yaml", split="val", imgsz=1280, batch=16)
    
    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Per-class AP50: {metrics.box.ap50}")
    print(f"Per-class Recall: {metrics.box.recall}")
    
    # Copy best model to output
    best_model = "/output/runs/detect/dentex_v1/weights/best.pt"
    if os.path.exists(best_model):
        print(f"Best model saved to: {best_model}")
    
    return {
        "map50": float(metrics.box.map50),
        "map50_95": float(metrics.box.map),
        "per_class_ap50": metrics.box.ap50.tolist(),
        "per_class_recall": metrics.box.recall.tolist(),
    }

@app.local_entrypoint()
def main():
    print("Starting DENTEX training on Modal...")
    result = train_dentex.remote()
    print(f"Training complete: {result}")