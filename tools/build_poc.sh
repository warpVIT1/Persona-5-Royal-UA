#!/usr/bin/env bash
# Builds the proof-of-concept Reloaded-II mod: Ukrainian FONT0.FNT + one translated scene (casino prologue).
#   dist/p5rpc.ukrainian/  -> copy into Reloaded-II/Mods/
set -euo pipefail
cd "$(dirname "$0")/.."
C=tools/bin/AtlusScriptCompiler/AtlusScriptCompiler.exe
MOD=dist/p5rpc.ukrainian
CPK=$MOD/P5REssentials/CPK/EN.CPK

python tools/scripts/make_cyr_font.py
./tools/bin/fonttool/fonttool.exe build extracted/EN/FONT/FONT0.FNT work/font/ukr/glyphs.bin work/font/ukr/widths.tsv work/font/FONT0_UKR.FNT > work/font/build_ukr.log
cp work/font/ukr/P5R_UKR.tsv tools/bin/AtlusScriptCompiler/Charsets/

python tools/scripts/import_strings.py --path EN/EVENT_DATA/MESSAGE/E100/E100_002
python tools/scripts/import_strings.py --path EN/SCRIPT/FIELD/FSCR0150
rm -rf "$MOD" work/poc; mkdir -p "$CPK/FONT" "$CPK/EVENT_DATA/MESSAGE/E100" "$CPK/SCRIPT/FIELD" work/poc
cp translated/EN/EVENT_DATA/MESSAGE/E100/E100_002.BMD.msg work/poc/
(cd work/poc && "../../$C" E100_002.BMD.msg -Compile -OutFormat V1BE -Library P5R -Encoding P5R_UKR -Out E100_002.BMD > /dev/null)
cp work/poc/E100_002.BMD "$CPK/EVENT_DATA/MESSAGE/E100/"
# casino prologue field scripts (first lines of a new game): flow + Ukrainian msg -> BF
for b in FSCR0150_002_100 FSCR0150_002_110 FSCR0150_002_120 FSCR0150_003_100; do
  cp translated/EN/SCRIPT/FIELD/$b.BF.flow translated/EN/SCRIPT/FIELD/$b.BF.msg translated/EN/SCRIPT/FIELD/$b.BF.msg.h work/poc/
  (cd work/poc && "../../$C" $b.BF.flow -Compile -OutFormat V3BE -Library P5R -Encoding P5R_UKR -Out $b.BF > /dev/null)
  cp work/poc/$b.BF "$CPK/SCRIPT/FIELD/"
done
cp work/font/FONT0_UKR.FNT "$CPK/FONT/FONT0.FNT"
cp tools/mod/ModConfig.template.json "$MOD/ModConfig.json"
find "$MOD" -type f -printf "%s\t%p\n"
