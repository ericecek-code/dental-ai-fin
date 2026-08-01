# Contributing to Dental AI

Thank you for your interest in contributing to Dental AI! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Git** for version control

### Local Development Setup

#### Backend (FastAPI)

```bash
cd dental-ai/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -v

# Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend (React + TypeScript)

```bash
cd dental-ai/frontend

# Install dependencies
npm install

# Start development server
npm run dev -- --host 127.0.0.1 --port 5173

# Build for production
npm run build
```

#### Full Stack with Docker

```bash
cd dental-ai
docker compose up --build
```

## 📋 Development Guidelines

### Code Style

#### Python (Backend)

- **Formatter:** `black` (line length: 88)
- **Linter:** `flake8` + `mypy` (strict)
- **Import sorting:** `isort` (profile: black)
- **Type hints:** Required for all public functions

```bash
# Format code
black .

# Check types
mypy .

# Lint
flake8 .
```

#### TypeScript (Frontend)

- **Formatter:** `prettier` (single quotes, trailing commas)
- **Linter:** `eslint` (airbnb + typescript)
- **Strict mode:** Enabled in `tsconfig.json`

```bash
# Format code
npm run format

# Lint
npm run lint

# Type check
npm run typecheck
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style (formatting, missing semicolons, etc.)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

**Examples:**
```
feat(frontend): add MeasurementsPanel component with mm display
fix(backend): handle empty file upload in analyze endpoint
docs(readme): update DENTEX dataset information
test(backend): add tests for PDF report generation
```

### Branch Naming

```
<type>/<short-description>
```

Examples:
- `feat/measurements-panel`
- `fix/pdf-report-measurements`
- `docs/update-readme`

### Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes with tests
4. **Run** the full test suite locally
5. **Submit** a PR with:
   - Clear description of changes
   - Link to related issue (if any)
   - Screenshots (for UI changes)
6. **Wait** for code review
7. **Merge** after approval

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest -v --cov=app --cov-report=term-missing
```

- **Unit tests:** `tests/test_*.py`
- **Integration tests:** `tests/integration/`
- **Coverage target:** ≥ 80%

### Frontend Tests

```bash
cd frontend
npm run test          # Unit tests (Vitest)
npm run test:e2e      # E2E tests (Playwright)
```

## 📦 Releases

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Breaking changes → MAJOR
- New features → MINOR
- Bug fixes → PATCH

### Release Process

1. Update `CHANGELOG.md`
2. Create release branch: `release/vX.Y.Z`
3. Update version in `pyproject.toml` / `package.json`
4. Create PR to `main`
5. After merge: tag and push: `git tag vX.Y.Z && git push --tags`
6. GitHub Actions builds and publishes Docker images

## 🔒 Security

### Reporting Vulnerabilities

**Do NOT** create public issues for security vulnerabilities.

Email: security@ericecek.com

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Dependencies

- Run `pip-audit` (Python) and `npm audit` (Node.js) regularly
- Keep dependencies updated
- Pin versions in production

## 🏗️ Architecture Overview

```
dental-ai/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/routes/         # REST endpoints
│   │   ├── core/               # Configuration
│   │   ├── ml/                 # ML pipeline
│   │   │   ├── detector.py     # YOLOv8 inference
│   │   │   ├── preprocessor.py # CLAHE + denoising
│   │   │   ├── reporter.py     # PDF reports
│   │   │   ├── measurements.py # CEJ-bone crest mm
│   │   │   └── gradcam.py      # Heatmaps
│   │   └── models/             # Pydantic schemas
│   ├── weights/                # YOLO model weights
│   └── tests/                  # 138 pytest tests
├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom hooks
│   │   ├── lib/                # Utilities
│   │   └── pages/              # Page components
│   └── package.json
├── datasets/dentex/            # DENTEX dataset (local/Modal)
├── .github/workflows/          # CI/CD pipelines
├── docker-compose.yml          # Multi-container deployment
├── Dockerfile                  # Production container
└── README.md
```

## 🧬 ML Pipeline Details

### Model
- **Architecture:** YOLOv8x (Ultralytics)
- **Classes:** 4 (Impacted, Caries, Periapical Lesion, Deep Caries)
- **Input:** 1280×1280 panoramic X-rays
- **Training:** DENTEX dataset (MICCAI 2023)

### Training (Modal GPU)

```bash
# Upload dataset to Modal volume
modal volume put dentex-dataset ./datasets/dentex /dentex

# Run training
modal run train_dentex_modal.py

# Download best model
modal volume get dentex-output /output/runs/detect/dentex_v1/weights/best.pt ./best.pt
```

### Inference

```python
from app.ml.detector import Detector

detector = Detector(model_path="weights/yolov8x_dental.pt")
detections = detector.predict(enhanced_image, conf=0.05)
```

## 📊 Monitoring & Logging

- **Structured logging:** JSON format
- **Health check:** `GET /health` (includes model_loaded status)
- **Metrics:** Prometheus-ready `/metrics` endpoint (planned)
- **Tracing:** OpenTelemetry integration (planned)

## 🤝 Community

- **Issues:** GitHub Issues for bugs and features
- **Discussions:** GitHub Discussions for questions
- **Discord:** [Dental AI Community](https://discord.gg/dental-ai) (planned)

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

**Thank you for contributing to Dental AI!** 🦷

*Questions? Open a [Discussion](https://github.com/ericecek-code/dental-ai-fin/discussions) or email contributors@ericecek.com*