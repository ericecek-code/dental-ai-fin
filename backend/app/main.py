from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

app = FastAPI(title="Dental AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 1) Register API routers
# ---------------------------------------------------------------------------
try:
    from .api.routes import health, analyze, websocket, results, vision
    _routers = [health.router, analyze.router, websocket.router, results.router, vision.router]
except Exception:
    try:
        from .api.routes import health, analyze, websocket, results
        _routers = [health.router, analyze.router, websocket.router, results.router]
    except Exception:
        try:
            from .api.routes import health, analyze, websocket
            _routers = [health.router, analyze.router, websocket.router]
        except Exception:
            _routers = []

for _router in _routers:
    app.include_router(_router)


# ---------------------------------------------------------------------------
# 2) Mount /assets directory for JS/CSS bundles
# ---------------------------------------------------------------------------
_static_dir = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
)

_assets_dir = os.path.join(_static_dir, "assets")
if os.path.isdir(_assets_dir):
    app.mount("/assets", StaticFiles(directory=_assets_dir), name="static-assets")


# ---------------------------------------------------------------------------
# 3) SPA fallback middleware: if a GET returns 404, serve index.html
#    This runs AFTER all API routes are checked, so it never intercepts them.
# ---------------------------------------------------------------------------
if os.path.isdir(_static_dir):
    _index_html = os.path.join(_static_dir, "index.html")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        # Only intercept 404s on GET requests (not API, not assets)
        if response.status_code == 404 and request.method == "GET":
            path = request.url.path
            # Don't intercept API routes
            if not any(path.startswith(p) for p in ("/analyze", "/results", "/health", "/ws", "/vision", "/assets")):
                return FileResponse(_index_html)
        return response
else:
    @app.get("/", tags=["root"])
    def root():
        return {"status": "ok", "service": "dental-ai", "note": "static not found"}
