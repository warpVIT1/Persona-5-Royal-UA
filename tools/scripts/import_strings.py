"""Build translated/ (.msg/.flow, same layout as source_en/) from strings_uk/.

For every source_en/**/*.msg: pages whose id has a non-empty "uk" in the matching
strings_uk JSON get prefix + uk + suffix; everything else stays English.
Speakers are replaced via strings_uk/_speakers.json. .flow and .msg.h files are copied as is.

  python tools/scripts/import_strings.py            # all files
  python tools/scripts/import_strings.py --path EN/EVENT_DATA/MESSAGE/E100   # only a subtree
  python tools/scripts/import_strings.py --init     # create empty strings_uk/ skeletons that don't exist yet
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import msgfmt as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SRC, EN, UK, OUT = ROOT / "source_en", ROOT / "strings_en", ROOT / "strings_uk", ROOT / "translated"


def init_skeletons():
    n = 0
    for en_path in sorted(EN.rglob("*.json")):
        if en_path.name.startswith("_"):
            continue
        uk_path = UK / en_path.relative_to(EN)
        if uk_path.exists():
            continue
        data = json.loads(en_path.read_text(encoding="utf-8"))
        entries = [dict(id=e["id"], speaker=e["speaker"], en=e["text"], uk="", note="")
                   for e in data["entries"] if e["translate"]]
        uk_path.parent.mkdir(parents=True, exist_ok=True)
        uk_path.write_text(json.dumps(dict(file=data["file"], entries=entries), ensure_ascii=False, indent=1),
                           encoding="utf-8")
        n += 1
    sp_uk = UK / "_speakers.json"
    if not sp_uk.exists():
        sp = json.loads((EN / "_speakers.json").read_text(encoding="utf-8"))
        sp_uk.write_text(json.dumps({k: "" for k in sp}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"created {n} skeleton files in strings_uk/")


def build(prefix=""):
    sp_path = UK / "_speakers.json"
    speakers = {k: v for k, v in json.loads(sp_path.read_text(encoding="utf-8")).items() if v} if sp_path.exists() else {}
    n_files = n_pages = 0
    for src in sorted(SRC.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(SRC)
        if not rel.as_posix().startswith(prefix):
            continue
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix != ".msg":
            shutil.copyfile(src, dst)
            continue
        uk_path = UK / (rel.as_posix() + ".json")
        uk = {}
        if uk_path.exists():
            uk = {e["id"]: e["uk"] for e in json.loads(uk_path.read_text(encoding="utf-8"))["entries"] if e.get("uk")}
        en_entries = json.loads((EN / (rel.as_posix() + ".json")).read_text(encoding="utf-8"))["entries"]
        dialogs = M.parse(src.read_text(encoding="utf-8-sig"))
        it = iter(en_entries)  # entries are in page order; ids carry disambiguation suffixes
        # the phone chat shows no names but picks each avatar by the EN speaker name (FONT/SPEAKER.DAT):
        # keep the original names there, otherwise every icon falls back to Morgana
        keep_names = rel.as_posix().startswith("EN/CAMP/CHAT/")
        for d in dialogs:
            if d.speaker and d.speaker in speakers and not keep_names:
                d.header = d.header.replace(f"[{d.speaker}]", f"[{speakers[d.speaker]}]", 1)
            for p in d.pages:
                e = next(it)
                if e["id"] in uk:
                    p.text = uk[e["id"]]
                    n_pages += 1
        dst.write_text(M.write(dialogs), encoding="utf-8")
        n_files += 1
    print(f"translated/: {n_files} msg files written, {n_pages} pages replaced, {len(speakers)} speakers mapped")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--path", default="", help="only files under this prefix, e.g. EN/EVENT_DATA/MESSAGE/E100")
    a = ap.parse_args()
    init_skeletons() if a.init else build(a.path)
