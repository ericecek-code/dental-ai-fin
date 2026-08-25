"""
Upload kernel to Kaggle using OAuth token
"""
import requests
import json
import base64

# Read OAuth token
with open(r'C:\Users\PC1\.kaggle\credentials.json', 'r') as f:
    creds = json.load(f)

access_token = creds['access_token']
username = creds['username']

print(f"Using token for user: {username}")

# Read notebook
with open(r'C:\Users\PC1\Desktop\dental-ai\kaggle_training.ipynb', 'r', encoding='utf-8') as f:
    notebook_content = f.read()

# Read kernel metadata
with open(r'C:\Users\PC1\Desktop\dental-ai\kernel-metadata.json', 'r') as f:
    metadata = json.load(f)

# Prepare request
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Kernel data
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

print(f"Pushing kernel: {metadata['id']}")

# Push kernel
response = requests.post(
    'https://api.kaggle.com/v1/kernels.KernelsApiService/SaveKernel',
    headers=headers,
    json=kernel_data
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"Success!")
    print(f"URL: https://www.kaggle.com/code/{result.get('ref', metadata['id'])}")
else:
    print(f"Error: {response.text[:500]}")
