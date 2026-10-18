"""Reader for P5R BATTLE/TABLE/NAME.TBL (big-endian).

Layout (verified: parsing consumes the whole file exactly):
  repeat:
    u32 size; u16[size/2] offsets          -- string start offsets into the next section
    pad to 16
    u32 size; char[size] NUL-terminated strings (P5R_EFIGS encoding)
    pad to 16
Each (offsets, strings) pair is one name list, indexed by entry id.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlusenc  # noqa: E402

# Section meaning, identified by content of the EN file (see docs/glossary_sources.md).
SECTIONS = ["arcana", "skill", "skill_alt", "enemy", "persona", "trait", "accessory", "armor",
            "consumable", "key_item", "material", "melee_weapon", "battle_action", "outfit",
            "skill_card", "party_first_name", "party_last_name", "party_nickname", "ranged_weapon"]


def _align(p, a=16):
    return (p + a - 1) // a * a


def read(path):
    d = Path(path).read_bytes()
    p, raw = 0, []
    while p + 4 <= len(d):
        n = struct.unpack_from(">I", d, p)[0]
        raw.append(d[p + 4 : p + 4 + n])
        p = _align(p + 4 + n)
    if p != len(d) or len(raw) % 2:
        raise ValueError(f"unexpected NAME.TBL layout: end {p} != {len(d)}, sections {len(raw)}")
    lists = []
    for k in range(0, len(raw), 2):
        offs = struct.unpack(f">{len(raw[k]) // 2}H", raw[k])
        blob = raw[k + 1]
        names = []
        for o in offs:
            end = blob.index(b"\0", o)
            names.append(atlusenc.decode(blob[o:end]))
        lists.append(names)
    return lists


if __name__ == "__main__":
    lists = read(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "extracted/EN/BATTLE/TABLE/NAME.TBL")
    for i, names in enumerate(lists):
        label = SECTIONS[i] if i < len(SECTIONS) else f"section{i}"
        real = [n for n in names if n not in ("BLANK", "RESERVE", "Unused", "Not Used") and not n.startswith(("0x", "00", "BLANK"))]
        print(f"[{i}] {label}: {len(names)} entries, {len(real)} real; e.g. {real[:6]} ... {real[-3:]}")


def write(lists, charset="P5R_EFIGS"):
    """Inverse of read(): lists of names -> NAME.TBL bytes (offsets are u16, so each blob must stay < 64 KB)."""
    out = bytearray()

    def section(data):
        out.extend(struct.pack(">I", len(data)) + data)
        out.extend(b"\x00" * (-len(out) % 16))

    for names in lists:
        blob, offs = bytearray(), []
        for n in names:
            offs.append(len(blob))
            blob += atlusenc.encode(n, charset) + b"\x00"
        if len(blob) > 0xFFFF:
            raise ValueError(f"name blob {len(blob)} bytes > 65535")
        section(struct.pack(f">{len(offs)}H", *offs))
        section(bytes(blob))
    return bytes(out)


def translated(lists, glossary):
    """Replace names by approved glossary translations: section category first, then any category."""
    anyg = {}
    for c in glossary.values():
        anyg.update(c)
    out = []
    for i, names in enumerate(lists):
        sec = SECTIONS[i] if i < len(SECTIONS) else None
        g = glossary.get(sec, {})
        out.append([g.get(n) or anyg.get(n) or n for n in names])
    return out


def build(path, new_lists, charset="P5R_UKR"):
    """Original NAME.TBL + new names -> bytes. Unchanged names keep their original bytes (the EN file has
    padding/garbage between some strings, so each string keeps its whole original slot when not translated)."""
    d = Path(path).read_bytes()
    old = read(path)
    p, raw = 0, []
    while p + 4 <= len(d):
        n = struct.unpack_from(">I", d, p)[0]
        raw.append(d[p + 4: p + 4 + n])
        p = _align(p + 4 + n)
    out = bytearray()

    def section(data):
        out.extend(struct.pack(">I", len(data)) + data)
        out.extend(b"\x00" * (-len(out) % 16))

    for k in range(0, len(raw), 2):
        offs = struct.unpack(f">{len(raw[k]) // 2}H", raw[k])
        blob = raw[k + 1]
        names_old, names_new = old[k // 2], new_lists[k // 2]
        # slot of each string = from its offset to the next larger offset (or end of blob)
        starts = sorted(set(offs)) + [len(blob)]
        nxt = {s: starts[i + 1] for i, s in enumerate(starts[:-1])}
        nb, new_offs, done = bytearray(), [], {}
        for o, a, b in zip(offs, names_old, names_new):
            key = (o, b)
            if key in done:                      # shared slots stay shared
                new_offs.append(done[key])
                continue
            done[key] = len(nb)
            new_offs.append(len(nb))
            nb += blob[o:nxt[o]] if a == b else atlusenc.encode(b, charset) + b"\x00"
        if len(nb) > 0xFFFF:
            raise ValueError(f"name blob {len(nb)} bytes > 65535")
        section(struct.pack(f">{len(new_offs)}H", *new_offs))
        section(bytes(nb))
    return bytes(out)
