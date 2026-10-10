# Persona 5 Royal — українська фан-локалізація (PC/Steam)

Мод для Reloaded-II + P5R Essentials (BF/BMD/PAK emulators). Оригінальні файли гри не змінюються.

## Структура

| Шлях | Що це | У git |
|---|---|---|
| `tools/cpktool/` | CLI для читання/розпакування CPK (поверх CriFsV2Lib, з дешифруванням P5R) | так |
| `tools/scripts/` | Python-скрипти пайплайну (див. нижче) | так |
| `tools/build_tools.sh` | Клонує й збирає сторонні інструменти на зафіксованих комітах | так |
| `tools/extract.sh` | Розпаковує EN.CPK і текстові файли BASE.CPK у `extracted/` | так |
| `docs/` | Інвентаризація, звіти, статистика кодів | так |
| `strings_uk/` | **Переклад** (JSON, редагується вручну) | так |
| `glossary.csv` | Глосарій (en, uk, альтернативи, категорія, частота, статус) | так |
| `tools/glossary/proposals.tsv` | Ручні пропозиції перекладу термінів | так |
| `extracted/` | Розпаковані файли гри | ні |
| `source_en/` | Декомпільовані `.msg` / `.flow` / `.msg.h` (EN) | ні |
| `strings_en/` | Рядки для перекладу (JSON на файл + `_all.csv`, `_speakers.json`) | ні |
| `translated/` | `.msg` / `.flow` з підставленим перекладом | ні |
| `tools/src/`, `tools/bin/` | Сирці та збірки сторонніх інструментів | ні |

## Пайплайн

```sh
bash tools/build_tools.sh                         # інструменти
P5R_CPK="C:/SteamLibrary/steamapps/common/P5R/CPK" bash tools/extract.sh   # extracted/ + docs/inventory.*
python tools/scripts/decompile_all.py             # extracted/ -> source_en/  (BMD -> .msg, BF -> .flow + .msg)
python tools/scripts/export_strings.py            # source_en/ -> strings_en/
python tools/scripts/import_strings.py --init     # порожні шаблони strings_uk/ (не перезаписує наявні)
python tools/scripts/validate.py                  # перевірка перекладу
python tools/scripts/import_strings.py            # strings_en + strings_uk -> translated/
python tools/scripts/roundtrip_test.py --sample 100   # самоперевірка пайплайну
python tools/scripts/glossary_candidates.py      # кандидати в глосарій -> docs/glossary_candidates.tsv
python tools/scripts/build_glossary.py           # glossary.csv (затверджені рядки не перезаписуються)
```

## Формат рядків

Кожна сторінка діалогу (`[s] … [e]`) ділиться на три частини:

- `prefix` — службові коди на початку (`[s]`, `[bup …]`, `[vp …]`, `[f …]`), не перекладаються;
- `text` — те, що перекладаємо; може містити вбудовані коди: `[n]` (перенос рядка, можна переставляти),
  `[clr N]` (колір), `[fName]`/`[lName]` (ім'я героя), `[var N]`, `[ref …]`, `[stLabel N]` тощо — їх
  треба зберегти (валідатор перевіряє набір);
- `suffix` — службові коди в кінці (`[n][f 1 3 65535][w][e]`), не перекладаються.

Літеральні дужки в тексті пишуться як `\[` і `\]`.

Файл перекладу `strings_uk/<шлях>.json`:

```json
{"file": "EN/EVENT_DATA/MESSAGE/E800/E827_123.BMD",
 "entries": [{"id": "MSG_000_0_0#0", "speaker": "Iwai", "en": "I see. Yeah…", "uk": "", "note": ""}]}
```

Порожній `uk` — ще не перекладено (лишається англійський текст). Імена мовців перекладаються один раз
у `strings_uk/_speakers.json`.

## Етапи

1. Інструменти, розпакування, інвентаризація ✔
2. Експорт тексту, валідатор ✔
3. Глосарій — `glossary.csv`, рішення в `docs/glossary_decisions.md`
4. Переклад
5. Шрифт і кодування (кирилиця)
6. Збірка мода Reloaded-II
7. Список текстур із запеченим текстом
8. Інсталятор, що автоматично ставить локалізацію (Reloaded-II, P5R Essentials, мод)
