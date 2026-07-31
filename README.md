---
title: Dental AI
emoji: 🦷
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
tags:
  - dental
  - xray
  - yolo
  - medical
  - computer-vision
---

# 🦷 Dental AI

**AI-powered dental X-ray analysis — detect dental conditions with color-coded overlays, measurements, and professional PDF reports.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B6B.svg)](https://docs.ultralytics.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev/)
[![CI](https://github.com/ericecek-code/dental-ai-fin/actions/workflows/ci.yml/badge.svg)](https://github.com/ericecek-code/dental-ai-fin/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

Dental AI is an end-to-end dental X-ray analysis platform that leverages YOLOv8 deep learning models to automatically detect and classify dental conditions from panoramic radiographs. The system provides real-time detection with color-coded overlays, interactive image viewing, **millimeter measurements**, PDF report generation, and Grad-CAM explainability — all with **Slovak localization** for clinical workflow.

**Live Demo:** [HuggingFace Spaces — Ericecek/dental-ai](https://huggingface.co/spaces/Ericecek/dental-ai)

---

## ✨ Features

- **4 Key Diagnoses Detected** — Impacted, Caries, Periapical Lesion, Deep Caries (trained on DENTEX dataset)
- **Color-Coded Overlays** — Each condition rendered with distinct color + severity (urgent / treat soon / watch)
- **Interactive Canvas Viewer** — Zoom (mouse wheel), pan (drag), fullscreen, CLAHE/pseudocolor/heatmap modes
- **Millimeter Measurements** — CEJ-to-bone-crest periodontal measurements per tooth
- **PDF Reports** — Clinical-grade reports with Slovak localization, severity triage, measurements, and recommendations
- **Grad-CAM Explainability** — Heatmaps showing which regions influenced the model's decisions
- **Health Score Gauge** — Visual 0-100 dental health score based on findings
- **Odontogram** — FDI notation (11-48) with color-coded tooth status
- **Confidence Threshold Control** — Adjustable sensitivity slider (0.01–0.95)
- **WebSocket Progress** — Real-time analysis progress tracking
- **DICOM Support** — Read standard medical imaging format files

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Build and run
cd dental-ai
docker compose up --build
```

Open `http://localhost:7860` in your browser.

### Local Development

#### Backend (Python/FastAPI)

```bash
cd dental-ai/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend (React/TypeScript)

```bash
cd dental-ai/frontend

# Install dependencies
npm install

# Start development server
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://localhost:5173` — the React app proxies API calls to the backend on port 8000.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
│  Vite + TypeScript + Tailwind CSS + Canvas Overlay          │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ X-ray Viewer │ │ Upload Zone  │ │ Detection Cards      │ │
│  │ (zoom/pan)   │ │ + Measurements│ │ (color-coded)       │ │
│  └─────────────┘ └──────────────┘ └──────────────────────┘ │
│                         │  HTTP / WebSocket                 │
├─────────────────────────┼───────────────────────────────────┤
│                    Backend (FastAPI)                         │
│  ┌──────────┐ ┌─────────────┐ ┌────────────┐ ┌──────────┐ │
│  │ /analyze │ │ /results    │ │ /health    │ │ /ws/     │ │
│  │ (POST)   │ │ (GET)       │ │ (GET)      │ │ (WS)     │ │
│  └────┬─────┘ └──────┬──────┘ └────────────┘ └──────────┘ │
│       │              │                                      │
│  ┌────▼──────────────▼──────────────────────────────────┐  │
│  │                    ML Pipeline                        │  │
│  │  Preprocessor → YOLOv8 Detector → Postprocessor      │  │
│  │  (CLAHE)       (4 classes)      (severity/overlay)   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐ │
│  │ Grad-CAM     │ │ PDF Reporter │ │ Measurements       │ │
│  │ (explain)    │ │ (Slovak)     │ │ (CEJ-Bone Crest)   │ │
│  └──────────────┘ └──────────────┘ └────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML Model** | YOLOv8x (Ultralytics) | Object detection — 4 dental diagnoses |
| **Backend** | Python 3.11 + FastAPI | REST API, WebSocket, file handling |
| **Preprocessing** | OpenCV (CLAHE, denoising) | Image enhancement before inference |
| **Explainability** | Grad-CAM | Visual heatmaps of model attention |
| **Reports** | ReportLab | PDF generation with Slovak labels |
| **Measurements** | Custom mm-calibration | CEJ-to-bone-crest periodontal distances |
| **Frontend** | React 18 + TypeScript | SPA with interactive X-ray viewer |
| **Build Tool** | Vite | Fast dev server + bundling |
| **Styling** | Tailwind CSS | Utility-first responsive UI |
| **Deployment** | Docker + HuggingFace Spaces | Containerized production hosting |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze/` | Upload X-ray image for analysis. Accepts `multipart/form-data` with optional `?conf=` threshold (default: 0.05). Returns detections, class breakdown, and job ID. |
| `GET` | `/results/{job_id}` | Retrieve full detection results for a completed analysis. |
| `GET` | `/results/{job_id}/overlay` | Download the annotated X-ray PNG with color-coded bounding boxes. |
| `GET` | `/results/{job_id}/report` | Generate a PDF report grouping findings by severity. |
| `GET` | `/results/{job_id}/measurements` | Retrieve CEJ-to-bone-crest measurements in mm. |
| `GET` | `/health` | Health check — returns `{"status": "healthy", "model_loaded": true}`. |
| `WS` | `/ws/status/{job_id}` | WebSocket stream for real-time analysis progress. |

### Example Request

```bash
curl -X POST "http://localhost:8000/analyze/?conf=0.05" \
  -F "file=@dental_xray.jpg"
```

### Example Response

```json
{
  "job_id": "abc123",
  "status": "completed",
  "filename": "dental_xray.jpg",
  "conf_threshold": 0.05,
  "detection_count": 12,
  "by_class": {
    "Caries": { "count": 5, "max_conf": 0.78, "severity": "urgent" },
    "Deep Caries": { "count": 2, "max_conf": 0.85, "severity": "urgent" },
    "Periapical Lesion": { "count": 3, "max_conf": 0.72, "severity": "treat_soon" },
    "Impacted": { "count": 2, "max_conf": 0.65, "severity": "watch" }
  },
  "detections": [
    {
      "label": "Caries",
      "confidence": 0.78,
      "bbox": [120, 200, 180, 260],
      "severity": "urgent",
      "tooth_number": "36",
      "class_id": 1
    }
  ],
  "measurements": [
    {
      "tooth_number": "36",
      "mm": 3.2,
      "status": "moderate",
      "note": "Stredná resorpcia kosti"
    }
  ]
}
```

---

## 📊 Model Performance

### Training Overview

| Metric | Value |
|--------|-------|
| **Model Architecture** | YOLOv8x (extra-large) |
| **Training Dataset** | DENTEX (705 train, 46 val, 250 test) |
| **Classes** | 4 diagnoses: Impacted, Caries, Periapical Lesion, Deep Caries |
| **Image Resolution** | 1280×1280 |
| **Training Hardware** | NVIDIA A10G (Modal) |
| **Target mAP50** | ≥ 0.50 |
| **Target Recall (Caries)** | ≥ 0.65 |

### 4 Detection Classes

| # | Class | Slovak | Color | Severity |
|---|-------|--------|-------|----------|
| 0 | Impacted | Retinovaný zub | 🟠 Orange | Watch |
| 1 | Caries | Kaz | 🔴 Red | Urgent |
| 2 | Periapical Lesion | Periapikálna lézia | 🟣 Purple | Treat Soon |
| 3 | Deep Caries | Hlbokejší kaz | 🔴 Dark Red | Urgent |

### Dataset Source

| Dataset | Source | Images | Classes |
|---------|--------|:------:|:-------:|
| **DENTEX** | MICCAI 2023 Challenge | 1,005 (705/46/250 split) | 4 diagnoses + FDI |
| **Validation** | Manual expert annotation | Hierarchical (quadrant + tooth + diagnosis) | |

---

## 🗺️ Roadmap

### Phase 1 — Foundation ✅
- YOLOv8 inference pipeline with 4 classes
- FastAPI backend with REST endpoints
- React frontend with canvas overlay viewer
- Docker deployment

### Phase 2 — Training & Optimization 🔄
- DENTEX dataset training (Modal A10G GPU)
- mAP50 improvement target: ≥ 0.50
- Per-class confidence distribution analysis

### Phase 3 — Clinical Features ✅
- PDF report generation with severity triage
- Grad-CAM explainability heatmaps
- CEJ-to-bone-crest millimeter measurements
- Slovak localization for clinical workflow
- Health score gauge + Odontogram FDI

### Phase 4 — Advanced ML
- Cross-validation across datasets
- Model ensemble (multi-scale inference)
- FDI tooth number integration (2nd model)

### Phase 5 — Production
- Multi-user authentication and session management
- DICOM native support
- PACS integration
- Regulatory compliance (CE marking preparation)

---

## 🧪 Testing

```bash
# Backend tests (138 tests)
cd dental-ai/backend
python -m pytest -v

# Frontend build
cd dental-ai/frontend
npm run build

# Full analysis test
curl -X POST "http://localhost:8000/analyze/?conf=0.05" \
  -F "file=@test_images/sample_xray.jpg"
```

---

## 📁 Project Structure

```
dental-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # FastAPI route handlers
│   │   ├── core/config.py       # Application configuration
│   │   ├── ml/                   # ML pipeline modules
│   │   │   ├── detector.py      # YOLOv8 inference engine
│   │   │   ├── preprocessor.py  # CLAHE + denoising
│   │   │   ├── reporter.py      # PDF report generation (Slovak)
│   │   │   ├── gradcam.py       # Explainability heatmaps
│   │   │   ├── heatmap.py       # Visualization
│   │   │   ├── measurements.py  # CEJ-to-bone-crest mm
│   │   │   └── database.py      # SQLite persistence
│   │   ├── models/schemas.py    # Pydantic data models
│   │   └── main.py              # FastAPI application
│   ├── weights/                  # YOLOv8 model weights
│   ├── requirements.txt
│   └── tests/                    # 138 pytest tests
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── FindingCard.tsx  # Detection cards (SK labels)
│   │   │   ├── Odontogram.tsx   # FDI 11-48 visualization
│   │   │   ├── MeasurementsPanel.tsx # mm measurements
│   │   │   ├── HealthScoreGauge.tsx  # 0-100 gauge
│   │   │   └── CanvasOverlay.tsx     # Interactive viewer
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities (labels, utils)
│   │   └── pages/Results.tsx    # Main analysis page
│   └── package.json
├── datasets/dentex/              # DENTEX dataset (local/Modal)
├── .github/workflows/ci.yml      # CI/CD pipeline
├── docker-compose.yml            # Multi-container deployment
├── Dockerfile                    # Production container
├── README.md
└── LICENSE
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up your development environment, code style, and the pull request process.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [DENTEX Dataset](https://huggingface.co/datasets/ibrahimhamamci/DENTEX) — MICCAI 2023 Challenge, hierarchical dental annotations
- [Ultralytics YOLOv8](https://docs.ultralytics.com/) — Object detection framework
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [HuggingFace Spaces](https://huggingface.co/spaces) — Free ML deployment platform
- Dental datasets from Kaggle and Roboflow communities
- Google Gemini API for vision-language analysis

---

## 📧 Contact

**Ericecek** — [GitHub](https://github.com/ericecek-code) | [HuggingFace](https://huggingface.co/Ericecek)