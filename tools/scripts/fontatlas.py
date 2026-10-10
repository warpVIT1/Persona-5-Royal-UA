"""Render glyphs from a fonttool dump (glyphs.bin, 96x96 8bpp intensity) into a contact-sheet PNG.
   python tools/scripts/fontatlas.py <dumpdir> <out.png> <first> <count> [cols] [scale]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

d, out, first, count = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 16
scale = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5
W = H = 96
data = (d / "glyphs.bin").read_bytes()
widths = [tuple(map(int, l.split("\t")[1:3])) for l in (d / "widths.tsv").read_text().splitlines()]
rows = (count + cols - 1) // cols
cw, ch = int(W * scale), int(H * scale) + 12
img = Image.new("RGB", (cols * cw, rows * ch), (40, 40, 40))
dr = ImageDraw.Draw(img)
for k in range(count):
    i = first + k
    if (i + 1) * W * H > len(data):
        break
    g = Image.frombytes("L", (W, H), data[i * W * H:(i + 1) * W * H])
    if widths[i][1] > widths[i][0]:  # mark the visible column range
        gd = ImageDraw.Draw(g)
        gd.line([(widths[i][0], 0), (widths[i][0], 4)], fill=128)
        gd.line([(widths[i][1], 0), (widths[i][1], 4)], fill=128)
    g = g.resize((cw, int(H * scale)))
    x, y = (k % cols) * cw, (k // cols) * ch
    img.paste(g, (x, y + 12))
    dr.text((x + 1, y), str(i), fill=(255, 200, 0))
img.save(out)
print(out)
