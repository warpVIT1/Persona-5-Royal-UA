"""String tables (FTD/CTD) — menus, config, difficulty, quests, calendar, chat titles, shop texts, place names.

Two FTD layouts carry text (big-endian, "FTD0" at 0x04, file size at 0x08):
  type 0, 1 block ("CTD"):  0x0C u16 0, u16 1; 0x10 u32 block_off; at block_off: u32 0, u32 data_size,
                            u32 count, u32 0; then `count` fixed records of data_size/count bytes,
                            each a NUL-terminated string padded with zeros
  type 1 (string list):     0x0C u16 1, u16 count; 0x10 u32 offsets[count]; entry = u8 len (incl. NUL),
                            u8 1, u16 0, char[len], padded to 16 (see ftd.py)
Text is in the game encoding (P5R_EFIGS; Cyrillic via P5R_UKR is 2 bytes per letter), so a fixed record
of N bytes holds at most N-1 bytes of text: the validator and the build check bytes, not characters.

  python tools/scripts/tables.py export     # strings_en/<path>.tbl.json (+ strings_uk skeletons, glossary prefill)
  python tools/scripts/tables.py build      # translated tables -> dist mod (PAK emulator / CPK)
  python tools/scripts/tables.py test       # write(read(x)) == x for every table
"""
import argparse
import csv
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlusenc as A  # noqa: E402
import inventory as I  # noqa: E402
import msgfmt as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXT, EN, UK = ROOT / "extracted", ROOT / "strings_en", ROOT / "strings_uk"
MOD = ROOT / "dist/p5rpc.ukrainian"
CONTAINERS = (".BIN", ".PAK", ".PAC", ".ARC", ".TBL")
# internal lookup tables / word lists that must stay as they are
SKIP = {"fclSklCardAttrTable.ftd", "autoAttrTable.ftd", "fclItemLineUpAccTable.ftd", "fclLogFormatText.ftd",
        "fclLogConjunctionText.ftd", "teamNameEntryNGWord.ftd"}
PLACEHOLDER = re.compile(r"^(RESERVE|BLANK|NULL|DUMMY|dummy|COMMUNITY RESERVE|ARCANA\d+|Location Name \d+|\?+|Shop OO)$")


def parse(b):
    """bytes -> dict(type, rs, strings) or None if this FTD is not a text table."""
    if len(b) < 0x20 or b[4:8] != b"FTD0" or struct.unpack_from(">I", b, 8)[0] > len(b):
        return None
    typ, count = struct.unpack_from(">HH", b, 12)
    out = []
    if typ == 0 and count == 1:
        off = struct.unpack_from(">I", b, 16)[0]
        dsize, n = struct.unpack_from(">II", b, off + 4)
        if not n or dsize % n or off + 16 + dsize > len(b):
            return None
        rs = dsize // n
        for i in range(n):
            r = b[off + 16 + i * rs: off + 16 + (i + 1) * rs]
            s = r.split(b"\0")[0]
            if r[len(s):].strip(b"\0") or (s and not re.fullmatch(rb"[\x20-\x7e\x80-\xff]+", s)):
                return None
            out.append(A.decode(s))
        res = dict(type=0, rs=rs, strings=out)
    elif typ == 1:
        if 16 + 4 * count > len(b):
            return None
        for o in struct.unpack_from(f">{count}I", b, 16):
            n = b[o]
            raw = b[o + 4: o + 4 + n]
            if not raw or raw[-1:] != b"\0":
                return None
            out.append(A.decode(raw[:-1].split(b"\0")[0]))
        res = dict(type=1, rs=None, strings=out)
    elif typ == 0 and count > 1:
        # one string per block (MISSION_LIST.TBL *_mission_title.ftd): block = u32 0, u32 size, u32 1, u32 0, text
        offs = struct.unpack_from(f">{count}I", b, 16)
        for o in offs:
            z, dsize, n, _ = struct.unpack_from(">IIII", b, o)
            raw = b[o + 16: o + 16 + dsize]
            if z or n != 1 or not raw or raw[-1:] != b"\0" or raw[:-1].count(b"\0"):
                return None
            out.append(A.decode(raw[:-1]))
        res = dict(type=2, rs=None, strings=out)
    else:
        return None
    return res if any(re.search("[A-Za-z]{2}", x) for x in out) else None


def write(b, t, strings, charset="P5R_UKR"):
    """Original bytes + new strings -> bytes with the same layout."""
    enc = [A.encode(s, charset) for s in strings]
    if t["type"] == 0:
        out = bytearray(b)
        off = struct.unpack_from(">I", b, 16)[0] + 16
        rs = t["rs"]
        for i, e in enumerate(enc):
            if len(e) >= rs:
                raise ValueError(f"record {i}: {len(e)} bytes > {rs - 1}: {strings[i]!r}")
            out[off + i * rs: off + (i + 1) * rs] = e.ljust(rs, b"\0")
        return bytes(out)
    count = len(enc)
    first = struct.unpack_from(">I", b, 16)[0]
    if t["type"] == 2:
        head, body, offs, pos = bytearray(b[:first]), bytearray(), [], first
        for e in enc:
            blk = struct.pack(">IIII", 0, len(e) + 1, 1, 0) + e + b"\0"
            blk += b"\0" * (-len(blk) % 16)
            offs.append(pos)
            body += blk
            pos += len(blk)
        struct.pack_into(f">{count}I", head, 16, *offs)
        out = head + body
        struct.pack_into(">I", out, 8, len(out))
        return bytes(out)
    head = bytearray(b[:first])          # header + offsets (+ padding as in the original)
    body, offs, pos = bytearray(), [], first
    for i, e in enumerate(enc):
        n = len(e) + 1
        if n > 255:
            raise ValueError(f"entry {i}: {n} bytes > 255")
        o = struct.unpack_from(">I", b, 16 + 4 * i)[0]
        flag = b[o + 1]
        ent = bytes([n, flag, 0, 0]) + e + b"\0"
        ent += b"\0" * (-len(ent) % 16)
        offs.append(pos)
        body += ent
        pos += len(ent)
    struct.pack_into(f">{count}I", head, 16, *offs)
    out = head + body
    struct.pack_into(">I", out, 8, len(out))
    return bytes(out)


