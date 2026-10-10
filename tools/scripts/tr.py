"""Translation workflow with translation memory (TM).

  python tools/scripts/tr.py next  [--path PREFIX] [--n 80]   # next untranslated unique lines -> work/batch.json
  python tools/scripts/tr.py apply work/answers.json           # write translations (+ TM propagation), validate
  python tools/scripts/tr.py stats [--path PREFIX]             # progress

TM key = (EN text, speaker): identical lines get one translation everywhere, but the speaker is part of
the key because Ukrainian past tense / adjectives agree with the speaker's gender.

work/batch.json items: {"k", "file", "id", "speaker", "kind", "lim": [chars, lines], "ctx": [...], "en"}
answers file: {"<k>": "<uk text>", ...}  — k from the batch. Lines are written to every TM occurrence.
"""
import argparse
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402
import validate as V  # noqa: E402
from limits import limit_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EN, UK, WORK = ROOT / "strings_en", ROOT / "strings_uk", ROOT / "work"


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def save_json(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def uk_files(prefix=""):
    for p in sorted(UK.rglob("*.json")):
        if p.name.startswith("_"):
            continue
        rel = p.relative_to(UK).as_posix()
        if rel.startswith(prefix):
            yield p, rel


def tm_index():
    """key -> list of (uk_path, entry_index). Cached in work/tm_index.pkl (EN text and ids never change;
    delete the cache after re-running export_strings / import_strings --init)."""
    cache = WORK / "tm_index.pkl"
    if cache.exists():
        with open(cache, "rb") as f:
            raw = pickle.load(f)
        return defaultdict(list, {k: [(UK / r, i) for r, i in v] for k, v in raw.items()})
    raw = defaultdict(list)
    for p, rel in uk_files():
        for i, e in enumerate(load_json(p)["entries"]):
            raw[(e["en"], e["speaker"] or "")].append((rel, i))
    WORK.mkdir(exist_ok=True)
    with open(cache, "wb") as f:
        pickle.dump(dict(raw), f)
    return defaultdict(list, {k: [(UK / r, i) for r, i in v] for k, v in raw.items()})


def cmd_next(a):
    batch, seen = [], set()
    for p, rel in uk_files(a.path):
        d = load_json(p)
        en_data = load_json(EN / rel)
        kinds = {e["id"]: e["kind"] for e in en_data["entries"]}
        ents = d["entries"]
        for i, e in enumerate(ents):
            if e["uk"]:
                continue
            key = (e["en"], e["speaker"] or "")
            if key in seen:
                continue
            seen.add(key)
            ctx = [f"{c['speaker'] or '-'}: {c['uk'] or c['en']}" for c in ents[max(0, i - 2):i]]
            kind = kinds.get(e["id"], "msg")
            batch.append(dict(k=str(len(batch)), file=rel[: -len(".msg.json")], id=e["id"], speaker=e["speaker"],
                              kind=kind, lim=list(limit_for(d["file"], kind)), ctx=ctx, en=e["en"]))
            if len(batch) >= a.n:
                break
        if len(batch) >= a.n:
            break
    save_json(WORK / "batch.json", batch)
    cur = None
    for b in batch:  # compact listing for the translator
        if b["file"] != cur:
            cur = b["file"]
            print(f"\n=== {cur}")
        print(f"#{b['k']} [{b['speaker'] or b['kind']}] ({b['lim'][0]}x{b['lim'][1]}) {b['en']}")
    print(f"\n{len(batch)} lines -> work/batch.json")


def cmd_apply(a):
    batch = {b["k"]: b for b in load_json(WORK / "batch.json")}
    answers = load_json(Path(a.answers))
    idx = tm_index()
    cache, errs, warns, n_occ = {}, [], [], 0
    for k, uk in answers.items():
        b = batch[k]
        key = (b["en"], b["speaker"] or "")
        e, w = V.check_pair(b["en"], uk, where=f"#{k} {b['file']}:{b['id']}", window=tuple(b["lim"]))
        errs += e
        warns += w
        if e and not a.force:
            continue
        for p, i in idx[key]:
            d = cache.setdefault(p, load_json(p))
            d["entries"][i]["uk"] = uk
            n_occ += 1
    for p, d in cache.items():
        save_json(p, d)
    for x in errs:
        print("ERROR", x)
    for x in warns:
        print("WARN ", x)
    print(f"applied {len(answers) - (0 if a.force else len({x.split()[0] for x in errs}))} lines "
          f"to {n_occ} occurrences in {len(cache)} files; {len(errs)} errors, {len(warns)} warnings")
    return 1 if errs else 0


def cmd_stats(a):
    tot = done = 0
    for p, _ in uk_files(a.path):
        for e in load_json(p)["entries"]:
            tot += 1
            done += bool(e["uk"])
    print(f"{a.path or 'all'}: {done}/{tot} pages translated ({100 * done / max(tot, 1):.2f}%)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("next")
    n.add_argument("--path", default="")
    n.add_argument("--n", type=int, default=80)
    ap_ = sub.add_parser("apply")
    ap_.add_argument("answers")
    ap_.add_argument("--force", action="store_true", help="write lines even if they have errors")
    s = sub.add_parser("stats")
    s.add_argument("--path", default="")
    a = ap.parse_args()
    return {"next": cmd_next, "apply": cmd_apply, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main() or 0)
