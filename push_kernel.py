"""
Push kernel to Kaggle
"""
import os
import json

# Read credentials
with open(r'C:\Users\PC1\.kaggle\kaggle.json', 'r') as f:
    creds = json.load(f)

os.environ['KAGGLE_USERNAME'] = creds['username']
os.environ['KAGGLE_KEY'] = creds['key']

from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

# Push kernel
print("Pushing kernel to Kaggle...")
result = api.kernels_push(
    folder='C:/Users/PC1/Desktop/dental-ai'
)

print(f"Kernel pushed successfully!")
print(f"URL: https://www.kaggle.com/code/{result.ref}")
