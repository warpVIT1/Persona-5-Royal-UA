"""Decompile every BMD/BF used by the game into source_en/.

Targets come from docs/inventory.tsv (rows with magic bmd/bf, not overridden by EN).
Nested files ("A.PAK::b.bmd") are carved out of their containers; the container
becomes a directory in the output: source_en/EN/INIT/DATMSG.PAK/datWeaponHelp.bmd.msg

Outputs per input X:
  BMD -> X.msg
  BF  -> X.flow, X.msg, X.msg.h  (flow imports "X.msg")

Usage: python tools/scripts/decompile_all.py [--limit N] [--match REGEX] [--jobs N]
Failures are written to docs/decompile_report.md.
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from inventory import parse_pak  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / "tools/bin/AtlusScriptCompiler/AtlusScriptCompiler.exe"
OUT = ROOT / "source_en"
LIBRARY, ENCODING = "P5R", "P5R_EFIGS"


def load_targets():
    with open(ROOT / "docs/inventory.tsv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return [r for r in rows if r["magic"] in ("bmd", "bf") and r["overridden"] != "yes"]


def read_bytes(cpk, vpath):
    parts = vpath.split("::")
    data = (ROOT / "extracted" / cpk / parts[0]).read_bytes()
    for name in parts[1:]:
        entries = {n.upper(): (o, s) for n, o, s in parse_pak(data) or []}
        off, size = entries[name.upper()]
        data = data[off : off + size]
    return data


def decompile(row):
    cpk, vpath, kind = row["cpk"], row["path"], row["magic"]
    rel = vpath.replace("::", "/")
    name = Path(rel).name
    dest = OUT / cpk / Path(rel).parent
    with tempfile.TemporaryDirectory(prefix="p5dec_") as tmp:
        tmp = Path(tmp)
        (tmp / name).write_bytes(read_bytes(cpk, vpath))
        out_name = f"{name}.flow" if kind == "bf" else f"{name}.msg"
        args = [str(COMPILER), name, "-Decompile", "-Library", LIBRARY, "-Encoding", ENCODING, "-Out", out_name]
        if kind == "bmd":
            args[3:3] = ["-InFormat", "MessageScriptBinary"]
        else:
            args[3:3] = ["-InFormat", "FlowScriptBinary"]
        p = subprocess.run(args, cwd=tmp, capture_output=True)
        produced = [f for f in tmp.iterdir() if f.name != name and not f.name.endswith(".log")]
        log = (tmp / "AtlusScriptCompiler.log")
        log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        ok = (tmp / out_name).exists() and (tmp / out_name).stat().st_size > 0
        if ok:
            dest.mkdir(parents=True, exist_ok=True)
            for f in produced:
                shutil.move(str(f), dest / f.name)
        errors = [l for l in log_text.splitlines() if re.search(r"\b(Error|Fatal)\b", l)]
        return dict(cpk=cpk, path=vpath, kind=kind, ok=ok, code=p.returncode, errors=errors[:5])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--match")
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()

    targets = load_targets()
    if a.match:
        targets = [t for t in targets if re.search(a.match, t["path"], re.I)]
    if a.limit:
        targets = targets[: a.limit]
    print(f"{len(targets)} files", flush=True)

    results = []
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(decompile, t) for t in targets]
        for i, f in enumerate(as_completed(futs), 1):
            results.append(f.result())
            if i % 250 == 0:
                print(f"{i}/{len(targets)}", flush=True)

    bad = [r for r in results if not r["ok"]]
    warn = [r for r in results if r["ok"] and r["errors"]]
    print(f"ok {len(results) - len(bad)}, failed {len(bad)}, ok-with-errors-in-log {len(warn)}")
    if not a.limit and not a.match:
        L = ["# Отчёт о декомпиляции", "", f"Всего: {len(results)}, успешно: {len(results) - len(bad)}, "
             f"неудачно: {len(bad)}, успешно, но с ошибками в логе: {len(warn)}.", ""]
        for title, lst in (("Неудачно", bad), ("Ошибки в логе", warn)):
            if lst:
                L += [f"## {title}", ""]
                for r in sorted(lst, key=lambda r: r["path"]):
                    L.append(f"- `{r['cpk']}/{r['path']}` ({r['kind']}, exit {r['code']})")
                    L += [f"  - `{e.strip()[:200]}`" for e in r["errors"]]
                L.append("")
        (ROOT / "docs/decompile_report.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
