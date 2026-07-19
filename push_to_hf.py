import os
from huggingface_hub import HfApi

token = os.getenv('HF_TOKEN')
api = HfApi(token=os.getenv('HF_TOKEN'))
repo_id = 'Ericecek/dental-ai'
deploy_dir = r'C:\Users\PC1\Desktop\dental-ai\deploy_hf'

count = 0
for root, dirs, files in os.walk(deploy_dir):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        local = os.path.join(root, f)
        rel = os.path.relpath(local, deploy_dir).replace('\\', '/')
        sz = os.path.getsize(local) / 1024 / 1024
        print(f'{rel} ({sz:.1f}MB)', flush=True)
        api.upload_file(path_or_fileobj=local, path_in_repo=rel, repo_id=repo_id, repo_type='space')
        count += 1
print(f'Done: {count} files')
