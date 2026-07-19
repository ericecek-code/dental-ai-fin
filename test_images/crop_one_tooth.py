"""
Vystrihne z overlay_demo.png jeden najvysie-confidence box
(najsilnejsi Crown, conf=0.87, bbox 342.6..392.1 / 639.1..731.7)
"""
from PIL import Image
import json, pathlib

IMG = pathlib.Path(r"C:/Users/PC1/Desktop/dental-ai/test_images/overlay_demo.png")
OUT_DIR = pathlib.Path(r"C:/Users/PC1/Desktop/dental-ai/test_images")

img = Image.open(IMG).convert("RGB")
print(f"Overlay size: {img.size}")

# Najvyssi detekovany objekt = Crown, conf 0.8690, bbox [342.64, 639.12, 392.07, 731.69]
x1, y1, x2, y2 = 342.64, 639.12, 392.07, 731.69

# Pridame padding aby box nebol orezany tesne
PAD = 30
W, H = img.size
x1p = max(0, int(x1) - PAD)
y1p = max(0, int(y1) - PAD)
x2p = min(W, int(x2) + PAD)
y2p = min(H, int(y2) + PAD)

crop = img.crop((x1p, y1p, x2p, y2p))
out = OUT_DIR / "tooth_crop_top1.png"
crop.save(out, "PNG", optimize=True)

print(f"Top1 tooth crop ({x2p-x1p}x{y2p-y1p}px) ulozeny: {out}")
print(f"Velkost suboru: {out.stat().st_size/1024:.1f} KB")

# Unikatne farby v crop-e (overenie, ze crop obsahuje detekciu, nie je prazdny)
colors = crop.getcolors(maxcolors=200000) or []
print(f"Unikatnych farieb v crop-e: {len(colors)}")
