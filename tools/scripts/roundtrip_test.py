"""Round-trip test of the text pipeline on a sample of files.

For each sampled source_en .msg (BMD) / .flow (BF):
  1. compile source_en file                     -> A
  2. compile translated/ file (import_strings.py with no translations must be lossless) -> B
  3. A == B byte for byte                         (export/import loses nothing)
  4. decompile(A) == source_en .msg               (compiler reproduces the game text)
Run `python tools/scripts/import_strings.py` first so translated/ exists.

  python tools/scripts/roundtrip_test.py [--sample N] [--seed S] [--all]
"""
import argparse
import random
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / "tools/bin/AtlusScriptCompiler/AtlusScriptCompiler.exe"
SRC, TR = ROOT / "source_en", ROOT / "translated"
COMMON = ["-Library", "P5R", "-Encoding", "P5R_EFIGS"]


def compile_one(src_file, tmp, tag):
    """Copy file (+ its msg/msg.h for flows) into tmp/tag and compile; return output bytes or None."""
    d = tmp / tag
    d.mkdir()
    for f in src_file.parent.glob(src_file.name.rsplit(".", 1)[0] + "*"):
        shutil.copy(f, d / f.name)
    if src_file.suffix == ".flow":
        out = src_file.name[: -len(".flow")]
        args = [str(COMPILER), src_file.name, "-Compile", "-OutFormat", "V3BE", *COMMON, "-Out", out]
    else:
        out = src_file.name[: -len(".msg")]
        args = [str(COMPILER), src_file.name, "-Compile", "-OutFormat", "V1BE", *COMMON, "-Out", out]
    subprocess.run(args, cwd=d, capture_output=True)
    p = d / out
    return p.read_bytes() if p.exists() and p.stat().st_size else None


def test(src_file):
    rel = src_file.relative_to(SRC)
    with tempfile.TemporaryDirectory(prefix="p5rt_") as tmp:
        tmp = Path(tmp)
        a = compile_one(src_file, tmp, "a")
        if a is None:
            return rel, "compile(source_en) FAILED"
        b = compile_one(TR / rel, tmp, "b")
        if b is None:
            return rel, "compile(translated) FAILED"
        if a != b:
            return rel, "A != B"
        if src_file.suffix == ".msg":
            (tmp / "x.bin").write_bytes(a)
            subprocess.run([str(COMPILER), "x.bin", "-Decompile", "-InFormat", "MessageScriptBinary", *COMMON,
                            "-Out", "x.msg"], cwd=tmp, capture_output=True)
            # an empty speaker decompiles as "[msg NAME ]" and recompiles to "[msg NAME]"
            norm = lambda s: re.sub(r"(\[(?:msg|dlg) \S+) \]", r"\1]", s.replace("\r", "").strip())
            if norm((tmp / "x.msg").read_text(encoding="utf-8-sig")) != norm(src_file.read_text(encoding="utf-8-sig")):
                return rel, "decompile(A) != source"
    return rel, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    bmd = [p for p in SRC.rglob("*.msg") if not p.with_suffix(".flow").exists()
           and not (p.parent / (p.name[: -len(".msg")] + ".flow")).exists()]
    bf = list(SRC.rglob("*.flow"))
    rnd = random.Random(a.seed)
    files = bmd + bf if a.all else rnd.sample(bmd, min(a.sample, len(bmd))) + rnd.sample(bf, min(a.sample, len(bf)))
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(test, files))
    from collections import Counter
    for kind in (".msg", ".flow"):
        c = Counter(r for p, r in res if p.suffix == kind)
        print(f"{'BMD' if kind == '.msg' else 'BF '}: {dict(c)}")
    for p, r in res:
        if r != "ok":
            print(f"  {r}: {p}")
    return 0 if all(r == "ok" for _, r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
