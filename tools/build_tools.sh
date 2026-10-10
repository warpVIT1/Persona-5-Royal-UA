#!/usr/bin/env bash
# Clones third-party tools at pinned commits and builds them into tools/bin/.
# Requires: git, .NET SDK 8+.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p src bin

fetch() { # name url commit
  [ -d "src/$1/.git" ] || git clone -q "$2" "src/$1"
  git -C "src/$1" fetch -q --depth 1 origin "$3" 2>/dev/null || true
  git -C "src/$1" checkout -q "$3"
}

fetch Atlus-Script-Tools     https://github.com/tge-was-taken/Atlus-Script-Tools.git     1c557a092dd7610829b7215be0f0f5101acf1d72
fetch CriFsV2Lib             https://github.com/Sewer56/CriFsV2Lib.git                   169b001c748dfffc28c9fc14fcec269dd45e6eec
fetch AtlusFileSystemLibrary https://github.com/tge-was-taken/AtlusFileSystemLibrary.git d70da989be2d82179b58b81c104b46778f409c91  # reference only (PAK format)

dotnet publish src/Atlus-Script-Tools/Source/AtlusScriptCompiler/AtlusScriptCompiler.csproj -c Release -o bin/AtlusScriptCompiler
dotnet publish cpktool/cpktool.csproj -c Release -o bin/cpktool
