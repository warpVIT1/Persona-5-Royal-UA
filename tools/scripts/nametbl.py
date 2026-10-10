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
