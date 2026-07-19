---
title: Dental-AI
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

# 🦷 Dental-AI (DenteScope)

AI-powered dental X-ray analysis using YOLOv8. Detects 31 dental conditions including caries, periapical lesions, crowns, implants, and more.

## Features
- Upload dental X-ray images
- Real-time detection with confidence slider
- Colored bounding box overlays
- PDF report generation
- 31 dental condition classes

## API
- `POST /analyze/?conf=0.05` - Upload X-ray for analysis
- `GET /results/{job_id}` - Get detection results
- `GET /results/{job_id}/overlay` - Get overlay image
- `GET /results/{job_id}/report` - Download PDF report
- `GET /docs` - Swagger UI documentation
