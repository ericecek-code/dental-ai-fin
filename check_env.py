import os
print("Current dir:", os.getcwd())
print("Python:", os.sys.executable)
try:
    import huggingface_hub
    print("huggingface_hub found")
except ImportError:
    print("huggingface_hub NOT found")
