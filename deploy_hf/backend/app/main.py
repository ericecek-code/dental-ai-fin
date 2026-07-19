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