def discover():
    """Yield (rel path like EN/INIT/CMPTABLE.BIN/x.ctd, original bytes, parsed table)."""
    for f in sorted((EXT / "EN").rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(EXT).as_posix()
        if f.suffix.upper() in CONTAINERS:
            d = f.read_bytes()
            try:
                ents = I.parse_pak(d) or []
            except Exception:
                ents = []
            for name, off, size in ents:
                if name.lower().endswith((".ctd", ".ftd")) and name not in SKIP:
                    t = parse(d[off:off + size])
                    if t:
                        yield f"{rel}/{name}", d[off:off + size], t
        elif f.suffix.upper() in (".FTD", ".CTD") and f.name not in SKIP:
            d = f.read_bytes()
            t = parse(d)
            if t:
                yield rel, d, t


def translatable(s):
    return bool(re.search("[A-Za-z]{2}", s)) and not PLACEHOLDER.match(s) and not re.search(r"[぀-鿿]", s)


def glossary():
    g = {}
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["status"] == "approved" and r["uk"]:
                g.setdefault(r["en"], r["uk"])
    return g


def cmd_export(a):
    gl = glossary()
    n_files = n_new = n_pre = 0
    for rel, _, t in discover():
        entries = [dict(id=f"#{i}", kind="table", speaker=None, lang="en", prefix="", text=s, suffix="",
                        translate=translatable(s),
                        context=dict(bytes=(t["rs"] - 1) if t["rs"] else 254))
                   for i, s in enumerate(t["strings"])]
        p = EN / (rel + ".tbl.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(file=rel, source=f"extracted/{rel}", entries=entries), ensure_ascii=False,
                                indent=1), encoding="utf-8")
        n_files += 1
        u = UK / (rel + ".tbl.json")
        if not u.exists():
            ue = []
            for e in entries:
                if not e["translate"]:
                    continue
                uk = gl.get(e["text"], "")
                n_pre += bool(uk)
                ue.append(dict(id=e["id"], speaker=None, en=e["text"], uk=uk, note="glossary" if uk else ""))
            u.parent.mkdir(parents=True, exist_ok=True)
            u.write_text(json.dumps(dict(file=rel, entries=ue), ensure_ascii=False, indent=1), encoding="utf-8")
            n_new += 1
    print(f"{n_files} tables exported, {n_new} new strings_uk files, {n_pre} entries prefilled from glossary")


def out_path(rel):
    parts = rel.split("/")[1:]
    for i, p in enumerate(parts[:-1]):
        if p.upper().endswith(CONTAINERS):
            return MOD / "FEmulator/PAK" / "/".join(parts)
    return MOD / "P5REssentials/CPK/EN.CPK" / "/".join(parts)


def cmd_build(a):
    ok = bad = 0
    for rel, data, t in discover():
        u = UK / (rel + ".tbl.json")
        if not u.exists():
            continue
        tr = {e["id"]: M.sanitize(e["uk"]) for e in json.loads(u.read_text(encoding="utf-8"))["entries"] if e["uk"]}
        if not tr:
            continue
        strings = [tr.get(f"#{i}", s) for i, s in enumerate(t["strings"])]
        try:
            out = write(data, t, strings)
        except ValueError as e:
            print(f"FAIL {rel}: {e}")
            bad += 1
            continue
        dst = out_path(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(out)
        ok += 1
    # battle names (skills, Personas, enemies, items...) from the approved glossary
    import nametbl
    src = EXT / "EN/BATTLE/TABLE/NAME.TBL"
    by_cat = {}
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["status"] == "approved" and r["uk"]:
                by_cat.setdefault(r["category"], {})[r["en"]] = M.sanitize(r["uk"])
    lists = nametbl.translated(nametbl.read(src), by_cat)
    # names with characters the font lacks stay English
    lists = [[n if all(c in A.tables("P5R_UKR")[0] for c in n) else o for n, o in zip(new, old)]
             for new, old in zip(lists, nametbl.read(src))]
    data = nametbl.build(src, lists)
    for dst in (out_path("EN/BATTLE/TABLE/NAME.TBL"), out_path("EN/BATTLE/TABLE.PAC/NAME.TBL")):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    n_names = sum(a != b for new, old in zip(lists, nametbl.read(src)) for a, b in zip(new, old))
    print(f"tables: {ok} written, {bad} failed; NAME.TBL: {n_names} battle names translated")
    return 1 if bad else 0


def cmd_test(a):
    n = 0
    for rel, data, t in discover():
        w = write(data, t, t["strings"], "P5R_EFIGS")   # bytes may differ: EFIGS has duplicate code points
        if parse(w)["strings"] != t["strings"] or (t["type"] != 1 and len(w) != len(data)):
            print("MISMATCH", rel)
        n += 1
    print(n, "tables round-tripped")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export", "build", "test"])
    a = ap.parse_args()
    return {"export": cmd_export, "build": cmd_build, "test": cmd_test}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main() or 0)
