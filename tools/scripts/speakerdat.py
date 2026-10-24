"""FONT/SPEAKER.DAT with Ukrainian speaker names.

NOT USED BY THE BUILD ANY MORE (see build_mod.py): the chat headers keep English names, so the original file is right.

SPEAKER.DAT is a flat array of 48-byte records: u16 BE icon id + speaker name in the game encoding,
NUL-padded. The phone chat (and other UI) finds a character's icon by the speaker name from the message
header ([msg X [Ryuji]]); an unknown name falls back to the default icon (Morgana). The game reads a fixed
number of records (records appended after the original 154 are ignored), so every name is replaced IN PLACE
with its Ukrainian translation (the same way the LBK translation does it); names without a translation, or too
long for the 46-byte field, stay English.

  python tools/scripts/speakerdat.py OUT [--src extracted/EN/FONT/SPEAKER.DAT]
"""
import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlusenc as A  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REC, NAME = 48, 46


def read(path):
    d = Path(path).read_bytes()
    return [(struct.unpack(">H", d[i:i + 2])[0], d[i + 2:i + REC].split(b"\0")[0]) for i in range(0, len(d), REC)]


def build(src, out, speakers):
    recs = read(src)
    done, skipped = 0, []
    out_recs = []
    for sid, name in recs:
        uk = speakers.get(A.decode(name, "P5R_EFIGS"))
        b = A.encode(uk, "P5R_UKR") if uk else None
        if b and len(b) >= NAME:
            skipped.append(uk)
            b = None
        if b:
            done += 1
        out_recs.append((sid, b or name))
    with open(out, "wb") as f:
        for sid, name in out_recs:
            f.write(struct.pack(">H", sid) + name.ljust(NAME, b"\0"))
    return len(recs), done, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--src", default=str(ROOT / "extracted/EN/FONT/SPEAKER.DAT"))
    a = ap.parse_args()
    sp = json.loads((ROOT / "strings_uk/_speakers.json").read_text(encoding="utf-8"))
    n, k, skipped = build(a.src, a.out, sp)
    print(f"SPEAKER.DAT: {n} records, {k} renamed to Ukrainian" + (f"; too long: {skipped}" if skipped else ""))


if __name__ == "__main__":
    main()
