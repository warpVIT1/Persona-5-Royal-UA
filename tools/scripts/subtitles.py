"""Movie (anime cutscene) subtitles embedded in P5R.exe.

  python tools/scripts/subtitles.py extract [--lbk PATH_TO_LBK_EXE]

The exe keeps every subtitle line as a UTF-8 C string (line breaks as <BR>) and a table of 64-bit pointers
to them. We read the vanilla exe (.lbk-backup/P5R.exe or the game's exe) and write
  work/subs/subtitles.tsv   slot (file offset of the pointer), English text, LBK's Ukrainian (decoded)

LBK stores its Ukrainian as the Latin keys of the Ukrainian keyboard layout, drawn by a remapped font
("Ojcm nen yt nfr!" = «Щось тут не так!"); their converter also turned '.'/',' into 'ю'/'б'. decode_lbk()
reverses that. LBK's lines are their work (credited); they are a reference for our own translation.
"""
import argparse
import re
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
VANILLA = ROOT / ".lbk-backup/P5R.exe"
OUT = ROOT / "work/subs"
SECS = [(0x1762e00, 0x1764000, 0x3f2400), (0x1b55200, 0x1b57000, 0x9d4e00)]   # (raw, rva, size): .debug, .code

LAT = "qwertyuiopasdfghjklzxcvbnm[];',.`"
UKR = "йцукенгшщзфівапролдячсмитьхїжєбю'"
LAT_UP = "QWERTYUIOPASDFGHJKLZXCVBNM{}:\"<>~"
UKR_UP = "ЙЦУКЕНГШЩЗФІВАПРОЛДЯЧСМИТЬХЇЖЄБЮ'"


def off2va(o):
    for ra, va, sz in SECS:
        if ra <= o < ra + sz:
            return 0x140000000 + va + o - ra


def va2off(v):
    r = v - 0x140000000
    for ra, va, sz in SECS:
        if va <= r < va + sz:
            return r - va + ra


def cstr(d, o):
    return d[o:d.find(b"\0", o)]


def decode_lbk(s):
    out = []
    for part in re.split(r"(<BR>)", s):
        if part == "<BR>":
            out.append(part)
            continue
        for c in part:
            if c == "ю":
                out.append(".")
            elif c == "б":
                out.append(",")
            elif c in LAT:
                out.append(UKR[LAT.index(c)])
            elif c in LAT_UP:
                out.append(UKR_UP[LAT_UP.index(c)])
            else:
                out.append(c)
    return "".join(out)


def english_strings(a, lo=0x17b8000, hi=0x17e0000):
    eng = {}
    for m in re.finditer(rb"[^\x00]+", a[lo:hi]):
        s = m.group()
        if len(s) > 3 and all(32 <= c < 127 for c in s) and re.search(rb"[a-z] [a-z]", s):
            eng[lo + m.start()] = s.decode()
    return eng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["extract"])
    ap.add_argument("--lbk", default=r"C:\SteamLibrary\steamapps\common\P5R\P5R.exe")
    a_ = ap.parse_args()
    a = VANILLA.read_bytes()
    lbk = Path(a_.lbk).read_bytes() if Path(a_.lbk).exists() else None
    eng = english_strings(a)
    q = np.frombuffer(a[: len(a) // 8 * 8], dtype="<u8")
    want = {off2va(o): o for o in eng}
    slots = np.nonzero(np.isin(q, np.array(list(want), dtype=np.uint64)))[0]
    OUT.mkdir(parents=True, exist_ok=True)
    n_lbk = 0
    with open(OUT / "subtitles.tsv", "w", encoding="utf-8", newline="\n") as w:
        w.write("slot\ten\tlbk_uk\n")
        for i in sorted(int(x) for x in slots):
            slot = i * 8
            en = eng[want[int(q[i])]]
            uk = ""
            if lbk:
                pb = struct.unpack_from("<Q", lbk, slot)[0]
                ob = va2off(pb) if pb else None
                if ob and pb != q[i]:
                    uk = decode_lbk(cstr(lbk, ob).decode("utf-8", "replace"))
                    n_lbk += 1
            w.write(f"{slot:#x}\t{en}\t{uk}\n")
    print(f"{len(slots)} subtitle lines ({len(set(eng.values()))} distinct), LBK translated {n_lbk} -> {OUT / 'subtitles.tsv'}")


if __name__ == "__main__":
    sys.exit(main())
