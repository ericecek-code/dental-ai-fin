import json, sys, base64, requests
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\PC1\.kaggle\credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)
with open(r'C:\Users\PC1\Desktop\dental-ai\kernel-metadata.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)
with open(r'C:\Users\PC1\Desktop\dental-ai\kaggle_training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb_str = json.dumps(nb, indent=1, ensure_ascii=False)

headers = {
    'Authorization': 'Basic ' + base64.b64encode(f"{creds['username']}:{creds['access_token']}".encode()).decode(),
    'Content-Type': 'application/json'
}

payload = {
    'id': meta['id'],
    'slug': meta['id'].split('/')[-1],
    'title': meta['title'],
    'code_file': meta['code_file'],
    'language': meta['language'],
    'kernel_type': meta['kernel_type'],
    'is_private': meta['is_private'],
    'enable_gpu': meta['enable_gpu'],
    'enable_internet': meta['enable_internet'],
    'dataset_sources': meta.get('dataset_sources', []),
    'kernel_sources': [],
    'competition_sources': [],
    'code': nb_str
}

r = requests.post(
    'https://www.kaggle.com/api/v1/kernels.KernelsApiService/SaveKernel',
    headers=headers,
    json=payload,
    timeout=120
)
print('Status:', r.status_code)
print('Response:', r.text[:800])
