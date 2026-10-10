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
  WARN   a visible line is longer than --max-line (default: the original's longest line, min 10)
  WARN   more lines than the original page
  ERROR  characters outside the charset (only with --charset FILE: tsv, one char per row in column 2)
Speakers (strings_uk/_speakers.json, {"en": "uk"}) get the same code check.

Exit code 1 if any ERROR. Usage: python tools/scripts/validate.py [paths...] [--max-line N] [--charset F]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402

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


def check_pair(en, uk, max_line=None, charset=None, where=""):
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
    limit = max_line or max(10, max((len(x) for x in le), default=0))
    for i, ln in enumerate(lu):
        if len(ln) > limit:
            warns.append(f"{where}: line {i + 1} is {len(ln)} chars > {limit}: {ln!r}")
    if len(lu) > len(le):
        warns.append(f"{where}: {len(lu)} lines > original {len(le)}")
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
    en = {e["id"]: e for e in json.loads(en_path.read_text(encoding="utf-8"))["entries"]}
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
        e, w = check_pair(src["text"], t["uk"], args.max_line, charset, where)
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
