import torch
_orig = torch.load

def _patched(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _orig(*args, **kwargs)

torch.load = _patched
