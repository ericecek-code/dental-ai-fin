"""
Test Kaggle API authentication
"""
import requests
import json

# Read API token
with open(r'C:\Users\PC1\.kaggle\kaggle.json', 'r') as f:
    creds = json.load(f)

# Test authentication
headers = {
    'Authorization': f'Bearer {creds["key"]}',
    'Content-Type': 'application/json'
}

# List kernels
print("Testing Kaggle API authentication...")
response = requests.get('https://api.kaggle.com/v1/kernels/list', headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    kernels = response.json()
    print(f"Kernels: {len(kernels)} found")
    for k in kernels[:5]:
        print(f"  - {k['ref']}")
else:
    print(f"Error: {response.text[:300]}")
