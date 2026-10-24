"""Export every texture of EN.CPK for redrawing.

  python tools/scripts/textures.py [--jobs 12] [--no-zip]

Sources (extracted/EN, read-only):
  * loose .DDS files;
  * sprite sets .SPD ("SPR0"): texture table at u32 @0x18, count u16 @0x14, entries of 0x30 bytes:
    u32 id, u32 ?, u32 data offset, u32 data size, u32 width, u32 height, 8 bytes ?, char name[16];
  * .DDS / .SPD inside PAK/PAC/BIN/ARC containers (recursively, parse_pak from inventory.py).
Models (.GMD/.EPL) are skipped: their textures are 3D surfaces, not captions.

Output (game folder structure; a container becomes a folder):
  work/textures/dds/<path>/...      original DDS (needed to put the redrawn picture back)
  work/textures/png/<path>/...      the same pictures as PNG, for editing
  work/textures/index.tsv           png path, source, width, height, DDS format
  work/textures.zip                 png/ + index.tsv
"""
import argparse
import struct
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from inventory import parse_pak  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "extracted/EN"
OUT = ROOT / "work/textures"
CONTAINERS = {".pak", ".pac", ".bin", ".arc"}


def spd_textures(data):
    if data[:4] != b"SPR0":
        return []
    count = struct.unpack_from("<H", data, 0x14)[0]
    table = struct.unpack_from("<I", data, 0x18)[0]
    out = []
    for i in range(count):
        e = table + 0x30 * i
        tid, _, off, size = struct.unpack_from("<IIII", data, e)
        name = data[e + 0x20:e + 0x30].split(b"\0")[0].decode("ascii", "replace") or f"tex{tid}"
        out.append((f"{tid:02d}_{name}.dds", data[off:off + size]))
    return out


def collect(data, rel, found, depth=0):
    """rel: path inside work/textures/{dds,png} (container names become folders)."""
    ext = Path(rel).suffix.lower()
    if data[:4] == b"DDS ":
        found.append((rel if ext == ".dds" else rel + ".dds", data))
    elif data[:4] == b"SPR0":
        for name, tex in spd_textures(data):
            found.append((f"{rel}/{name}", tex))
    elif (ext in CONTAINERS or depth > 0) and depth < 4:
        for name, off, size in parse_pak(data) or []:
            collect(data[off:off + size], f"{rel}/{name.strip()}", found, depth + 1)


def dds_format(b):
    four = b[84:88]
    if four == b"DX10":
        return f"DX10:{struct.unpack_from('<I', b, 128)[0]}"
    return four.decode("ascii", "replace").strip("\0") or "RGBA"


def to_png(item):
    rel, = item
    from PIL import Image
    src = OUT / "dds" / rel
    dst = (OUT / "png" / rel).with_suffix(".png")
    try:
        with Image.open(src) as im:
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst)
            return rel, im.width, im.height, ""
    except Exception as e:
        return rel, 0, 0, str(e)[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--no-zip", action="store_true")
    a = ap.parse_args()

    found = []
    for f in sorted(SRC.rglob("*")):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext not in {".dds", ".spd"} | CONTAINERS:
            continue
        collect(f.read_bytes(), f.relative_to(SRC).as_posix(), found)
    fmt = {}
    for rel, b in found:
        p = OUT / "dds" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b)
        fmt[rel] = dds_format(b)
    print(f"{len(found)} textures -> {OUT / 'dds'}", flush=True)

    rows, bad = [], []
    with ProcessPoolExecutor(a.jobs) as ex:
        for i, (rel, w, h, err) in enumerate(ex.map(to_png, [(r,) for r, _ in found], chunksize=8), 1):
            (bad if err else rows).append((rel, w, h, err))
            if i % 200 == 0:
                print(f"{i}/{len(found)}", flush=True)
    with open(OUT / "index.tsv", "w", encoding="utf-8", newline="\n") as w:
        w.write("png\tsource_dds\twidth\theight\tformat\terror\n")
        for rel, wd, ht, err in sorted(rows + bad):
            w.write(f"{Path(rel).with_suffix('.png').as_posix()}\t{rel}\t{wd}\t{ht}\t{fmt[rel]}\t{err}\n")
    print(f"png: {len(rows)} ok, {len(bad)} failed")
    for rel, *_, err in bad[:20]:
        print("  FAILED", rel, err)

    if not a.no_zip:
        z = ROOT / "work/textures.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:   # PNG is already compressed
            zf.write(OUT / "index.tsv", "index.tsv")
            for p in sorted((OUT / "png").rglob("*.png")):
                zf.write(p, p.relative_to(OUT / "png").as_posix())
        print(f"zip: {z} ({z.stat().st_size / 2**20:.0f} MB)")


if __name__ == "__main__":
    main()
