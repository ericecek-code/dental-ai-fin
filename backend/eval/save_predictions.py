"""
Helper: spusti /analyze nad test obrazkami a uloz kazdy vysledok ako
   eval/predictions/<image_basename>.json
   aby ich mohol scorer.py konzumovat.

Pouzitie:
    PYTHONPATH=backend python -m eval.save_predictions \
        --input test_images/ \
        --backend http://127.0.0.1:8000 \
        --output eval/predictions/
"""
import argparse
import json
from pathlib import Path
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True,
                        help="Adresar s testovacimi obrazkami (.jpg/.png)")
    parser.add_argument("--backend", "-b", default="http://127.0.0.1:8000",
                        help="URL FastAPI backendu (default 127.0.0.1:8000)")
    parser.add_argument("--conf", "-c", type=float, default=0.05,
                        help="Confidence threshold")
    parser.add_argument("--output", "-o", default="eval/predictions/",
                        help="Output adresar pre JSON subory")
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    extensions = [".jpg", ".jpeg", ".png", ".JPG", ".PNG", ".tif", ".tiff"]
    images = []
    for ext in extensions:
        images.extend(sorted(in_dir.glob(f"*{ext}")))
    print(f"Najdenych {len(images)} obrazkov")

    # Health check
    try:
        h = requests.get(f"{args.backend}/health", timeout=5)
        h.raise_for_status()
        print(f"Backend zdravy: {h.json()}")
    except Exception as e:
        print(f"[ERR] Backend neodpoveda na {args.backend}/health: {e}")
        return 1

    ok = 0
    fail = 0
    for img_path in images:
        out_path = out_dir / f"{img_path.stem}.json"
        print(f"  -> {img_path.name}", end="", flush=True)
        try:
            with img_path.open("rb") as f:
                r = requests.post(
                    f"{args.backend}/analyze/?conf={args.conf}",
                    files={"file": (img_path.name, f, "image/jpeg")},
                    timeout=120,
                )
            r.raise_for_status()
            data = r.json()
            # Uloz iba relevantne data (bez image paths)
            trimmed = {
                "image": img_path.name,
                "job_id": data.get("job_id"),
                "detection_count": data.get("detection_count"),
                "detections": data.get("detections", []),
                "by_class": data.get("by_class", {}),
                "conf_threshold": data.get("conf_threshold"),
            }
            out_path.write_text(json.dumps(trimmed, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f" OK ({trimmed['detection_count']} det.)")
            ok += 1
        except Exception as e:
            print(f" FAIL: {e}")
            fail += 1

    print()
    print(f"Vysledok: {ok} OK, {fail} FAIL")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    main()
