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
       BMDs inside P5R.exe (EXE/X.BMD) -> dist/p5rpc.ukrainian/exebmd/<sha1 of English blob>.bmd,
                                          loaded by the mod DLL (tools/exemod, see exe_bmd.py)
  4. FONT0.FNT with Cyrillic, mod DLL, ModConfig.json
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

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / "tools/bin/AtlusScriptCompiler/AtlusScriptCompiler.exe"
SRC, TR = ROOT / "source_en", ROOT / "translated"
MOD = ROOT / "dist/p5rpc.ukrainian"
CPK = MOD / "P5REssentials/CPK/EN.CPK"
PAK = MOD / "FEmulator/PAK"
CONTAINER = re.compile(r"\.(PAK|PAC|BIN|ARC)$", re.I)
COMMON = ["-Library", "P5R", "-Encoding", "P5R_UKR"]
EXEMOD = ROOT / "tools/exemod"
# EXE/X.BMD -> SHA-1 of the English blob in P5R.exe (written by exe_bmd.py extract)
_h = ROOT / "extracted/EXE/hashes.tsv"
EXE_HASHES = dict(l.split("\t")[:2] for l in _h.read_text(encoding="utf-8").splitlines()) if _h.exists() else {}


def norm(s):
    return s.replace("\r", "").strip()


def targets(prefix):
    for msg in sorted([*(TR / "EN").rglob("*.msg"), *(TR / "EXE").rglob("*.msg")]):
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
    if rel.parts[0] == "EXE":
        return MOD / "exebmd" / (EXE_HASHES[parts[-1]] + ".bmd")
    for i, p in enumerate(parts[:-1]):
        if CONTAINER.search(p):
            return PAK.joinpath(*parts)   # inside an archive: emulator merges it into the PAK
    return CPK.joinpath(*parts)


def splice_bf(bf, bmd):
    """Original FlowScript (FLW0, big-endian) with its message section (type 3) replaced by `bmd`.

    Header: u32 0, u32 file size @0x04, "FLW0" @0x08, u32 section count @0x10; section table @0x20,
    16 bytes each: type, element size, element count, offset. Code refers to messages by index,
    so only the message section and the offsets after it change.
    """
    import struct
    if bf[8:12] != b"FLW0":
        raise ValueError("not a FLW0 script")
    out = bytearray(bf)
    n = struct.unpack_from(">I", bf, 0x10)[0]
    secs = [list(struct.unpack_from(">IIII", bf, 0x20 + 16 * i)) for i in range(n)]
    msg = [s for s in secs if s[0] == 3]
    if len(msg) != 1 or msg[0][1] != 1:
        raise ValueError("unexpected message section layout")
    _, _, size, off = msg[0]
    out[off:off + size] = bmd
    delta = len(bmd) - size
    for i, s in enumerate(secs):
        if s[0] == 3:
            s[2] = len(bmd)
        elif s[3] > off:
            s[3] += delta
        struct.pack_into(">IIII", out, 0x20 + 16 * i, *s)
    struct.pack_into(">I", out, 4, len(out))
    return bytes(out)


def compile_one(rel):
    msg = TR / rel
    name = msg.name[: -len(".msg")]                 # X.BMD or X.BF
    flow = msg.with_name(name + ".flow")
    is_bf = flow.exists()
    with tempfile.TemporaryDirectory(prefix="p5build_") as tmp:
        tmp = Path(tmp)
        for f in msg.parent.glob(name + ".*"):
            shutil.copy(f, tmp / f.name)
        m = tmp / msg.name   # the game font lacks some typographic characters
        m.write_text(M.sanitize(m.read_text(encoding="utf-8-sig")), encoding="utf-8")
        if is_bf:
            args = [str(COMPILER), flow.name, "-Compile", "-OutFormat", "V3BE", *COMMON, "-Out", name]
        else:
            args = [str(COMPILER), msg.name, "-Compile", "-OutFormat", "V1BE", *COMMON, "-Out", name]
        subprocess.run(args, cwd=tmp, capture_output=True)
        out = tmp / name
        if is_bf and (not out.exists() or out.stat().st_size == 0):
            # the decompiled flow does not recompile: keep the original code, replace only the message section
            orig = ROOT / "extracted" / rel.with_suffix("")
            bmd = tmp / (name + ".bmd")
            subprocess.run([str(COMPILER), msg.name, "-Compile", "-OutFormat", "V1BE", *COMMON, "-Out", bmd.name],
                           cwd=tmp, capture_output=True)
            if orig.exists() and bmd.exists() and bmd.stat().st_size:
                out.write_bytes(splice_bf(orig.read_bytes(), bmd.read_bytes()))
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
    ap.add_argument("--keep", action="store_true", help="do not wipe the mod folder (rebuild a subset)")
    a = ap.parse_args()

    font = ROOT / "work/font/FONT0_UKR.FNT"
    charset = ROOT / "work/font/ukr/P5R_UKR.tsv"
    if not font.exists() or not charset.exists():
        sys.exit("font not built: run tools/build_poc.sh once (make_cyr_font.py + fonttool build)")
    shutil.copy(charset, COMPILER.parent / "Charsets" / "P5R_UKR.tsv")

    if not a.skip_import:
        subprocess.run([sys.executable, str(ROOT / "tools/scripts/import_strings.py")], check=True)

    if MOD.exists() and not a.keep:
        shutil.rmtree(MOD)
    (CPK / "FONT").mkdir(parents=True, exist_ok=True)
    shutil.copy(font, CPK / "FONT/FONT0.FNT")
    # chat icons are looked up by speaker name -> add the Ukrainian names
    subprocess.run([sys.executable, str(ROOT / "tools/scripts/speakerdat.py"), str(CPK / "FONT/SPEAKER.DAT")], check=True)
    shutil.copy(ROOT / "tools/mod/ModConfig.template.json", MOD / "ModConfig.json")
    # DLL that swaps in the translated BMDs embedded in P5R.exe
    subprocess.run(["dotnet", "build", "-c", "Release", "-v", "q", "-nologo"], cwd=EXEMOD, check=True)
    for f in (EXEMOD / "bin/Release/net8.0-windows").glob("p5rpc.ukrainian.*"):
        if f.suffix != ".pdb":
            shutil.copy(f, MOD / f.name)
    # bytes of each letter in the mod's encoding, for Cyrillic player names (tools/exemod/Names.cs)
    import atlusenc
    letters = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
    with open(MOD / "namechars.tsv", "w", encoding="utf-8", newline="\n") as w:
        for c in letters + letters.upper() + "'":
            w.write(f"{c}\t{atlusenc.encode(c, 'P5R_UKR').hex()}\n")

    todo = list(targets(a.path))
    print(f"{len(todo)} files with translation to compile", flush=True)
    ok, bad = [], []
    with ThreadPoolExecutor(a.jobs) as ex:
        for i, (rel, good, err) in enumerate(ex.map(compile_one, todo), 1):
            (ok if good else bad).append((rel, err))
            if i % 500 == 0:
                print(f"{i}/{len(todo)}", flush=True)

    # menus, config, quests, calendar, place names... (FTD/CTD string tables)
    subprocess.run([sys.executable, str(ROOT / "tools/scripts/tables.py"), "build"])

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
