"""Inventory of text-relevant files in extracted CPK contents.

Walks extracted/EN and extracted/BASE, lists .bmd/.bf/.tbl/.ftd/.ctd/.pak/.fnt
(+ any .pac/.bin/.arc/.spd that parse as Atlus PAK), recursing into PAK containers.

PAK parsing follows AtlusFileSystemLibrary (tge-was-taken), FileSystems/PAK/PAKFileSystem.cs:
  V1: [name 252][int32 size][data] aligned to 64
  V2: int32 count, [name 32][int32 size][data]
  V3: int32 count, [name 24][int32 size][data]
P5R (PC too) stores them big-endian (Version2BE/Version3BE); both endiannesses are tried.

Outputs: docs/inventory.tsv (full list) and docs/inventory.md (summary).
"""
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTRACTED = ROOT / "extracted"
DOCS = ROOT / "docs"

LISTED_EXTS = {"bmd", "bf", "tbl", "ftd", "ctd", "pak", "fnt"}
CONTAINER_EXTS = {"pak", "pac", "bin", "arc", "spd"}
MAX_DEPTH = 4


def align(v, a):
    return (v + a - 1) // a * a


def _name_ok(raw):
    """Name field: non-empty, printable, zero-padded with nothing after the terminator."""
    if not raw or raw[0] == 0:
        return False
    term = raw.find(b"\0")
    if term != -1 and any(raw[term:]):
        return False
    name = raw[: term if term != -1 else len(raw)]
    return all(0x20 <= b < 0x7F for b in name)


def parse_pak(data):
    """Return list of (name, offset, size) or None if not a PAK. P5R uses big-endian PAKs."""
    for endian in (">", "<"):
        r = _parse_pak(data, endian)
        if r:
            return r
    return None


def _parse_pak(data, en):
    n = len(data)
    # V1
    if n > 256 and _name_ok(data[:252]):
        entries, pos = [], 0
        while pos + 256 <= n:
            raw = data[pos : pos + 252]
            size = struct.unpack_from(en + "i", data, pos + 252)[0]
            if not _name_ok(raw) or size <= 0 or pos + 256 + size > n:
                break
            entries.append((raw.split(b"\0")[0].decode("ascii"), pos + 256, size))
            pos = align(pos + 256 + size, 64)
        if entries and pos >= n - 64:
            return entries
    # V2 / V3
    for name_len in (32, 24):
        esz = name_len + 4
        if n <= 4 + esz:
            continue
        count = struct.unpack_from(en + "i", data, 0)[0]
        if not (1 <= count <= 1024) or count * esz > n:
            continue
        entries, pos, ok = [], 4, True
        for _ in range(count):
            if pos + esz > n:
                ok = False
                break
            raw = data[pos : pos + name_len]
            size = struct.unpack_from(en + "i", data, pos + name_len)[0]
            if not _name_ok(raw) or size < 0 or pos + esz + size > n:
                ok = False
                break
            entries.append((raw.split(b"\0")[0].decode("ascii"), pos + esz, size))
            pos += esz + size
        if ok and entries:
            return entries
    return None


def magic_kind(data):
    if data[8:12] in (b"MSG1", b"1GSM"):
        return "bmd"
    if data[8:12] in (b"FLW0", b"0WLF"):
        return "bf"
    return ""


def ext_of(name):
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def walk_blob(data, vpath, depth, out, cpk):
    """Recurse into container; record listed entries."""
    entries = parse_pak(data) if depth < MAX_DEPTH else None
    if entries is None:
        return 0
    for name, off, size in entries:
        sub = data[off : off + size]
        sub_path = f"{vpath}::{name}"
        e = ext_of(name)
        kind = magic_kind(sub)
        n_inner = 0
        if e in CONTAINER_EXTS or e == "" or e not in LISTED_EXTS:
            n_inner = walk_blob(sub, sub_path, depth + 1, out, cpk)
        if e in LISTED_EXTS or kind or n_inner:
            out.append(dict(cpk=cpk, path=sub_path, ext=e or "(none)", size=size,
                            magic=kind, nested=depth + 1, inner=n_inner, overridden=""))
    return len(entries)


