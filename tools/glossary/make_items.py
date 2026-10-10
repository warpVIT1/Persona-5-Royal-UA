"""Generate tools/glossary/proposals_items.tsv for consumables, key items and gifts.

Rules: ordinary objects/food — translated; brand-like and pun names — adapted (note column);
book/film titles — translated as titles; stat suffixes ST/MA/EN/AG/LU -> Сил/Маг/Вит/Спр/Удч.
Run: python tools/glossary/make_items.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATS = ("consumable", "key_item", "item")

STAT = {"ST": "Сил", "MA": "Маг", "EN": "Вит", "AG": "Спр", "LU": "Удч"}
WHO_GEN = {"Ann": "Анн", "Chihaya": "Тіхаї", "Futaba": "Футаби", "Haru": "Хару", "Hifumi": "Хіфумі",
           "Kawakami": "Кавакамі", "Makoto": "Макото", "Ohya": "Оя", "Sumire": "Суміре", "Takemi": "Такемі",
           "Ryuji": "Рюдзі", "Sojiro": "Содзіро", "Sae": "Сае"}
AIL = {"Brainwash": "промивання мізків", "Confuse": "сум'яття", "Despair": "відчаю", "Dizzy": "запаморочення",
       "Fear": "страху", "Forget": "забуття", "Rage": "люті", "Sleep": "сну"}
COLOR = {"Red": "Червоне", "Green": "Зелене", "Blue": "Синє"}
SIN = {"Gluttony": "ненажерливості", "Greed": "жадібності", "Jealousy": "заздрощів", "Lust": "хтивості",
       "Pride": "гордині", "Sorrow": "скорботи", "Vanity": "марнославства", "Wrath": "гніву"}
MAGATAMA = {"Arc": "дуги", "Blast": "вибуху", "Cyclone": "циклону", "Fire": "вогню", "Frost": "морозу",
            "Gale": "бурі", "Godly": "божества", "Grudge": "образи", "Hell": "пекла", "Holy": "святості",
            "Ice": "льоду", "Shock": "удару струмом"}


def pattern(en):
    m = re.fullmatch(r"(\w+)'s (Candy|Chocolate|Giri-Choco)", en)
    if m and m.group(1) in WHO_GEN:
        what = {"Candy": "Цукерки", "Chocolate": "Шоколад", "Giri-Choco": "Ввічливий шоколад"}[m.group(2)]
        return f"{what} від {WHO_GEN[m.group(1)]}", "Giri-choco — шоколад «з обов'язку», не романтичний." if "Giri" in en else ""
    m = re.fullmatch(r"(\w+) Vial ([LS])", en)
    if m and m.group(1) in AIL:
        return f"Флакон {AIL[m.group(1)]} {'(вел.)' if m.group(2) == 'L' else '(мал.)'}", ""
    m = re.fullmatch(r"(Red|Green|Blue) (\w+) Seed", en)
    if m and m.group(2) in SIN:
        return f"{COLOR[m.group(1)]} зерно {SIN[m.group(2)]}", ""
    m = re.fullmatch(r"(Incense|Ambergris|Nirvana) (ST|MA|EN|AG|LU)", en)
    if m:
        return f"{ {'Incense': 'Пахощі', 'Ambergris': 'Амбра', 'Nirvana': 'Нірвана'}[m.group(1)]}: {STAT[m.group(2)]}", ""
    m = re.fullmatch(r"Musk (ST|MA|EN|AG)-(MA|EN|AG|LU)", en)
    if m:
        return f"Мускус: {STAT[m.group(1)]}-{STAT[m.group(2)]}", ""
    m = re.fullmatch(r"(\w+) Magatama", en)
    if m and m.group(1) in MAGATAMA:
        return f"Магатама {MAGATAMA[m.group(1)]}", ""
    m = re.fullmatch(r"Torn Page (\d)", en)
    if m:
        return f"Вирвана сторінка {m.group(1)}", ""
    m = re.fullmatch(r"Movie (\d+) Ticket", en)
    if m:
        return f"Квиток у кіно {m.group(1)}", ""
    return None


MANUAL = """
1UP	1UP		Предмет-відсилка до ігор; лишаємо.
ABCs of Crafting	Абетка майстрування		Книга.
Abyss Gem	Самоцвіт безодні
Accu-Speed S	Аку-Спід S		Брендова назва ліків.
Acidic Coffee	Кисла кава
Adhesive Bandage	Пластир
Advanced	Просунутий		Рівень складності (риболовля/бейсбол).
Agodashi Oden	Агодасі-оден		Страва.
Air Cannon	Повітряна гармата
Alert Capsule	Капсула бадьорості
Aluminum Sheet	Алюмінієвий лист
Amateur Coffee	Аматорська кава
Amateur Curry	Аматорське карі
Angel Tart	Ангельський тарт
Ann Cream Puffs	Заварні тістечка від Анн
Aquarium-a-Day	Акваріум щодня		Журнал.
Arginade	Аргінад		Напій (гра слів з аргініном).
Aroma Machine	Аромадифузор
Atom Match	Атомний сірник
Autumn Bread	Осінній хліб
Awake Incense	Пахощі пробудження
Awakening Incense	Пахощі пробудження
Balloons	Повітряні кульки
Band-Ace	Бенд-Ейс		Пародія на Band-Aid.
Bank Blueprint	План банку
Bank Keycard	Ключ-картка банку
Baptismal Water	Вода хрещення
Basement Blueprint	План підвалу
Bath of Roses	Ванна з трояндами
Batting Coupon	Купон на бейсбольну тренувалку
Batting Science	Наука удару		Книга про бейсбол.
Beauty Aojiru	Аодзіру краси		Аодзіру — зелений напій.
Beef Patty Ration	Пайок: яловича котлета
Beginner	Початківець		Рівень складності.
Beni-Azuma	Бені-адзума		Сорт батату.
Best of KGB49	Найкраще з KGB49		Пародія на AKB48.
Billiards Magician	Маг більярду		Книга.
Bio Nutrients	Біодобрива
Bitter Coffee	Гірка кава
Black Frost Doll	Лялька Чорного Фроста
Black Mug	Чорна чашка
Bland Cheese	Прісний сир
Blaring Alarm Clock	Гучний будильник
Blaze Curry	Полум'яне карі
Blowtorch	Паяльна лампа
Blue Hyacinth	Синій гіацинт
Bonehead	Бовдур		Книга/фільм.
Book Cover	Обкладинка для книги
Boxing Card	Боксерська картка
Broken Laptop	Зламаний ноутбук
Broken Rock Salt	Подрібнена кам'яна сіль
Bubbly Hills, 90210	Бульбашкові пагорби, 90210		Пародія на Beverly Hills, 90210.
Buchi Calculator	Калькулятор Бучі
Buchiko's Story	Історія Бучіко
Buchimaru Doll	Лялька Бучімару
Building Blueprint	План будівлі
Burger-kun Doll	Лялька Бургер-куна		Талісман закладу; «-кун» лишаємо як частину імені.
Business Card	Візитка
CRT Television	Кінескопний телевізор
Call Me Chief	Звіть мене шефом		DVD/серіал.
Calling Postcard	Листівка-попередження		Не плутати з візитною карткою Злодіїв.
Calming Aroma	Заспокійливий аромат
Camera	Фотоапарат
Casino Map	Мапа казино
Castella	Кастелла		Бісквіт.
Castle Map	Мапа замку
Casual Rod	Звичайна вудка
Cell Key	Ключ від камери
Cereal Multi-Pack	Набір пластівців
Chief Clerk ID	Посвідчення головного клерка
Chief Director ID	Посвідчення головного директора
Chinese Sweets	Китайські солодощі
Choco Fountain	Шоколадний фонтан
Chunky Katsu	Товста котлета-кацу
Chunky Potage	Густий суп-пюре
Classical Hits	Класичні хіти
Cleaning Spray	Очищувальний спрей
Clothing Grab Bag	Мішок-сюрприз з одягом
Coin Jewel	Самоцвіт монет		Аркана Таро (масть).
Cologne	Одеколон
Condenser Lens	Конденсорна лінза
Cork Bark	Коркова кора
Corned Beef Special	Особлива солонина
Covertizer	Маскувальник
Creature	Створіння		Фільм.
Crime Lab Squad	Криміналістичний загін		Серіал.
Crimson Lipstick	Багряна помада
Cruise Ship Map	Мапа круїзного лайнера
Cry of Cthulhu	Поклик Ктулху		Пародія на «Поклик Ктулху».
Cup Jewel	Самоцвіт чаш
Cup Noodle Set	Набір локшини швидкого приготування
Curse Bomb	Бомба прокляття
DVD Player	DVD-програвач
Dart Set	Набір дротиків
Debilitator Ofuda	Офуда знесилення		Офуда — паперовий амулет.
Decent Curry	Пристойне карі
Decked Decarabia	Причепурена Декарабія		Фігурка.
Delish Bitterling	Смачний гірчак		Риба.
Designer Perfume	Дизайнерські парфуми
Desire and Hope	Бажання і надія		Предмет-сюжетна книга.
Devil Fruit	Диявольський плід
Die-soujou	Дай-сьодзьо		Фігурка (гра слів з Daisoujou).
Digital Camera	Цифрова камера
Dipped Katsu Sando	Кацу-сендвіч у соусі
Discharge Crystal	Розрядний кристал
Documentary Plans	План документального фільму
Dog Tag	Армійський жетон
Donut-Worry	Пончик-без-турбот		Гра слів Don't worry.
Double Bookmark	Подвійна закладка
Douse Orb	Гасильна сфера
Dr. Salt NEO	Доктор Солт NEO		Газований напій (пародія на Dr Pepper).
Dressed in Ashes	Вбрана в попіл		Книга.
Drizzled Natto	Натто з соусом
Durian Au Lait	Дуріан-о-ле
Dyed Handkerchief	Фарбована хустинка
Earl Green	Ерл Грін		Чай.
Earmuffs	Навушники від холоду
Earth Beans	Земляні боби
Electric Toothbrush	Електрична зубна щітка
Element Set	Набір стихій
Empowering Ofuda	Офуда наснаги
Essence of Fishing	Суть риболовлі		Книга.
Evil Snow Crystal	Злий сніговий кристал
Exorcism Water	Вода екзорцизму
Expert	Експерт		Рівень складності.
Expert Billiards	Більярд для експертів
Face Beautifier	Масажер для обличчя
Factorization Guide	Посібник з факторизації
Famidrive	Фамідрайв		Ретро-приставка (пародія на Famicom).
Fashion Magazine	Модний журнал
Feather Card	Пір'яна картка
Featherman Seeker	Пошуковець Фезермена		Іграшка.
Feathermen Dolls	Ляльки Фезерменів
Fighting Card	Бойова картка
Fire Curry	Вогняне карі
Fishpond Spotter	Пошуковець ставків		Журнал.
Five-inch Nail	П'ятидюймовий цвях
Flower Basket	Кошик квітів
Flowerpedia	Квітопедія
Forces Set	Набір сил
Foreign Nikuman	Закордонний ніку-ман		Ніку-ман — булочка на пару.
Fortune Tarot Card	Карта Таро «Фортуна»
Fountain Pen	Перова ручка
Free Darts Ticket	Квиток на безкоштовний дартс
Freeze Spray	Заморожувальний спрей
Fried Bread	Смажений хліб
Frui-Tea	Фрук-чай
Fruit Danish	Фруктова слойка
Fruit Ration	Фруктовий пайок
Fulfiller	Здійснювач
Gambla Goemon	Гамбла Гоемон		Ретро-гра (пародія на Ganbare Goemon).
Gambling Card	Картка азартних ігор
Game Secrets	Ігрові секрети		Журнал.
Garden Energy	Садова енергія		Добриво.
Gear Girimehkala	Гірімехкала-механізм		Фігурка.
Gecko Pin	Значок-гекон
Ghost Encounters	Зустрічі з привидами
Gi-Nyant Doll	Лялька Гі-Нянт
Giant Spatula	Велетенська лопатка
Glass Vase	Скляна ваза
Gloves	Рукавички
Golf Card	Гольфова картка
Golfer Sarutahiko	Гольфіст Сарутахіко		Фігурка.
Grappling Hook	Гак-кішка
Green Key	Зелений ключ
Guardian Boilie	Бойлі-охоронець		Бойлі — рибальська наживка.
Guilt Gem	Самоцвіт провини
Gun Controller	Світловий пістолет		Контролер для приставки.
Guy McVer	Гай Маквер		Пародія на MacGyver.
Gymnastics Baton	Гімнастична палиця
Hamaya	Хамая		Стріла-оберіг.
Hand Warmalizer	Грілка для рук
Happy Bomb	Весела бомба
Happy Pop	Веселий попкорн
Harder Core S	Хардкор S		Брендова назва ліків.
Harsh Coffee	Різка кава
Hat	Капелюх
Healing IV	Цілюща крапельниця
Heart Necklace	Намисто-серце
Heart Ring	Каблучка-серце
Hero Figure	Фігурка героя
Heroic Revelations	Героїчні одкровення
Hi-Tech Rod	Високотехнологічна вудка
High Limit Card	Картка високих ставок
High Limit Floor Map	Мапа поверху високих ставок
Hogyoku Apple	Яблуко Хогьоку
Holy Shroud	Свята плащаниця
Homemaker Hero	Герой-домогосподар		Книга.
Hot and Sour Tea	Гостро-кислий чай
Hustle S	Хасл S		Брендова назва ліків.
Hypno Mist	Гіпнотичний туман
I <3 Tokyo Shirt	Футболка «Я <3 Токіо»
ICU	Реанімація
Ichigaya Guardian	Охоронець Ітігаї		Риба-легенда.
Ichigaya Kingpin	Король Ітігаї		Риба-легенда.
Idaten Ofuda	Офуда Ідатен
Idol Pins	Значки айдолів
Idol Poster	Плакат айдола
Imported Protein	Імпортний протеїн
Insane	Божевільний		Рівень складності.
Intermediate	Середній		Рівень складності.
Interview Notes	Нотатки інтерв'ю
Intricate Bookmark	Вишукана закладка
Invincible Ofuda	Офуда непереможності
Iron Sand	Залізний пісок
Item Distributor	Роздавач предметів
Jack Frost Doll	Лялька Джека Фроста
Jagao Doll	Лялька Ягао
Jagariko	Джагаріко		Снек.
Jail Break	Втеча з в'язниці
Jam Bread	Хліб з джемом
Jose's Star	Зірка Хосе
Joylent	Джойлент		Пародія на Soylent.
Juicy Nikuman	Соковитий ніку-ман
Jump Cue	Кий для стрибка
Kajaclear-R	Кадзяклір-R		Ліки (знімає -кадзя).
Kamoshida's Medal	Медаль Камосіди
Kaneshiro's Journal	Щоденник Канесіро
Karaage King	Король караге
Katana Keychain	Брелок-катана
Kebab Ration	Пайок: кебаб
Key to Leblanc	Ключ від «Леблану»
King Piece	Фігура короля
Kinky Kin-Ki	Збочений Кін-Кі		Фігурка.
Kitchen Tools Set	Набір кухонного начиння
Knowing the Heart	Пізнаючи серце		Книга.
Kommissbrot	Коммісброт		Армійський хліб.
Kongou Ofuda	Офуда Конго
Kosha Piece	Фрагмент Коса
Kumade	Кумаде		Грабельки-талісман.
Kundaclear-R	Кундаклір-R		Ліки (знімає -нда).
Lab Blueprint	План лабораторії
Laptop	Ноутбук
Large Boilie	Великий бойлі
Learn Pro Darts	Вчимося професійного дартсу		Книга.
Leather Gloves	Шкіряні рукавички
Leather Pen Case	Шкіряний пенал
Leblanc Coffee	Кава з «Леблану»
Leblanc Curry	Карі з «Леблану»
Left Key	Лівий ключ
Legendary Yaki-Imo	Легендарний печений батат
Letter from Royalty	Лист від королівської особи
Lexy Doll	Лялька Лексі
Life Ointment	Мазь життя
Limelight	У центрі уваги		Книга.
Liquid Mercury	Рідка ртуть
Local Mascot Set	Набір місцевих талісманів
Lockpick	Відмичка
Lotto R	Лото R
Lotto S	Лото S
Love★Pancake	Кохання★Млинець
Lustful Left Eye	Хтиве ліве око
Luxury Aroma Set	Розкішний набір ароматів
MRE Ration	Сухий пайок
Magic Ointment	Магічна мазь
Magic Up Ofuda	Офуда магії
Magneto Coil	Магнітна котушка
Makara Hammer	Молот макари
Makoto Donuts	Пончики від Макото
Manta	Манта
Master Coffee	Кава від майстра
Master Curry	Карі від майстра
Master Swordsman	Майстер меча		Книга.
Mayo Locust	Сарана з майонезом
Medium Boilie	Середній бойлі
Medjed Menace	Загроза Меджеда
Mega Fertilizer	Мегадобриво
Megido Bomb	Бомба мегідо
Melon Pan	Мелон-пан		Солодка булочка.
Member's Card	Членська картка
Members Floor Map	Мапа поверху для членів клубу
Membership Card	Членська картка
Mental Floss	Ментальна нитка		Гра слів (dental floss).
Mini Cactus	Міні-кактус
Mini Dominion	Міні-Панування		Фігурка.
Miracle Rod	Чудо-вудка
Miso Starfish	Морська зірка в місо
Mixed Nuts	Горіхове асорті
Mochi Cushion	Подушка-моті
Moist Protein	Вологий протеїн
Molotov Cocktail	Коктейль Молотова
Money Distributor	Роздавач грошей
Mont Blanc Ration	Пайок: монблан
Moon Dango	Місячні данго
Moonlight Carrot	Морква місячного світла
Morgana's Scarf	Шарф Моргани
Mossy Mothman	Мшиста Людина-метелик		Фігурка.
Motorbike Figure	Фігурка мотоцикла
Mouse M.D.	Миша, доктор медицини		Фільм.
Muffler	Шарф
Muscle Tea	М'язовий чай
Museum Brochure 1	Буклет музею 1
Museum Brochure 2	Буклет музею 2
Musty Pages	Затхлі сторінки
Mystery Stew	Таємниче рагу
Nakano Walker	Накано Вокер		Журнал-путівник.
Napolitan Nikuman	Ніку-ман «Наполітан»
Nastea	Настіа		Гра слів nasty + tea; напій.
Nasty Aojiru	Гидкий аодзіру
Night Pennant	Нічний вимпел
Night Skies	Нічні небеса
Nightlife Hotspots	Гарячі точки нічного життя
Nofeever Sheet	Ноуфівер-пластир		Жарознижувальний пластир.
Nohar-M	Ноухар-М		Ліки.
Non-Static Gum	Антистатична жуйка
Nostalgic Steak	Ностальгічний стейк
Not-so-hot Betsy	Не дуже гаряча Бетсі		Фільм.
Nude Statue	Оголена статуя
Nuke Cracker	Ядерна петарда
Oatmeal Ration	Пайок: вівсянка
Oh! Shiruko	О! Сіруко		Солодкий суп з бобів.
Oil Painting Set	Набір для олійного живопису
Old Key	Старий ключ
Old Man's Elixir	Еліксир старого
Old Videotape	Стара відеокасета
Omni-Vitamin	Мультивітамін
Onsen Aojiru	Онсен-аодзіру
Oo-hot Tea	Ух-гарячий чай		Гра слів (oolong).
Osechi Chocolate	Шоколад осеті		Новорічна їжа.
Osechi Ration	Пайок осеті
Ouija Board	Дошка Уіджа
PC Tool Set	Набір інструментів для ПК
Paper Bag	Паперовий пакет
Party in a Can	Вечірка в банці
Peerless Carp	Неперевершений короп
Pen Case	Пенал
Peppery Nikuman	Перчений ніку-ман
Perma-Pick	Вічна відмичка
Personnel ID	Посвідчення співробітника
Phantom Wafers	Фантомні вафлі
Photo of Clara	Фото Клари
Physical Ointment	Фізична мазь
Pirate Legend	Піратська легенда		Книга.
Plant Balm	Бальзам для рослин
Popcorn Bomb	Попкорн-бомба
Power Intuition	Сила інтуїції		Книга.
Powerful Rod	Потужна вудка
Promise List	Список обіцянок
Protein	Протеїн
Psy-Wheel	Псі-колесо
Psycho Bomb	Псі-бомба
Pumpkin Soup	Гарбузовий суп
Punch Ouch	Пунш-ой		Гра слів (punch).
Puzzle Rings	Кільця-головоломка
Pyramid Sketch	Ескіз піраміди
Quick Spray	Швидкий спрей
Railroad Card	Залізнична картка
Rakugo Collection	Збірка ракуго		Японські комічні оповіді.
Ramen Bowl	Миска рамену
Randy Right Eye	Хтиве праве око
Rasetsu Ofuda	Офуда Расецу
Rasta Sandalwood	Растасандал
Raw Punch	Сирий удар
Recipe Notes	Нотатки з рецептами
Reckless Casanova	Безрозсудний Казанова		Книга/фільм.
Recov-R: 100 mg	Рековер: 100 мг		Брендові ліки; «-R» → «-р».
Recov-R: 50 mg	Рековер: 50 мг
Recover Oil	Відновлювальна олія
Red Fish	Червона риба
Red Key	Червоний ключ
Red Phosphorus	Червоний фосфор
Refresh Aroma	Освіжальний аромат
Rejection Gem	Самоцвіт відмови
Rejuvenating IV	Омолоджувальна крапельниця
Relax Gel	Розслаблювальний гель
Relaxing Coffee	Розслаблювальна кава
Renew-All	Рінью-Ол		Ліки.
Repentance Ashes	Попіл каяття
Research Notebook	Дослідницький записник
Reserve Ammo	Запасні набої
Revivadrin	Ревівадрин		Ліки.
Rich Cheese	Насичений сир
Right Key	Правий ключ
Robot Vacuum	Робот-пилосос
Rough Carp	Грубий короп
Royal Jelly R	Маточне молочко R
Rubbish	Сміття
Ryuji Dog	Рюдзі-дог		Хот-дог (гра слів).
Sacramental Bread	Причасний хліб
Sadayo Taiyaki	Тайякі від Садайо
Sakura Amezaiku	Сакура-амедзайку		Цукрова скульптура.
Sakura Fan	Віяло з сакурою
Sakura Mochi	Сакура-моті
Salvation S	Спасіння S
Sanctuary Gem	Самоцвіт святилища
Sandwich	Сендвіч
Saturn Fries	Картопля «Сатурн»
Scarlet Rose	Багряна троянда
Scratch Lottery	Миттєва лотерея
Sea Slug Doll	Лялька-голозябровий молюск
Seafood Aojiru	Аодзіру з морепродуктами
Second Maid	Друга покоївка
Section Chief ID	Посвідчення начальника відділу
Security Keycard	Ключ-картка охорони
Seeker's Tools	Інструменти шукача
Segaki Rice	Рис сегакі
Seven-Color Trout	Семибарвна форель
Sharp Cheese	Гострий сир
Sheep Man Doll	Лялька Людини-вівці
Shitamachi Reborn	Відродження Сітаматі
Shooting Card	Стрілецька картка
Shumai Cushion	Подушка-шумай
Sikkenine	Сіккенін		Ліки.
Sikkenine A	Сіккенін A
Sikkenine EX	Сіккенін EX
Silk Yarn	Шовкова пряжа
Silver Bangle	Срібний браслет
Sincere Omelette	Щирий омлет
Skytree Lamp	Лампа «Скайтрі»
Small Boilie	Малий бойлі
Small Key	Маленький ключ
Smokescreen	Димова завіса
Snack Pack	Набір снеків
Social Thought	Суспільна думка		Книга.
Soothing Soba	Заспокійлива соба
Spaceport Map	Мапа космопорту
Special Chimaki	Особливий тімакі
Speed Reader	Швидкочитач		Книга.
Sports Sunglasses	Спортивні окуляри
Sports Watch	Спортивний годинник
Spotlight	Прожектор
Spring Fruit Pack	Весняний набір фруктів
Squid Tri-Pack	Потрійний набір кальмарів
Stamina Kit L	Набір витривалості (вел.)
Stamina Kit S	Набір витривалості (мал.)
Stamp Book	Книжка для печаток
Stamp Card	Картка з печатками
Star Forneus	Зірковий Форнеус		Фігурка.
Star Lilina's New CD	Новий CD зірки Ліліни
Star Mirror	Зіркове дзеркало
Star Onion	Зіркова цибуля
Star Stickers	Наліпки-зірочки
Star Water Tray	Зіркова таця для води
Starvicks	Старвікс		Пародія на Starbucks.
Sticky Hairball	Липка грудка шерсті
Stolen Papyrus	Викрадений папірус
Straw Doll	Солом'яна лялька
Strawberry Curry	Полуничне карі
Strawberry Daifuku	Полуничне дайфуку
Strength Up Ofuda	Офуда сили
Stronger Lift S	Стронгер-ліфт S		Брендова назва.
Stun Gun	Електрошокер
Summer Lotto R	Літнє лото R
Summer Lotto S	Літнє лото S
Sun Tomato	Сонячний помідор
Supernova Burger	Бургер «Наднова»
Surprise Sando	Сендвіч-сюрприз
Sushi Teacup	Чашка для суші
Suspicious Boilie	Підозрілий бойлі
Swan Boat	Човен-лебідь
Sword Jewel	Самоцвіт мечів
Takemedic	Такемедик		Ліки Такемі (гра слів).
Takemedic-All	Такемедик-Ол
Takemedic-All V	Такемедик-Ол V
Takemedic-All Z	Такемедик-Ол Z
Tanned Leather	Дублена шкіра
Tee	Футболка
Tetra Hammer	Молот тетри
Thaw Stone	Камінь відлиги
The Alluring Dancer	Чарівна танцівниця		Книга/фільм.
The Art of Automata	Мистецтво автоматів		Книга.
The Art of Charm	Мистецтво чарівності		Книга.
The Beefcake Book	Книга м'язистих красенів
The Craft of Cinema	Ремесло кіно		Книга.
The Fader	Згасання		Фільм.
The Gallant Rogue	Шляхетний пройдисвіт		Книга.
The Great Thief	Великий злодій		Книга.
The Hero with a Bow	Герой з луком		Книга.
The Illusory Popess	Примарна папеса		Книга.
The King Book	Книга короля
The Queen Book	Книга королеви
The Running Dead	Мерці, що біжать		Пародія на The Walking Dead.
The Slave Book	Книга раба
The X Folders	Теки X		Пародія на The X-Files.
Theme Park Escort	Супровід у парку розваг
Thick Parchment	Товстий пергамент
Tidying the Heart	Порядок у серці		Книга.
Tin Clasp	Олов'яна застібка
Tokyo Bitterling	Токійський гірчак		Риба.
Tokyo Shrines	Святилища Токіо		Журнал.
Top-class Boilie	Першокласний бойлі
Torimeshi Ration	Пайок торімесі
Totem Pole	Тотемний стовп
Tower Map	Мапа вежі
Train of Life	Потяг життя		Книга.
Treasure Trap	Пастка скарбу
Treasure Trout	Скарбова форель
Truffles	Трюфелі
Udagawa Soda	Содова «Удагава»
Udagawa Water	Вода «Удагава»
Uji Matcha Flan	Флан з матчею Удзі
Ultimate Amazake	Найкраще амадзаке
Ultimate Spray	Найкращий спрей
Unlimited Service	Необмежене обслуговування
VIP Invitation	VIP-запрошення
Vacuum Cutter	Вакуумний різак
Vague	Вейг		Журнал (пародія на Vogue).
Veg. Stew Ration	Пайок: овочеве рагу
Venus Salad	Салат «Венера»
Vermilion Disk	Кіноварний диск
Viennese Jelly	Віденське желе
Vitality Aojiru	Аодзіру життєвої сили
Wand Jewel	Самоцвіт жезлів
Wanna-kun Doll	Лялька Ванна-куна
Water of Rebirth	Вода відродження
Watercolor Postcard	Акварельна листівка
Weakener Spray	Послаблювальний спрей
Weekend Parks	Парки вихідного дня		Журнал.
White Carp	Білий короп
Wide Eye Drops	Очні краплі «Широкий погляд»
Wine of Grace	Вино благодаті
Wise Men's Words	Слова мудреців		Книга.
Woman in the Dark	Жінка в темряві		Фільм.
Wraith	Примара		Фільм.
Wrist Weights	Обважнювачі для зап'ясть
Wristwatch	Наручний годинник
Yakisoba Pan	Якісоба-пан		Булочка з локшиною.
Yellow Gerbera	Жовта гербера
Yoncha Walker 04	Йонтя Вокер 04		Журнал-путівник Йонген-Дзяя.
Zorro, the Outlaw	Зорро, поза законом		Книга.
Inferno Curry	Пекельне карі		
Movie Ticket	Квиток у кіно		
"""


def main():
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    rows = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["category"] in CATS and r["status"] != "approved" and r["en"] not in main_prop:
                rows.append(r)
    manual = {}
    for l in MANUAL.strip().splitlines():
        en, uk, alt, note = (l.split("\t") + ["", "", ""])[:4]
        manual[en] = (uk, alt, note)
    out, missing = [], []
    for r in sorted(rows, key=lambda r: r["en"]):
        en = r["en"]
        if en in manual:
            uk, alt, note = manual[en]
        else:
            p = pattern(en)
            if not p:
                missing.append(en)
                continue
            (uk, note), alt = p, ""
            note = note or "шаблон"
        out.append((en, uk, alt, r["category"], note))
    with open(ROOT / "tools/glossary/proposals_items.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for row in out:
            f.write("\t".join(row) + "\n")
    print(f"{len(out)} written, {len(missing)} missing: {missing}")


if __name__ == "__main__":
    main()
