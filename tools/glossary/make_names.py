"""Generate tools/glossary/proposals_names.tsv for speakers, NPCs, field labels, titles.

Glossary gets only what must be identical everywhere:
  * proper names (Kovalenko transliteration), "X's Voice", "Shadow X", "(Phone) X";
  * movie / drink / show titles, field actions, stat-raising activities.
Everything else (role names like "Timid Man", tutorial headings, inspect labels, mined fragments)
gets an empty uk = status `text`: translated in context together with the dialogue (stage 4).
Run: python tools/glossary/make_names.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATS = ("speaker", "npc", "field_check", "term?", "movie", "field_action", "ui", "activity")

NAMES = """
Eiko	Ейко
Tsuda	Цуда
Rumi	Румі
Takakura	Такакура
Yamauchi	Ямаууті
Mika	Міка
Akiyama	Акіяма
Ms. Kawakami	пані Кавакамі
Iida	Ііда
Tsukasa	Цукаса
Nakanohara	Наканохара
Oyamada	Оямада
Nakaoka	Накаока
Tanaka	Танака
Kawanabe	Каванабе
Takeishi	Такеісі
Masa	Маса
Taihei	Тайхей
Nishiyama	Нісіяма
Takekuma	Такекума
Coach Hiraguchi	тренер Хірагуті
Shibusawa	Сібусава
Sakoda	Сакода
Ms. Chouno	пані Тьоно
Osagiri	Осагірі
King Yama	Цар Яма
Octavius	Октавій
Star Lilina	зірка Ліліна
Yokoda	Йокода
Alya	Аля
Nakaoka and Takeishi	Накаока й Такеісі
Hisashi Ushiwata	Хісасі Усівата
Shinsuke Kishi	Сінсуке Кісі
Dietman Matsushita	депутат Мацусіта
Wanna-Wanna-kun	Ванна-Ванна-кун
Chairman Fukurai	голова Фукурай
Mr. Hiruta	пан Хірута
Mr. Ushimaru	пан Усімару
Yumeko Mogami	Юмеко Могамі
Lala Escargot	Лала Ескарго
Benzo	Бендзо
Clara	Клара
Cognitive Wakaba	Когнітивна Вакаба
Cognitive Akechi	Когнітивний Акеті
Daisuke Takanashi	Дайсуке Таканасі
Hanasaki	Ханасакі
Ikeda-senpai	Ікеда-семпай
Kazuo Tsuboi	Кадзуо Цубой
Keisuke	Кейсуке
Mitsumi Kure	Міцумі Куре
Muneo Horiguchi	Мунео Хорігуті
Muneo's Grandson	онук Мунео
Nanami	Нанамі
Phantom Thief Alibaba	Фантомний Злодій Алібаба
Red Eagle	Червоний Орел
Shiro Asakura	Сіро Асакура
Yuuta	Юта
Katsushika	Кацусіка
Artie Lury	Арті Люрі
Fumio Akitsu	Фуміо Акіцу
Julian	Джуліан
Kuroko Hara	Куроко Хара
Miki-chan	Мікі-тян
Mr. Inui	пан Інуї
Ms. Usami	пані Усамі
Sayuri Yoshioka	Саюрі Йосіока
Shigeru Ooe	Сігеру Ое
Politician Ooe	політик Ое
Takuro	Такуро
Tohru	Тору
Tomoko Kamata	Томоко Камата
Tsubakiyama	Цубакіяма
Yasuo Jochi	Ясуо Дзьоті
Yoshihito Wakasa	Йосіхіто Вакаса
Yoshimori Sakoda	Йосіморі Сакода
Yusei Arita	Юсей Аріта
Anji Fuwa	Андзі Фува
Muhen	Мухен
(Phone) Kawakami	(Телефон) Кавакамі
??? Yoshizawa	??? Йосідзава
Daichi Nakamura	Дайті Накамура
Doctor Mouse	Доктор Миша
Hitoe Takeishi	Хітое Такеісі
Keiko Shiratori	Кейко Сіраторі
Matoba	Матоба
Megumi Hoshii	Мегумі Хосії
Nene Otsubo	Нене Оцубо
Ryota Tennou	Рьота Тенно
Sachiko Kuwai	Сатіко Куваї
Sadao Hashisato	Садао Хасісато
Seiji Kanemoto	Сейдзі Канемото
Shinichi Yoshizawa	Сінїті Йосідзава
Showai Shigeta	Сьоваї Сігета
Thuggish Masa	Бандюк Маса
Trader Sakai	трейдер Сакаї
Ann and Makoto	Анн і Макото
Caroline & Justine	Кароліна й Жюстіна
Igor?	Ігор?
Mako	Мако
Kidd	Кідд
Procky	Прокі
Tycoon	Магнат
Beauty Thief	Злодійка краси
The King	Король
Treasure Demons	Скарбові демони
Twin Wardens	Наглядачки-близнючки
God of Control	Бог контролю
Prime Minister	прем'єр-міністр
Velvet Resident	Мешканка Оксамитової кімнати
Student Called Yoshizawa	Учениця на прізвище Йосідзава
Man Called Shibusawa	Чоловік на прізвище Сібусава
Futaba's Uncle	дядько Футаби
Hifumi's Mother	мати Хіфумі
Shinya's Mother	мати Сін'ї
Takase's Female Relative	родичка Такасе
Takase's Male Relative	родич Такасе
Ririna Fan Club President	голова фан-клубу Ріріни
Mosquiternum	Москітернум
Phoneternum	Фонетернум
Scrapeternum	Скрепетернум
Alligater	Алігейтер
Phanboy	Фанбой
Day of Fates	День долі
Phoenix Rangers	Рейнджери Фенікса
Tanaka's Shady Commodities	Сумнівні товари Танаки
The Tale of the Bamboo Cutter	Повість про старого бамбукоруба
Legend of Gambla Goemon	Легенда про Гамблу Гоемона
Yoshida Toranosuke Impression Management	Управління іміджем Тораносуке Йосіди
Town Detectives	Міські детективи
Holy Stones	Святі камені
Good Tora	Добрий Тора
Tora	Тора
Debug Mode	Режим налагодження
Counter Revolution	Контрреволюція
Thieves Guild	Гільдія Злодіїв
The Thieves Guild	Гільдія Злодіїв
Money	Гроші
Le Misérable	Знедолений
Like A Dragon	Як дракон
Heart	Серце
Love Possibly	Кохання, можливо
Pach-Saw	Пач-пила
Tanktop Millionaire	Мільйонер у майці
The Cake Knight Rises	Лицар тістечок повертається
Back to the Ninja	Назад до ніндзя
Bite Club	Бійцівський прикус
Admission Impossible	Вступ неможливий
Clean Hard	Міцний прибиральник
Finding Beemo	У пошуках Бімо
Magic Fizz	Магічна шипучка
Mightini	Могутіні
Omni-Fizz	Омні-шипучка
Power Fizz	Шипучка сили
Saraemon	Сараемон
Soultini	Душетіні
The Duhvengers	Месники-дурники
Underwear	Спідня білизна
Ali Dance Punch	Пунш «Танок Алі»
Arabian Knight	Арабський лицар
Arms Master Punch	Пунш «Майстер зброї»
Charge-ade	Заряд-ад
Concentr-ade	Концентр-ад
Debilit-ade	Знесил-ад
Fujiyama Soul	Душа Фудзіями
Heat Riser Punch	Пунш «Розпал»
Makarakarn Soda	Содова «Макаракарн»
Marakukaja Soda	Содова «Маракукадзя»
Marakunda Soda	Содова «Маракунда»
March of the Lambs	Марш ягнят
Masukukaja Soda	Содова «Масукукадзя»
Masukunda Soda	Содова «Масукунда»
Matarukaja Soda	Содова «Матарукадзя»
Matarunda Soda	Содова «Матарунда»
Merry Christmess	Веселого Різдвяного безладу
Over the Pigeon's Nest	Пролітаючи над голубиним гніздом
Red string	Червона нитка
Royal Rainbow	Королівська веселка
Salty Ocean	Солоний океан
Showtime Redemption	Шоутайм: втеча з Шоушенка
Sonic Boom	Звуковий бум
Spell Master Punch	Пунш «Майстер заклинань»
Tetrakarn Soda	Содова «Тетракарн»
The Goodfather	Добрий хрещений батько
Volcano	Вулкан
Train	Потяг
Consult	Порадитися
Return to Metaverse	Повернутися до Метавсесвіту
Unlock	Відімкнути
Break Wall	Пробити стіну
Brew Coffee	Зварити каву
Call Elevator	Викликати ліфт
Climb	Залізти
Control Dimmer	Регулювати світло
Crawl	Проповзти
Cross Over	Перелізти
Crossword Puzzle	Кросворд
Emerge	Вилізти
Flip Sign	Перевернути табличку
Go Batting	Піти на тренувалку
Go to Bed	Лягти спати
Jump Down	Зістрибнути
Jump Out of Painting	Вистрибнути з картини
Jump into Painting	Стрибнути в картину
Kick Down	Вибити ногою
Let Your Mind Wander	Помріяти
Open Chest	Відкрити скриню
Open Door	Відчинити двері
Open Vault	Відкрити сховище
Operate Lift	Керувати підйомником
Pull Jaw	Потягнути щелепу
Pull Lever	Потягнути важіль
Rat Walk	Пройти щурячим ходом
Return to Reality	Повернутися в реальність
Save Woman	Врятувати жінку
Slide	Проковзнути
Slide Down	З'їхати
Take Elevator Down	Ліфтом униз
Take Elevator Up	Ліфтом угору
Take Will Seed	Взяти Зерно Волі
Use Keycard	Скористатися карткою
Improve Charm	Покращити чарівність
Improve Guts	Покращити сміливість
Improve Kindness	Покращити доброту
Improve Knowledge	Покращити знання
Improve Proficiency	Покращити вправність
Increase HP	Збільшити ОЗ
Increase SP	Збільшити ОД
Clean Up	Прибирання
Beef Bowl Job	Робота в закусочній з гюдоном
Crossroads Job	Робота в барі «Crossroads»
Florist Job	Робота у квітковій крамниці
Outing With the Twins	Прогулянка з близнючками
Store Job	Робота в магазині
"""

VOICE_GEN = {"Akechi": "Акеті", "Alibaba": "Алібаби", "Ann": "Анн", "Kaneshiro": "Канесіро", "Kawakami": "Кавакамі",
             "Lavenza": "Лавенци", "Madarame": "Мадараме", "Makoto": "Макото", "Maruki": "Марукі",
             "Mishima": "Місіми", "Ryuji": "Рюдзі", "Sae": "Сае", "Sojiro": "Содзіро", "Yamauchi": "Ямаууті",
             "SIU Director": "директора ВСР", "Former Noble": "колишнього аристократа",
             "Shadow Futaba": "Тіні Футаби", "Shadow Sae": "Тіні Сае"}
SHADOW = {"Madarame": "Мадараме", "Okumura": "Окумури", "Futaba": "Футаби", "Kamoshida": "Камосіди",
          "Shido": "Сідо", "Iwai": "Іваї", "Mishima": "Місіми", "Mariko": "Маріко", "Tamako": "Тамако"}


def pattern(en):
    m = re.fullmatch(r"(.+)'s Voice", en)
    if m and m.group(1) in VOICE_GEN:
        return f"Голос {VOICE_GEN[m.group(1)]}"
    m = re.fullmatch(r"Shadow (\w+)", en)
    if m and m.group(1) in SHADOW:
        return f"Тінь {SHADOW[m.group(1)]}"
    return None


def main():
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    rows = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["category"] in CATS and r["status"] != "approved" and r["en"] not in main_prop:
                rows.append(r)
    N = dict(l.split("\t", 1) for l in NAMES.strip().splitlines())
    n_name = n_text = 0
    with open(ROOT / "tools/glossary/proposals_names.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for r in sorted(rows, key=lambda r: r["en"]):
            uk = N.get(r["en"]) or pattern(r["en"])
            if uk:
                n_name += 1
                f.write(f"{r['en']}\t{uk}\t\t{r['category']}\t{'' if r['en'] in N else 'шаблон'}\n")
            else:
                n_text += 1
                f.write(f"{r['en']}\t\t\t{r['category']}\tперекладається в контексті (етап 4)\n")
    print(f"{n_name} names/titles, {n_text} -> text")


if __name__ == "__main__":
    main()
