# 📊 Stav projektu Dental AI — Identifikácia zubných kázov

**Dátum poslednej kontroly:** 19. november 2026  
**Posledná session s vývojom:** 19. november 2026 (@session:default/20261119_060112)

---

## 1. Prehľad projektu

| Položka | Hodnota |
|---|---|
| **Názov** | Dental AI (dental-ai-fin) |
| **Účel** | Detekcia zubných kázov a patológií na RTG snímkach |
| **Architektúra** | FastAPI backend + React/Vite frontend |
| **Model** | YOLOv8x (YOLOv8m pre tréning na Kaggle) |
| **Počet tried** | 5 (Caries, Crown, Filling, Implant, Periapical lesion) |
| **Backend** | Python 3.11, FastAPI, Uvicorn, SQLite |
| **Frontend** | React + Vite + Tailwind CSS |
| **Docker** | Áno (Dockerfile + docker-compose.yml) |
| **CI** | GitHub Actions (.github/workflows/ci.yml) |
| **Testy** | 138 testov (pytest) — 4 testy opravené 2026-11-19 |
| **GitHub** | ericecek-code/dental-ai-fin (public) |

---

## 2. Stav na disku

### 2.1 Hlavné priečinky

| Priečinok | Obsah | Veľkosť |
|---|---|---|
| `backend/` | FastAPI app, ML moduly, testy | ~1.3 GB (vrátane váh) |
| `backend/weights/` | `yolov8x_dental.pt` (368 MB), `candidate_dental_best.pt` (6 MB) | 374 MB |
| `frontend/` | React/Vite app, node_modules | ~110 MB |
| `mega-dataset/` | Tréningový dataset (5 tried) | 742 MB |
| `runs/detect/` | Tréningové runs | ~800 MB |
| `combined-dataset/` | Starší dataset (5 tried) | ~307 MB |
| `dental_yolo_v8-420/` | Starší dataset (38 tried) | ~270 MB |
| `Dental-X-ray-1/` | Starší dataset (4 tried) | — |
| `restorative-ai-bbox/` | Starší dataset (5 tried) | ~234 MB |
| `verified_models/` | Overené modely z testov | ~56 MB |
| `datasets/` | Kaggle datasety | — |
| `kaggle_kernel/`, `kernel_out/`, `out_variantb/` | Kaggle tréningové artefakty | — |
| `coco-dental-31class.zip` | COCO dataset (31 tried) | 750 MB |
| `mega-dataset.zip` | Komprimovaný mega-dataset | 741 MB |

### 2.2 Celkové využitie disku (odhad)

| Kategória | Veľkosť |
|---|---|
| Modely (.pt) | ~1.5 GB |
| Datasety (zip + extracted) | ~3.5 GB |
| Tréningové runs | ~800 MB |
| Backend + frontend | ~500 MB |
| **Celkom** | **~6.3 GB** |

---

## 3. Presnosť detekcie

### 3.1 Najnovšie validačné výsledky (YOLOv8x, 5 tried, mega-dataset)

**Zdroj:** `val_log2.txt` — validácia na `combined-dataset/val` (148 obrázkov, 771 inštancií)

| Trieda | Presnosť (P) | Recall (R) | mAP50 | mAP50-95 |
|---|---|---|---|---|
| **Caries** | 0.556 | 0.134 | **0.102** | 0.032 |
| **Crown** | 0.778 | 0.643 | **0.602** | 0.444 |
| **Filling** | 0.726 | 0.697 | **0.618** | 0.334 |
| **Implant** | 0.833 | 0.814 | **0.813** | 0.690 |
| **Periapical-lesion** | 0.000 | 0.000 | **0.000** | 0.000 |
| **Priemer (all)** | **0.578** | **0.458** | **0.427** | **0.300** |

### 3.2 Tréningové epochy (YOLOv8x, mega-dataset, 10 epôch)

**Zdroj:** `runs/detect/dental_5class_1080ti-2/results.csv`

| Epoch | mAP50 | mAP50-95 | Poznámka |
|---|---|---|---|
| 1 | 0.305 | 0.163 | Po prvej epoche |
| 2 | 0.329 | 0.172 | |
| 3 | 0.370 | 0.194 | Najlepšia epocha |
| 4 | 0.370 | 0.194 | Tréning prerušený (freeze_support chyba) |

**Poznámka:** Tréning bol spustený na CPU (AMD Ryzen 5 1600) a následne na GPU (1080 Ti), ale bol prerušený na epoche 4/10. Model `best.pt` (207 MB) bol uložený po epoche 3.

### 3.3 Kaggle tréning (YOLOv8m, mega-dataset)

**Stav:** Zlyhal — `data.yaml` nebol nájdený v `/kaggle/input/mega-dataset-dental/`

