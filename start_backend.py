"""Start the dental-ai FastAPI backend server."""
import os, sys

# Set CWD to deploy_hf/backend so relative imports work
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy_hf", "backend")
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

print(f"Starting backend from: {backend_dir}")
import uvicorn
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
