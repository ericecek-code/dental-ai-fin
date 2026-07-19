
import requests, os, sys
test_dir = r"C:\Users\PC1\Desktop\dental-ai\benchmark_test"
os.makedirs(test_dir, exist_ok=True)
base = "https://huggingface.co/datasets/liodon-ai/dental-panoramic-xray-yolo/resolve/main"
names = ["oral_005606", "oral_005607", "oral_005608"]
for name in names:
    try:
        r = requests.get(f"{base}/images/train/{name}.jpg", timeout=30)
        print(f"Image {name}: {r.status_code}, {len(r.content)} bytes")
        if r.status_code == 200:
            open(os.path.join(test_dir, f"{name}.jpg"), "wb").write(r.content)
        lr = requests.get(f"{base}/labels/train/{name}.txt", timeout=15)
        print(f"Label {name}: {lr.status_code}, {lr.text[:100]}")
        if lr.status_code == 200:
            open(os.path.join(test_dir, f"{name}.txt"), "w").write(lr.text)
    except Exception as e:
        print(f"Error {name}: {e}")
print("DONE")
