# =============================================================================
# Dental AI — single-image build (API + frontend served by FastAPI)
# =============================================================================
# Build:  docker build -t dental-ai .
# Run:    docker run -p 8000:8000 --env-file backend/.env dental-ai

# ---------- Stage 1: Frontend build ----------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: Backend ----------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    YOLO_VERBOSE=False

WORKDIR /app/backend

# System deps for OpenCV (headless) – libgl1 on Debian bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch first, so ultralytics does not pull CUDA wheels
RUN pip install --upgrade pip \
    && pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static

RUN mkdir -p /tmp/dental-ai/uploads /tmp/dental-ai/outputs /tmp/dental-ai/reports \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /tmp/dental-ai

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
