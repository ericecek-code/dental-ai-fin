"""
Dental AI — FastAPI application factory.

Spustenie:
    uvicorn app.main:app --host 0.0.0.0 --port 8000

Produkcia (Render/Docker):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
"""

import logging
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from app.core.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware

# Initialize SQLite database on startup
from app.ml.database import init_db

init_db()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# Middleware (poradie má význam: CORS najskôr, potom auth, potom logging)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)


# ---------------------------------------------------------------------------
# 1) Register API routers
# ---------------------------------------------------------------------------
from app.api.routes import (  # noqa: E402
    analyze,
    health,
    history,
    results,
    vision,
    websocket,
)

for _router in (
    health.router,
    analyze.router,
    websocket.router,
    results.router,
    vision.router,
    history.router,
):
    app.include_router(_router)


# ---------------------------------------------------------------------------
# 2) Mount /assets directory for JS/CSS bundles
# ---------------------------------------------------------------------------
_static_dir = str(settings.static_path)
_assets_dir = settings.static_path / "assets"
if _assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="static-assets")


# ---------------------------------------------------------------------------
# 3) SPA fallback middleware: serve index.html for non-API GET 404s
# ---------------------------------------------------------------------------
_API_PREFIXES = (
    "/analyze",
    "/results",
    "/health",
    "/ws",
    "/vision",
    "/history",
    "/assets",
    "/docs",
    "/openapi.json",
    "/redoc",
)

if settings.static_path.is_dir():
    _index_html = settings.static_path / "index.html"

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            if not request.url.path.startswith(_API_PREFIXES):
                return FileResponse(str(_index_html))
        return response
else:

    @app.get("/", tags=["root"])
    def root():
        return {
            "status": "ok",
            "service": "dental-ai",
            "version": settings.version,
            "note": "static not found",
        }


# ---------------------------------------------------------------------------
# 4) Enhanced health endpoint — reports model + dependency status
# ---------------------------------------------------------------------------
@app.get("/health/v1", tags=["health"])
async def health_v1():
    """Rozšírený health check s informáciami o modeli a závislostiach."""
    try:
        import torch

        cuda_available = torch.cuda.is_available()
    except Exception:
        cuda_available = None

    return {
        "status": "healthy",
        "version": settings.version,
        "model_loaded": settings.weights_path.exists(),
        "model_path": str(settings.weights_path),
        "cuda_available": cuda_available,
        "python_version": sys.version.split()[0],
    }
