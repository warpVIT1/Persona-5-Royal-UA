"""Reader for P5R string-list FTD tables (big-endian), e.g. FIELD/FTD/FLDPLACENAME.FTD.

Layout observed in the EN files (and checked by read(): every offset/length must be consistent):
  0x00 u16 1, u16 0, "FTD0", u32 file_size
  0x0C u16 type (1 = string list), u16 count
  0x10 u32 offsets[count]                     -- absolute
  entry at offset: u8 len (incl. NUL), u8 1, u16 0, char[len] (P5R_EFIGS), padded to 16
Returns None for FTDs of other types (binary data tables).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlusenc  # noqa: E402


def read(data):
    if data[4:8] != b"FTD0" or len(data) < 16:
        return None
    size = struct.unpack_from(">I", data, 8)[0]
    typ, count = struct.unpack_from(">HH", data, 12)
    if typ != 1 or size != len(data) or 16 + 4 * count > len(data):
        return None
    out = []
    for off in struct.unpack_from(f">{count}I", data, 16):
        if off + 4 > len(data):
            return None
        n, flag = data[off], data[off + 1]
        raw = data[off + 4 : off + 4 + n]
        if not raw or raw[-1:] != b"\0":
            return None
        out.append(atlusenc.decode(raw.split(b"\0")[0]))
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = read(Path(p).read_bytes())
        print(p, "not a string FTD" if r is None else f"{len(r)} strings: {r[:8]}")
