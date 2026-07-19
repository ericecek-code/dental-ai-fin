try:
    import pypdf
    print("pypdf OK")
except ImportError:
    pass

try:
    import PyPDF2
    print("PyPDF2 OK")
except ImportError:
    pass

import subprocess
r = subprocess.run(['python', '-m', 'pip', 'install', 'pypdf', '-q'], capture_output=True, text=True, timeout=30)
print("install:", r.returncode)

from pypdf import PdfReader
r = PdfReader('test_report_sk.pdf')
print(f"Pages: {len(r.pages)}")
for i, page in enumerate(r.pages):
    print(f"=== Strana {i+1} ===")
    txt = page.extract_text()
    print(txt[:2000])
    print("...")
