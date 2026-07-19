"""Prep HF deployment: update main.py to serve static + fix Dockerfile."""
import os, sys, shutil
from pathlib import Path

hf_upload = Path(r"C:\Users\PC1\Desktop\dental-ai\hf_upload")

# ---- 1. Update main.py to serve static frontend ----
main_py = hf_upload / "backend" / "app" / "main.py"
content = main_py.read_text(encoding="utf-8")

# Add static file mounting before the routers loop
static_mount = """
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
        \"\"\"Serve the SPA index.html for all non-API routes.\"\"\"
        file_path = _os.path.join(_static_dir, full_path)
        if _os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(_os.path.join(_static_dir, "index.html"))
"""

# Insert static mount BEFORE the router inclusion loop
marker = "# Lazy import routes so missing optional packages don't crash startup"
if marker in content:
    content = content.replace(marker, static_mount + "\n" + marker)
    main_py.write_text(content, encoding="utf-8")
    print("[OK] main.py updated with static file serving")
else:
    print("[WARN] Could not find marker in main.py, manually add static serving")

# ---- 2. Update Dockerfile to copy static files ----
dockerfile = hf_upload / "Dockerfile"
df_content = dockerfile.read_text(encoding="utf-8")
if "static/" not in df_content:
    df_content = df_content.replace(
        "COPY backend/ .",
        "COPY backend/ .\nCOPY static/ ./static/"
    )
    dockerfile.write_text(df_content, encoding="utf-8")
    print("[OK] Dockerfile updated to copy static/")
else:
    print("[INFO] Dockerfile already copies static/")

# ---- 3. Fix model path for HF deployment ----
# The analyze.py uses relative path "weights/yolov8x_dental.pt"
# We need to make sure it works relative to /app/backend/ in Docker
analyze_py = hf_upload / "backend" / "app" / "api" / "routes" / "analyze.py"
acontent = analyze_py.read_text(encoding="utf-8")
if 'model_path="weights/yolov8x_dental.pt"' in acontent:
    acontent = acontent.replace(
        'model_path="weights/yolov8x_dental.pt"',
        'model_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "weights", "yolov8x_dental.pt")'
    )
    if "import os" not in acontent.split("router")[0]:
        acontent = "import os\n" + acontent
    analyze_py.write_text(acontent, encoding="utf-8")
    print("[OK] analyze.py model path fixed for HF")
else:
    print("[INFO] analyze.py model path already absolute-ish")

# ---- 4. Remove junk files ----
junk = [
    hf_upload / "backend" / "test_imports.py",
    hf_upload / "backend" / "${Root}",
]
for j in junk:
    if j.exists():
        if j.is_dir():
            shutil.rmtree(j)
        else:
            j.unlink()
        print(f"[OK] Removed {j.name}")

print("\n[READY] HF deployment prepared at:", hf_upload)
