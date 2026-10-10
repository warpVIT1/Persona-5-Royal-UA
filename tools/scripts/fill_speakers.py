"""Fill strings_uk/_speakers.json from approved glossary entries (exact EN match). Existing values are kept."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "strings_uk/_speakers.json"
sp = json.loads(p.read_text(encoding="utf-8"))
gl = {r["en"]: r["uk"] for r in csv.DictReader(open(ROOT / "glossary.csv", encoding="utf-8-sig"))
      if r["status"] == "approved" and r["uk"]}
n = 0
for en in sp:
    if not sp[en] and en in gl:
        sp[en] = gl[en]
        n += 1
p.write_text(json.dumps(sp, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"filled {n} speakers, {sum(1 for v in sp.values() if v)}/{len(sp)} translated")
