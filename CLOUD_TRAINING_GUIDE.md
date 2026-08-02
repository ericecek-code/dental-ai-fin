# ☁️ Cloud Training Guide - Dental AI

This guide explains how to train Dental AI models using **free cloud GPUs** (Kaggle, Colab) or paid cloud (RunPod).

---

## 🎯 **Quick Start Options**

| Platform | GPU | Free Hours | Best For | Setup Time |
|----------|-----|------------|----------|------------|
| **Kaggle** | P100/T4 | 30h/week | Production training | 5 min |
| **Colab** | T4/A100 | Limited | Prototyping | 3 min |
| **RunPod** | A100/H100 | Pay (~$0.50/h) | Heavy training | 5 min |
| **Local** | Your GPU | Unlimited | Development | 0 min |

---

## 🚀 **QUICK START: KAGGLE (RECOMMENDED)**

### 1. Prepare Kaggle Account
1. Go to [kaggle.com](https://kaggle.com) → Settings → API → **Create New Token**
2. Download `kaggle.json` → note username & key

### 2. Open Notebook on Kaggle
1. Go to [kaggle.com/code](https://kaggle.com/code)
2. **New Notebook** → **Import** → Select `kaggle_train_dentex.ipynb`
3. **Settings** → **Accelerator** → **GPU P100** (or T4)
4. **Settings** → **Internet** → **ON** (for HF upload)

### 3. Configure Credentials
In the notebook, edit Cell 3:
```python
os.environ["KAGGLE_USERNAME"] = "YOUR_KAGGLE_USERNAME"
os.environ["KAGGLE_KEY"] = "YOUR_KAGGLE_API_KEY"
```

### 4. (Optional) HuggingFace Upload
- Add HF token in **Settings → Secrets** → **Add secret** → `HF_TOKEN`
- Or set in notebook: `os.environ["HF_TOKEN"] = "hf_..."`

### 5. Run All Cells (Ctrl+Shift+Enter)
- Training: ~2-4 hours for 100 epochs
- Best model saved to `/kaggle/working/output/best.pt`
- Download from **Output** tab

---

## 🚀 **COLAB (FALLBACK)**

### 1. Open in Colab
1. Go to [colab.research.google.com](https://colab.research.google.com)
2. **File** → **Upload notebook** → Select `colab_train_dentex.ipynb`

### 2. Enable GPU
- **Runtime** → **Change runtime type** → **GPU T4** (or A100 if available)

### 3. Mount Google Drive
- Run Cell 2 → Authorize Google Drive access
- Models saved to `MyDrive/dental-ai/output/`

### 3. Run All Cells
- Same workflow as Kaggle
- Models persist in Google Drive across sessions

---

## 🔧 **UNIVERSAL SCRIPT: `train_cloud.py`**

Works on **Kaggle, Colab, RunPod, Local, RunPod**:

```bash
# Basic usage (auto-detects environment)
python train_cloud.py

# With custom config
python train_cloud.py --config config.yaml

# Override specific params
python train_cloud.py --model yolov8m --epochs 50 --batch 8

# Only prepare data (no training)
python train_cloud.py --download-data --no-train

# Export existing model to ONNX
python train_cloud.py --export-only --model-path runs/detect/dentex_v1/weights/best.pt
```

### Key Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--config` | Path to config YAML | `config.yaml` |
| `--model` | Model variant | `yolov8x.pt` |
| `--epochs` | Training epochs | 100 |
| `--batch` | Batch size | 16 |
| `--imgsz` | Image size | 1280 |
| `--model` | Model variant | `yolov8x.pt` |
| `--download-data` | Auto-download dataset | false |
| `--no-train` | Only prepare data | false |
| `--export-only` | Export existing model | false |
| `--model-path` | Model to export | - |

### Environment Variables
```bash
# Required for Kaggle
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key

# Optional: HuggingFace upload
export HF_TOKEN=hf_xxxxxxxxxxxxx

# Optional: Override config
export HF_TOKEN=hf_xxx
```

---

## 📊 **EXPECTED RESULTS**

| Metric | Target | Typical Result |
|--------|--------|----------------|
| **mAP50** | ≥ 0.50 | 0.52-0.58 |
| **Recall (Caries)** | ≥ 0.65 | 0.68-0.75 |
| **Training Time** | - | 2-4 hours (100 epochs) |
| **Model Size** | - | ~367 MB (yolov8x) |

### Success Criteria
- ✅ mAP50 ≥ 0.50
- ✅ Recall (Caries) ≥ 0.65
- ✅ Model exports to ONNX successfully

---

## 📁 **OUTPUT STRUCTURE**

After training:
```
runs/detect/dentex_v1/
├── weights/
│   ├── best.pt          # Best model (use this!)
│   ├── last.pt          # Last epoch
│   └── epoch_XX.pt      # Periodic checkpoints
├── results.csv          # Training metrics
├── results.png          # Training curves
└── confusion_matrix.png
```

**Deploy model:**
```bash
cp runs/detect/dentex_v1/weights/best.pt backend/weights/yolov8x_dental.pt
```

---

## 🔐 **CREDENTIALS SETUP**

### Kaggle (Required)
```bash
# ~/.kaggle/kaggle.json
{
  "username": "your_username",
  "key": "your_api_key"
}
```

### HuggingFace (Optional - for auto-upload)
```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

### Google Colab
- Mount Drive automatically in notebook
- Or set in Colab: **Settings → Secrets → HF_TOKEN**

---

## 🐛 **TROUBLESHOOTING**

| Issue | Solution |
|-------|----------|
| **OOM (Out of Memory)** | Reduce `batch` to 8 or 4, reduce `imgsz` to 1024 |
| **Slow training** | Enable `cache: true` if RAM > 16GB, reduce `workers` |
| **Kaggle GPU not available** | Wait for quota reset (weekly), use Colab/RunPod |
| **Colab disconnects** | Enable "Keep alive" extension, save checkpoints to Drive |
| **Dataset not found** | Run with `--download-data` flag first |
| **HF upload fails** | Check `HF_TOKEN` validity, repo exists |

---

## 📚 **RESOURCES**

- **Kaggle Notebook**: `kaggle_train_dentex.ipynb`
- **Colab Notebook**: `colab_train_dentex.ipynb`
- **Universal Script**: `train_cloud.py`
- **Config**: `config.yaml`
- **Dataset**: `truthisneverlinear/dentex-challenge-2023` (705 train, 50 val, 250 test)
- **Model Weights**: `yolov8x.pt` (auto-downloaded by ultralytics)

---

## 📞 **SUPPORT**

- **Issues**: GitHub Issues
- **Kaggle**: [Kaggle Forums](https://kaggle.com/discussions)
- **Colab**: [Colab FAQ](https://research.google.com/colab/faq.html)
- **Ultralytics**: [YOLOv8 Docs](https://docs.ultralytics.com)

---

**Happy Training! 🦷🚀**