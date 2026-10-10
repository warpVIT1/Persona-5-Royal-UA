"""Build/refresh glossary.csv from docs/glossary_candidates.tsv + tools/glossary/proposals.tsv.

glossary.csv columns:
  en, uk, alternatives, category, count, source, note, status
status: proposed (my suggestion) | approved (set by the project owner) | todo (no proposal yet)

Rows already marked `approved` in an existing glossary.csv are kept untouched (uk/alternatives/note),
so the owner's decisions survive a rebuild. Sorted by category priority, then frequency.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "glossary.csv"
COLS = ["en", "uk", "alternatives", "category", "count", "source", "note", "status"]
ORDER = ["character", "codename", "term", "phrase", "location", "battle", "battle_action", "element", "ailment",
         "stat", "social", "arcana", "persona", "skill", "skill_alt", "skill_card", "trait", "speaker", "npc",
         "enemy", "consumable", "key_item", "material", "accessory", "armor", "melee_weapon", "ranged_weapon",
         "outfit", "movie", "activity", "ui", "field_check", "field_action", "item", "term?"]


def main():
    cand = {}
    with open(ROOT / "docs/glossary_candidates.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            cand[r["en"]] = r

    prop = {}
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    for r in csv.DictReader(lines, delimiter="\t"):
        prop[r["en"]] = r

    old = {}
    if OUT.exists():
        with open(OUT, encoding="utf-8-sig") as f:
            old = {r["en"]: r for r in csv.DictReader(f)}

    rows = {}
    for en in list(cand) + [p for p in prop if p not in cand]:
        c, p = cand.get(en, {}), prop.get(en)
        cats = (c.get("category") or "").split(",") if c else []
        cat = p["category"] if p else (cats[0] if cats else "term")
        row = dict(en=en, uk=p["uk"] if p else "", alternatives=p["alternatives"] if p else "",
                   category=cat, count=c.get("count", ""), source=c.get("source", "proposals"),
                   note=p["note"] if p else "", status="proposed" if p else "todo")
        o = old.get(en)
        if o and o.get("status") == "approved":
            row.update(uk=o["uk"], alternatives=o["alternatives"], note=o["note"], status="approved")
        rows[en] = row
    for en, o in old.items():  # keep owner-added rows that no source knows about
        if en not in rows and o.get("status") == "approved":
            rows[en] = o

    rank = {c: i for i, c in enumerate(ORDER)}
    ordered = sorted(rows.values(), key=lambda r: (rank.get(r["category"], len(ORDER)),
                                                   -int(r["count"] or 0), r["en"]))
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(ordered)

    st = {}
    for r in ordered:
        st[r["status"]] = st.get(r["status"], 0) + 1
    print(f"glossary.csv: {len(ordered)} rows, {st}")


if __name__ == "__main__":
    main()
