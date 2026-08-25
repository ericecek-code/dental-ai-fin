# Upload DENTEX dataset to Modal volumes using Modal mount
# Run: modal run upload_dentex_modal.py

import modal
from modal.mount import Mount

app = modal.App("dental-ai-upload-dataset")

dataset_volume = modal.Volume.from_name("dentex-dataset", create_if_missing=True)

image = modal.Image.debian_slim(python_version="3.11").pip_install(["pyyaml"])

# Mount the local dataset directory - use class method
mount = Mount._from_local_dir(
    "/c/Users/PC1/Desktop/dental-ai/datasets/dentex",
    remote_path="/data"
)

@app.function(
    image=image,
    volumes={"/data": dataset_volume},
    mounts=[mount],
    timeout=3600,
)
def upload_dataset():
    import os
    import shutil
    from pathlib import Path
    
    # The mounted data is at /data in the container
    remote_data = Path("/data")
    
    print(f"Uploading from mounted /data to volume /data")
    
    # Verify mount
    if not (remote_data / "data.yaml").exists():
        print("ERROR: data.yaml not found in mount")
        print("Contents of /data:", list(remote_data.iterdir()))
        return
    
    # Copy data.yaml to volume (already there via mount, but ensure)
    print("data.yaml found in mount")
    
    # Copy images and labels for train/val to volume
    for split in ["train", "val"]:
        local_img = remote_data / "images" / split
        local_lbl = remote_data / "labels" / split
        remote_img = Path("/data") / "images" / split
        remote_lbl = Path("/data") / "labels" / split
        
        remote_img.mkdir(parents=True, exist_ok=True)
        remote_lbl.mkdir(parents=True, exist_ok=True)
        
        # Copy images
        img_files = list(local_img.glob("*.png")) + list(local_img.glob("*.jpg"))
        for f in img_files:
            shutil.copy2(f, remote_img / f.name)
        print(f"  {split}: {len(img_files)} images")
        
        # Copy labels
        lbl_files = list(local_lbl.glob("*.txt"))
        for f in lbl_files:
            shutil.copy2(f, remote_lbl / f.name)
        print(f"  {split}: {len(lbl_files)} labels")
    
    print("Dataset upload complete!")

@app.local_entrypoint()
def main():
    upload_dataset.remote()