def main():
    rows = []
    for cpk in ("EN", "BASE"):
        base = EXTRACTED / cpk
        for f in sorted(base.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(base).as_posix()
            e = ext_of(f.name)
            if e not in LISTED_EXTS and e not in CONTAINER_EXTS:
                continue
            data = f.read_bytes()
            n_inner = walk_blob(data, rel, 0, rows, cpk) if e in CONTAINER_EXTS else 0
            if e in LISTED_EXTS or n_inner:
                rows.append(dict(cpk=cpk, path=rel, ext=e, size=len(data), magic=magic_kind(data),
                                 nested=0, inner=n_inner, overridden=""))

    en_paths = {r["path"].split("::")[0].upper() for r in rows if r["cpk"] == "EN" and r["nested"] == 0}
    for r in rows:
        if r["cpk"] == "BASE" and r["path"].split("::")[0].upper() in en_paths:
            r["overridden"] = "yes"

    rows.sort(key=lambda r: (r["cpk"] != "EN", r["path"].upper()))
    DOCS.mkdir(exist_ok=True)
    cols = ["cpk", "path", "ext", "size", "magic", "nested", "inner", "overridden"]
    with open(DOCS / "inventory.tsv", "w", encoding="utf-8", newline="\n") as w:
        w.write("\t".join(cols) + "\n")
        for r in rows:
            w.write("\t".join(str(r[c]) for c in cols) + "\n")

    write_md(rows)
    print(f"{len(rows)} rows -> docs/inventory.tsv, docs/inventory.md")


def write_md(rows):
    def kind(r):
        return r["magic"] or r["ext"]

    L = ["# Инвентаризация текстовых и контейнерных файлов P5R (PC/Steam)", "",
         "Сгенерировано `tools/scripts/inventory.py`. Полный список — [inventory.tsv](inventory.tsv) "
         "(колонки: cpk, path, ext, size, magic, nested, inner, overridden).", "",
         "- `path` с `::` — файл внутри контейнера (PAK/PAC/BIN), напр. `INIT/X.PAK::Y.BMD`.",
         "- `magic` — тип по сигнатуре (`bmd` = MSG1, `bf` = FLW0), независимо от расширения.",
         "- `overridden=yes` — файл BASE.CPK, перекрытый одноимённым файлом из EN.CPK (игра берёт EN).",
         "- `inner` — число записей внутри контейнера.", "",
         "Источники: `C:\\SteamLibrary\\steamapps\\common\\P5R\\CPK\\EN.CPK` (целиком) и `BASE.CPK` "
         "(только bmd/bf/tbl/ftd/ctd/pak/pac/arc/fnt/msg). Оглавления всех CPK — [cpk_lists/](cpk_lists/).", ""]

    L += ["## Сводка по типам", "", "| CPK | уровень | тип | файлов | размер, КБ |", "|---|---|---|---:|---:|"]
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        k = (r["cpk"], "в контейнере" if r["nested"] else "файл", kind(r))
        agg[k][0] += 1
        agg[k][1] += r["size"]
    for (cpk, lvl, k), (c, s) in sorted(agg.items(), key=lambda x: (x[0][0] != "EN", x[0][1], -x[1][0])):
        L.append(f"| {cpk} | {lvl} | {k} | {c} | {s // 1024} |")

    txt = [r for r in rows if r["magic"] and not r["overridden"]]
    L += ["", "## Текстовые скрипты (BMD/BF), которые реально использует игра", "",
          "Без учёта BASE-файлов, перекрытых EN. Группировка по верхней папке.", "",
          "| CPK | папка | BMD | BF |", "|---|---|---:|---:|"]
    g = defaultdict(Counter)
    for r in txt:
        top = r["path"].split("::")[0].split("/")
        g[(r["cpk"], "/".join(top[:2]) if len(top) > 2 else top[0])][r["magic"]] += 1
    for (cpk, d), c in sorted(g.items(), key=lambda x: (x[0][0] != "EN", -sum(x[1].values()))):
        L.append(f"| {cpk} | {d} | {c['bmd']} | {c['bf']} |")
    tot = Counter(r["magic"] for r in txt)
    L += ["", f"**Итого:** BMD — {tot['bmd']}, BF — {tot['bf']}.", ""]

    L += ["## Таблицы (.tbl / .ctd / .ftd)", "", "| CPK | путь | размер |", "|---|---|---:|"]
    for r in rows:
        if r["ext"] in ("tbl", "ctd") or (r["ext"] == "ftd" and r["cpk"] == "EN"):
            L.append(f"| {r['cpk']} | `{r['path']}` | {r['size']} |")
    n_ftd_base = sum(1 for r in rows if r["ext"] == "ftd" and r["cpk"] == "BASE")
    L += ["", f"Плюс {n_ftd_base} .ftd в BASE (в основном параметры полей FIELD/FTD, не текст) — см. tsv.", ""]

    L += ["## Шрифты", "", "| CPK | путь | размер |", "|---|---|---:|"]
    for r in rows:
        if r["ext"] == "fnt":
            L.append(f"| {r['cpk']} | `{r['path']}` | {r['size']} |")

    L += ["", "## Контейнеры с текстом внутри", "",
          "Контейнеры верхнего уровня, внутри которых есть BMD/BF/TBL/CTD/FTD.", "",
          "| CPK | контейнер | BMD | BF | таблиц |", "|---|---|---:|---:|---:|"]
    cont = defaultdict(Counter)
    for r in rows:
        if r["nested"] and not r["overridden"]:
            top = r["path"].split("::")[0]
            k = r["magic"] or ("tbl" if r["ext"] in ("tbl", "ctd", "ftd") else None)
            if k:
                cont[(r["cpk"], top)][k] += 1
    for (cpk, p), c in sorted(cont.items(), key=lambda x: (x[0][0] != "EN", x[0][1])):
        L.append(f"| {cpk} | `{p}` | {c['bmd']} | {c['bf']} | {c['tbl']} |")
    (DOCS / "inventory.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
