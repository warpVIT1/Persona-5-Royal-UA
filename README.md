# Persona 5 Royal — українська фан-локалізація (PC/Steam)

Мод для Reloaded-II + P5R Essentials (BF/BMD/PAK emulators). Оригінальні файли гри не змінюються.

## Для гравців

### Що перекладено
- усі діалоги сюжету, Конфіденти, телефонні чати, імена мовців;
- меню, предмети, навички, Персони, вороги, підказки;
- мапа, станції та описи районів, місця у списку збережень;
- журнал активності, нотатки календаря, ранги соціальних характеристик;
- меню навчальних довідок і сюжетних розділів, довідка Оксамитової кімнати;
- коментарі Фан-сайту;
- репліки навігаторів у бою (Морґана, Футаба, Акечі), екран збереження, «Нова гра+»;
- субтитри аніме-роликів;
- шрифт з українськими літерами (ґ, є, і, ї), перемальовані текстури;
- введення імені героя та назви команди українською (розкладка ЙЦУКЕН).

Ще в роботі: рядки інтерфейсу всередині P5R.exe (дні тижня, тактика, частина бойових написів),
кросворди, частина текстур із написами.

### Встановлення
1. Встановіть [Reloaded-II](https://github.com/Reloaded-Project/Reloaded-II/releases) і додайте до нього Persona 5 Royal.
2. Встановіть мод: кнопка 1-click install на [GameBanana](https://gamebanana.com/mods/731484), пошук у Reloaded-II
   («Download Mods» → «Persona 5 Royal — Українська локалізація») або архів `Mod.zip` з
   [Releases](https://github.com/warpVIT1/Persona-5-Royal-UA/releases), розпакований у `Reloaded-II/Mods`.
3. Увімкніть мод (Persona 5 Royal Essentials підтягнеться автоматично).
4. Мова гри в Steam — **English**.
5. Запустіть гру через Reloaded-II. Оновлення приходять автоматично.

### Запуск зі Steam кнопкою «Грати»
1. Один раз запустіть гру через Reloaded-II (мод сам скопіює лаунчер).
2. Steam → Persona 5 Royal → Властивості → Загальні → **Параметри запуску** → вставте:
   `cmd /c ""%LOCALAPPDATA%\P5R_UA\launcher\P5R_UA_Launcher.exe" %command%"`
3. Далі просто натискайте «Грати».

Не вмикайте «Deploy ASI Loader» у Reloaded-II — з ним P5R зависає на чорному екрані.

### Нюанси
- Під час набору імені видно латиницю — кирилицею ім'я стає після підтвердження.
- Імена зі збережень інших перекладів: Configure Mod → «Перетворити ім'я зі старого перекладу»;
  у списку збережень кирилиця з'явиться після повторного збереження.
- Якщо раніше ставили інший переклад прямо в теку гри — спершу Steam → Перевірити цілісність файлів
  (і видаліть `TRANSL.DAT` та `xinput1_4.dll`, якщо вони лишилися).
- Якщо щось не працює — надішліть `Reloaded-II\Mods\p5rpc.ukrainian\exebmd_log.txt` і скріншот
  в [Issues](https://github.com/warpVIT1/Persona-5-Royal-UA/issues).

## Для розробників

### Структура

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

### Пайплайн

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

### Формат рядків

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

### Етапи

1. Інструменти, розпакування, інвентаризація ✔
2. Експорт тексту, валідатор ✔
3. Глосарій — `glossary.csv`, рішення в `docs/glossary_decisions.md`
4. Переклад
5. Шрифт і кодування (кирилиця)
6. Збірка мода Reloaded-II
7. Список текстур із запеченим текстом
8. Інсталятор, що автоматично ставить локалізацію (Reloaded-II, P5R Essentials, мод)


## Подяки

- Перемальовані текстури (меню, мапа, вивіски, міні-ігри, титульний екран) — команда [LBK](https://lbklauncher.com/).
