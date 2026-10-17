"""Switch Japanese names from Kovalenko transliteration to the practical one with ґ.

  Kovalenko (old):  Рюдзі, Сібуя, Акеті, Кітагава, Содзіро, Канадзава
  practical (new):  Рюджі, Шібуя, Акечі, Кітаґава, Соджіро, Каназава

Japanese names are detected automatically: an approved glossary word is renamed only when its current
Ukrainian form equals the Kovalenko transliteration of the EN (Hepburn) word, so Вельзевул, Джокер etc.
are never touched. The resulting word map is applied to glossary.csv, tools/glossary/proposals*.tsv,
strings_uk (incl. _speakers.json) and docs, with Ukrainian case endings kept.

  python tools/scripts/rename_names.py            # dry run: print the map and counts
  python tools/scripts/rename_names.py --apply
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOW = "aiueo"
CYR_VOW = "аеєиіїоуюяАЕЄИІЇОУЮЯ"

BASE = {"a": "а", "i": "і", "u": "у", "e": "е", "o": "о"}
# consonant -> (Cyrillic consonant, palatal form used before y-vowels)
CONS = {"k": "к", "s": "с", "t": "т", "n": "н", "h": "х", "m": "м", "r": "р", "b": "б", "p": "п",
        "d": "д", "w": "в"}


def syllables(word):
    """Hepburn word -> list of (consonant, vowel) with special consonants shi/chi/tsu/ji/fu."""
    w, out, i = word.lower(), [], 0
    while i < len(w):
        for cons in ("tch", "sh", "ch", "ts", "j", "f", "g", "z", "k", "s", "t", "n", "h", "m", "r", "b",
                     "p", "d", "w", "y", ""):
            if not w.startswith(cons, i):
                continue
            j = i + len(cons)
            if cons == "tch":
                out.append(("sokuon", "t"))
                cons = "ch"
            if cons == "n" and (j >= len(w) or w[j] not in VOW + "y"):
                out.append(("n", ""))
                i = j
                break
            if cons and cons != "y" and j < len(w) and w[j] == cons[0] and cons[0] not in VOW + "n":
                out.append(("sokuon", cons[0]))   # doubled consonant
                i = j - len(cons) + 1 if len(cons) > 1 else j
                break
            y = ""
            if cons not in ("y", "") and j < len(w) and w[j] == "y":
                y, j = "y", j + 1
            if j < len(w) and w[j] in VOW:
                out.append((cons + y, w[j]))
                i = j + 1
                break
            if cons == "m" and j < len(w) and w[j] in "bp":
                out.append(("n", ""))
                i = j
                break
            return None   # not a Japanese syllable sequence
        else:
            return None
    return out


def translit(word, practical):
    syl = syllables(word)
    if not syl:
        return None
    res = []
    for k, (c, v) in enumerate(syl):
        if c == "sokuon":
            nxt = syl[k + 1][0] if k + 1 < len(syl) else ""
            res.append(translit_cons(nxt, "a", practical)[0][:1] if nxt else "")
            continue
        if c == "n" and not v:
            res.append("н")
            continue
        s = translit_cons(c, v, practical)
        if s is None:
            return None
        res.append(s)
    out = "".join(res)
    # і after a vowel -> ї
    out = re.sub(r"(?<=[аеіоуюяї])і", "ї", out)
    return out[:1].upper() + out[1:] if word[:1].isupper() else out


def translit_cons(c, v, practical):
    soft = {"a": "я", "u": "ю", "o": "ьо", "e": "е", "i": "і"}
    if c == "":
        return BASE[v]
    if c == "y":
        return {"a": "я", "u": "ю", "o": "йо", "e": "е", "i": "і"}[v]
    if c in ("sh", "ch", "j"):
        if practical:
            return {"sh": "ш", "ch": "ч", "j": "дж"}[c] + BASE[v]
        base = {"sh": "с", "ch": "т", "j": "дз"}[c]
        return base + soft[v]
    if c == "ts":
        return "ц" + BASE[v]
    if c == "f":
        return "ф" + BASE[v]
    if c in ("g", "gy"):
        g = "ґ" if practical else "г"
        return g + (BASE[v] if c == "g" else soft[v])
    if c in ("z", "zy"):
        z = "з" if practical else "дз"
        return z + (BASE[v] if c == "z" else soft[v])
    base = c[0]
    if base not in CONS:
        return None
    if len(c) == 2:   # palatal: kya kyu kyo
        return CONS[base] + soft[v]
    if base == "w":
        return {"a": "ва", "o": "о"}.get(v, "в" + BASE[v])
    return CONS[base] + BASE[v]


# not Japanese, keep the established Ukrainian form
KEEP = {"Омега", "Гаруда", "Нага", "нага", "Мегідо", "мегідо"}


def glossary_words():
    """Old Ukrainian word -> (new word, set of EN words it comes from), for Japanese names in the glossary."""
    m = {}
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["status"] != "approved" or not r["uk"]:
                continue
            for w in re.findall(r"[A-Za-z]+", r["en"]):
                if len(w) < 3:
                    continue
                kov, new = translit(w, False), translit(w, True)
                if not kov or kov == new:
                    continue
                for u in re.findall(r"[\w'ʼ]+", r["uk"]):
                    if u.lower() == kov.lower() and u not in KEEP:
                        m.setdefault(u, (new if u[:1].isupper() else new.lower(), set()))[1].add(w.lower())
    return m


def make_rx(m):
    # whole word, optionally followed by a Ukrainian case ending; the stem is the word without its final vowel
    pats = {}
    for old, (new, _) in m.items():
        if old[-1] in CYR_VOW and new[-1] == old[-1] and len(old) >= 5:
            pats[old[:-1]] = (new[:-1], r"[аеєиіїоуюяь]\w{0,2}")
        else:
            pats[old] = (new, r"(?:ові|ом|у|а|і|ою|ей|ям)?")
    alt = "|".join(re.escape(k) for k in sorted(pats, key=len, reverse=True))
    rx = re.compile(r"(?<![\w'ʼ])(" + alt + r")(?=\w{0,3}(?!\w))")
    return rx, pats


def apply_text(s, rx, pats, m, en):
    """Replace names in s, but only those whose EN source word occurs in en (the original text)."""
    en = en.lower()
    allowed = {k for k, (_, ws) in m.items() if any(re.search(r"(?<![a-z])" + w, en) for w in ws)}
    allowed = {k[:-1] if k[:-1] in pats and k not in pats else k for k in allowed}
    if not allowed:
        return s, 0
    n = 0

    def sub(mo):
        nonlocal n
        stem = mo.group(1)
        if stem not in allowed:
            return stem
        new, end_re = pats[stem]
        tail = re.match(r"\w{0,3}", s[mo.end():]).group()
        if not re.fullmatch(end_re, tail):
            return stem
        n += 1
        return new
    return rx.sub(sub, s), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    m = glossary_words()
    for k in sorted(m):
        print(f"{k} -> {m[k][0]}  ({'/'.join(sorted(m[k][1]))})")
    print(len(m), "words")
    rx, pats = make_rx(m)

    files = [ROOT / "glossary.csv", ROOT / "docs/translation_guide.md", ROOT / "docs/glossary_decisions.md",
             ROOT / "docs/agent_brief.md"] + sorted((ROOT / "tools/glossary").glob("*.tsv")) \
        + sorted((ROOT / "strings_uk").rglob("*.json"))
    total, changed = 0, 0
    for f in files:
        if not f.exists():
            continue
        if f.suffix == ".json":
            d = json.loads(f.read_text(encoding="utf-8"))
            k = 0
            if f.name == "_speakers.json":
                for en in d:
                    d[en], c = apply_text(d[en], rx, pats, m, en)
                    k += c
            else:
                for e in d["entries"]:
                    if e.get("uk"):
                        e["uk"], c = apply_text(e["uk"], rx, pats, m, e.get("en") or "")
                        k += c
            if k and a.apply:
                f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        else:
            t = f.read_text(encoding="utf-8-sig")
            k, out = 0, []
            for line in t.splitlines(keepends=True):   # glossary rows / doc lines carry their EN word
                line, c = apply_text(line, rx, pats, m, line)
                out.append(line)
                k += c
            t2 = "".join(out)
            if k and a.apply:
                f.write_text(t2, encoding="utf-8-sig" if f.suffix == ".csv" else "utf-8", newline="")
        total += k
        changed += bool(k)
    print(f"{'replaced' if a.apply else 'would replace'} {total} occurrences in {changed} files")


if __name__ == "__main__":
    main()


# EN words that look like romaji but are not Japanese names (or have an established Ukrainian form)
NOT_JP = {"She", "Joe", "Chi", "Ago", "Mega", "Megaton", "Goetia", "Murugan", "Zen", "Yakuza", "Shu", "Gya"}
# common nouns written in lowercase in Ukrainian
LOWER_OK = {"Shogi", "Shinkansen", "Nihonga", "Monja", "Mochi", "Dango", "Osechi", "Shochu", "Onmyoji"}


def entry_pass(apply=False):
    """Second pass for names missing from the glossary: in each entry, capitalized EN words whose
    Kovalenko form occurs in the Ukrainian text (with a case ending) are switched to the practical form."""
    seen, total = {}, 0
    for f in sorted((ROOT / "strings_uk").rglob("*.json")):
        if f.name.startswith("_"):
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        k = 0
        for e in d["entries"]:
            uk = e.get("uk")
            if not uk:
                continue
            for w in set(re.findall(r"[A-Z][a-z]{2,}", e.get("en") or "")):
                kov, new = translit(w, False), translit(w, True)
                if not kov or kov == new or kov in KEEP or w in NOT_JP:
                    continue
                stem, nstem = (kov[:-1], new[:-1]) if kov[-1] in CYR_VOW and new[-1] == kov[-1] and len(kov) >= 5 \
                    else (kov, new)
                rx = re.compile(r"(?<![\w'ʼ])" + re.escape(stem) + r"(?=\w{0,3}(?!\w))", re.I if w in LOWER_OK else 0)
                for mo in rx.finditer(uk):
                    seen.setdefault((mo.group(), nstem if mo.group()[0].isupper() else nstem.lower()), w)
                uk, c = rx.subn(lambda mo: nstem if mo.group()[0].isupper() else nstem.lower(), uk)
                k += c
            e["uk"] = uk
        if k and apply:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        total += k
    return seen, total
