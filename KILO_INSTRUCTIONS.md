# AGENT KILO — TRÉNING YOLOv8x NA DENTEX
## Samostatná práca — Čítaj a spusti

---

### 🎯 CIEĽ
Natrénovať YOLOv8x na DENTEX datasete (4 triedy: Impacted, Caries, Periapical Lesion, Deep Caries).
**Kritériá úspechu:** mAP50 ≥ 0.50, Recall Caries ≥ 0.65

---

### 📂 KDE PRACUJEŠ
```
C:\Users\PC1\Desktop\dental-ai
Dataset: datasets/dentex/data.yaml (UŽ HOTOVÝ)
```

---

### ⏰ KEDY ZAČAŤ
Počkaj na signál v `status.yaml`:
```yaml
ready_for_training: true
```
Alebo v `messages.md`: `✅ DENTEX conversion complete`

---

### 🐍 ENVIRONMENT
```bash
cd C:\Users\PC1\Desktop\dental-ai
python -c "import ultralytics; print(ultralytics.__version__)"
```

---

### 🏋️ TRÉNING — SKOPÍRUJ A SPUSTI
```bash
yolo detect train \
  data=datasets/dentex/data.yaml \
  model=yolov8x.pt \
  epochs=100 \
  imgsz=1280 \
  batch=8 \
  device=0 \
  project=runs/detect \
  name=dentex_v1 \
  patience=20 \
  lr0=0.01 \
  cos_lr=True \
  close_mosaic=10 \
  workers=4 \
  amp=True
```
> Ak VRAM nevyhovuje: `batch=4` a `imgsz=1024`

---

### 📊 LOGUJ DO status.yaml (KAŽDÉ 10 EPOCH)
```yaml
agent: Kilo
task: "YOLOv8x training on DENTEX"
status: in_progress
epoch: 30
metrics:
  mAP50: 0.42
  mAP50-95: 0.25
  recall_caries: 0.58
  precision: 0.71
best_epoch: 28
next_check: "2026-07-31 20:00"
```

---

### ✅ KRITÉRIÁ UKONČENIA
| Metrika | Akcia |
|---------|-------|
| mAP50 ≥ 0.50 | Ulož model, konč |
| Recall Caries ≥ 0.65 | Ulož model, konč |
| Epoch ≥ 100 | Early stopping |
| Stagnácia 20 epoch | Early stopping |

---

### 💾 KDE ULOŽIŤ VÝSLEDKY
- Best model: `runs/detect/dentex_v1/weights/best.pt`
- Skopíruj do produkcie:
```bash
cp runs/detect/dentex_v1/weights/best.pt backend/weights/yolov8x_dental.pt
```

---

### 🔍 VALIDÁCIA PO TRÉNINGU
```bash
yolo detect val \
  model=runs/detect/dentex_v1/weights/best.pt \
  data=datasets/dentex/data.yaml \
  split=val \
  imgsz=1280 \
  batch=8
```

---

### 📝 TVOJE DELIVERABLES
1. **status.yaml** — aktualizuj každých 10 epoch
2. **messages.md** — loguj: `epoch 50`, `best mAP50`, `training done`
3. **backend/weights/yolov8x_dental.pt** — finalný model
4. **Report v messages.md:**
```
[KILO] Training complete.
Best epoch: 67
mAP50: 0.53
Recall Caries: 0.71
Model copied to backend/weights/yolov8x_dental.pt
```

---

### ❌ ČO NEROBIŤ
- Nepýtaj sa na hyperparametre
- Necommituj `runs/` ani `*.pt` > 100MB
- Nepoužívaj `python3.11` — len `python`
- Nezastavuj manuálne kým nezasiahneš cieľ

---

### 🆘 AK ZASEKNEŠ
Do `messages.md`:
```
[KILO] BLOCKED: <presný error>
Need: <čo potrebuješ>
```
V `status.yaml`: `status: blocked`

---

### 🚀 ŠTART
1. Over `ready_for_training: true` v status.yaml
2. Spusti tréning
3. Loguj

**Mimo robí iné veci. Ty rob tréning. Komunikujeme cez súbory.**

---

**MAŠ VŠETKO. IDEŠ.**