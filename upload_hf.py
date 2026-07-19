"""Upload dental-ai to HuggingFace Spaces."""
import os, sys
sys.path.insert(0, r"C:\Users\PC1\Desktop\dental-ai\.venv\Lib\site-packages")
from pathlib import Path

try:
    from huggingface_hub import HfApi, login
except ImportError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# Check token
token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
if not token:
    cache = Path.home() / ".cache" / "huggingface" / "token"
    if cache.exists():
        token = cache.read_text().strip()

if not token:
    print("[ERROR] No HF token found. Run: huggingface-cli login")
    sys.exit(1)

print(f"[OK] HF token found (len={len(token)})")

# Login
login(token=token)

api = HfApi()

# Get current user
user = api.whoami()
username = user.get("name") or user.get("fullname", "unknown")
print(f"[OK] Logged in as: {username}")

# Space name
space_id = f"{username}/dental-ai"
print(f"[INFO] Target space: {space_id}")

# Check if space exists
try:
    space_info = api.space_info(space_id)
    print(f"[INFO] Space already exists: {space_info.id}")
except Exception:
    print("[INFO] Space does not exist, will create...")
    try:
        api.create_repo(
            repo_id=space_id,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True,
        )
        print(f"[OK] Space created: {space_id}")
    except Exception as e:
        print(f"[ERROR] Failed to create space: {e}")
        sys.exit(1)

# Upload files
upload_dir = Path(r"C:\Users\PC1\Desktop\dental-ai\hf_upload")
print(f"\n[INFO] Uploading from {upload_dir} ...")

try:
    api.upload_folder(
        folder_path=str(upload_dir),
        repo_id=space_id,
        repo_type="space",
    )
    print(f"\n[SUCCESS] Deployed to: https://{username}-dental-ai.hf.space")
except Exception as e:
    print(f"[ERROR] Upload failed: {e}")
    import traceback
    traceback.print_exc()
