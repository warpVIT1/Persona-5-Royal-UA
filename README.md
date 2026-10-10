# Persona 5 Royal — українська фан-локалізація (PC/Steam)

Мод для Reloaded-II + P5R Essentials (BF/BMD/PAK emulators). Оригінальні файли гри не змінюються.

## Структура

| Шлях | Що це | У git |
|---|---|---|
| `tools/cpktool/` | CLI для читання/розпакування CPK (поверх CriFsV2Lib, з дешифруванням P5R) | так |
| `tools/scripts/` | Python-скрипти (інвентаризація, далі — експорт/валідація тексту) | так |
| `tools/build_tools.sh` | Клонує й збирає сторонні інструменти на зафіксованих комітах | так |
| `tools/extract.sh` | Розпаковує EN.CPK і текстові файли BASE.CPK у `extracted/` | так |
| `docs/` | Інвентаризація, оглавлення CPK | так |
| `tools/src/`, `tools/bin/` | Сирці та збірки сторонніх інструментів | ні |
| `extracted/` | Розпаковані файли гри | ні |

## Відтворення

```sh
bash tools/build_tools.sh
P5R_CPK="C:/SteamLibrary/steamapps/common/P5R/CPK" bash tools/extract.sh
```
