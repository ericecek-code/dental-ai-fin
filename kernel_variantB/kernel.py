# Dental AI - Variant B: YOLOv8m na mega-datasete
# Kaggle P100/T4, diskovo bezpecne (<6 GB z 20 GB limitu)
import os, shutil, json, glob

W = "/kaggle/working"
DATA = "/kaggle/input/mega-dataset-dental"

# ---- 0. Disk check ----
def disk(path):
    t, u, f = shutil.disk_usage(path)
    return f"free {f//2**30}GB / {t//2**30}GB"
print("WORKING:", disk(W))

# ---- 1. Najdi data.yaml v datasete ----
yamls = glob.glob(f"{DATA}/**/data.yaml", recursive=True)
print("Najdene yaml:", yamls)
assert yamls, "data.yaml not found!"
src_yaml = yamls[0]
root = os.path.dirname(src_yaml)
print("Dataset root:", root, "|", disk(root))

# Oprava path na Kaggle cestu
import yaml
cfg = yaml.safe_load(open(src_yaml))
cfg["path"] = root
os.makedirs(f"{W}/data", exist_ok=True)
yaml.safe_dump(cfg, open(f"{W}/data/data.yaml", "w"), sort_keys=False)
print("data.yaml:", cfg)

# ---- 2. Trening ----
from ultralytics import YOLO
model = YOLO("yolov8m.pt")
results = model.train(
    data=f"{W}/data/data.yaml",
    epochs=70,
    imgsz=640,
    batch=32,
    cache=False,          # CRITICAL: bez diskovej cache
    patience=15,
    project=f"{W}/train",
    name="variantb",
    exist_ok=True,
)
print("TRENING DOKONCENY |", disk(W))

# ---- 3. Validacia na test split ----
best = YOLO(f"{W}/train/variantb/weights/best.pt")
metrics = best.val(split="test", project=f"{W}/val", name="test")
print("\n===== VYSLEDKY =====")
print(metrics.results_dict)

# ---- 4. Uloz LEN podstatne (disk discipline) ----
out = f"{W}/output"
os.makedirs(out, exist_ok=True)
shutil.copy(f"{W}/train/variantb/weights/best.pt", f"{out}/best.pt")
shutil.copy(f"{W}/train/variantb/weights/last.pt", f"{out}/last.pt")
with open(f"{out}/metrics.json", "w") as f:
    json.dump({k: float(v) for k, v in metrics.results_dict.items()}, f, indent=2)

# Zmaz treninkovy adresar s plots/batchmi - nechame len weights (uz skopirovane)
shutil.rmtree(f"{W}/train", ignore_errors=True)
shutil.rmtree(f"{W}/val", ignore_errors=True)
print("FINAL:", os.listdir(out), "|", disk(W))
