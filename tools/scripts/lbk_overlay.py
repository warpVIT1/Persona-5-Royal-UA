"""Overlay with the textures redrawn by the LBK Ukrainian translation (LOCAL USE ONLY).

These pictures are LBK's work: they are NOT part of public releases unless LBK gives permission.
build_mod.py adds the overlay only with --lbk-textures.

  python tools/scripts/lbk_overlay.py

Input:
  work/lbk_textures_changed/<texture path>.png  which textures to take (the user's selection; a picture
                                                 deleted from this folder is not taken)
  work/lbk/EN/                                   LBK's EN.CPK, extracted (cpktool)
Output, mirroring the mod layout:
  work/lbk_overlay/P5REssentials/CPK/EN.CPK/<file>        loose .DDS / .SPD replaced whole
  work/lbk_overlay/FEmulator/PAK/<container>/<inner file> texture files inside PAK/PAC/BIN (only the
                                                          texture file; LBK's texts in the container are not used)
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from inventory import parse_pak  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PICK = ROOT / "work/lbk_textures_changed"
LBK = ROOT / "work/lbk/EN"
OUT = ROOT / "work/lbk_overlay"
CONTAINER = (".PAK", ".PAC", ".BIN", ".ARC")


def inner_bytes(data, parts):
    """Bytes of a nested entry; PAK entry names may contain '/', so path parts are joined greedily."""
    parts = list(parts)
    while parts:
        ents = {n.strip().upper(): (o, s) for n, o, s in parse_pak(data) or []}
        for k in range(len(parts), 0, -1):
            key = "/".join(parts[:k]).upper()
            if key in ents:
                o, s = ents[key]
                data, parts = data[o:o + s], parts[k:]
                break
        else:
            raise KeyError("/".join(parts))
    return data


def carrier(rel):
    """Texture path -> ('cpk', file path) or ('pak', container path, [inner path parts])."""
    parts = rel.split("/")
    for i, p in enumerate(parts):
        u = p.upper()
        if u.endswith(CONTAINER):
            inner = []
            for q in parts[i + 1:]:
                inner.append(q)
                if q.upper().endswith((".SPD", ".DDS")):
                    break
            return ("pak", "/".join(parts[:i + 1]), tuple(inner))
        if u.endswith(".SPD"):
            return ("cpk", "/".join(parts[:i + 1]))
    return ("cpk", "/".join(parts)[: -len(".png")] if rel.lower().endswith(".png") else rel)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    done = set()
    for png in sorted(PICK.rglob("*.png")):
        rel = png.relative_to(PICK).as_posix()
        c = carrier(rel)
        if c in done:
            continue
        done.add(c)
        if c[0] == "cpk":
            src = LBK / c[1]
            if not src.exists():   # loose texture: the .png name stands for X.DDS
                src = next((p for p in src.parent.glob(src.name + ".*")), None) or LBK / (c[1] + ".DDS")
            dst = OUT / "P5REssentials/CPK/EN.CPK" / src.relative_to(LBK)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        else:
            _, cont, inner = c
            data = inner_bytes((LBK / cont).read_bytes(), inner)
            dst = OUT / "FEmulator/PAK" / cont / "/".join(inner)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
    files = [p for p in OUT.rglob("*") if p.is_file()]
    print(f"{len(files)} files from {len(list(PICK.rglob('*.png')))} pictures -> {OUT}")


if __name__ == "__main__":
    main()
