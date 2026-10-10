"""Translation workflow with translation memory (TM); safe for several translators (agents) in parallel.

  python tools/scripts/tr.py next  --agent A [--path PREFIX] [--n 80]   # next lines -> work/agents/A/batch.json
  python tools/scripts/tr.py apply --agent A work/agents/A/answers.json  # write (+TM), validate
  python tools/scripts/tr.py stats [--path PREFIX]                       # progress

TM key = (EN text, speaker): identical lines get one translation everywhere; the speaker is part of the key
because Ukrainian past tense / adjectives agree with the speaker's gender.

Parallel safety:
  * each agent has its own batch file; `next` skips keys that sit in another agent's current batch;
  * `apply` holds work/apply.lock while it rewrites files, and files are replaced atomically.

Batch items: {"k", "file", "id", "speaker", "kind", "lim": [chars, lines], "ctx": [...], "en", "gl": {en: uk}}
answers file: {"<k>": "<uk text>", ...}
"""
import argparse
import csv
import json
import os
import pickle
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402
import validate as V  # noqa: E402
from limits import limit_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EN, UK, WORK = ROOT / "strings_en", ROOT / "strings_uk", ROOT / "work"
AGENTS = WORK / "agents"


def load_json(p, tries=20):
    for t in range(tries):  # another process may be replacing the file right now
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, PermissionError, FileNotFoundError):
            if t == tries - 1:
                raise
            time.sleep(0.2)


