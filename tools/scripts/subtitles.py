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
STORE = ROOT / "strings_uk/EXE/SUBTITLES.tsv"   # the translation kept in git (copy of work/subs/subtitles.tsv)
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


LBK_CHARS = {"э": "'", "あ": "—", "‘": "ґ", "《": "«", "》": "»"}   # LBK's stand-ins in their encoding
TAGS = {"News", "Loudspeaker", "TV", "Phone"}   # [tags] LBK translated; other tags are user names, kept


def fix_lbk(uk, en):
    for k, v in LBK_CHARS.items():
        uk = uk.replace(k, v)
    # "[News] ..." comes out as "хНовиниъ ..." ('[' and ']' sit on the х/ї keys)
    m, t = re.match(r"\[([^\]]+)\]", en), re.match(r"х(.+?)ъ", uk)
    if m and t:
        inner = t.group(1) if m.group(1) in TAGS or " " in m.group(1) else m.group(1)
        uk = f"[{inner}]" + uk[t.end():]
    return uk


def apply_transl(exe, path):
    """LBK's loader writes TRANSL.DAT into the exe at run time: records of u64 VA, u32 length, bytes.
    Some subtitle pointers lead to placeholders ("2198") that only these patches fill in."""
    if not path.exists():
        return 0
    d = path.read_bytes()
    o = n = 0
    while o + 12 <= len(d):
        va, ln = struct.unpack_from("<QI", d, o)
        off = va2off(va)
        if off is not None:
            exe[off:off + ln] = d[o + 12:o + 12 + ln]
            n += 1
        o += 12 + ln
    return n


def english_strings(a, lo=0x17b8000, hi=0x17e0000):
    eng = {}
    for m in re.finditer(rb"[^\x00]+", a[lo:hi]):
        s = m.group()
        if len(s) > 3 and all(32 <= c < 127 for c in s) and re.search(rb"[a-z] [a-z]", s):
            eng[lo + m.start()] = s.decode()
    return eng


# English lines LBK left untranslated (the rest of their untranslated slots are other languages)
OWN = {
    "How long will you stay?": "Надовго ти до нас?",
    "It's fine": "Усе гаразд",
    "[News] However, considering the number of charges<BR>brought against him, it's unlikely that he was working alone.":
        "[Новини] Утім, зважаючи на кількість висунутих йому<BR>звинувачень, малоймовірно, що він діяв сам.",
}


def build(out):
    """work/subs/subtitles.tsv -> <mod>/subs.tsv: pointer slot RVA, RVA of the English string it must hold now,
    UTF-8 text for the game's own character table (і ї є ґ written as the characters at our glyph indices)."""
    sys.path.insert(0, str(Path(__file__).parent))
    import atlusenc
    ukr = atlusenc.read_charset(ROOT / "work/font/ukr/P5R_UKR.tsv")
    efigs = atlusenc.read_charset(atlusenc.CHARSETS / "P5R_EFIGS.tsv")
    sub = {c: efigs[ukr.index(c)] for c in set(ukr) if len(c) == 1 and c not in efigs and ukr.index(c) < len(efigs)}
    a = VANILLA.read_bytes()
    n = 0
    nl, tab = chr(10), chr(9)
    with open(STORE if STORE.exists() else OUT / "subtitles.tsv", encoding="utf-8") as f, open(out, "w", encoding="utf-8", newline=nl) as w:
        next(f)
        for line in f:
            slot, en, uk = line.rstrip(nl).split(tab)
            uk = OWN.get(en, uk)
            if not re.search("[А-Яа-яІіЇїЄєҐґ]", uk):
                continue
            slot = int(slot, 16)
            str_rva = struct.unpack_from("<Q", a, slot)[0] - 0x140000000
            slot_rva = off2va(slot) - 0x140000000
            text = "".join(sub.get(c, c) for c in uk)
            w.write(f"{slot_rva:x}{tab}{str_rva:x}{tab}{text}{nl}")
            n += 1
    print(f"subtitles: {n} lines -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["extract", "build"])
    ap.add_argument("--out", help="build: output file (mod folder/subs.tsv)")
    ap.add_argument("--lbk", default=r"C:\SteamLibrary\steamapps\common\P5R\P5R.exe")
    a_ = ap.parse_args()
    if a_.cmd == "build":
        return build(Path(a_.out))
    a = VANILLA.read_bytes()
    lbk = bytearray(Path(a_.lbk).read_bytes()) if Path(a_.lbk).exists() else None
    if lbk:
        apply_transl(lbk, Path(a_.lbk).with_name("TRANSL.DAT"))
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
                    raw = cstr(lbk, ob)
                    if raw.isdigit():   # numbered entry: the text follows the number after its NUL padding
                        o2 = ob + len(raw)
                        while o2 < len(lbk) and lbk[o2] == 0:
                            o2 += 1
                        raw = cstr(lbk, o2)
                    uk = fix_lbk(decode_lbk(raw.decode("utf-8", "replace")), en)
                    n_lbk += 1
            w.write(f"{slot:#x}\t{en}\t{uk}\n")
    print(f"{len(slots)} subtitle lines ({len(set(eng.values()))} distinct), LBK translated {n_lbk} -> {OUT / 'subtitles.tsv'}")


if __name__ == "__main__":
    sys.exit(main())
