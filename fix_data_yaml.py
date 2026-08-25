import modal
import os

volume = modal.Volume.from_name('dentex-dataset')

app = modal.App("fix-dentex-data-yaml")

@app.function(volumes={'/data': volume})
def fix_data_yaml():
    # Update data.yaml with absolute paths
    yaml_content = """# DENTEX Dataset - YOLO Configuration
# Paths absolute to dataset root

path: /dentex  # dataset root
train: images/train  # train images
val: images/val      # val images
test: images/test    # test images (optional)

# Classes: 4 diagnoses from DENTEX categories_3
# 0: Impacted
# 1: Caries
# 2: Periapical Lesion
# 3: Deep Caries

names:
  0: Impacted
  1: Caries
  2: Periapical Lesion
  3: Deep Caries

# nc: 4
"""
    with open('/data/data.yaml', 'w') as f:
        f.write(yaml_content)
    print("Updated data.yaml with absolute paths")
    
    # Verify
    with open('/data/data.yaml', 'r') as f:
        print(f.read())

@app.local_entrypoint()
def main():
    fix_data_yaml.remote()