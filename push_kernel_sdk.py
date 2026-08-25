import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\PC1\.kaggle\credentials.json', 'r', encoding='utf-8') as f:
    creds = json.load(f)
with open(r'C:\Users\PC1\Desktop\dental-ai\kernel-metadata.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)
with open(r'C:\Users\PC1\Desktop\dental-ai\kaggle_training.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

nb_str = json.dumps(nb, indent=1, ensure_ascii=False)

from kagglesdk import KaggleClient
client = KaggleClient(username=creds['username'], api_token=creds['access_token'])
api = client.kernels.kernels_api_client

from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest
req = ApiSaveKernelRequest()
req.slug = meta['id']
req.new_title = meta['title']
req.language = meta['language']
req.kernel_type = meta['kernel_type']
req.is_private = meta['is_private']
req.enable_gpu = meta['enable_gpu']
req.enable_internet = meta['enable_internet']
req.dataset_data_sources = meta.get('dataset_sources', [])
req.kernel_data_sources = meta.get('kernel_sources', [])
req.competition_data_sources = meta.get('competition_sources', [])
req.text = nb_str

try:
    result = api.save_kernel(req)
    print('Response:', result.to_dict() if hasattr(result, 'to_dict') else result)
except Exception as e:
    print('Error:', type(e).__name__, e)
    if hasattr(e, 'response'):
        print('Response:', e.response.text[:800] if hasattr(e.response, 'text') else e.response)