**Chyba:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/kaggle/input/mega-dataset-dental/data.yaml'
```

**Príčina:** Dataset bol nahraný na Kaggle, ale `data.yaml` nebol v koreňovom priečinku datasetu.

### 3.4 Staršie validačné výsledky (YOLOv8m, combined-dataset)

**Zdroj:** `val_log.txt` — validácia na `mega-dataset/test` (1103 obrázkov)

| Trieda | mAP50 | mAP50-95 |
|---|---|---|
| **all** | 0.370 | 0.194 |

---

## 4. Problémy a riziká

### 4.1 Kritické problémy

| # | Problém | Dopad | Riešenie |
|---|---|---|---|
| 1 | **Caries mAP50 = 0.102** | Veľmi nízka presnosť na kazoch | Vyváženie tried, viac augmentácie, CLAHE preprocessing |
| 2 | **Periapical-lesion mAP50 = 0.000** | Trieda úplne nefunguje | Nedostatok tréningových dát (22 inštancií) |
| 3 | **Kaggle tréning zlyhal** | Žiadne nové váhy z Kaggle | Opraviť `data.yaml` cestu, spustiť znova |
| 4 | **Tréning na CPU preružený** | Nepretrénovaný model | Spustiť na GPU (Kaggle/Colab) |

### 4.2 Riziká

| Riziko | Pravdepodobnosť | Dopad |
|---|---|---|
| mAP 0.85 na Caries nie je dosiahnuteľné za 3 dni | Vysoká | Cieľ je ambiciózny, open-source projekty sa zastavujú na 0.5–0.7 |
| Nedostatok tréningových dát pre Periapical-lesion | Vysoká | Trieda nebude fungovať bez dodatočných dát |
| Overfitting na malom datasete | Stredná | Potrebná augmentácia a regularizácia |

---

## 5. Architektúra backendu

### 5.1 API endpointy

| Endpoint | Metóda | Popis |
|---|---|---|
| `/health` | GET | Health check |
| `/analyze` | POST | Analýza RTG snímky (upload → detekcia → overlay) |
| `/results` | GET | Zoznam výsledkov |
| `/results/{id}` | GET | Detail výsledku |
| `/vision` | GET | Vizuálne porovnanie |
| `/history` | GET | História analýz |
| `/ws` | WebSocket | Real-time progress |

### 5.2 ML pipeline

```
RTG snímka → CLAHE → Bilateral filter → Morphological caries enhance → YOLOv8x → Detekcie → Merania (mm) → PDF report
```

### 5.3 Kľúčové moduly

| Modul | Funkcia |
|---|---|
| `backend/app/ml/detector.py` | YOLO detektor s 5 triedami |
| `backend/app/ml/preprocessor.py` | CLAHE, bilaterálny filter, morfologické zlepšenie kázov |
| `backend/app/ml/measurements.py` | Merania v mm (CEJ → kosťový hrebeň) |
| `backend/app/ml/reporter.py` | PDF reporty v slovenčine |
| `backend/app/ml/database.py` | SQLite databáza výsledkov |
| `backend/app/ml/gradcam.py` | Grad-CAM vysvetliteľnosť |
| `backend/app/ml/heatmap.py` | Heatmapa detekcií |

---

## 6. Dataset

### 6.1 mega-dataset (primárny)

| Split | Obrázky | Poznámka |
|---|---|---|
| train | 7 228 | 1 194 backgrounds |
| valid | 1 840 | 133 backgrounds |
| test | 1 103 | 232 backgrounds |
| **Celkom** | **10 171** | |

**Triedy (5):** Caries, Crown, Filling, Implant, Periapical-lesion

### 6.2 Staršie datasety

| Dataset | Obrázky | Triedy |
|---|---|---|
| dental_yolo_v8-420 | 3 802 | 38 |
| Dental-X-ray-1 | 753 | 4 |
| combined-dataset (v3) | 969 | 5 |
| restorative-ai-bbox (v2) | 849 | 5 |

---

## 7. Plán ďalšieho vývoja

### 7.1 Krátkodobé (1–3 dni)

1. **Opraviť Kaggle tréning** — pridať `data.yaml` do datasetu, spustiť YOLOv8m na Kaggle GPU
2. **Vyvážiť triedy** — class-balancing pre Caries (najväčší problém)
3. **Augmentácia** — CLAHE, rotácie, zmena kontrastu
4. **Threshold tuning** — nastaviť confidence threshold na 0.25–0.30

### 7.2 Strednodobé (1–2 týždne)

1. **Rozšíriť dataset** — viac obrázkov s kazmi a periapicalnými léziami
2. **Trénovať YOLOv8x na Kaggle** — 100+ epôch, imgsz=1280
3. **Ensemble modelov** — kombinovať YOLOv8x + YOLOv8m
4. **Validácia na test sete** — získať reálne mAP

### 7.3 Dlhodobé (mesiace)

1. **Export do ONNX** — pre rýchlejšiu inferenciu
2. **Deploy na HF Spaces** — demo aplikácia
3. **Klinická validácia** — spolupráca so zubnými lekármi
4. **FDA/CE certifikácia** — pre komerčné použitie

---

## 8. Zdroje a odkazy

| Zdroj | Odkaz |
|---|---|
| GitHub repo | https://github.com/ericecek-code/dental-ai-fin |
| Kaggle dataset | https://www.kaggle.com/datasets/eriksmite/mega-dataset-dental |
| Kaggle kernel | https://www.kaggle.com/code/eriksmite/dental-variantb-mega-training |
| Posledná session | @session:default/20261119_060112 |

---

## 9. Záver

**Aktuálny stav:** Projekt je funkčný, ale presnosť detekcie kázov (Caries mAP50 = 0.102) je príliš nízka na komerčné použitie. Tréning bol prerušený a Kaggle tréning zlyhal.

**Priorita:** Opraviť tréning, vyvážiť triedy a získať mAP50 ≥ 0.5 na Caries.

**Realistický cieľ:** mAP50 ≥ 0.7 na Caries, mAP50 ≥ 0.85 celkový — dosiahnuteľné za 2–4 týždne s správnym tréningom.

---

*Report vygenerovaný automaticky — 19. november 2026*
