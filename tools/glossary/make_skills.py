"""Generate tools/glossary/proposals_skills.tsv for todo skills (skill, skill_alt, skill_card).

Rules (approved in docs/glossary_decisions.md, item 4):
  * spell series (Agi, Bufu, Zio, Mudo, Hama, -kaja, -nda, Patra ...) — transliteration (Kovalenko);
  * descriptive names — translation;
  * patterned names (Null Fire, Fire Boost, Low Burn, Magic Up 2 ...) — generated from templates below,
    so the whole family stays consistent.
Run: python tools/glossary/make_skills.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# element: (nominative, genitive)
EL = {"Phys": ("Фіз", "фіз. атак"), "Gun": ("Вогн", "вогнепальної зброї"), "Fire": ("Вогонь", "вогню"),
      "Ice": ("Лід", "льоду"), "Elec": ("Ел", "електрики"), "Wind": ("Вітер", "вітру"), "Psy": ("Псі", "псі"),
      "Nuke": ("Ядер", "ядерної енергії"), "Bless": ("Світло", "світла"), "Curse": ("Прокляття", "прокляття"),
      "Almighty": ("Всемогутня", "всемогутніх атак"), "Bless/Curse": ("Світло/Прокляття", "світла й прокляття")}
# ailment: genitive
AIL = {"Burn": "опіку", "Freeze": "замороження", "Shock": "шоку", "Dizzy": "запаморочення", "Confuse": "сум'яття",
       "Fear": "страху", "Forget": "забуття", "Sleep": "сну", "Rage": "люті", "Despair": "відчаю",
       "Brainwash": "промивання мізків", "Hunger": "голоду", "Insta-kill": "миттєвої смерті"}
AIL_NOM = {"Burn": "Опік", "Freeze": "Замороження", "Shock": "Шок", "Dizzy": "Запаморочення", "Confuse": "Сум'яття",
           "Fear": "Страх", "Forget": "Забуття", "Sleep": "Сон", "Rage": "Лють", "Despair": "Відчай",
           "Brainwash": "Промивання мізків", "All Ail": "Усі стани"}
LVL = {"Low": "низ.", "Med": "сер.", "Mid": "сер.", "High": "вис."}


def pattern(en):
    m = re.fullmatch(r"(Null|Resist|Repel|Drain|Dodge|Evade) (.+)", en)
    if m:
        verb, what = m.groups()
        if what.endswith(" Insta-kill"):
            el = what[: -len(" Insta-kill")]
            if verb == "Null" and el in EL:
                return f"Імунітет до миттєвої смерті від {EL[el][1]}"
        gen = EL.get(what, (None, None))[1] or AIL.get(what)
        if gen:
            return {"Null": f"Імунітет до {gen}", "Resist": f"Опір {gen}", "Repel": f"Відбиття {gen}",
                    "Drain": f"Поглинання {gen}", "Dodge": f"Ухилення від {gen}", "Evade": f"Уникнення {gen}"}[verb]
    m = re.fullmatch(r"(\S+) (Boost|Amp|Break|Wall|Magatama|Ball)", en)
    if m and m.group(1) in EL:
        n, g = EL[m.group(1)]
        return {"Boost": f"Посилення {g}", "Amp": f"Надпосилення {g}", "Break": f"Пробиття опору {g}",
                "Wall": f"Стіна від {g}", "Magatama": f"Магатама: {n.lower()}", "Ball": f"Куля: {n.lower()}"}[m.group(2)]
    m = re.fullmatch(r"(\S+) Boost", en)
    if m and m.group(1) in AIL:
        return f"Посилення {AIL[m.group(1)]}"
    m = re.fullmatch(r"(Low|Med|High) (.+)", en)
    if m and m.group(2) in AIL_NOM:
        return f"{AIL_NOM[m.group(2)]} ({LVL[m.group(1)]})"
    m = re.fullmatch(r"(.+?) (Unison Attack)", en)
    if m and not m.group(1).startswith("UNUSED"):
        names = {"Ryuji": "Рюдзі", "Ann": "Анн", "Morgana": "Моргана", "Mona": "Мона", "Yusuke": "Юсуке",
                 "Makoto": "Макото", "Haru": "Хару", "Futaba": "Футаба", "Akechi": "Акеті", "Kasumi": "Касумі",
                 "Protag": "Протагоніст", "Ikumi": "Ікумі"}
        who = "/".join(names.get(x, x) for x in m.group(1).split("/"))
        return f"Спільна атака: {who}"
    m = re.fullmatch(r"(.+?) (\d+|★)", en)  # numbered trait families
    if m and m.group(1) in NUMBERED:
        return f"{NUMBERED[m.group(1)]} {m.group(2)}"
    m = re.fullmatch(r"(Phys|Magic|Heal|Attack|Insta-kill SP|Critical Up|Technical Up|Magic Up|Phys Up|Critical Rate Up) "
                     r"\((Low|Mid|High)\)", en)
    if m:
        base = {"Phys": "Фіз. витрати", "Magic": "Маг. витрати", "Heal": "Витрати на лікування",
                "Attack": "Витрати на атаку", "Insta-kill SP": "ОД за миттєве вбивство"}.get(m.group(1))
        base = base or {"Critical Up": "Шанс крит. удару", "Technical Up": "Технічний удар+", "Magic Up": "Магія+",
                        "Phys Up": "Фізична сила+", "Critical Rate Up": "Шанс крит. удару"}[m.group(1)]
        if "Cost" in en or m.group(1) in ("Phys", "Magic", "Heal", "Attack"):
            base = base  # "(Low)" for costs means small reduction
        return f"{base} ({LVL[m.group(2)]})"
    return None


NUMBERED = {
    "Magic Up": "Магія+", "Phys Up": "Фізична сила+", "Ailment Up": "Шанс станів+", "Ailment Multiplier": "Множник станів",
    "Ambush Up": "Засідка+", "Baton Pass Up": "Естафета+", "Crit Atk Up": "Крит. атака+", "Magic Atk Cost": "Маг. витрати-",
    "Phys HP Cost": "Фіз. витрати ОЗ-", "SP Recovery": "Відновлення ОД", "Single-Target Up": "Одна ціль+",
    "Mult-Target Up": "Кілька цілей+", "Member 1 Pursue Up": "Переслідування: учасник 1",
    "Down Shot": "Постріл зі збиттям", "Growth": "Зростання", "Regenerate": "Регенерація", "Invigorate": "Бадьорість",
    "Support Plus": "Підтримка+", "All-out Lv": "Загальна атака, рів.", "Drug Store": "Аптека",
    "Canned Juice": "Сік у банці", "Juice": "Сік", "Juicer Bar": "Фреш-бар", "Health Drink": "Напій здоров'я",
    "Nutritional Drink": "Поживний напій", "Military Food": "Армійський пайок", "Special Coffee": "Особлива кава",
    "New Curry": "Нове карі", "Roulette: Support": "Рулетка: підтримка", "Adam Skill": "Навичка Адама",
}

MANUAL = """
+15% EXP	+15% досвіду
+50% EXP	+50% досвіду
100% Crit, 0% Evade	100% крит, 0% ухилення
200% Damage	200% шкоди
200% Phys, 50% Hit	200% фіз., 50% влучання
ATK Up, Aim Down	Атака+, влучність-
Abysmal Surge	Безодня, що здіймається
Abyssal Eye	Око безодні
Abyssal Wings	Крила безодні
Active Barrier	Активний бар'єр
Active Support	Активна підтримка
Adverse Resolve	Рішучість у скруті
Agility Master	Майстер спритності
Agneyastra	Агнеястра
Ailment Boost	Посилення станів
Ailment Dmg Up	Шкода по станах+
Ailment Dmg Up+	Шкода по станах++
Ailment Effect Up	Ефект станів+
Ailment Effect Up+	Ефект станів++
Ailment Success Up	Успіх станів+
Akashic Arts	Акашичні мистецтва
Ali Dance	Танок Алі
All Crits, No Evasion	Лише крити, без ухилення
All Target ATK Up	Атака по всіх+
All Target ATK Up+	Атака по всіх++
All-Out Attack	Загальна атака
All-Out Attack Boost	Посилення загальної атаки
Ambient Aid	Сприятливе оточення
Amplify Force	Посилення сили
Amplify Magic	Посилення магії
Amrita Drop	Крапля амріти
Amrita Shower	Злива амріти
Amrita Soda	Содова амріта
Analysis	Аналіз
Angelic Grace	Ангельська благодать
Antibiotic Gel	Антибіотичний гель
Antique Rifle	Старовинна гвинтівка
Apt Pupil	Тямущий учень
Arm of Destruction	Рука руйнування
Arms Master	Майстер зброї
Army Might 1	Міць війська 1
Arrow of Light	Стріла світла
Art Talk	Розмова про мистецтво
Artist Talk	Розмова з митцем
Assault Dive	Штурмове піке
Assault Rifle	Штурмова гвинтівка
Atomic Flare	Атомний спалах
Attack Master	Майстер атаки
Attack Position	Атакувальна позиція
Auto Barrier	Автобар'єр
Auto-Maraku	Авто-Маракукадзя
Auto-Masuku	Авто-Масукукадзя
Auto-Mataru	Авто-Матарукадзя
Ayamur	Аямур
Backup	Підстраховка
Backup Support	Резервна підтримка
Bad Beat	Невдала роздача
Baisudi	Байсуді
Ball Lightning	Кульова блискавка
Balm of Life	Бальзам життя
Baptism Ball	Куля хрещення
Barrage	Шквал
Bead	Намистина
Bead Chain	Нитка намистин
Beast King's Wrath	Гнів царя звірів
Beast Weaver	Ткач звірів
Berserker Dance	Танок берсерка
Big Bang Challenge	Челендж «Біг Бенг»
Big Bang Order	Замовлення «Біг Бенг»
Big Bang Treat	Частування «Біг Бенг»
Bite	Укус
Black Belt Talk	Розмова майстра бойових мистецтв
Black Viper	Чорна гадюка
Blank Card	Порожня карта
Blazing Hell	Палаюче пекло
Bleeding Dry Brush	Пензель, що висушує кров
Bloodbath	Кривава баня
Brain Buster	Мозкодробарка
Brain Jack	Злам мозку
Brain Shake	Струс мозку
Brainiac Talk	Розмова розумників
Brave Blade	Хоробрий клинок
Brave Step	Відважний крок
Brush of Vanity	Пензель марнославства
Brutal Impact	Жорстокий удар
Bullet Hail	Град куль
Cadenza	Каденція
Call for Backup	Виклик підкріплення
Call of Chaos	Поклик хаосу
Cannon Barrage	Гарматний шквал
Cannon Fire	Гарматний вогонь
Capital Punishment	Смертна кара
Caro Attack	Атака Каро
Caro Rod	Жезл Каро
Caroline Attack	Атака Кароліни
Celeb Talk	Розмова знаменитостей
Champion's Cup	Кубок чемпіона
Chance of 0 HP Cost	Шанс на 0 витрат ОЗ
Chance of 0 SP Cost	Шанс на 0 витрат ОД
Charge Ball	Заряджена куля
Charismatic Speech	Харизматична промова
Checkmate	Шах і мат
Chewing Soul	Жувальна душа
Climate Decorum	Кліматичний етикет
Coin Attack	Атака монетами
Concealment	Маскування
Concentrated Ball	Концентрована куля
Confuse Ball	Куля сум'яття
Cooking	Кулінарія
Cornered Fang	Ікло загнаного звіра
Cosmic Flare	Космічний спалах
Counterstrike	Зустрічний удар
Cripple	Скалічення
Critical Atk Up	Крит. атака+
Critical Atk Up+	Крит. атака++
Critical Effect Up	Ефект крит. удару+
Critical Effect Up+	Ефект крит. удару++
Critical Glare	Критичний погляд
Crocodile Tears	Крокодилячі сльози
Cross Slash	Хрестовий удар
Curry Charge	Карі: зарядка
Curry Concentrate	Карі: концентрація
Curry Endure	Карі: витримка
Curry Heat Riser	Карі: розпал
Curry Makara	Карі: макара
Curry Raku	Карі: раку
Curry Suku	Карі: суку
Curry Tetra	Карі: тетра
Curse Paper	Прокляті папірці
Cursed Strike	Проклятий удар
Dazzler	Засліплювач
Deadly Fury	Смертельна лють
Death (Despair)	Смерть (відчай)
Death Scythe	Коса смерті
Deathbound	Приречення
Debilitate	Знесилення
Decoy Ball	Куля-приманка
Deep Analysis	Глибокий аналіз
Defense Master	Майстер захисту
Demonic Decree	Демонічний указ
Desperation	Відчайдушність
Detective Talk	Детективна розмова
Detox	Детокс
Diamond Dust	Діамантовий пил
Die For Me!	Помри за мене!
Diffraction Arrow	Стріла дифракції
Diplomacy	Дипломатія
Disclose	Розкриття
Dispose Item	Позбутися предмета
Distorted Avarice	Спотворена жадібність
Distorted Envy	Спотворені заздрощі
Distorted Gluttony	Спотворена ненажерливість
Distorted Lust	Спотворена хтивість
Distorted Pride	Спотворена гордість
Distorted Vanity	Спотворене марнославство
Distorted Wrath	Спотворений гнів
Distortion Surge	Сплеск спотворення
Distortion Wave	Хвиля спотворення
Divine Apex	Божественна вершина
Divine Grace	Божественна благодать
Divine Judgment	Божественний суд
Divine Punishment	Божественна кара
Door of Hades	Брама Аїду
Dormin Rush	Дормін-натиск
Dormina	Дорміна
Double Fangs	Подвійні ікла
Double Shot	Подвійний постріл
Down Shot	Постріл зі збиттям
Dreadful Scream	Жахливий крик
Dream Needle	Голка сновидінь
Drift	Дрифт
Dry Ice	Сухий лід
Dust Flurry	Пиловий вихор
Earth Burger	Бургер «Земля»
Ease Flow	Легкий потік
Ease Leak	Легкий витік
Ease Surge	Легкий сплеск
Eiga Ball	Куля: ейга
Elec Break	Пробиття опору електриці
Electro Attack	Електроатака
Emergency Escape	Аварійна втеча
Emergency Shift	Аварійна заміна
Endure	Витримка
Enduring Soul	Незламна душа
Enemy Benefit	Вигода ворога
Energy Drop	Крапля енергії
Energy Shower	Злива енергії
Energy Stream	Потік енергії
Eternal Light	Вічне світло
Eternal Radiance	Вічне сяйво
Evil Smile	Лиха усмішка
Evil Touch	Лихий дотик
Executive Punch	Директорський удар
Exorcism Ball	Куля екзорцизму
Explosion!	Вибух!
Fake Artist's Grace	Фальшива благодать митця
Famine's Breath	Подих голоду
Famine's Scream	Крик голоду
Fear Gas	Газ страху
Fig Seed	Насінина інжиру
Fighting Spirit	Бойовий дух
Final Guard	Останній захист
Fire Ball	Вогняна куля
Firecracker	Петарда
Firm Stance	Тверда стійка
Fitness Talk	Розмова про фітнес
Flame Dance	Танок полум'я
Flash Bomb	Світлова граната
Flow	Потік
Follow Axe	Наступ: сокира
Follow Blade	Наступ: клинок
Follow Claw	Наступ: кігті
Follow Crush	Наступ: трощення
Follow Knuckle	Наступ: кастет
Follow Saber	Наступ: шабля
Follow Whip	Наступ: батіг
Fortified Moxy	Загартована відвага
Fortify Spirit	Зміцнення духу
Foul Breath	Смердючий подих
Frail Law	Закон слабкості
Freila Ball	Куля: фрейла
Full Analysis	Повний аналіз
Full Force	Повна сила
Fundraising	Збір коштів
Fusion Accident Up	Шанс збою злиття+
Gale Ball	Куля бурі
Gambler's Foresight	Передбачення гравця
Gathering Light	Збирання світла
Gatling Blow	Гатлінг-удар
Gatling Gun	Кулемет Гатлінга
Ghastly Wail	Моторошне виття
Giant Slice	Велетенський розріз
Gigantomachia	Гігантомахія
Girl Talk	Дівоча розмова
Gluttonous Snuff	Ненажерливе знищення
God's Hand	Рука бога
Goho-M	Гохо-М
Gold Medal Spike	Золотий смеш
Golden Knife	Золотий ніж
Gospel	Євангеліє
Grail Light 2	Світло Грааля 2
Grand Palm	Велика долоня
Grenade Launcher	Гранатомет
Gryphon's Breath	Подих грифона
Guard Reward Up	Нагорода за захист+
Guiding Tendril	Провідний пагін
Guillotine Punishment	Кара гільйотиною
Gun Accuracy +5%	Влучність вогн. +5%
Gunfire Punishment	Кара пострілами
HP Cost -10%	Витрати ОЗ -10%
HP Cost -25%	Витрати ОЗ -25%
HP Cost 0	Витрати ОЗ 0
HP Cost Down 10%	Витрати ОЗ -10%
HP Cost Down 25%	Витрати ОЗ -25%
Hama	Хама
Hamaon	Хамаон
Handgun	Пістолет
Harisen Recovery	Відновлення харісеном
Hassou Tobi	Хассо-тобі
Headbutt	Удар головою
Heal Cost -10%	Витрати на лікування -10%
Heal Cost -25%	Витрати на лікування -25%
Heal Cost Down 10%	Витрати на лікування -10%
Heal Cost Down 25%	Витрати на лікування -25%
Heal Enemy	Лікування ворога
Heal Magic +10%	Лікувальна магія +10%
Heal Magic +25%	Лікувальна магія +25%
Heal Magic Up 10%	Лікувальна магія +10%
Heal Magic Up 25%	Лікувальна магія +25%
Healing Power	Цілюща сила
Heat Up	Розігрів
Heat Wave	Теплова хвиля
Hide	Сховатися
High Analyze	Вищий аналіз
High Counter	Вища контратака
High Energy	Висока енергія
Hiranya	Хіранья
Hit Damage Doubled	Подвійна шкода від влучань
Holy Benevolence	Свята доброчинність
Holy Change	Свята переміна
Holy Embrace	Святі обійми
Holy Strike	Святий удар
Holy Whisper	Святий шепіт
Homunculus	Гомункул
Hundred Slaps	Сотня ляпасів
Hunger All	Голод для всіх
Hunting Stance	Мисливська стійка
Hyakka Ryouran	Хякка Рьоран
Hysterical Slap	Істеричний ляпас
Ice Age	Льодовиковий період
Ice Cube	Кубик льоду
Indignant Revenge	Обурена помста
Inferno	Інферно
Inferno Punishment	Кара інферно
Insatiable Strike	Ненаситний удар
Insta-Heal	Миттєве зцілення
Insta-kill Up	Миттєва смерть+
Insta-kill Up+	Миттєва смерть++
Instakill SP Heal High	ОД за миттєве вбивство (вис.)
Instakill SP Heal Low	ОД за миттєве вбивство (низ.)
Instakill SP Heal Mid	ОД за миттєве вбивство (сер.)
Iridescent Change	Райдужна переміна
Justine Attack	Атака Жюстіни
Kakoi Kuzushi	Какой-кудзусі
Kill Reward Up	Нагорода за вбивство+
Kill Rush	Смертельний натиск
Killshot of Love	Смертельний постріл кохання
Kitty Talk	Котяча розмова
Koma Sabaki	Кома-сабакі
Kopi Luwak	Копі лювак
Kouga Ball	Куля: коуга
Kuzunoha Emblem	Герб Кудзунохи
Laevateinn	Левантейн
Laser Gun	Лазерна гармата
Last Stand	Останній рубіж
Launch	Запуск
Libido Boost	Посилення лібідо
Lick	Лизь
Life Aid	Життєва допомога
Life Bonus	Бонус до життя
Life Boost	Посилення життя
Life Drain	Висмоктування життя
Life Gain	Приріст життя
Life Leech	П'явка життя
Life Rise	Підйом життя
Life Stone	Камінь життя
Life Surge	Сплеск життя
Life Wall	Стіна життя
Light Edge	Світлове лезо
Lightning Punishment	Кара блискавкою
Low HP Atk Up	Атака при низьких ОЗ+
Low HP Atk Up+	Атака при низьких ОЗ++
Low HP Attack Up	Атака при низьких ОЗ+
Low HP Attack Up+	Атака при низьких ОЗ++
Lucky Punch	Щасливий удар
Lullaby	Колискова
Lust Sphere	Сфера хтивості
Lustful Slurp	Хтиве сьорбання
Mabaisudi	Мабайсуді
Mabufu	Мабуфу
Mabufudyne	Мабуфудайн
Mabufula	Мабуфула
Machine Gun	Кулемет
Madara-Megido	Мадара-Мегідо
Maeiga	Маейга
Maeiga Ball	Куля: маейга
Maeigaon	Маейгаон
Maeiha	Маейха
Maelstrom	Вир
Mafrei	Мафрей
Mafrei Ball	Куля: мафрей
Mafreidyne	Мафрейдайн
Mafreila	Мафрейла
Magaru	Магару
Magarudyne	Магарудайн
Magarula	Магарула
Magatsu Mandala	Магацу-мандала
Magic Ability	Магічна здібність
Magic Master	Майстер магії
Magic Mirror	Магічне дзеркало
Magic Wall	Магічна стіна
Mahama	Махама
Mahamaon	Махамаон
Maka Leaf	Лист маки
Makajama	Макадзяма
Makajamaon	Макадзямаон
Makara Break	Злам макари
Makarakarn	Макаракарн
Make it Rain	Грошовий дощ
Makouga	Макоуга
Makougaon	Макоугаон
Makouha	Макоуха
Makouha Ball	Куля: макоуха
Mamudo	Мамудо
Mamudoon	Мамудоон
Mana Bonus	Бонус мани
Mana Gain	Приріст мани
Mana Rise	Підйом мани
Mana Surge	Сплеск мани
Manifest Bell	Явлення: дзвін
Manifest Book	Явлення: книга
Manifest Gun	Явлення: зброя
Manifest Sword	Явлення: меч
Manipulation	Маніпуляція
Mapsi	Мапсі
Mapsi Ball	Куля: мапсі
Mapsio	Мапсіо
Mapsiodyne	Мапсіодайн
Marakukaja	Маракукадзя
Marakunda	Маракунда
March of the Piggy	Марш поросяти
Marin Karin	Марін Карін
Mars Burger	Бургер «Марс»
Martial Arts Master	Майстер бойових мистецтв
Maruki Punch	Удар Марукі
Masquerade	Маскарад
Mass Ball	Масова куля
Masukukaja	Масукукадзя
Masukunda	Масукунда
Matarukaja	Матарукадзя
Matarunda	Матарунда
Mazio	Мадзіо
Maziodyne	Мадзіодайн
Mazionga	Мадзіонга
Me Patra	Ме Патра
Medical Kit	Аптечка
Medicine	Ліки
Megaton Raid	Мегатонний наліт
Memory Blow	Удар пам'яті
Mental Hack	Ментальний злам
Metabolic Wave	Метаболічна хвиля
Military  Food 1	Армійський пайок 1
Mind Control	Контроль розуму
Mind Slice	Розсічення розуму
Mindfulness	Усвідомленість
Miracle Punch	Дивовижний удар
Miracle Rush	Дивовижний натиск
Missile Party	Ракетна вечірка
Missionary of Dark	Місіонер темряви
Missionary of Light	Місіонер світла
Money Boost	Посилення грошей
Moon Burger	Бургер «Місяць»
Moral Support	Моральна підтримка
Morning Star	Ранкова зоря
Mudo	Мудо
Mudo Boost	Посилення мудо
Mudoon	Мудоон
Multi-Target Up	Кілька цілей+
Multi-Target Up+	Кілька цілей++
Muscle Drink	Напій для м'язів
Myriad Slashes	Міріади розрізів
Myriad Truths	Міріади істин
NOT USED	НЕ ВИКОРИСТОВУЄТЬСЯ
Negative Pile	Негативна купа
Negotiating	Переговори
Neo Cadenza	Нео-каденція
New Creation	Нове творіння
Nocturnal Flash	Нічний спалах
Nose Dive	Піке
Not Found by Enemy	Непомітність для ворогів
Nuclear Crush	Ядерне трощення
Nuclear Strike	Ядерний удар
Obsidian Mirror	Обсидіанове дзеркало
Ocular Vulcan	Окулярний вулкан
Odd Morsel	Дивний шматочок
Ointment	Мазь
Ominous Words	Зловісні слова
Oni-Kagura	Оні-кагура
Oratario	Ораторія
Organic Herb	Органічна трава
Origin Light	Первісне світло
Outlaw Attack	Атака поза законом
Panta Rhei	Панта рей
Patra	Патра
Penalty	Штраф
Phantom Show	Фантомне шоу
Physical Mirror	Фізичне дзеркало
Pickpocket	Кишеньковий злодій
Piercing Strike	Пронизливий удар
Pinwheel	Вертушка
Plume of Dusk	Перо сутінків
Position Hack	Злам позиції
Power Slash	Потужний розріз
Power Up Enemy	Посилення ворога
President's Insight	Прозорливість президента
Protect	Захист
Psio Ball	Куля: псіо
Psy Ball	Куля: псі
Psycho Blast	Псі-вибух
Psycho Force	Псі-сила
Psychokinesis Strike	Психокінетичний удар
Pulinpa	Пулінпа
Punishing Hail	Карний град
Punk Talk	Розмова панків
Purifying Salt	Очищувальна сіль
Purifying Water	Очищувальна вода
Pyramid Blast	Вибух піраміди
Quadruple Summon	Четверний виклик
Rage Atk Up	Атака в люті+
Rage Transmission	Передача люті
Raging Flames	Шалене полум'я
Raining Seeds	Дощ насінин
Rancid Gravy	Прогірла підлива
Rapid Ascent	Стрімкий підйом
Rays of Control	Промені контролю
Rebellion Blade	Клинок бунту
Recarmdra	Рекармдра
Recovery Sage	Мудрець відновлення
Regeneration	Регенерація
Removal Potion	Зілля очищення
Restore	Відновлення
Reverse Rub	Зворотне розтирання
Revitalize Soul	Оживлення душі
Reviv-All	Ревів-Ол
Reviv-All Z	Ревів-Ол Z
Revival Bead	Намистина відродження
Revolver	Револьвер
Riot Gun	Помпова рушниця
Rising Slash	Висхідний розріз
Roulette Time	Час рулетки
Roulette: HP	Рулетка: ОЗ
Roulette: Money	Рулетка: гроші
Roulette: SP	Рулетка: ОД
Royal Jelly	Маточне молочко
Royal Wing Beam	Королівський промінь крил
SP Cost -10%	Витрати ОД -10%
SP Cost -25%	Витрати ОД -25%
SP Cost 0	Витрати ОД 0
SP Cost Down 10%	Витрати ОД -10%
SP Cost Down 25%	Витрати ОД -25%
Sacrifice Order	Наказ жертви
Salvation	Спасіння
Samsara	Сансара
Samurai Spirit	Дух самурая
San-zun Tama	Сан-дзун тама
Saturn Burger	Бургер «Сатурн»
Segami Rice	Рис Сеґамі
Self-destruct	Самознищення
Selfless Devotion	Безкорислива відданість
Severing Slash	Відсічний удар
Sexy Technique	Спокуслива техніка
Shapeless Guard	Безформний захист
Sharp Student	Кмітливий учень
Shining Arrows	Сяйливі стріли
Shoot Up	Злет
Shot of Lust	Постріл хтивості
Shotgun	Дробовик
Silent Snowscape	Тихий сніговий краєвид
Sinful Shell	Грішна оболонка
Single-Target Up	Одна ціль+
Single-Target Up+	Одна ціль++
Skull Cracker	Череполом
Slam	Гуп
Sledgehammer	Кувалда
Sleipnir	Слейпнір
Sleuthing Instinct	Детективний інстинкт
Sleuthing Mastery	Детективна майстерність
Slingshot	Рогатка
Sloth Defense	Лінивий захист
Smart Bomb	Розумна бомба
Smooth Talk	Красномовство
Snack	Перекус
Snap	Клац
Snipe	Снайперський постріл
Snow Ball	Сніжка
Snuff Soul	Згасання душі
Soma	Сома
Song of Placation	Пісня умиротворення
Song of Salvation	Пісня спасіння
Soul Chain	Ланцюг душі
Soul Drop	Крапля душі
Soul Food	Їжа для душі
Soul Touch	Дотик душі
Soul Touch Unused	Дотик душі (не використ.)
Special Fireworks	Особливий феєрверк
Special Guards	Особлива охорона
Speed Master	Майстер швидкості
Spell Master	Майстер заклинань
Sphinx Dive	Піке сфінкса
Sphinx Swipe	Удар сфінкса
Spirit Drain	Висмоктування духу
Spirit Leech	П'явка духу
Stagnant Air	Застояне повітря
Steal Info	Викрадення інформації
Stomach Blow	Удар у живіт
Storm Punishment	Кара бурею
Subrecover HP	Додаткове відновлення ОЗ
Subrecover HP EX	Додаткове відновлення ОЗ EX
Subrecover SP	Додаткове відновлення ОД
Subrecover SP EX	Додаткове відновлення ОД EX
Summon	Виклик
Sup All Kaja	Підтримка: усі -кадзя
Sup Charge	Підтримка: зарядка
Sup Escape Route	Підтримка: шлях утечі
Sup HP +30%	Підтримка: ОЗ +30%
Sup Marakukaja	Підтримка: маракукадзя
Sup Masukukaja	Підтримка: масукукадзя
Sup Matarukaja	Підтримка: матарукадзя
Sup SP +10%	Підтримка: ОД +10%
Sup Third Eye	Підтримка: третє око
Super Decoy Ball	Супер-куля-приманка
Super VIP Form	Супер-VIP-форма
Support Extension	Подовження підтримки
Support Rate Up	Шанс підтримки+
Support Turn Extend	Подовження ходів підтримки
Survival Trick	Хитрість виживання
Swift Strike	Швидкий удар
Swirling Psychokinesis	Вихровий психокінез
Sword Dance	Танок мечів
Sword of Judgment	Меч суду
Target ATK Up	Атака по цілі+
Target ATK Up+	Атака по цілі++
Taste of Wrath	Смак гніву
Taunt	Провокація
Taunting Aura	Зухвала аура
Technical Effect Up	Технічний ефект+
Technical Effect Up+	Технічний ефект++
Technical Up	Технічний удар+
Technical Up+	Технічний удар++
Tempest Slash	Буряний розріз
Tentarafoo	Тентарафу
Terror Claw	Кіготь жаху
Tesla Coil	Котушка Тесли
Tetra Break	Злам тетри
Tetraja	Тетрадзя
Tetrakarn	Тетракарн
The Artist's Grace	Благодать митця
Thermopylae	Фермопіли
Thunder Reign	Громове владарювання
Thunderclap	Гуркіт грому
Titanomachia	Титаномахія
Togo System	Система Того
Tongue Whip	Язиковий батіг
Touch n' Go	Торкнись і йди
Tough Law	Суворий закон
Touryou	Торьо
Traesto	Траесто
Trafuri	Трафурі
Trait DLC for Bitedown	Риса DLC (Bitedown)
Tranquilizer	Транквілізатор
Trapped Rat	Щур у пастці
Treasure Skimmer	Ловець скарбів
Trigger Happy	Гарячий палець
Trip-Upper	Підніжка
True Fake	Справжня підробка
Twins Down Attack	Атака близнюків
Tyrant Chaos	Хаос тирана
Tyrant Stance	Стійка тирана
Tyrant's Fist	Кулак тирана
Tyrant's Glare	Погляд тирана
Tyrant's Judgement	Суд тирана
Tyrant's Mind	Розум тирана
Tyrant's Purge	Чистка тирана
Tyrant's Wave	Хвиля тирана
Tyrant's Will	Воля тирана
UNUSED	НЕ ВИКОРИСТОВУЄТЬСЯ
UNUSED: Akechi Unison Attack	НЕ ВИКОРИСТ.: спільна атака Акеті
Ultimate Support	Абсолютна підтримка
Unholy Convergence	Нечестиве злиття
Universal Power	Вселенська сила
Universe Ring	Кільце всесвіту
Unshaken Will	Непохитна воля
Vacuum Wave	Вакуумна хвиля
Vajra Blast	Вибух ваджри
Value Medicine	Бюджетні ліки
Vanish Ball	Куля зникнення
Vanity Copy	Марнославна копія
Vault Guardian	Вартовий сховища
Vicious Strike	Лютий удар
Victory Cry	Переможний клич
Vitality Flow	Потік життєвої сили
Vitality Leak	Витік життєвої сили
Vitality Surge	Сплеск життєвої сили
Volleyball Assault	Волейбольний штурм
Volt Ball	Електрокуля
Vorpal Blade	Вострий клинок
WEAK Hit Effect Up	Ефект удару по вразливості+
WEAK Hit Effect Up+	Ефект удару по вразливості++
WEAK Hit Up	Удар по вразливості+
WEAK Hit Up+	Удар по вразливості++
Wage War	Оголошення війни
Wakefulness	Пильність
Warning Shot	Попереджувальний постріл
Whip Strike	Удар батогом
Wild Talk	Дика розмова
Wild Thunder	Дикий грім
Will of the People	Воля народу
Wind Cutter	Вітряний різак
Wing Blast	Удар крилами
Wings of Wisdom	Крила мудрості
Womanizing	Ловеласство
Work Order	Робоче замовлення
Wrath of God	Гнів божий
Yashichi	Ясіті
Zenith Defense	Зеніт захисту
Attack Cost (High)	Витрати на атаку- (вис.)
Attack Cost (Low)	Витрати на атаку- (низ.)
Attack Cost (Mid)	Витрати на атаку- (сер.)
Heal Cost (High)	Витрати на лікування- (вис.)
Heal Cost (Low)	Витрати на лікування- (низ.)
Heal Cost (Mid)	Витрати на лікування- (сер.)
Magic Cost (High)	Маг. витрати- (вис.)
Magic Cost (Low)	Маг. витрати- (низ.)
Magic Cost (Mid)	Маг. витрати- (сер.)
Phys Cost (High)	Фіз. витрати- (вис.)
Phys Cost (Low)	Фіз. витрати- (низ.)
Phys Cost (Mid)	Фіз. витрати- (сер.)
Flame Magatama	Магатама полум'я
Bolt Magatama	Магатама блискавки
Freeze Magatama	Магатама холоду
Hama Boost	Посилення хами
Member 1 Pursue Up	Переслідування+: учасник 1
Member 2 Pursue Up	Переслідування+: учасник 2
Member 3 Pursue Up	Переслідування+: учасник 3
Member 4 Pursue Up	Переслідування+: учасник 4
Member 5 Pursue Up	Переслідування+: учасник 5
Member 6 Pursue Up	Переслідування+: учасник 6
Member 7 Pursue Up	Переслідування+: учасник 7
Ailment Up (Low)	Шанс станів+ (низ.)
"""


def main():
    # every skill-type candidate, except approved rows and hand-written ones in proposals.tsv
    # (selecting by status would make reruns see their own output as "proposed" and skip it)
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    todo = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if (r["category"] in ("skill", "skill_alt", "skill_card") and r["status"] != "approved"
                    and r["en"] not in main_prop):
                todo.append(r)
    manual = dict(l.split("\t", 1) for l in MANUAL.strip().splitlines())
    out, missing = [], []
    for r in sorted(todo, key=lambda r: r["en"]):
        en = r["en"]
        uk = manual.get(en) or pattern(en)
        if uk:
            out.append((en, uk, r["category"], "шаблон" if en not in manual else ""))
        else:
            missing.append(en)
    with open(ROOT / "tools/glossary/proposals_skills.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for en, uk, cat, note in out:
            f.write(f"{en}\t{uk}\t\t{cat}\t{note}\n")
    print(f"{len(out)} written, {len(missing)} missing: {missing}")


if __name__ == "__main__":
    main()
