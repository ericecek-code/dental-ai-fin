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

**AI-powered dental X-ray analysis — detect 19 conditions with color-coded overlays.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B6B.svg)](https://docs.ultralytics.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Overview

Dental AI is an end-to-end dental X-ray analysis platform that leverages YOLOv8 deep learning models to automatically detect and classify dental conditions from intraoral radiographs. The system provides real-time detection with color-coded overlays, interactive image viewing, PDF report generation, and Grad-CAM explainability.

**Live Demo:** [HuggingFace Spaces — Ericecek/dental-ai](https://huggingface.co/spaces/Ericecek/dental-ai)

---

## ✨ Features

- **19 Dental Conditions Detected** — Caries, Deep Caries, Crown, Implant, Malaligned, Mandibular Canal, Missing Teeth, Periapical Lesion, Retained Root, Root Canal Treatment, Root Piece, Impacted Tooth, Filling, Plating, Wire, Cyst, Root Resorption, Primary Teeth
- **Color-Coded Overlays** — Each condition rendered with a distinct color for instant visual identification
- **Interactive Canvas Viewer** — Zoom (mouse wheel), pan (drag), and fullscreen lightbox with keyboard shortcuts
- **PDF Reports** — Clinical-grade reports with Slovak localization and severity triage (urgent / treat soon / watch)
- **Grad-CAM Explainability** — Heatmaps showing which regions influenced the model's decisions
- **Gemini Vision Integration** — AI-powered natural language description of detected findings
- **Real-Time Analysis** — WebSocket-based progress tracking during inference
- **DICOM Support** — Read standard medical imaging format files
- **Confidence Threshold Control** — Adjustable sensitivity slider (0.01–0.95) to balance recall vs. precision

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Build and run the backend
cd dental-ai
docker build -t dental-ai .
docker run -p 7860:7860 dental-ai
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
│  │ (zoom/pan)   │ │              │ │ (color-coded)        │ │
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
│  │  (CLAHE)       (19 classes)      (severity/overlay)  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐ │
│  │ Grad-CAM     │ │ PDF Reporter │ │ Gemini Vision      │ │
│  │ (explain)    │ │ (Slovak)     │ │ (AI description)   │ │
│  └──────────────┘ └──────────────┘ └────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **ML Model** | YOLOv8x (Ultralytics) | Object detection — 19 dental conditions |
| **Backend** | Python 3.11 + FastAPI | REST API, WebSocket, file handling |
| **Preprocessing** | OpenCV (CLAHE, denoising) | Image enhancement before inference |
| **Explainability** | Grad-CAM | Visual heatmaps of model attention |
| **Reports** | ReportLab | PDF generation with Slovak labels |
| **Vision AI** | Google Gemini | Natural language analysis of findings |
| **Frontend** | React 18 + TypeScript | SPA with interactive X-ray viewer |
| **Build Tool** | Vite | Fast dev server + bundling |
| **Styling** | Tailwind CSS | Utility-first responsive UI |
| **Deployment** | Docker + HuggingFace Spaces | Containerized production hosting |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze/` | Upload X-ray image for analysis. Accepts `multipart/form-data` with optional `?conf=` threshold (default: 0.01). Returns detections, class breakdown, and job ID. |
| `GET` | `/results/{job_id}` | Retrieve full detection results for a completed analysis. |
| `GET` | `/results/{job_id}/overlay` | Download the annotated X-ray PNG with color-coded bounding boxes. |
| `GET` | `/results/{job_id}/report` | Generate a PDF report grouping findings by severity. |
| `GET` | `/health` | Health check — returns `{"status": "healthy"}`. |
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
  "detection_count": 42,
  "by_class": {
    "Caries": { "count": 8, "max_conf": 0.78 },
    "Filling": { "count": 5, "max_conf": 0.92 },
    "Crown": { "count": 3, "max_conf": 0.88 }
  },
  "detections": [
    {
      "label": "Caries",
      "confidence": 0.78,
      "bbox": [120, 200, 180, 260],
      "severity": "urgent",
      "tooth_number": "Q3-5"
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
| **Training Dataset** | 10,171 images (merged from 3 datasets) |
| **Classes** | 19 dental conditions |
| **mAP50** | 0.306 (Phase 2, YOLOv8m) |
| **Training Hardware** | NVIDIA GPU (local) / Kaggle P100 |

### 19 Detection Classes

| # | Class | Color | Severity |
|---|-------|-------|----------|
| 1 | Caries | 🟡 Gold-red | Urgent |
| 2 | Deep Caries | 🔴 Red | Urgent |
| 3 | Periapical Lesion | 🟣 Purple | Urgent |
| 4 | Crown | 🔵 Blue | Watch |
| 5 | Filling | ⚪ White | Watch |
| 6 | Implant | 🔵 Teal | Watch |
| 7 | Root Canal Treatment | 🔵 Blue | Watch |
| 8 | Malaligned | ⚪ Gray | Watch |
| 9 | Mandibular Canal | ⚪ Gray | Watch |
| 10 | Impacted Tooth | 🟠 Orange | Treat Soon |
| 11 | Missing Teeth | 🔴 Dark Red | Treat Soon |
| 12 | Retained Root | 🔵 Navy | Treat Soon |
| 13 | Root Piece | 🔵 Navy | Treat Soon |
| 14 | Plating | ⚪ Silver | Watch |
| 15 | Wire | ⚪ Silver | Watch |
| 16 | Cyst | 🟣 Purple | Treat Soon |
| 17 | Root Resorption | 🔴 Dark Red | Treat Soon |
| 18 | Primary Teeth | ⚪ Gray | Watch |
| 19 | — | — | — |

### Dataset Sources

| Dataset | Source | Images | Classes |
|---------|--------|:------:|:-------:|
| oral-disease | Kaggle | 8,616 | 5 |
| dental-radiography | Kaggle | 1,269 | 2 |
| tooth-dataset | Kaggle | 1,900 | 1 |
| **Combined** | **Merged** | **10,171** | **5 → 19** |

### Confidence Threshold Guide

| Threshold | Behavior |
|-----------|----------|
| `0.01` | Maximum recall — detects weak Caries signals (recommended for screening) |
| `0.05` | Balanced — catches most conditions with moderate noise |
| `0.25` | Conservative — high-confidence detections only (default YOLO) |
| `0.50+` | Strict — near-certainty detections only |

> ⚠️ **Note:** The default YOLO confidence of 0.25 will miss most Caries detections. For comprehensive screening, use `conf=0.01`–`0.05`.

---

## 🗺️ Roadmap

### Phase 1 — Foundation ✅
- YOLOv8 inference pipeline with 19 classes
- FastAPI backend with REST endpoints
- React frontend with canvas overlay viewer
- Docker deployment

### Phase 2 — Training & Optimization 🔄
- Combined dataset from 3 sources (10,171 images)
- YOLOv8x training with augmentation
- mAP50 improvement target: 0.306 → 0.60+
- Per-class confidence distribution analysis

### Phase 3 — Clinical Features
- PDF report generation with severity triage
- Grad-CAM explainability heatmaps
- Gemini Vision natural language descriptions
- Slovak localization for clinical workflow

### Phase 4 — Advanced ML
- YOLOv8x retraining on expanded dataset
- Cross-validation across datasets
- Model ensemble (multi-scale inference)
- FDI tooth number integration

### Phase 5 — Production
- Multi-user authentication and session management
- DICOM native support
- PACS integration
- Regulatory compliance (CE marking preparation)
- Performance benchmarking vs. commercial systems (Diagnocat, Pearl AI)

---

## 🧪 Testing

```bash
# Backend health check
curl http://localhost:8000/health

# Full analysis test
curl -X POST "http://localhost:8000/analyze/?conf=0.05" \
  -F "file=@test_images/sample_xray.jpg"

# Frontend smoke test
curl -s http://localhost:5173 | head -20
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
│   │   │   ├── reporter.py      # PDF report generation
│   │   │   ├── gradcam.py       # Explainability heatmaps
│   │   │   ├── heatmap.py       # Visualization
│   │   │   └── gemini_vision.py # AI description
│   │   ├── models/schemas.py    # Pydantic data models
│   │   └── main.py              # FastAPI application
│   ├── weights/                  # YOLOv8 model weights
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities (labels, utils)
│   │   └── App.tsx
│   └── package.json
├── training/                     # YOLOv8 training scripts
├── scripts/                      # Utility scripts
├── Dockerfile                    # Production container
├── status.yaml                   # Project phase tracker
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up your development environment, code style, and the pull request process.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://docs.ultralytics.com/) — Object detection framework
- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [HuggingFace Spaces](https://huggingface.co/spaces) — Free ML deployment platform
- Dental datasets from Kaggle and Roboflow communities
- Google Gemini API for vision-language analysis

---

## 📧 Contact

**Ericecek** — [GitHub](https://github.com/ericecek-code) | [HuggingFace](https://huggingface.co/Ericecek)
