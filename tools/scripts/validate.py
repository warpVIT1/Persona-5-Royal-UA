"""Validate translations in strings_uk/ against strings_en/.

Translation file format (strings_uk/<same path as strings_en>.json):
  {"file": "...", "entries": [{"id": "MSG_000_0_0#0", "en": "...", "uk": "...", "note": ""}]}
An empty "uk" means "not translated yet" (English is kept on import).

Checks per translated entry:
  ERROR  unknown id (not in strings_en)
  ERROR  control codes differ from the original (multiset; [n] is excluded — line breaks are free)
  ERROR  unescaped '[' / ']' or malformed code
  ERROR  "en" field no longer matches strings_en (source changed — retranslate)
  WARN   same codes but in a different order (check [clr] pairs etc.)
  WARN   a visible line is longer than the window limit (tools/scripts/limits.py; never stricter than EN)
  ERROR  ... longer than limit + 2, or more lines than the window holds
  WARN   an approved glossary term from the EN text has no matching Ukrainian stem
  ERROR  characters outside the charset (only with --charset FILE: tsv, one char per row in column 2)
Speakers (strings_uk/_speakers.json, {"en": "uk"}) get the same code check.

Exit code 1 if any ERROR. Usage: python tools/scripts/validate.py [paths...] [--max-line N] [--charset F]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402
from limits import HARD_EXTRA, limit_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EN, UK = ROOT / "strings_en", ROOT / "strings_uk"


def syntax_errors(s):
    errs = []
    # strip escaped brackets, then every '[' must open a well-formed code
    t = s.replace("\\[", "").replace("\\]", "")
    depth = 0
    for c in t:
        depth += c == "["
        depth -= c == "]"
        if depth < 0 or depth > 1:
            return ["unbalanced brackets"]
    if depth:
        return ["unbalanced brackets"]
    for code in re.findall(r"\[([^\[\]]*)\]", t):
        if not re.fullmatch(r"[A-Za-z_]\w*(\s+(-?\d+|0x[0-9A-Fa-f]+|[A-Za-z_]\w*))*", code.strip()):
            errs.append(f"malformed code [{code}]")
    return errs


class Glossary:
    """Approved glossary terms that must keep their Ukrainian form in translations.

    Only name-like categories are checked, and terms whose lowercase form is an ordinary English
    word in the corpus are skipped ("Attack", "Death", "Star"). Ukrainian inflects, so each word of the
    Ukrainian term is reduced to a stem (drop up to 2 final letters, keep >= 3) and matched case-insensitively.
    """
    CATS = {"character", "codename", "term", "phrase", "location", "persona", "enemy"}

    def __init__(self):
        self.terms = {}
        path = ROOT / "glossary.csv"
        if not path.exists():
            self.rx = None
            return
        common = set()
        lc, cache = ROOT / "strings_en/_all.csv", ROOT / "work/common_words.json"
        if cache.exists():
            common = set(json.loads(cache.read_text(encoding="utf-8")))
        elif lc.exists():
            words = re.findall(r"\b[a-z][a-z'’]+\b", lc.read_text(encoding="utf-8-sig"))
            from collections import Counter
            common = {w for w, c in Counter(words).items() if c > 20}
            cache.parent.mkdir(exist_ok=True)
            cache.write_text(json.dumps(sorted(common)), encoding="utf-8")
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                en, uk = r["en"], r["uk"]
                if (r["status"] != "approved" or not uk or r["category"] not in self.CATS or len(en) < 3
                        or en.lower() in common or not en[0].isupper()):
                    continue
                self.terms[en] = [self._stem(w) for w in re.findall(r"[\w'ʼ’-]+", uk.lower())][:1] or [uk.lower()]
        alt = "|".join(re.escape(t) for t in sorted(self.terms, key=len, reverse=True))
        self.rx = re.compile(r"(?<![A-Za-z])(" + alt + r")(?![A-Za-z])") if alt else None

    @staticmethod
    def _stem(w):
        return w[: max(3, len(w) - 2)] if len(w) > 4 else w

    def match(self, en):
        if not self.rx:
            return []
        vis = M.visible(en.replace("[n]", " "), 0)
        return [(m.group(1), self.terms[m.group(1)]) for m in self.rx.finditer(vis)]


GLOSSARY = None


def check_pair(en, uk, max_line=None, charset=None, where="", window=None, glossary=None):
    global GLOSSARY
    if glossary is None and GLOSSARY is None:
        GLOSSARY = Glossary()
    errs, warns = [], []
    e = syntax_errors(uk)
    if e:
        return [f"{where}: {x}" for x in e], warns
    ce, cu = M.codes(en), M.codes(uk)
    if ce != cu:
        missing, extra = ce - cu, cu - ce
        errs.append(f"{where}: codes differ; missing {dict(missing) or '-'}, extra {dict(extra) or '-'}")
    else:
        oe = [t[1] for t in M.tokenize(en) if t[0] == "code" and t[2] not in M.LAYOUT_CODES]
        ou = [t[1] for t in M.tokenize(uk) if t[0] == "code" and t[2] not in M.LAYOUT_CODES]
        if oe != ou:
            warns.append(f"{where}: code order changed")
    le, lu = M.lines(en), M.lines(uk)
    # window limit for this file/kind, never stricter than what the EN original already uses
    lim_chars, lim_lines = window or (44, 3)
    limit = max_line or max(lim_chars, max((len(x) for x in le), default=0))
    max_lines = max(lim_lines, len(le))
    for i, ln in enumerate(lu):
        if len(ln) > limit + HARD_EXTRA:
            errs.append(f"{where}: line {i + 1} is {len(ln)} chars > {limit}: {ln!r}")
        elif len(ln) > limit:
            warns.append(f"{where}: line {i + 1} is {len(ln)} chars > {limit}: {ln!r}")
    if len(lu) > max_lines:
        errs.append(f"{where}: {len(lu)} lines > window {max_lines}")
    for en_term, stems in (glossary or GLOSSARY).match(en):
        if not any(s in uk.lower() for s in stems):
            warns.append(f"{where}: glossary term {en_term!r} -> expected «{stems[0]}…»")
    if charset:
        bad = sorted({c for c in M.visible(uk, 0) if c not in charset})
        if bad:
            errs.append(f"{where}: chars not in charset: {''.join(bad)!r}")
    return errs, warns


def load_charset(path):
    chars = set()
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        parts = line.split("\t")
        for p in parts:
            if len(p) == 1:
                chars.add(p)
    return chars | {" "}


def validate_file(uk_path, args, charset):
    errs, warns = [], []
    rel = uk_path.relative_to(UK)
    en_path = EN / rel
    if not en_path.exists():
        return [f"{rel}: no matching strings_en file"], []
    en_data = json.loads(en_path.read_text(encoding="utf-8"))
    en = {e["id"]: e for e in en_data["entries"]}
    for t in json.loads(uk_path.read_text(encoding="utf-8"))["entries"]:
        where = f"{rel}:{t['id']}"
        src = en.get(t["id"])
        if src is None:
            errs.append(f"{where}: unknown id")
            continue
        if t.get("en") is not None and t["en"] != src["text"]:
            errs.append(f"{where}: 'en' differs from strings_en (source changed)")
        if not t.get("uk"):
            continue
        e, w = check_pair(src["text"], t["uk"], args.max_line, charset, where,
                          window=limit_for(en_data["file"], src["kind"]))
        errs += e
        warns += w
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", help="strings_uk files/dirs (default: all)")
    ap.add_argument("--max-line", type=int)
    ap.add_argument("--charset")
    ap.add_argument("--quiet-warnings", action="store_true")
    args = ap.parse_args()
    charset = load_charset(args.charset) if args.charset else None

    files = []
    for p in [Path(x) for x in args.paths] or [UK]:
        p = p.resolve()
        files += sorted(p.rglob("*.json")) if p.is_dir() else [p]
    files = [f for f in files if not f.name.startswith("_")]

    errs, warns, done, total = [], [], 0, 0
    for f in files:
        e, w = validate_file(f, args, charset)
        errs += e
        warns += w
        entries = json.loads(f.read_text(encoding="utf-8"))["entries"]
        total += len(entries)
        done += sum(1 for x in entries if x.get("uk"))

    sp = UK / "_speakers.json"
    if sp.exists():
        for en, uk in json.loads(sp.read_text(encoding="utf-8")).items():
            if uk:
                e, w = check_pair(en, uk, 10_000, charset, f"speaker {en!r}")
                errs += e

    for x in errs:
        print("ERROR", x)
    if not args.quiet_warnings:
        for x in warns:
            print("WARN ", x)
    print(f"{len(files)} files, {done}/{total} translated, {len(errs)} errors, {len(warns)} warnings")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
