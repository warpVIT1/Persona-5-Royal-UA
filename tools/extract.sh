#!/usr/bin/env bash
# Extracts game archives into extracted/ (read-only access to the game folder).
#   EN.CPK   -> extracted/EN   (everything)
#   BASE.CPK -> extracted/BASE (text/container types only)
# Also writes CPK tables of contents to docs/cpk_lists/ and rebuilds the inventory.
set -euo pipefail
cd "$(dirname "$0")/.."
GAME_CPK="${P5R_CPK:-C:/SteamLibrary/steamapps/common/P5R/CPK}"
CPK=tools/bin/cpktool/cpktool.exe

mkdir -p docs/cpk_lists
for c in EN BASE SOUND_E MOVIE_JE; do "$CPK" list "$GAME_CPK/$c.CPK" "docs/cpk_lists/$c.tsv"; done
"$CPK" extract "$GAME_CPK/EN.CPK" extracted/EN
"$CPK" extract "$GAME_CPK/BASE.CPK" extracted/BASE '\.(bmd|bf|tbl|ftd|ctd|pak|pac|arc|fnt|msg)$'
python tools/scripts/inventory.py