def save_json(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    for t in range(50):
        try:
            os.replace(tmp, p)
            return
        except PermissionError:
            time.sleep(0.1)
    raise RuntimeError(f"cannot replace {p}")


class Lock:
    def __init__(self, path, stale=300):
        self.path, self.stale = path, stale

    def __enter__(self):
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale:
                        self.path.unlink()
                except FileNotFoundError:
                    pass
                time.sleep(0.3)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def uk_files(prefix=""):
    for p in sorted(UK.rglob("*.json")):
        if p.name.startswith("_"):
            continue
        rel = p.relative_to(UK).as_posix()
        if rel.startswith(prefix):
            yield p, rel


def tm_index():
    """key -> list of (uk_path, entry_index); cached in work/tm_index.pkl (EN text and ids never change;
    delete the cache after re-running export_strings / import_strings --init)."""
    cache = WORK / "tm_index.pkl"
    if not cache.exists():
        raw = defaultdict(list)
        for p, rel in uk_files():
            for i, e in enumerate(load_json(p)["entries"]):
                raw[(e["en"], e["speaker"] or "")].append((rel, i))
        WORK.mkdir(exist_ok=True)
        with open(cache, "wb") as f:
            pickle.dump(dict(raw), f)
    with open(cache, "rb") as f:
        raw = pickle.load(f)
    return defaultdict(list, {k: [(UK / r, i) for r, i in v] for k, v in raw.items()})


class Hints:
    """Approved glossary terms found in a line -> {en: uk}, as reminders for the translator."""

    def __init__(self):
        common = set()
        cw = WORK / "common_words.json"
        if cw.exists():
            common = set(json.loads(cw.read_text(encoding="utf-8")))
        self.t = {}
        with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                en = r["en"]
                if r["status"] == "approved" and r["uk"] and len(en) >= 3 and en[0].isupper() \
                        and not (" " not in en and en.lower() in common):
                    self.t[en] = r["uk"]
        alt = "|".join(re.escape(x) for x in sorted(self.t, key=len, reverse=True))
        self.rx = re.compile(r"(?<![A-Za-z])(" + alt + r")(?![A-Za-z])")

    def __call__(self, en):
        vis = M.visible(en.replace("[n]", " "), 0)
        out = {}
        for m in self.rx.finditer(vis):
            out.setdefault(m.group(1), self.t[m.group(1)])
        return dict(list(out.items())[:8])


def claimed_by_others(agent):
    keys = set()
    for b in AGENTS.glob("*/batch.json"):
        if b.parent.name == agent:
            continue
        try:
            keys |= {(x["en"], x["speaker"] or "") for x in load_json(b)}
        except Exception:
            pass
    return keys


def cmd_next(a):
    out = AGENTS / a.agent / "batch.json"
    taken = claimed_by_others(a.agent)
    hints = Hints()
    batch, seen = [], set()
    for p, rel in uk_files(a.path):
        d = load_json(p)
        if all(e["uk"] for e in d["entries"]):
            continue
        kinds = {e["id"]: e["kind"] for e in load_json(EN / rel)["entries"]}
        ents = d["entries"]
        for i, e in enumerate(ents):
            if e["uk"]:
                continue
            key = (e["en"], e["speaker"] or "")
            if key in seen or key in taken:
                continue
            seen.add(key)
            ctx = [f"{c['speaker'] or '-'}: {c['uk'] or c['en']}" for c in ents[max(0, i - 2):i]]
            kind = kinds.get(e["id"], "msg")
            batch.append(dict(k=str(len(batch)), file=rel[: -len(".msg.json")], id=e["id"], speaker=e["speaker"],
                              kind=kind, lim=list(limit_for(d["file"], kind)), ctx=ctx, en=e["en"],
                              gl=hints(e["en"])))
            if len(batch) >= a.n:
                break
        if len(batch) >= a.n:
            break
    save_json(out, batch)
    cur = None
    for b in batch:  # compact listing for the translator
        if b["file"] != cur:
            cur = b["file"]
            print(f"\n=== {cur}")
            if b["ctx"]:
                print("    ctx: " + " | ".join(b["ctx"]))
        print(f"#{b['k']} [{b['speaker'] or b['kind']}] ({b['lim'][0]}x{b['lim'][1]}) {b['en']}")
        if b["gl"]:
            print("    gl: " + "; ".join(f"{k}={v}" for k, v in b["gl"].items()))
    print(f"\n{len(batch)} lines -> {out.relative_to(ROOT).as_posix()}" if batch else "\nNOTHING LEFT under this path")


def cmd_apply(a):
    batch_path = AGENTS / a.agent / "batch.json"
    batch = {b["k"]: b for b in load_json(batch_path)}
    answers = load_json(Path(a.answers))
    errs, warns, good = [], [], {}
    for k, uk in answers.items():
        if k not in batch:
            errs.append(f"#{k}: not in this agent's batch")
            continue
        b = batch[k]
        e, w = V.check_pair(b["en"], uk, where=f"#{k} {b['file']}:{b['id']}", window=tuple(b["lim"]))
        errs += e
        warns += w
        if not e or a.force:
            good[k] = uk
    n_occ = n_files = 0
    with Lock(WORK / "apply.lock"):
        idx = tm_index()
        cache = {}
        for k, uk in good.items():
            b = batch[k]
            for p, i in idx[(b["en"], b["speaker"] or "")]:
                d = cache.setdefault(p, None) or load_json(p)
                cache[p] = d
                d["entries"][i]["uk"] = uk
                n_occ += 1
        for p, d in cache.items():
            save_json(p, d)
        n_files = len(cache)
    # lines that failed stay in the batch so the agent can fix and re-apply them; done ones are released
    left = [b for k, b in batch.items() if k not in good]
    save_json(batch_path, left)
    for x in errs:
        print("ERROR", x)
    for x in warns:
        print("WARN ", x)
    print(f"applied {len(good)}/{len(answers)} lines to {n_occ} occurrences in {n_files} files; "
          f"{len(errs)} errors, {len(warns)} warnings; {len(left)} lines still pending in batch")
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
    n.add_argument("--agent", default="main")
    n.add_argument("--path", default="")
    n.add_argument("--n", type=int, default=80)
    ap_ = sub.add_parser("apply")
    ap_.add_argument("answers")
    ap_.add_argument("--agent", default="main")
    ap_.add_argument("--force", action="store_true", help="write lines even if they have errors")
    s = sub.add_parser("stats")
    s.add_argument("--path", default="")
    a = ap.parse_args()
    return {"next": cmd_next, "apply": cmd_apply, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main() or 0)
