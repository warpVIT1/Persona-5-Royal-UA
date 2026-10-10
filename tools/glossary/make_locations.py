"""Generate tools/glossary/proposals_locations.tsv for remaining location names.

Rules: Japanese toponyms — Kovalenko transliteration; Mementos paths (Qliphoth sephirot) —
transliteration; room/floor names — translation; subway-map captions — translated as short slogans.
Run: python tools/glossary/make_locations.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATHS = {"Qimranut": "Кімранут", "Aiyatsbus": "Айяцбус", "Chemdah": "Хемда", "Kaitul": "Кайтул",
         "Akzeriyyuth": "Акзерійют", "Adyeshach": "Адйешах", "Sheriruth": "Шерірут", "Da'at": "Даат",
         "Iweleth": "Івелет"}
INVITE = {"Ann": "Анн", "Futaba": "Футабу", "Haru": "Хару", "Makoto": "Макото", "Ryuji": "Рюдзі", "Yusuke": "Юсуке"}

MANUAL = """
1st Exhibition Room	Перша виставкова зала
2nd Exhibition Room	Друга виставкова зала
??? Auditorium	??? Аудиторія
??? Corridor	??? Коридор
??? Entrance Hall	??? Вестибюль
??? Entryway	??? Вхід
??? Monitoring Room	??? Кімната спостереження
??? Test Track	??? Випробувальний трек
??? Warehouse	??? Склад
Accessway	Прохід
Airport Lobby	Зала аеропорту
Akasaka-Mitsuke	Акасака-Міцуке
Akihabara Arcade	Аркада в Акіхабарі
Akihabara Gigolo	«Жиголо» в Акіхабарі
Akihabara Station	станція Акіхабара
Aoyama Platform	Платформа Аояма
Aoyama-Itchome Station	станція Аояма-Іттьоме
Aoyama-Itchome Station Platform	Платформа станції Аояма-Іттьоме
Assembly Hall	Актова зала
Atelier	Майстерня
Attic	Горище
Awards	Нагороди
Back Deck	Кормова палуба
Backstreets	Провулки
Banker Passageway	Прохід банкірів
Bar Maradonna	Бар «Марадонна»
Barracks	Казарми
Bars Open to Minors	Бари, відкриті для неповнолітніх
Battle Arena	Бойова арена
Beach	Пляж
Book Town	Книжкове містечко
Boss's Car	Машина шефа
Boss's House	Дім шефа
Buffet	Шведський стіл
Buffet Venue	Зала шведського столу
Built on a River	Збудований на річці
Cancel	Скасувати
Casino Entrance	Вхід до казино
Castle Gate	Брама замку
Cavernous Void	Печериста порожнеча
Central Factory	Центральний завод
Central Garden	Центральний сад
Central Hall 2F	Центральна зала, 2 пов.
Central Passage	Центральний прохід
Central Tower	Центральна вежа
Chamber of Emptiness	Зала порожнечі
Chamber of Guilt	Зала провини
Chamber of Rejection	Зала відмови
Chamber of Sanctuary	Зала святилища
Chamber of Sanctuary East	Зала святилища, схід
Chamber of Sanctuary West	Зала святилища, захід
Chamber of Sarcophagi	Зала саркофагів
Chapel	Каплиця
Chinatown	Чайнатаун
Church	Церква
Classroom	Класна кімната
Classroom Building	Навчальний корпус
Clear Data	Очистити дані
Club, VIP Seating	Клуб, VIP-зона
Cognitive Control Room	Когнітивна диспетчерська
Construction Site	Будмайданчик
Corridor	Коридор
Corridor Bottom	Низ коридору
Corridor Middle	Середина коридору
Corridor Summit	Вершина коридору
Counselling Room	Кабінет психолога
Courthouse	Будівля суду
Courtroom	Зала суду
Courtyard	Внутрішній двір
Crossroads	Перехрестя
Darkness Goal	Ціль темряви
Desert Town	Пустельне місто
Dice Game Area	Зона гри в кості
Diet Building (Metaverse)	Будівля парламенту (Метавсесвіт)
Diet Building (Real)	Будівля парламенту (реальність)
Disposal Line	Лінія утилізації
Dome Town	Доум-Таун
Downtown Fishing	Риболовля в центрі
East Building Annex	Прибудова Східного корпусу
Electric Town	Електричне місто
Empty Room	Порожня кімната
Engine Room	Машинне відділення
Enjoy the Stars	Милуйтеся зорями
Enter Mementos	Увійти до Мементосу
Entertainment Hall	Розважальна зала
Entrance Hall	Вестибюль
Entryway	Вхід
Exam Room	Оглядовий кабінет
Expensive Sushi Shop	Дорогий суші-ресторан
Export Line	Лінія експорту
Facility Passageway	Прохід комплексу
Facility Surroundings	Околиці комплексу
Ferris Wheel	Оглядове колесо
Find Your Own Style	Знайди свій стиль
Fishing Pond	Рибальський ставок
Front Deck	Носова палуба
Front Hall	Передня зала
Futaba's Room	Кімната Футаби
Gallery	Галерея
Get Cultured in Art	Долучіться до мистецтва
Giant Market	Величезний ринок
Ginza Line Gate	Турнікети лінії Гіндза
Ginza Ticket Gate	Турнікети Гіндзи
Go to Kichijoji Station	До станції Кітідзьодзі
Great Corridor	Великий коридор
Hall of the Grail	Зала Грааля
Hallway	Коридор
Head Down	Спуститися
Head Up	Піднятися
Heart of the Nation	Серце нації
Hidden Chamber	Прихована зала
High Limit Floor	Поверх високих ставок
High Limit Lobby	Хол високих ставок
Holy Grail Temple	Храм Святого Грааля
Hometown	Рідне місто
Hotel Elevator	Ліфт готелю
Hotel Lobby	Хол готелю
House of Darkness	Дім темряви
Ichigaya	Ітігая
Inside	Усередині
Inside Leblanc	У «Леблані»
Inside Limousine	У лімузині
Inside Vault	У сховищі
Interrogation Room	Кімната для допитів
Intimate Date Spot	Місце для інтимного побачення
Iweleth	Івелет
Jinbocho	Дзімботьо
Jumbotron	Великий екран
Kamehameha Statue	Статуя Камеамеа
Kanda Church	Церква в Канді
Kanda Station	станція Канда
Kaneshiro's Hideout	Сховок Канесіро
Kichijoji Station	станція Кітідзьодзі
Laboratory Auditorium	Аудиторія лабораторії
Laboratory Corridor	Коридор лабораторії
Laboratory Entrance Hall	Вестибюль лабораторії
Laboratory Entryway	Вхід до лабораторії
Laboratory Monitoring Room	Кімната спостереження лабораторії
Laboratory Test Track	Випробувальний трек лабораторії
Laboratory Warehouse	Склад лабораторії
Landing	Сходовий майданчик
Laundering Office	Контора з відмивання грошей
Leave	Піти
Lip-smackin' Good Ramen	Рамен — пальчики оближеш
Lobby	Хол
Lower Passageway	Нижній прохід
Lower Port Hallway	Нижній лівий коридор
Lower Starboard Hallway	Нижній правий коридор
Lowest Passageway	Найнижчий прохід
Madarame Residence	Резиденція Мадараме
Madarame's Exhibition	Виставка Мадараме
Maihama	Маіхама
Main Floor	Головний поверх
Main Hall	Головна зала
Main Treasure Hall	Головна скарбниця
Manager's Area	Зона менеджера
Members Floor	Поверх для членів клубу
Members Floor Lobby	Хол поверху для членів клубу
Mementos Depths	Глибини Мементосу
Mementos Entrance	Вхід до Мементосу
Mid Port Hallway	Середній лівий коридор
Mid-Starboard Hallway	Середній правий коридор
Middle Passageway	Середній прохід
Miura Beach	Пляж Міура
Miyashita Park	Парк Міясіта
Mock Exam Site	Місце пробного іспиту
Monitoring Prep Room	Підготовча кімната спостереження
Monjayaki Shop	Мондзяякі-закусочна
Morgana Car	Машина-Моргана
Movie	Кіно
Museum	Музей
Museum Entrance	Вхід до музею
Music Player	Музичний програвач
Mysterious Shrine	Таємниче святилище
Nagatacho	Нагататьо
Nakano	Накано
Near the Diet Building	Біля будівлі парламенту
News Studio	Студія новин
Nostalgic Japanese Flavor	Ностальгійний японський смак
Not Just High Rent	Не лише висока оренда
Not Just for Bookworms	Не лише для книголюбів
Observation Deck: Top Section	Оглядовий майданчик: верхня частина
Ochanomizu	Отяномідзу
Office	Офіс
Ogikubo	Огікубо
Okumura Estate	Маєток Окумури
Okumura Foods HQ	Штаб-квартира «Окумура Фудс»
PM's Residence	Резиденція прем'єр-міністра
Palace Maker	Конструктор Палаців
Path of New Plans	Шлях нових задумів
Path to the Holy Grail	Шлях до Святого Грааля
Planetarium	Планетарій
Play Area	Ігрова зона
Playing with Fire	Гра з вогнем
Police Station	Поліцейська дільниця
Pool Deck	Палуба з басейном
Practice Building	Практичний корпус
Pray Your Heart Out	Моліться від щирого серця
Press Conference	Прес-конференція
Previous Area	Попередня зона
Prison Passageway	Тюремний прохід
Production Line	Виробнича лінія
Progress Further	Йти далі
Prosecutor's Home	Дім прокурора
Prosecutor's Office	Прокуратура
Psientific Model Eden	Псі-наукова модель «Едем»
Psientific Model Eden Prep Room	Підготовча кімната моделі «Едем»
Pyramid Entrance	Вхід до піраміди
Qliphoth World	Світ Кліфот
Red-light District	Квартал червоних ліхтарів
Reflect on Your Past	Озирніться на своє минуле
Research Ward	Дослідницьке крило
Research Ward Prep Room	Підготовча кімната дослідницького крила
Residential District	Житловий квартал
Restaurant	Ресторан
Return to Shibuya	Повернутися до Сібуї
Roof	Дах
Rooftop	Дах
Roppongi	Роппонгі
Royal Cabin	Королівська каюта
SIU Director's Office	Кабінет директора ВСР
SP Exhibition Room	Спецвиставкова зала
School	Школа
School Building	Шкільна будівля
School Gate	Шкільна брама
Seaside Park	Приморський парк
Shibumachi	Сібуматі
Shibuya Arcade	Аркада в Сібуї
Shibuya Gigolo	«Жиголо» в Сібуї
Shibuya Station Square	Привокзальна площа Сібуї
Shido's Room	Кімната Сідо
Shinjuku Bar	Бар у Сіндзюку
Shinjuku Station	станція Сіндзюку
Shopping District	Торговий квартал
Shopping Mall	Торговий центр
Shrine	Святилище
Shrine Entrance	Вхід до святилища
Shujin Cafeteria	Їдальня Сюдзіну
Shujin Classroom	Клас Сюдзіну
Shujin Courtyard	Двір Сюдзіну
Shujin Library	Бібліотека Сюдзіну
Shujin Rooftop	Дах Сюдзіну
Shujin School Gate	Шкільна брама Сюдзіну
Side Deck	Бічна палуба
Side Entrance	Бічний вхід
Sky Tower	Небесна вежа
Sleep with the Fishes	Спати з рибами
Slot Room	Зала ігрових автоматів
Sports Gym	Спортзал
Stadium Construction Site	Будмайданчик стадіону
Staff-Only Area	Службова зона
Station Exit	Вихід зі станції
Station Square	Привокзальна площа
Storage Area	Комора
Subway Platform	Платформа метро
Subway Train	Потяг метро
Suidobashi	Суйдобасі
TDL	TDL
TV Studio	Телестудія
Takemi Medical Clinic	Клініка Такемі
Takenoko Street Fashion	Мода вулиці Такеноко
Takeshita Street	вулиця Такесіта
Teikyu Accessway	Прохід «Тейкю»
The Forefront of Trends	На вістрі трендів
The Land of Dreams	Країна мрій
Thieves Den	Лігво Злодіїв
Throne Room	Тронна зала
Tomes and Spice	Томи та спеції
Tourist Heaven	Рай для туристів
Train Station	Залізнична станція
Training Hall of Love	Тренувальна зала кохання
Transfer Line	Лінія переміщення
Treasure Hall	Скарбниця
Treasure Hall Gallery	Галерея скарбниці
Treasure Hall Lounge	Вітальня скарбниці
Treasure Room	Кімната скарбу
Tsukiji	Цукідзі
Tsukishima	Цукісіма
Twilight Corridor	Сутінковий коридор
Twilight Corridor Prep Room	Підготовча кімната сутінкового коридору
Ultimate Urban Leisure	Найкращий міський відпочинок
Under Bridge	Під мостом
Underground Cavern	Підземна печера
Underground Corridor	Підземний коридор
Underground Mall	Підземний торговий центр
Underground Prison	Підземна в'язниця
Underground Vault	Підземне сховище
Underground Walkway	Підземний перехід
Underground Waterway	Підземний водоканал
Untouchable	«Недоторканний»
Upper Main Hall	Верхня головна зала
Upper Passageway	Верхній прохід
Upper Starboard Hallway	Верхній правий коридор
Vault	Сховище
Vault Center	Центр сховища
Visiting Room	Кімната побачень
Waikiki Beach	Пляж Вайкікі
Wanderlust	Жага мандрів
Warehouse	Склад
Warehouse Prep Room	Підготовча кімната складу
Weapon Maintenance	Обслуговування зброї
Weapon Production	Виробництво зброї
Yongen-Jaya Platform	Платформа Йонген-Дзяя
Yongen-Jaya Station	станція Йонген-Дзяя
Yongen-Jaya Station Platform	Платформа станції Йонген-Дзяя
"""


def pattern(en):
    m = re.fullmatch(r"(\S+): (Area (\d+)|\?\?\?|Treasure Area)", en)
    if m and m.group(1) in PATHS:
        tail = f"зона {m.group(3)}" if m.group(3) else ("???" if m.group(2) == "???" else "зона скарбу")
        return f"{PATHS[m.group(1)]}: {tail}"
    m = re.fullmatch(r"(Classroom|Practice|East|West) (?:Building|Bldg) (\d)F", en)
    if m:
        b = {"Classroom": "Навчальний корпус", "Practice": "Практичний корпус", "East": "Східний корпус",
             "West": "Західний корпус"}[m.group(1)]
        return f"{b}, {m.group(2)} пов."
    m = re.fullmatch(r"Vault: (\d)F", en)
    if m:
        return f"Сховище: {m.group(1)} пов."
    m = re.fullmatch(r"Invite (\w+)", en)
    if m and m.group(1) in INVITE:
        return f"Запросити {INVITE[m.group(1)]}"
    m = re.fullmatch(r"(Placement Item|Stamp) (\d+)", en)
    if m:
        return f"{'Предмет для розміщення' if m.group(1) == 'Placement Item' else 'Печатка'} {m.group(2)}"
    return None


def main():
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    rows = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["category"] == "location" and r["status"] != "approved" and r["en"] not in main_prop:
                rows.append(r)
    M = dict(l.split("\t", 1) for l in MANUAL.strip().splitlines())
    out, missing = [], []
    for r in sorted(rows, key=lambda r: r["en"]):
        uk = M.get(r["en"]) or pattern(r["en"])
        (out.append((r["en"], uk, "" if r["en"] in M else "шаблон")) if uk else missing.append(r["en"]))
    with open(ROOT / "tools/glossary/proposals_locations.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for en, uk, note in out:
            f.write(f"{en}\t{uk}\t\tlocation\t{note}\n")
    print(f"{len(out)} written, {len(missing)} missing: {missing}")


if __name__ == "__main__":
    main()
