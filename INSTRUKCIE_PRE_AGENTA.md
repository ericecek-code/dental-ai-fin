# 🤖 Inštrukcie pre ďalšieho agenta — Tréning Dental AI na Kaggle

**Dátum:** 4. október 2026  
**Projekt:** dental-ai-fin (https://github.com/ericecek-code/dental-ai-fin)  
**Cieľ:** Natrénovať YOLOv8 model na detekciu zubných kázov s mAP50 ≥ 0.50 (ideálne ≥ 0.70)

---

## 1. Kontext projektu

### Čo je Dental AI
- **FastAPI backend** + **React/Vite frontend** na detekciu zubných patológií na RTG snímkach
- **Model:** YOLOv8x (368 MB, 19 tried) alebo YOLOv8m (52 MB, rýchlejší)
- **Triedy:** Caries, Deep Caries, Crown, Filling, Implant, Periapical lesion, Retained root, Root Canal Treatment, Impacted tooth, Malaligned, Mandibular Canal, Missing teeth, Root Piece, Plating, Wire, Cyst, Root resorption, Primary teeth
- **Pipeline:** RTG → CLAHE → Bilateral filter → Morphological caries enhance → YOLO → Detekcie → Merania (mm) → PDF report

### Kde sú súbory
```
C:\Users\PC1\Desktop\dental-ai\
├── backend/                    # FastAPI app
│   ├── weights/
│   │   ├── yolov8x_dental.pt  # Súčasný model (368 MB)
│   │   └── candidate_dental_best.pt
│   ├── app/
│   │   ├── ml/
│   │   │   ├── detector.py     # YOLO detektor (19 tried)
│   │   │   ├── preprocessor.py # CLAHE, bilaterálny filter, morfologické zlepšenie
│   │   │   ├── measurements.py # Merania v mm (CEJ → kosťový hrebeň)
│   │   │   ├── reporter.py     # PDF reporty v slovenčine
│   │   │   ├── database.py     # SQLite databáza
│   │   │   ├── gradcam.py      # Grad-CAM vysvetliteľnosť
│   │   │   └── heatmap.py      # Heatmapa detekcií
│   │   ├── api/routes/
│   │   │   ├── analyze.py      # Hlavný endpoint /analyze
│   │   │   ├── health.py       # Health check
│   │   │   ├── results.py      # Výsledky
│   │   │   ├── vision.py       # Vizuálne porovnanie
│   │   │   ├── history.py      # História
│   │   │   └── websocket.py    # Real-time progress
│   │   └── core/config.py      # Nastavenia (CORS, upload limit, confidence)
│   ├── tests/                  # 138 testov (pytest)
│   └── requirements.txt
├── frontend/                   # React/Vite app
├── mega-dataset/               # Tréningový dataset (5 tried)
│   ├── data.yaml               # Konfigurácia datasetu
│   ├── train/images/           # 7 228 obrázkov
│   ├── valid/images/           # 1 840 obrázkov
│   └── test/images/            # 1 103 obrázkov
├── mega-dataset.zip            # 741 MB (nahraný na Kaggle)
├── runs/detect/                # Tréningové runs
├── kaggle_train_dentex.ipynb   # Kaggle notebook
├── train_cloud.py              # Univerzálny tréningový skript
├── config.yaml                 # Konfigurácia tréningu
└── KAGGLE_INSTRUCTIONS_FOR_AGENT.md  # Tento súbor
```

---

## 2. Kde sme sa nachádzali (stav k 4.10.2026)

### Čo sa podarilo
| Úloha | Stav | Poznámka |
|---|---|---|
| Backend (FastAPI) | ✅ Hotový | 138 testov, všetky endpointy fungujú |
| Frontend (React/Vite) | ✅ Hotový | Dark theme, upload, overlay, PDF |
| Dataset (mega-dataset) | ✅ Hotový | 10 171 obrázkov, 5 tried |
| Tréning YOLOv8x (CPU) | ⚠️ Čiastočný | 3 epochy, mAP50 = 0.370 |
| Tréning YOLOv8x (1080 Ti) | ⚠️ Prerušený | Epocha 4/10, freeze_support chyba |
| Tréning YOLOv8m (Kaggle) | ❌ Zlyhal | data.yaml nebol nájdený |
| Validácia | ✅ Hotová | mAP50 = 0.427 (Caries = 0.102) |

### Čo sa NEPODARILO
| Problém | Príčina | Riešenie |
|---|---|---|
| Kaggle tréning zlyhal | `data.yaml` nebol v `/kaggle/input/mega-dataset-dental/` | Skopírovať dataset do `/kaggle/working/` a opraviť cestu |
| Caries mAP50 = 0.102 | Nedostatok tréningových dát, trieda nevyvážená | Class-balancing, augmentácia, CLAHE |
| Periapical-lesion mAP50 = 0.000 | Len 22 inštancií v tréningovom sete | Rozšíriť dataset |
| Tréning na CPU prerušený | `freeze_support()` chyba | Použiť `if __name__ == '__main__':` |
| Kaggle CUDA chyba | Tesla P100 (CUDA 6.0) nie je kompatibilný s PyTorch | Použiť Google Colab (T4 GPU) |

---

## 3. Kľúče a kredenciale

### Kaggle
```
Username: eriksmite
API key: 3c4c916999ab702c0205a6cd2942dd27
Kaggle dataset: eriksmite/mega-dataset-dental
Kaggle kernel: eriksmite/dental-variantb-mega-training
```

### HuggingFace (voliteľné)
```
Token: hf_aWf-zDplSgGkMhVvHwOqVjYpCqBqZcEMvj
Repo: Ericecek/dental-ai-models
```

### GitHub
```
User: ericecek-code
Repo: dental-ai-fin (public)
```

---

## 4. Tréningové konfigurácie

### Odporúčaná konfigurácia pre Kaggle (YOLOv8m)
```python
CONFIG = {
    "model": "yolov8m.pt",
    "data": "/kaggle/working/dataset/data.yaml",
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
```

### Pre Google Colab (YOLOv8x, väčší model)
```python
CONFIG = {
    "model": "yolov8x.pt",
    "data": "/content/mega-dataset/data.yaml",
    "epochs": 100,
    "imgsz": 1280,
    "batch": 8,  # T4 má 16 GB VRAM
    "device": 0,
    "patience": 20,
    "lr0": 0.01,
    "cos_lr": True,
    "close_mosaic": 10,
    "workers": 4,
    "amp": True,
    "mosaic": 1.0,
    "mixup": 0.1,
    "copy_paste": 0.1,
}
```

### Pre lokálny tréning (GTX 1080 Ti)
```bash
python train_cloud.py --model yolov8m --epochs 60 --batch 8 --imgsz 640
```

---

## 5. Kaggle — krok za krokom

### Krok 1: Otvor Kaggle
1. Choď na https://www.kaggle.com/code
2. Prihlás sa (ak treba)

### Krok 2: Importuj notebook
- **File → Import Notebook**
- Vyber `kaggle_train_dentex.ipynb` z `C:\Users\PC1\Desktop\dental-ai\`
- ALEBO nahraj priamo z GitHub:
  ```
  https://github.com/ericecek-code/dental-ai-fin/raw/main/kaggle_train_dentex.ipynb
  ```

### Krok 3: Nastav GPU + Internet
- **Settings** (v menu bare) →
- **Accelerator** → **GPU P100** (alebo GPU T4)
- **Internet** → **ON**

### Krok 4: Nastav credentials
V **Cell 3** (Kaggle Authentication) zmeň:
```python
os.environ["KAGGLE_USERNAME"] = "eriksmite"
os.environ["KAGGLE_KEY"] = "3c4c916999ab702c0205a6cd2942dd27"
```

### Krok 5: Spusti
- Klikni **⏩ Run All** (vpravo hore)
- Alebo **Run → Run All Cells**

### Krok 6: Sleduj výstup
- Tréning beží ~2–4 hodiny (60 epôch)
- V **Output** tabe nájdeš `best.pt` na download
- Stiahni `best.pt` a `metrics.json`

### Krok 7: Deploy modelu
```bash
cp backend/weights/yolov8x_dental.pt backend/weights/yolov8x_dental.pt.backup
cp /kaggle/working/output/best.pt backend/weights/yolov8x_dental.pt
```

---

## 6. Google Colab — krok za krokom (AKO ALTERNATÍVA)

### Krok 1: Otvor Colab
1. Choď na https://colab.research.google.com
2. **File → Upload notebook** → Vyber `kaggle_train_dentex.ipynb`

### Krok 2: Povoľ GPU
- **Runtime → Change runtime type → GPU T4**

### Krok 3: Nahraj dataset
```python
# V prvom cellu nahraj mega-dataset.zip
from google.colab import files
uploaded = files.upload()
!unzip -q mega-dataset.zip -d /content/
```

### Krok 4: Spusti všetky celly
- **Runtime → Run all**

### Krok 5: Stiahni model
```python
from google.colab import files
files.download('/content/runs/detect/dental_5class_v1/weights/best.pt')
```

---

## 7. Riešenie známych chýb

### Chyba 1: Read-only file system
```
OSError: [Errno 30] Read-only file system: '/kaggle/input/.../data.yaml'
```
**Riešenie:** Skopíruj dataset do `/kaggle/working/` pred úpravami:
```python
import shutil
shutil.copytree("/kaggle/input/mega-dataset-dental/mega-dataset", "/kaggle/working/dataset")
DATASET_PATH = "/kaggle/working/dataset"
```

### Chyba 2: Dataset path issues
```
FileNotFoundError: '/kaggle/input/mega-dataset-dental/data.yaml' does not exist
```
**Riešenie:** Dataset je vnorený — skutočná cesta je:
```python
DATASET_PATH = "/kaggle/input/mega-dataset-dental/mega-dataset"
```

### Chyba 3: CUDA compatibility (Tesla P100)
```
CUDA error: no kernel image is available for execution on the device
```
**Riešenie:** Tesla P100 (CUDA 6.0) nie je kompatibilný s PyTorch. Použi Google Colab (T4 GPU).

### Chyba 4: nbformat is null
```
Error converting value {null} to type 'System.Int32'. Path 'nbformat'
```
**Riešenie:** Vytvor notebook pomocou nbformat:
```python
import nbformat as nbf
nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, "notebook.ipynb")
```

### Chyba 5: freeze_support
```
An attempt has been made to start a new process before the current process has finished its bootstrapping phase.
```
**Riešenie:** Pridaj `if __name__ == '__main__':` pred spustenie tréningu:
```python
if __name__ == '__main__':
    model = YOLO(CONFIG["model"])
    results = model.train(**CONFIG)
