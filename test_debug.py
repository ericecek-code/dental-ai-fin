"""Debug: trace import chain to find Flask reference."""
import sys
import traceback
try:
    from app.ml.detector import Detector
    print("[OK] Detector imported")
except Exception as e:
    traceback.print_exc()
    print(f"\n--- Looking for 'flask' in sys.modules ---")
    for k in sorted(sys.modules):
        if 'flask' in k.lower():
            print(f"  {k}")
