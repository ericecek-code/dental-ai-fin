"""Prepare HF deployment."""
import os, sys, shutil
from pathlib import Path

deploy_src = Path(r"C:\Users\PC1\Desktop\dental-ai\deploy_hf")
frontend_dist = Path(r"C:\Users\PC1\Desktop\dental-ai\frontend\dist")
hf_upload = Path(r"C:\Users\PC1\Desktop\dental-ai\hf_upload")

# Create clean upload directory
if hf_upload.exists():
    shutil.rmtree(hf_upload)
hf_upload.mkdir()

# Copy backend (with weights)
backend_src = deploy_src / "backend"
backend_dst = hf_upload / "backend"
shutil.copytree(backend_src, backend_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
print(f"[OK] Backend copied to {backend_dst}")

# Copy frontend dist -> static
static_dst = hf_upload / "static"
shutil.copytree(frontend_dist, static_dst)
print(f"[OK] Frontend dist -> {static_dst}")

# Copy Dockerfile, README
for f in ["Dockerfile", "README.md"]:
    src = deploy_src / f
    if src.exists():
        shutil.copy2(src, hf_upload / f)
        print(f"[OK] Copied {f}")

# Write the backend __main__.py for HF Spaces
main_py = hf_upload / "backend" / "__main__.py"
main_py.write_text("""\
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=7860, log_level="info")
""")
print(f"[OK] Written {main_py}")

# Check for HF token
hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
if hf_token:
    print(f"[OK] HF_TOKEN found (len={len(hf_token)})")
else:
    # Check HF CLI config
    hf_cache = Path.home() / ".cache" / "huggingface" / "token"
    if hf_cache.exists():
        hf_token = hf_cache.read_text().strip()
        print(f"[OK] HF token from cache (len={len(hf_token)})")
    else:
        print("[WARN] No HF_TOKEN found. Will need to login manually.")

# List final structure
for root, dirs, files in os.walk(hf_upload):
    level = str(root).replace(str(hf_upload), "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    if level < 2:
        for f in files[:10]:
            fpath = os.path.join(root, f)
            size = os.path.getsize(fpath)
            print(f"{indent}  {f} ({size:,} bytes)")
        if len(files) > 10:
            print(f"{indent}  ... +{len(files)-10} more files")

print("\n[OK] HF upload directory ready at:", hf_upload)
