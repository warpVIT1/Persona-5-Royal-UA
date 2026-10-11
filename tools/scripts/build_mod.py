"""Build the Reloaded-II mod from the current translation state.

  python tools/scripts/build_mod.py [--jobs 16] [--skip-import] [--path PREFIX]

Steps:
  1. strings_uk -> translated/ (import_strings), unless --skip-import
  2. every translated .msg that differs from source_en is compiled with the P5R_UKR charset:
       BMD (X.BMD.msg)            -> V1BE
       BF  (X.BF.flow + X.BF.msg) -> V3BE
     Files with no translated page are left out (the game keeps its original).
  3. output layout (Persona Essentials):
       loose CPK files   -> dist/p5rpc.ukrainian/P5REssentials/CPK/EN.CPK/<path>
       files in archives -> dist/p5rpc.ukrainian/FEmulator/PAK/<archive path>/<file>   (PAK emulator)
  4. FONT0.FNT with Cyrillic, ModConfig.json
Report: docs/build_report.md (compiled / skipped / failed).
"""
import argparse
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
MOD = ROOT / "dist/p5rpc.ukrainian"
CPK = MOD / "P5REssentials/CPK/EN.CPK"
PAK = MOD / "FEmulator/PAK"
CONTAINER = re.compile(r"\.(PAK|PAC|BIN|ARC)$", re.I)
COMMON = ["-Library", "P5R", "-Encoding", "P5R_UKR"]


def norm(s):
    return s.replace("\r", "").strip()


def targets(prefix):
    for msg in sorted((TR / "EN").rglob("*.msg")):
        rel = msg.relative_to(TR)
        if not rel.as_posix().startswith(prefix):
            continue
        src = SRC / rel
        if not src.exists() or norm(src.read_text(encoding="utf-8-sig")) == norm(msg.read_text(encoding="utf-8-sig")):
            continue  # nothing translated in this file
        yield rel


def out_path(rel):
    """rel = EN/<path>/X.BMD.msg -> destination of the compiled binary."""
    parts = list(rel.parts[1:])
    parts[-1] = parts[-1][: -len(".msg")]
    for i, p in enumerate(parts[:-1]):
        if CONTAINER.search(p):
            return PAK.joinpath(*parts)   # inside an archive: emulator merges it into the PAK
    return CPK.joinpath(*parts)


def compile_one(rel):
    msg = TR / rel
    name = msg.name[: -len(".msg")]                 # X.BMD or X.BF
    flow = msg.with_name(name + ".flow")
    is_bf = flow.exists()
    with tempfile.TemporaryDirectory(prefix="p5build_") as tmp:
        tmp = Path(tmp)
        for f in msg.parent.glob(name + ".*"):
            shutil.copy(f, tmp / f.name)
        if is_bf:
            args = [str(COMPILER), flow.name, "-Compile", "-OutFormat", "V3BE", *COMMON, "-Out", name]
        else:
            args = [str(COMPILER), msg.name, "-Compile", "-OutFormat", "V1BE", *COMMON, "-Out", name]
        subprocess.run(args, cwd=tmp, capture_output=True)
        out = tmp / name
        if not out.exists() or out.stat().st_size == 0:
            log = tmp / "AtlusScriptCompiler.log"
            err = ""
            if log.exists():
                lines = [l for l in log.read_text(encoding="utf-8", errors="replace").splitlines()
                         if re.search(r"\b(Error|Fatal)\b", l)]
                err = lines[0].strip()[:200] if lines else ""
            return rel, False, err
        dst = out_path(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out, dst)
    return rel, True, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=16)
    ap.add_argument("--skip-import", action="store_true")
    ap.add_argument("--path", default="EN")
    a = ap.parse_args()

    font = ROOT / "work/font/FONT0_UKR.FNT"
    charset = ROOT / "work/font/ukr/P5R_UKR.tsv"
    if not font.exists() or not charset.exists():
        sys.exit("font not built: run tools/build_poc.sh once (make_cyr_font.py + fonttool build)")
    shutil.copy(charset, COMPILER.parent / "Charsets" / "P5R_UKR.tsv")

    if not a.skip_import:
        subprocess.run([sys.executable, str(ROOT / "tools/scripts/import_strings.py")], check=True)

    if MOD.exists():
        shutil.rmtree(MOD)
    (CPK / "FONT").mkdir(parents=True)
    shutil.copy(font, CPK / "FONT/FONT0.FNT")
    shutil.copy(ROOT / "tools/mod/ModConfig.template.json", MOD / "ModConfig.json")

    todo = list(targets(a.path))
    print(f"{len(todo)} files with translation to compile", flush=True)
    ok, bad = [], []
    with ThreadPoolExecutor(a.jobs) as ex:
        for i, (rel, good, err) in enumerate(ex.map(compile_one, todo), 1):
            (ok if good else bad).append((rel, err))
            if i % 500 == 0:
                print(f"{i}/{len(todo)}", flush=True)

    n_pak = sum(1 for r, _ in ok if PAK in out_path(r).parents)
    L = ["# Звіт збірки мода", "",
         f"Скомпільовано: {len(ok)} файлів ({len(ok) - n_pak} у CPK, {n_pak} в архівах через PAK-емулятор). "
         f"Не скомпільовано: {len(bad)} (лишаються англійськими).", ""]
    if bad:
        L += ["## Не скомпільовано", ""] + [f"- `{r.as_posix()}` — {e or 'немає вихідного файлу'}" for r, e in bad]
    (ROOT / "docs/build_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    size = sum(f.stat().st_size for f in MOD.rglob("*") if f.is_file())
    print(f"compiled {len(ok)} ({n_pak} via PAK emulator), failed {len(bad)}; mod size {size / 1e6:.1f} MB -> {MOD}")


if __name__ == "__main__":
    main()
