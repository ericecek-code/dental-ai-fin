# 🎯 Pokyny pre Goose - Kaggle Training

## Cieľ
Spustiť tréning YOLOv8x na Kaggle GPU pre Dental AI projekt.

## Súbory
- **Notebook**: `kaggle_train_dentex.ipynb` (v koreni repozitára)
- **GitHub**: https://github.com/ericecek-code/dental-ai-fin

## Kredenciale

### Kaggle
```python
os.environ["KAGGLE_USERNAME"] = "eriksmite"
os.environ["KAGGLE_KEY"] = "3c4c916999ab702c0205a6cd2942dd27"
```

### HuggingFace (voliteľné, pre upload modelu)
```python
os.environ["HF_TOKEN"] = "hf_aWf-zDplSgGkMhVvHwOqVjYpCqBqZcEMvj"
```

## Postup (5 krokov)

### 1. Otvor Kaggle
- URL: https://www.kaggle.com/code
- Prihlás sa (ak treba)

### 2. Importuj notebook
- **File → Import Notebook**
- Vyber `kaggle_train_dentex.ipynb` z repozitára
- ALEBO nahraj priamo z GitHub:
  ```
  https://github.com/ericecek-code/dental-ai-fin/raw/main/kaggle_train_dentex.ipynb
  ```

### 3. Nastav GPU + Internet
- **Settings** (v menu bare) →
- **Accelerator** → **GPU P100** (alebo GPU T4)
- **Internet** → **ON**

### 4. Nastav credentials
V **Cell 3** (Kaggle Authentication) zmeň:
```python
os.environ["KAGGLE_USERNAME"] = "eriksmite"
os.environ["KAGGLE_KEY"] = "3c4c916999ab702c0205a6cd2942dd27"
```

### 5. Spusti
- Klikni **⏩ Run All** (vpravo hore)
- Alebo **Run → Run All Cells**

## Čo sa stane
1. Stiahne sa dataset (~3 GB) - len training data
2. Konvertuje sa do YOLO formátu
3. Tréning beží ~2-4 hodiny (100 epochs)
4. V **Output** tabe nájdeš `best.pt` na download

## Výstup
- **best.pt** - YOLOv8x weights (pre deployment)
- **best.onnx** - ONNX export (cross-platform)
- **metrics.json** - mAP, recall, precision per class

## Ciele
| Metrika | Cieľ |
|---------|------|
| mAP50 | ≥ 0.50 |
| Recall (Caries) | ≥ 0.65 |

## Riešenie problémov

### "Notebook tried to use more disk space than is available"
- Notebook už je optimalizovaný (maže zip, original data)
- Ak stále problém, zníž `batch` z 16 na 8 v Cell 6

### "CUDA out of memory"
- Zmeň `batch` z 16 na 8 v Cell 6
- Alebo `imgsz` z 1280 na 640

### Kaggle CLI 401 Unauthorized
- Kaggle API key nemá write prístup pre kernels
- Použi browser upload (nie CLI)

## Kontakt
- GitHub: ericecek-code
- HuggingFace: Ericecek
- Kaggle: eriksmite
