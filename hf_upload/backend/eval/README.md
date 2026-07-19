# DenteScope AI — YOLO Eval Pipeline

Nastroje na **(a) zbieranie predictions**, **(b) ich porovnanie s ground truth labelmi**, a nasledny vypocet **precision/recall/F1** po triedach.

## Tok prace

```
1. Tagging dat (ruzne sposoby):
   A) tagging tool (UI): frontend/src/components/TaggingTool.tsx
   B) ručne otaguj obrazky + vytvor .txt subory
   C) stiahni verejny dataset (napr. Roboflow YOLO format)

2. Vygeneruj predictions z backendu:
   PYTHONPATH=backend python -m eval.save_predictions \
       --input ../test_images/ \
       --backend http://127.0.0.1:8000 \
       --output predictions/

3. Porovnaj predictions s ground-truth:
   PYTHONPATH=backend python -m eval.scorer \
       --predictions predictions/ \
       --ground-truth datasets/labeled/ \
       --iou-threshold 0.5

4. Vystup:
   - results/metrics.json   - global + per-image
   - results/per_class.json - per class breakdown
```

## Adresárová štruktúra

```
backend/eval/
├── __init__.py
├── CLASSES_MD.md        # single source of truth: triedy + ID
├── scorer.py            # hlavny eval modul — IoU matching + metriky
├── save_predictions.py  # helper: uloz YOLO outputy do json
├── predictions/         # generovane save_predictions
│   ├── caries_1.json
│   └── ...
├── datasets/labeled/    # Tvoj tagged dataset
│   ├── caries_1.jpg
│   ├── caries_1.txt     # YOLO format
│   └── ...
└── results/             # generovane scorer
    ├── metrics.json
    └── per_class.json
```

## YOLO .txt formát

Kazdy riadok = 1 bbox:

```
<class_id> <x_center_norm> <y_center_norm> <width_norm> <height_norm>
```

Priklad (3 triedy v jednom obrázku 800x600):

```
1 0.412500 0.530000 0.098750 0.121667    # Crown
2 0.654321 0.234567 0.045123 0.067890    # Filling
7 0.812345 0.890123 0.056789 0.034567    # Periapical lesion
```

- Súradnice su **normalizovane** na 0–1 (0.5 = stred)
- class_id pozri `CLASSES_MD.md`

## Interpretácia výsledkov

| Metrika | Význam |
|---|---|
| **TP** (true positive) | Model detekoval niečo, čo naozaj je tam |
| **FP** (false positive) | Model detekoval niečo, čo tam nie je (false alarm) |
| **FN** (false negative) | Model prehliadol niečo, čo tam je (miss) |
| **Precision = TP / (TP+FP)** | Zo všetkých detekcií modelu, koľko % je správnych |
| **Recall = TP / (TP+FN)** | Zo všetkých skutočných nálezov, koľko % model našiel |
| **F1** | Harmonický priemer P+R (vyvážená metrika) |
| **Macro P/R/F1** | Priemer cez všetky triedy (aj keď niektoré majú 0) |
| **Micro P/R/F1** | Vážený priemer (počíta sa cez celkové TP/FP/FN) |

### Co je dobre vs zle (orientačne)

| Stav | Macro F1 | Interpretation |
|---|---|---|
| 🟢 Vyborne | >0.75 | Model je production-ready pre kliniku |
| 🟡 Solidne | 0.5–0.75 | Pouzitelne s manual review |
| 🔴 Slabe | <0.5 | Treba doladit / viac dat / lepsi model |

## Confidence threshold experiment

Príkaz sa dá opakovať s rôznym `--iou-threshold` alebo `--conf` v `save_predictions.py` aby si našiel **optimálny conf prah** pre každú triedu.

## Single source of truth

Ak zmeníš ktorúkoľvek triedu, musíš zmeniť **3 súbory** (vid `CLASSES_MD.md`):
- `backend/app/ml/detector.py` — COLOR_MAP
- `backend/eval/scorer.py` — CLASS_NAMES (tu)
- `frontend/src/lib/labels.ts` — UI preklad

Ak sa toto rozsynchronizuje, evalskript vypíše iné class_ids ako UI.
