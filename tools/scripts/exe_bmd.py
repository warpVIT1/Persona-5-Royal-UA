"""Message scripts embedded in P5R.exe (battle navigator lines, battle retry, Persona stock full, DLC error).

The game keeps these BMDs inside the executable, one copy per language (11 languages); code picks one with
`lea reg, [rip + blob]` by the language index. The English blobs are found by SHA-1 of their bytes.

  python tools/scripts/exe_bmd.py extract   # (read-only) exe -> extracted/EXE/*.BMD, decompiled to source_en/EXE/
  python tools/scripts/exe_bmd.py list      # all BMD blobs in the exe with offsets and hashes

At run time the mod DLL (tools/exemod) hashes the blobs in the loaded image the same way and redirects every
`lea` that points at a known English blob to the translated BMD (dist/.../exebmd/<sha1>.bmd).
"""
import hashlib
import mmap
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from decompile_all import decompile  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXE = Path(r"C:\SteamLibrary\steamapps\common\P5R\P5R.exe")
OUT = ROOT / "extracted/EXE"

# file name -> SHA-1 of the English blob (the exe holds 2-3 identical copies of each)
ENGLISH = {
    "BTL_SUPPORT_03.BMD": "436052c180",   # navigator 03 (Morgana)
    "BTL_SUPPORT_08.BMD": "1e37e11c26",   # navigator 08 (Futaba)
    "BTL_SUPPORT_09.BMD": "36dc370671",   # navigator 09
    "BTL_RETRY.BMD": "889a7a3134",        # "You can start over..."
    "BTL_RETRY_2.BMD": "58827c5e29",      # same, second English variant
    "BTL_PERSONA_GET.BMD": "24bbf31dc4",  # Persona stock full
    "MSG_ERROR.BMD": "0e5f0d0cc4",        # DLC / save errors
}


def blobs(data):
    """(offset, bytes, sha1) for every BMD ("1GSM" big-endian header) in the exe."""
    pos = 0
    while True:
        p = data.find(b"1GSM", pos)
        if p < 0:
            return
        pos = p + 1
        st = p - 8
        size = struct.unpack_from(">I", data, st + 4)[0]
        if data[st] != 7 or not 0x20 <= size <= 0x100000:
            continue
        b = bytes(data[st:st + size])
        yield st, b, hashlib.sha1(b).hexdigest()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    with open(EXE, "rb") as f:
        data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        found = list(blobs(data))
    if cmd == "list":
        for st, b, h in found:
            print(f"{st:#010x}\t{len(b):#08x}\t{h}")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, prefix in ENGLISH.items():
        hit = [(st, b, h) for st, b, h in found if h.startswith(prefix)]
        if not hit:
            sys.exit(f"{name}: blob {prefix} not found (game updated?)")
        st, b, h = hit[0]
        (OUT / name).write_bytes(b)
        rows.append(f"{name}\t{h}\t{len(hit)}")
        r = decompile(dict(cpk="EXE", path=name, magic="bmd"))
        print(f"{name}: {len(hit)} copies, {len(b)} bytes, decompiled {'ok' if r['ok'] else 'FAILED'}")
    (OUT / "hashes.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
