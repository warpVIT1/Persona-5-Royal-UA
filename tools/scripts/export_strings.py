"""Export translatable strings from source_en/**/*.msg into strings_en/.

One JSON per .msg file (mirrors source_en paths, "X.msg" -> "X.msg.json"):
{
  "file": "EN/EVENT_DATA/MESSAGE/E800/E827_123.BMD",   # game file (container entries as dirs)
  "source": "source_en/EN/.../E827_123.BMD.msg",
  "entries": [
    {"id": "MSG_000_0_0#0", "kind": "msg", "speaker": "Iwai",
     "prefix": "[s][bup 0 104 0 0 0]...", "text": "I see. Yeah...[n]and ...", "suffix": "[n][f 1 3 65535][w][e]",
     "translate": true,
     "context": {"dialog": "MSG_000_0_0", "page": 0, "pages": 3, "max_line": 37, "lines": 2}}
  ]
}
`translate` is false for pages with no visible text and for Japanese leftovers ("lang": "ja" —
placeholder/voice-only lines Atlus left untranslated in the EN release; listed in docs/japanese_leftovers.md).
Prefix/suffix are fixed; only `text` is translated.

Also writes:
  strings_en/_speakers.json  — speaker name -> occurrence count (translated once, globally)
  strings_en/_all.csv        — every translatable entry in one table (id, file, speaker, text, context)
  docs/codes.md              — statistics of control codes
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CJK = re.compile(r"[぀-ヿ一-鿿]")  # kana + CJK ideographs
SRC = ROOT / "source_en"
DST = ROOT / "strings_en"


def game_file(msg_path):
    rel = msg_path.relative_to(SRC).as_posix()
    return rel[: -len(".msg")]  # "EN/.../X.BF.msg" -> "EN/.../X.BF"


def export_file(path, speakers, code_stats):
    dialogs = M.parse(path.read_text(encoding="utf-8-sig"))
    entries = []
    for d in dialogs:
        if d.speaker:
            speakers[d.speaker] += 1
        for i, p in enumerate(d.pages):
            vis = M.visible(p.text).strip()
            ls = M.lines(p.text)
            for k, v, tag in M.tokenize(p.raw):
                if k == "code":
                    where = "text" if v in p.text and tag in M.INLINE_CODES else "fixed"
                    code_stats[(tag, where)] += 1
            lang = "ja" if CJK.search(vis) else "en"
            entries.append(dict(
                id=f"{d.name}#{i}", kind=d.kind, speaker=d.speaker, lang=lang,
                prefix=p.prefix, text=p.text, suffix=p.suffix,
                translate=bool(vis) and lang == "en",
                context=dict(dialog=d.name, page=i, pages=len(d.pages),
                             max_line=max((len(x) for x in ls), default=0), lines=len(ls)),
            ))
    ids = Counter(e["id"] for e in entries)
    dup = [k for k, v in ids.items() if v > 1]
    if dup:  # same dialog name twice in one file — disambiguate by order
        seen = Counter()
        for e in entries:
            if e["id"] in dup:
                seen[e["id"]] += 1
                e["id"] += f"~{seen[e['id']]}"
    return dict(file=game_file(path), source=path.relative_to(ROOT).as_posix(), entries=entries)


def main():
    speakers, code_stats = Counter(), Counter()
    rows, n_files, ja = [], 0, Counter()
    for path in sorted(SRC.rglob("*.msg")):
        data = export_file(path, speakers, code_stats)
        out = DST / (path.relative_to(SRC).as_posix() + ".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        n_files += 1
        for e in data["entries"]:
            if e["lang"] == "ja":
                ja[data["file"]] += 1
            if e["translate"]:
                rows.append([e["id"], data["file"], e["speaker"] or "", e["text"],
                             f"{e['kind']} page {e['context']['page'] + 1}/{e['context']['pages']}"])

    (DST / "_speakers.json").write_text(
        json.dumps(dict(speakers.most_common()), ensure_ascii=False, indent=1), encoding="utf-8")
    with open(DST / "_all.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "file", "speaker", "text", "context"])
        w.writerows(rows)

    write_ja_report(ja)
    words = sum(len(re.findall(r"[A-Za-z']+", M.visible(r[3]))) for r in rows)
    uniq = len({r[3] for r in rows})
    L = ["# Управляющие коды в текстах P5R", "",
         "Сгенерировано `tools/scripts/export_strings.py`. `в тексте` — код внутри переводимой части "
         "(переводчик сохраняет его, может переставить); `служебный` — в неизменяемых prefix/suffix.", "",
         f"Файлов: {n_files}, переводимых строк (страниц): {len(rows)}, уникальных: {uniq}, слов (EN): {words}, "
         f"спикеров: {len(speakers)}.", "",
         "| код | в тексте | служебный |", "|---|---:|---:|"]
    tags = defaultdict(lambda: [0, 0])
    for (tag, where), c in code_stats.items():
        tags[tag][0 if where == "text" else 1] += c
    for tag, (a, b) in sorted(tags.items(), key=lambda x: -sum(x[1])):
        L.append(f"| `{tag}` | {a} | {b} |")
    (ROOT / "docs/codes.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{n_files} files, {len(rows)} translatable entries, {uniq} unique, {words} words, {len(speakers)} speakers")


def write_ja_report(ja):
    by_dir = Counter()
    for f, c in ja.items():
        by_dir["/".join(f.split("/")[:3])] += c
    L = ["# Японские остатки в EN-версии", "",
         "Страницы, где видимый текст содержит японские символы. В EN-релизе это, по всей видимости, "
         "служебные заглушки (`【仮】ダミー`), звуковые ремарки (`(軽く笑う)`) и неиспользуемые скрипты "
         "(BASE-файлы, не перекрытые EN). По умолчанию они **не переводятся** (`translate: false`, `lang: ja`). "
         "Если какая-то из них всплывёт в игре — включаем перевод для конкретного файла.", "",
         f"Всего страниц: {sum(ja.values())}, файлов: {len(ja)}.", "",
         "## По папкам", "", "| папка | страниц |", "|---|---:|"]
    L += [f"| {k} | {v} |" for k, v in by_dir.most_common()]
    L += ["", "## По файлам", "", "| файл | страниц |", "|---|---:|"]
    L += [f"| `{k}` | {v} |" for k, v in sorted(ja.items())]
    (ROOT / "docs/japanese_leftovers.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
