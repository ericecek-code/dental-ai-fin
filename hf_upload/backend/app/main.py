from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def root():
    return {"status": "ok", "service": "dental-ai"}



# --- Mount static frontend ---
import os as _os
_static_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "static")
if _os.path.isdir(_static_dir):
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse

    # Serve the built frontend
    app.mount("/assets", StaticFiles(directory=_os.path.join(_static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA index.html for all non-API routes."""
        file_path = _os.path.join(_static_dir, full_path)
        if _os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(_os.path.join(_static_dir, "index.html"))

# Lazy import routes so missing optional packages don't crash startup
try:
    from .api.routes import health, analyze, websocket, results, vision
    routers = [health.router, analyze.router, websocket.router, results.router, vision.router]
except Exception:
    try:
        from .api.routes import health, analyze, websocket, results
        routers = [health.router, analyze.router, websocket.router, results.router]
    except Exception:
        routers = []

for router in routers:
    app.include_router(router)
