"""
Push kernel na Kaggle cez Python API
"""
import os
import json
import requests

# Načítaj credentials
with open(r'C:\Users\PC1\.kaggle\kaggle.json', 'r') as f:
    creds = json.load(f)

username = creds['username']
api_key = creds['key']

print(f"Používateľ: {username}")

# Načítaj notebook
notebook_path = r'C:\Users\PC1\Desktop\dental-ai\kaggle_training.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook_content = f.read()

# Načítaj metadata
with open(r'C:\Users\PC1\Desktop\dental-ai\kernel-metadata.json', 'r') as f:
    metadata = json.load(f)

# Priprav dáta pre API
kernel_data = {
    'id': metadata['id'],
    'slug': metadata['id'].split('/')[-1],
    'title': metadata['title'],
    'code_file': metadata['code_file'],
    'language': metadata['language'],
    'kernel_type': metadata['kernel_type'],
    'is_private': metadata['is_private'],
    'enable_gpu': metadata['enable_gpu'],
    'enable_internet': metadata['enable_internet'],
    'dataset_sources': metadata.get('dataset_sources', []),
    'kernel_sources': [],
    'competition_sources': [],
    'code': notebook_content
}

# Headers
headers = {
    'Authorization': f'Basic {__import__("base64").b64encode(f"{username}:{api_key}".encode()).decode()}',
    'Content-Type': 'application/json'
}

print(f"Pushing kernel: {metadata['id']}")

# Push
response = requests.post(
    'https://www.kaggle.com/api/v1/kernels.KernelsApiService/SaveKernel',
    headers=headers,
    json=kernel_data
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"Úspech!")
    print(f"URL: https://www.kaggle.com/code/{result.get('ref', metadata['id'])}")
else:
    print(f"Chyba: {response.text[:500]}")
