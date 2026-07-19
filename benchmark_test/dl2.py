
import requests, os
test_dir = r"C:\Users\PC1\Desktop\dental-ai\benchmark_test"
base = "https://huggingface.co/datasets/liodon-ai/dental-panoramic-xray-yolo/resolve/main"
names = ["oral_005609","oral_005610","oral_005611","oral_005612","oral_005613","oral_005614","oral_005616"]
for name in names:
    r = requests.get(f"{base}/images/train/{name}.jpg", timeout=30)
    if r.status_code == 200:
        open(os.path.join(test_dir, f"{name}.jpg"), "wb").write(r.content)
    lr = requests.get(f"{base}/labels/train/{name}.txt", timeout=15)
    if lr.status_code == 200:
        open(os.path.join(test_dir, f"{name}.txt"), "w").write(lr.text)
    print(f"{name}: img={r.status_code} lbl={lr.status_code}")

# Caries dataset
base2 = "https://huggingface.co/datasets/reza362/dental-xray-caries/resolve/main"
for i in range(5):
    r = requests.get(f"{base2}/train/caries_{i:03d}.jpg", timeout=30)
    if r.status_code == 200:
        open(os.path.join(test_dir, f"caries_{i:03d}.jpg"), "wb").write(r.content)
        print(f"caries_{i:03d}: {r.status_code} ({len(r.content)//1024}KB)")
print("DONE")
