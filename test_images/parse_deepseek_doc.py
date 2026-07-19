import re
from pathlib import Path

html = Path("C:/Users/PC1/AppData/Local/Temp/deepseek_claude.html").read_text(encoding="utf-8")

print("=== Hľadané env vars v dokumentácii ===\n")
expected = [
    "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL", "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
]
for v in expected:
    for m in re.finditer(rf'{v}\s*=\s*"?([^"<\s]+)', html):
        print(f"  {m.group(0)}")
        break

print("\n=== Anthropic-API base URL (DeepSeek) ===")
for m in re.finditer(r'api\.deepseek\.com/?[\w/\-]*', html):
    print(f"  {m.group(0)}")
    break

print("\n=== Windows users shell prikaz ===")
# Match text after "Windows users:" anchor
m = re.search(r"Windows users.*?<", html, re.DOTALL)
if m:
    snippet = m.group(0)[:600]
    print(snippet)
