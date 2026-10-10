"""Atlus custom text encoding (P5R_EFIGS etc.), ported from Atlus-Script-Tools
AtlusScriptLibrary/Common/Text/Encodings/AtlusEncoding.cs.

Charset TSV: characters in glyph order, tab-separated, "\\uXXXX" escapes allowed.
  index <= 0x7F            -> single byte = index
  index >  0x7F            -> glyph = index + 0x60; table = glyph // 0x80 - 1
                              bytes = [0x80 | table, glyph - table * 0x80]
Decoding: a byte with bit 0x80 set starts a 2-byte code point.
"""
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHARSETS = ROOT / "tools/bin/AtlusScriptCompiler/Charsets"

CHAR_TO_GLYPH_INDEX_OFFSET = 0x60
GLYPH_TABLE_SIZE = 0x80
ASCII_RANGE = 0x7F
MARKER = 0x80


def read_charset(path):
    table = []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        for cs in line.split("\t"):
            table.append(chr(int(cs[2:], 16)) if cs.startswith("\\u") else cs)
    return table


def _codepoint(index):
    glyph = index + CHAR_TO_GLYPH_INDEX_OFFSET
    table = glyph // GLYPH_TABLE_SIZE - 1
    return bytes([MARKER | table, glyph - table * GLYPH_TABLE_SIZE])


@lru_cache(maxsize=None)
def tables(name="P5R_EFIGS"):
    t = read_charset(CHARSETS / f"{name}.tsv")
    enc, dec = {}, {}
    for i in range(ASCII_RANGE + 1):
        enc.setdefault(t[i], bytes([i]))
        dec[bytes([i])] = t[i]
    for i in range(ASCII_RANGE + 1, len(t)):
        enc.setdefault(t[i], _codepoint(i))
    for i in range(0x20, len(t)):
        dec[_codepoint(i)] = t[i]
    return enc, dec


def decode(b, name="P5R_EFIGS"):
    """bytes -> str; unknown code points become \\x{hi}{lo} markers."""
    _, dec = tables(name)
    out, i = [], 0
    while i < len(b):
        if b[i] & MARKER and i + 1 < len(b):
            cp = b[i : i + 2]
            i += 2
        else:
            cp = b[i : i + 1]
            i += 1
        out.append(dec.get(cp, "".join(f"\\x{x:02X}" for x in cp)))
    return "".join(out)


def encode(s, name="P5R_EFIGS"):
    enc, _ = tables(name)
    try:
        return b"".join(enc[c] for c in s)
    except KeyError as e:
        raise ValueError(f"character {e.args[0]!r} not in charset {name}") from None
