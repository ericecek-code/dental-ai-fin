import os, sys, traceback, shutil
sys.stdout.reconfigure(encoding='utf-8')
from huggingface_hub import HfApi

api = HfApi(token=os.getenv('HF_TOKEN'))
base = r'C:\Users\PC1\Desktop\dental-ai\deploy_hf'

try:
    result = api.upload_folder(
        folder_path=base,
        repo_id='Ericecek/dental-ai',
        repo_type='space',
        commit_message='Full update: CLAHE, heatmap, gradcam, rounded boxes, fullscreen, canvas fixes',
        ignore_patterns=['**/*.pt', '**/__pycache__/**'],
    )
    with open(r'C:\Users\PC1\Desktop\deploy_result.txt', 'w', encoding='utf-8') as f:
        f.write(f'SUCCESS: {result}\n')
except Exception as e:
    with open(r'C:\Users\PC1\Desktop\deploy_result.txt', 'w', encoding='utf-8') as f:
        f.write(f'ERROR: {traceback.format_exc()}\n')
