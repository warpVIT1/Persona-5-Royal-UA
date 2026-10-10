"""Sanity checks for tools/glossary/proposals*.tsv: non-Ukrainian characters and mixed-script words
(a Latin 'i'/'a'/'o' inside a Cyrillic word looks identical but breaks the game's charset)."""
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OK_EXTRA = set("«»—–’ʼ…★·−")
problems = 0
for f in sorted(glob.glob(str(ROOT / "tools/glossary/proposals*.tsv"))):
    for line in open(f, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) < 2 or line.startswith(("#", "en\t")):
            continue
        en, uk = p[0], p[1]
        odd = [c for c in uk if ord(c) > 127 and not ("Ѐ" <= c <= "ӿ" or c in OK_EXTRA)]
        # each hyphen-separated part must be single-script ("USB-кабель" is fine, "Пiксі" is not)
        mixed = [w for w in re.findall(r"[\w'ʼ’]+", uk) if re.search("[Ѐ-ӿ]", w) and re.search("[A-Za-z]", w)]
        if odd or mixed:
            problems += 1
            print(f"{Path(f).name}: {en!r} -> {uk!r} odd={odd} mixed={mixed}")
print(f"{problems} problem lines")
sys.exit(1 if problems else 0)
