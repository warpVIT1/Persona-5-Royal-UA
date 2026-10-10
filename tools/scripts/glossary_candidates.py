"""Collect glossary candidates from game tables and the dialogue corpus.

Sources:
  NAME.TBL          — arcana, skills, enemies, Personas, items, equipment, party names
  string FTDs       — FIELD/FTD/*NAME.FTD (places, NPCs, check points, actions, movies)
  data FTDs         — FLDWHOLEMAPTABLE / FLDLMAPSTATION / FLDSAVEDATAPLACE (ASCII heuristics, names only)
  speakers          — strings_en/_speakers.json
  corpus mining     — capitalised multi-word phrases and mid-sentence capitalised words in dialogue

Output: docs/glossary_candidates.tsv  (en, category, source, count)
`count` = occurrences in translatable dialogue pages (strings_en/_all.csv), case-sensitive, whole words.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ftd  # noqa: E402
import msgfmt as M  # noqa: E402
import nametbl  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / "extracted/EN"
JUNK = re.compile(r"^(BLANK|RESERVE|Unused|Not Used|NULL|TEMP|Dummy|Test|DUMMY|[0-9A-F]{1,2}|0x\w+|0+|"
                  r"(DNG)?CHK\d+|.*用.*|Unused Item|Ultimate Vessel)\b|[぀-ヿ一-鿿]")

FTD_CATEGORY = {
    "FLDPLACENAME.FTD": "location", "FLDNPCNAME.FTD": "npc", "FLDCHECKNAME.FTD": "field_check",
    "FLDDNGCHECKNAME.FTD": "field_check", "FLDKFECHECKNAME.FTD": "field_check", "FLDACTIONNAME.FTD": "field_action",
    "FLDSCRIPTNAME.FTD": "movie", "FLDARCANANAME.FTD": "item", "FLDPARAMUPFUNCNAME.FTD": "activity",
    "FLDASSISTLISTNAME_SOCIAL.FTD": "ui", "FLDASSISTLISTNAME_TRAIN.FTD": "ui",
}
DATA_FTD = {"FIELD/PANEL/FLDWHOLEMAPTABLE.FTD": "location", "FIELD/PANEL/LMAP/FLDLMAPSTATION.FTD": "location",
            "FIELD/FTD/FLDSAVEDATAPLACE.FTD": "location"}


def table_terms():
    out = []  # (en, category, source)
    for i, names in enumerate(nametbl.read(EN / "BATTLE/TABLE/NAME.TBL")):
        cat = nametbl.SECTIONS[i]
        for n in names:
            n = n.strip()
            if n and not JUNK.search(n):
                out.append((n, cat, "NAME.TBL"))
    for f in sorted((EN / "FIELD/FTD").glob("*.FTD")):
        r = ftd.read(f.read_bytes())
        if r:
            for n in r:
                n = n.strip()
                if n and not JUNK.search(n):
                    out.append((n, FTD_CATEGORY.get(f.name, "field"), f.name))
    for rel, cat in DATA_FTD.items():
        d = (EN / rel).read_bytes()
        for m in re.finditer(rb"(?<=\0)[A-Z][A-Za-z0-9 '\-.&]{2,40}(?=\0)", d):
            s = m.group().decode()
            # names only: short, title-cased words (function words aside), no sentence fragments,
            # no length-byte artefacts glued to the front ("HChurch", "ERide Train", "CNULL")
            words = s.split()
            small = {"of", "the", "to", "and", "on", "a", "in", "with", "for", "is", "at"}
            if (len(words) <= 5 and not s.endswith(".") and not JUNK.search(s)
                    and not re.match(r"^[A-Z][A-Z][a-z]|^[A-Z]NULL$|^FTD0$", s)
                    and all(w[0].isupper() or w in small or not w[0].isalpha() for w in words)
                    and words[-1] not in small):
                out.append((s, cat, Path(rel).name))
    return out


def corpus():
    with open(ROOT / "strings_en/_all.csv", encoding="utf-8-sig") as f:
        # [n] separates words in English text, so it becomes a space before codes are stripped
        return [M.visible(r["text"].replace("[n]", " "), 0) for r in csv.DictReader(f)]


def mine(texts):
    """Capitalised phrases (2+ words) and proper-noun-like single words."""
    phrases, mid_caps, lower = Counter(), Counter(), Counter()
    ph = re.compile(r"\b[A-Z][a-z'’]+(?:(?: of the| of| the| de| no| and)? [A-Z][a-z'’]+)+\b")
    for t in texts:
        for m in ph.finditer(t):
            phrases[m.group()] += 1
        for m in re.finditer(r"(?<=[a-z,;] )[A-Z][a-z'’]{2,}\b", t):  # capitalised mid-sentence
            mid_caps[m.group()] += 1
        for w in re.findall(r"\b[a-z][a-z'’]{2,}\b", t):
            lower[w] += 1
    out = [(p, "term?", "corpus", c) for p, c in phrases.items() if c >= 15]
    out += [(w, "term?", "corpus", c) for w, c in mid_caps.items()
            if c >= 25 and lower[w.lower()] < c * 0.2]
    return out


def count_terms(terms, texts):
    """Single pass: longest term wins at each position (so 'Velvet Room' is not also counted as 'Velvet')."""
    big = "\n".join(texts)
    alt = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    cnt = Counter(m.group(1) for m in re.finditer(r"(?<![A-Za-z])(" + alt + r")(?![A-Za-z])", big))
    return {t: cnt.get(t, 0) for t in terms}


def main():
    rows = table_terms()
    texts = corpus()
    mined = mine(texts)
    speakers = json.loads((ROOT / "strings_en/_speakers.json").read_text(encoding="utf-8"))

    cats, srcs = defaultdict(list), defaultdict(list)
    for en, cat, src in rows:
        if cat not in cats[en]:
            cats[en].append(cat)
        if src not in srcs[en]:
            srcs[en].append(src)
    for sp, c in speakers.items():
        if c >= 3 and not JUNK.search(sp) and "[" not in sp and not re.match(r"^[ef]\d{3}_", sp):
            if "speaker" not in cats[sp]:
                cats[sp].append("speaker")
            srcs[sp].append(f"speaker×{c}")
    pre = {}
    for en, cat, src, c in mined:
        if en not in cats:
            cats[en].append(cat)
            srcs[en].append(src)
            pre[en] = c

    # drop blanks, contractions and ordinary words that only look like terms
    lower = Counter(w for t in texts for w in re.findall(r"\b[a-z][a-z'’]*\b", t))
    table_cats = set(nametbl.SECTIONS) | {"location", "npc", "movie"}
    for en in list(cats):
        single = " " not in en
        if (not en.strip() or re.search(r"['’](m|ll|ve|d|re|s|t)$", en)
                or (single and en[0].islower())
                or (single and not table_cats & set(cats[en]) and lower[en.lower()] > 50)):
            del cats[en]

    # hand-written proposals are candidates too (so they get frequencies)
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        for r in csv.DictReader([l for l in f if l.strip() and not l.startswith("#")], delimiter="\t"):
            if r["en"] not in cats:
                cats[r["en"]].append(r["category"])
                srcs[r["en"]].append("proposals")
    for en in list(cats):  # numeric ids / punctuation-only entries
        if not re.search(r"[A-Za-z]{2}", en):
            del cats[en]

    counts = count_terms(list(cats), texts)
    # longest-match counting hides "Treasure" inside "The Treasure": add the containing terms back
    base = {o: c for o, c in counts.items() if c}
    for t in cats:
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(t) + r"(?![A-Za-z])")
        counts[t] += sum(c for o, c in base.items() if o != t and t in o and pat.search(o))
    out = ROOT / "docs/glossary_candidates.tsv"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tcategory\tsource\tcount\n")
        for en in sorted(cats, key=lambda k: (-counts[k], k)):
            f.write(f"{en}\t{','.join(cats[en])}\t{','.join(srcs[en])}\t{counts[en]}\n")
    print(f"{len(cats)} candidates -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
