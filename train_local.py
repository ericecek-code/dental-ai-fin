"""
YOLOv8 Lokálny tréning - Dental AI
"""
from ultralytics import YOLO
import torch

print("=" * 60)
print("DENTAL AI - YOLOV8X TRAINING")
print("=" * 60)

# Kontrola GPU
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"GPU: {gpu_name} ({gpu_mem:.1f} GB)")
else:
    print("GPU nenájdený! Tréning bude pomalý.")

# Konfigurácia
CONFIG = {
    "model": "yolov8x.pt",
    "data": "C:/Users/PC1/Desktop/dental-ai/mega-dataset/data.yaml",
    "epochs": 100,
    "patience": 20,
    "batch": 4,
    "imgsz": 640,
    "device": 0,
    "project": "C:/Users/PC1/Desktop/dental-ai/runs",
    "name": "dental_yolov8x_local",
}

print(f"\nModel: {CONFIG['model']}")
print(f"Epochs: {CONFIG['epochs']}")
print(f"Batch: {CONFIG['batch']}")
print(f"Image size: {CONFIG['imgsz']}")
print("=" * 60)

# Načítanie modelu
model = YOLO(CONFIG["model"])

# Tréning
print("\n🚀 Spúšťam tréning...")
results = model.train(
    data=CONFIG["data"],
    epochs=CONFIG["epochs"],
    batch=CONFIG["batch"],
    imgsz=CONFIG["imgsz"],
    device=CONFIG["device"],
    patience=CONFIG["patience"],
    project=CONFIG["project"],
    name=CONFIG["name"],
    exist_ok=True,
    pretrained=True,
    verbose=True,
)

print("\n✅ Tréning dokončený!")

# Výsledky
print("\n📊 VÝSLEDKY:")
print(f"  mAP50: {results.box.map50:.4f} ({results.box.map50*100:.1f}%)")
print(f"  mAP50-95: {results.box.map:.4f} ({results.box.map*100:.1f}%)")
print(f"  Precision: {results.box.mp:.4f}")
print(f"  Recall: {results.box.mr:.4f}")
