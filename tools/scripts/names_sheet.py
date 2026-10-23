"""Name sheet for review: glossary names -> docs/glossary_names.csv, and edits back into glossary.csv.

  python tools/scripts/names_sheet.py export   # write docs/glossary_names.csv (open in Excel / LibreOffice)
  python tools/scripts/names_sheet.py import   # copy changed "uk" values back into glossary.csv

Only the "uk" column is read back; rows are matched by (category, en).
After import, run the usual pipeline (rename/apply) yourself — this script only edits glossary.csv.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = ROOT / "glossary.csv"
SHEET = ROOT / "docs/glossary_names.csv"
# name-like categories, in reading order
CATS = ["character", "codename", "speaker", "npc", "persona", "enemy", "location"]
TITLES = {"character": "Персонажі", "codename": "Кодові імена", "speaker": "Імена мовців",
          "npc": "NPC", "persona": "Персони", "enemy": "Вороги", "location": "Місця"}


def read_glossary():
    with open(GLOSSARY, encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def export():
    _, rows = read_glossary()
    out = []
    for cat in CATS:
        part = [r for r in rows if r["category"] == cat]
        part.sort(key=lambda r: -int(r["count"] or 0))
        out += [(TITLES[cat], cat, r) for r in part]
    SHEET.parent.mkdir(exist_ok=True)
    with open(SHEET, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Розділ", "category", "en", "uk", "count", "status", "note"])
        for title, cat, r in out:
            w.writerow([title, cat, r["en"], r["uk"], r["count"], r["status"], r["note"]])
    print(f"{len(out)} names -> {SHEET.relative_to(ROOT)}")


def import_():
    fields, rows = read_glossary()
    with open(SHEET, encoding="utf-8-sig", newline="") as f:
        edits = {(r["category"], r["en"]): r["uk"].strip() for r in csv.DictReader(f, delimiter=";")}
    changed = 0
    for r in rows:
        new = edits.get((r["category"], r["en"]))
        if new is not None and new != r["uk"]:
            print(f"{r['en']}: {r['uk']} -> {new}")
            r["uk"] = new
            changed += 1
    with open(GLOSSARY, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    print(f"{changed} names changed in glossary.csv")


if __name__ == "__main__":
    {"export": export, "import": import_}[sys.argv[1] if len(sys.argv) > 1 else "export"]()
