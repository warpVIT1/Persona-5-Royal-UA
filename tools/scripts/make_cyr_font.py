"""Add Ukrainian Cyrillic to P5R FONT0.FNT and build the matching charset for AtlusScriptCompiler.

Input: a fonttool dump of the original font (glyphs.bin / widths.tsv), Charsets/P5R_EFIGS.tsv.
Output (in --out):
  glyphs.bin, widths.tsv   — for `fonttool build`
  P5R_UKR.tsv              — EFIGS charset with the chosen slots renamed to Ukrainian letters
  slots.tsv                — letter -> charset index -> glyph index
  preview.png              — game Latin vs generated Cyrillic, for visual QA

Slot choice: rare kanji at the end of the charset that occur in NO text of the game (not even unused
Japanese leftovers), so replacing their glyphs cannot affect anything displayed.
Glyph index = charset index - 0x20 (verified: glyph 0 = space, 1 = '!').
Letters that look identical to Latin ones are copied from the game's own Latin glyphs; the rest are
rendered with --ttf and fitted to the game's cap height, x-height, baseline and stem width.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import atlusenc as A  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
W = H = 96
BG = 1  # background palette value used by the game's glyphs

UPPER = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
LOWER = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
# Cyrillic letter -> Latin glyph in the game font with the same shape
HOMOGLYPH = {"А": "A", "В": "B", "Е": "E", "І": "I", "Ї": "Ï", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P",
             "С": "C", "Т": "T", "Х": "X", "а": "a", "е": "e", "і": "i", "ї": "ï", "о": "o", "р": "p", "с": "c",
             "у": "y", "х": "x"}


def load_glyphs(d):
    data = bytearray((d / "glyphs.bin").read_bytes())
    widths = [list(map(int, l.split("\t")[1:3])) for l in (d / "widths.tsv").read_text().splitlines()]
    return data, widths


def glyph(data, gi):
    return Image.frombytes("L", (W, H), bytes(data[gi * W * H:(gi + 1) * W * H]))


def ink_rows(im, thr=128):
    rows = [y for y in range(H) if any(im.getpixel((x, y)) > thr for x in range(W))]
    return rows[0], rows[-1]


def ink_cols(im, thr=40):
    cols = [x for x in range(W) if any(im.getpixel((x, y)) > thr for y in range(H))]
    return (cols[0], cols[-1]) if cols else (0, 0)


def stem(im, y, thr=128):
    return sum(1 for x in range(W) if im.getpixel((x, y)) > thr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=str(ROOT / "work/font/orig"))
    ap.add_argument("--out", default=str(ROOT / "work/font/ukr"))
    ap.add_argument("--ttf", default="C:/Windows/Fonts/segoeuib.ttf")
    a = ap.parse_args()
    dump, out = Path(a.dump), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data, widths = load_glyphs(dump)
    n_glyphs = len(data) // (W * H)
    table = A.read_charset(A.CHARSETS / "P5R_EFIGS.tsv")
    gi = lambda ch: table.index(ch) - 0x20  # noqa: E731

    # --- slots: rare kanji present in no text at all
    present = set("".join(p.read_text(encoding="utf-8-sig") for p in (ROOT / "source_en").rglob("*.msg")))
    free = [i for i in range(0x20, n_glyphs + 0x20) if "\u4e00" <= table[i] <= "\u9fff" and table[i] not in present]
    letters = UPPER + LOWER
    slots = dict(zip(letters, free[-len(letters):]))

    # --- game metrics
    Hm, xm, pm, lm = (glyph(data, gi(c)) for c in "Hxpl")
    cap_top, base = ink_rows(Hm)
    x_top, _ = ink_rows(xm)
    _, desc = ink_rows(pm)
    stem_w = stem(lm, (cap_top + base) // 2)
    h_l, h_r = ink_cols(Hm)
    pad_l, pad_r = h_l - widths[gi("H")][0], widths[gi("H")][1] - h_r
    print(f"game: cap {cap_top}-{base}, x-height top {x_top}, desc {desc}, stem {stem_w}, pad {pad_l}/{pad_r}")

    # --- fit TTF: size by cap height, stroke by stem width
    font = None
    for size in range(40, 120):
        f = ImageFont.truetype(a.ttf, size)
        bb = f.getbbox("H")
        if bb[3] - bb[1] >= base - cap_top + 1:
            font = f
            break
    tmp = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(tmp).text((10, 10), "l", font=font, fill=255)
    ttf_stem = stem(tmp, 10 + (font.getbbox("l")[1] + font.getbbox("l")[3]) // 2)
    stroke = max(0, round((stem_w - ttf_stem) / 2))
    print(f"ttf: size {font.size}, stem {ttf_stem} -> stroke {stroke}")

    def render(ch):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        ref = font.getbbox("H", stroke_width=stroke)
        y = base - ref[3]                      # put the TTF baseline on the game baseline
        bb = font.getbbox(ch, stroke_width=stroke)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]  # centre horizontally in the cell
        d.text((x, y), ch, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
        return im

    rows = []
    for ch, ci in slots.items():
        g = ci - 0x20
        if ch in HOMOGLYPH:
            src = gi(HOMOGLYPH[ch])
            data[g * W * H:(g + 1) * W * H] = data[src * W * H:(src + 1) * W * H]
            widths[g] = list(widths[src])
        else:
            im = render(ch)
            px = bytes(max(BG, v) for v in im.tobytes())
            data[g * W * H:(g + 1) * W * H] = px
            l, r = ink_cols(im)
            widths[g] = [max(0, l - pad_l), min(W - 1, r + pad_r)]
        rows.append((ch, ci, g, "copy:" + HOMOGLYPH[ch] if ch in HOMOGLYPH else "ttf"))

    (out / "glyphs.bin").write_bytes(bytes(data))
    (out / "widths.tsv").write_text("".join(f"{i}\t{l}\t{r}\n" for i, (l, r) in enumerate(widths)))
    with open(out / "slots.tsv", "w", encoding="utf-8") as f:
        f.write("letter\tcharset_index\tglyph\tsource\n")
        f.writelines(f"{c}\t{ci}\t{g}\t{s}\n" for c, ci, g, s in rows)

    # charset: the original EFIGS file with only the slot cells replaced (same flattening as read_charset)
    src_lines = A.split_lines((A.CHARSETS / "P5R_EFIGS.tsv").read_text(encoding="utf-8-sig"))
    cells, pos = [l.split("\t") for l in src_lines], {}
    k = 0
    for li, row in enumerate(cells):
        for ci_ in range(len(row)):
            pos[k] = (li, ci_)
            k += 1
    for ch, ci in slots.items():
        li, c_ = pos[ci]
        cells[li][c_] = ch
    (out / "P5R_UKR.tsv").write_text("\r\n".join("\t".join(r) for r in cells) + "\r\n", encoding="utf-8", newline="")
    check = A.read_charset(out / "P5R_UKR.tsv")
    assert len(check) == len(table) and all(check[ci] == ch for ch, ci in slots.items())
    assert all(check[i] == table[i] for i in range(len(table)) if i not in slots.values())

    # preview: game Latin reference + every Cyrillic glyph, cut by its width entry like the game does
    sample = "HxpAbg" + letters
    prev = Image.new("L", (len(sample) * 40 + 20, 70), 0)
    x = 10
    for ch in sample:
        g = gi(ch) if ch in "HxpAbg" else slots[ch] - 0x20
        l, r = widths[g]
        cell = glyph(data, g).crop((l, 0, r + 1, H)).resize(((r - l + 1) * 60 // 96, 60))
        prev.paste(cell, (x, 5))
        x += cell.width + 2
    prev.crop((0, 0, x + 10, 70)).save(out / "preview.png")
    print(f"{len(slots)} letters -> slots {min(slots.values())}..{max(slots.values())}; {out}")


if __name__ == "__main__":
    main()