```

### Chyba 6: Out of Memory
```
CUDA out of memory
```
**Riešenie:** Zniž `batch` z 16 na 8, alebo `imgsz` z 1280 na 640.

---

## 8. Očakávané výsledky

| Metrika | Cieľ | Realistický |
|---|---|---|
| mAP50 | ≥ 0.50 | 0.55–0.70 |
| mAP50-95 | ≥ 0.35 | 0.40–0.55 |
| Precision | ≥ 0.70 | 0.70–0.80 |
| Recall (Caries) | ≥ 0.65 | 0.60–0.75 |
| Tréningový čas | — | 2–4 hodiny (60 epôch) |
| Veľkosť modelu | — | ~52 MB (YOLOv8m) / ~368 MB (YOLOv8x) |

### Per-class ciele
| Trieda | mAP50 cieľ |
|---|---|
| Caries | ≥ 0.50 |
| Crown | ≥ 0.70 |
| Filling | ≥ 0.70 |
| Implant | ≥ 0.80 |
| Periapical-lesion | ≥ 0.30 |

---

## 9. Po tréningu — čo robiť

### 1. Stiahni model
- Z Kaggle Output tabu stiahni `best.pt` a `metrics.json`
- Alebo z Colab: `files.download('best.pt')`

### 2. Nahraj na GitHub
```bash
cd C:\Users\PC1\Desktop\dental-ai
git add backend/weights/yolov8x_dental.pt
git commit -m "Update model: mAP50=XX, trained on Kaggle"
git push origin main
```

### 3. Spusti validáciu lokálne
```bash
cd C:\Users\PC1\Desktop\dental-ai
python -c "
from ultralytics import YOLO
model = YOLO('backend/weights/yolov8x_dental.pt')
metrics = model.val(data='mega-dataset/data.yaml', split='test')
print(f'mAP50: {metrics.box.map50:.4f}')
print(f'mAP50-95: {metrics.box.map:.4f}')
print(f'Precision: {metrics.box.mp:.4f}')
print(f'Recall: {metrics.box.mr:.4f}')
"
```

### 4. Spusti testy
```bash
cd C:\Users\PC1\Desktop\dental-ai\backend
python -m pytest tests/ -v
```

### 5. Aktualizuj STATUS_PROJEKTU.md
- Zapíš nové mAP hodnoty
- Zapíš čo sa podarilo / nepodarilo
- Zapíš ďalšie kroky

---

## 10. Dôležité poznámky

### Dataset
- **mega-dataset** má 5 tried: Caries, Crown, Filling, Implant, Periapical-lesion
- **Caries** je najväčší problém — nízky recall (0.134)
- **Periapical-lesion** má len 22 inštancií — trieda prakticky nefunguje
- Pre lepšie výsledky je potrebné:
  - Vyvážiť triedy (class-balancing)
  - Pridať augmentáciu (CLAHE, rotácie, zmena kontrastu)
  - Rozšíriť dataset o viac obrázkov s kazmi

### Model
- **YOLOv8m** je rýchlejší a menší (52 MB) — vhodný pre Kaggle
- **YOLOv8x** je presnejší ale väčší (368 MB) — vhodný pre Colab
- Súčasný model `yolov8x_dental.pt` má mAP50 = 0.427 (Caries = 0.102)

### Kaggle limity
- **30 hodín GPU** týždenne
- **19 GB disk** (mega-dataset.zip = 741 MB)
- **Tesla P100** nie je kompatibilný s PyTorch (CUDA 6.0)
- **Google Colab** je lepšia alternatíva (T4 GPU, 16 GB VRAM)

### Zdroje
- **Kaggle dataset:** https://www.kaggle.com/datasets/eriksmite/mega-dataset-dental
- **Kaggle notebook:** https://www.kaggle.com/code/eriksmite/dental-variantb-mega-training
- **GitHub:** https://github.com/ericecek-code/dental-ai-fin
- **Ultralytics docs:** https://docs.ultralytics.com

---

## 11. Zhrnutie pre rýchly štart

```
1. Otvor Kaggle → Import notebook → Nastav GPU P100 → Run All
2. Počkaj 2–4 hodiny
3. Stiahni best.pt z Output tabu
4. Nahraj na GitHub: git add backend/weights/yolov8x_dental.pt
5. Spusti validáciu: python -c "from ultralytics import YOLO; ..."
6. Aktualizuj STATUS_PROJEKTU.md
```

**Ak Kaggle nefunguje (CUDA chyba):**
```
1. Otvor Colab → Upload notebook → Nahraj mega-dataset.zip
2. Runtime → Change runtime type → GPU T4
3. Run All
4. Stiahni best.pt
```

---

*Inštrukcie vygenerované pre ďalšieho agenta — 4. október 2026*
