"""Generate tools/glossary/proposals_enemies.tsv for enemy names (+ leftover Persona variants).

Rules: descriptive enemy titles are translated; Japanese surnames — Kovalenko transliteration;
"<Persona> Picaro", "P3/P4 <Persona>" reuse the approved Persona names from proposals.tsv.
Run: python tools/glossary/make_enemies.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SURNAMES = {
    "Aino": "Айно", "Akitsu": "Акіцу", "Amai": "Амаї", "Amasaki": "Амасакі", "Arihara": "Аріхара", "Arita": "Аріта",
    "Asakura": "Асакура", "Chiyo": "Тійо", "Fukurai": "Фукурай", "Fuwa": "Фува", "Hashisato": "Хасісато",
    "Honjo": "Хондзьо", "Isazuka": "Ісадзука", "Isshiki": "Іссікі", "Jochi": "Дзьоті", "Kagami": "Кагамі",
    "Kaneshiro": "Канесіро", "Kiritani": "Кірітані", "Kishi": "Кісі", "Makigami": "Макігамі", "Minamoto": "Мінамото",
    "Mogami": "Могамі", "Mr. Magario": "пан Магаріо", "Mr. Takase": "пан Такасе", "Mrs. Magario": "пані Магаріо",
    "Mrs. Takase": "пані Такасе", "Mrs. Togo": "пані Того", "Nagata": "Нагата", "Naguri": "Нагурі",
    "Nakanohara": "Наканохара", "Nejima": "Недзіма", "Oda": "Ода",
    "Odo": "Одо", "Oi": "Ої", "Ono": "Оно", "Oyamada": "Оямада", "Saburi": "Сабурі",
    "Sae": "Сае", "Saeki": "Саекі", "Sakoda": "Сакода", "Shimizu": "Сімідзу", "Shimomi": "Сімомі",
    "Takanashi": "Таканасі", "Takena": "Такена", "Togo": "Того", "Tsuboi": "Цубой", "Tsuda": "Цуда",
    "Uchimura": "Утімура", "Ushiwata": "Усівата", "Wakasa": "Вакаса", "Yatagai": "Ятагай", "Yoshioka": "Йосіока",
}
SHADOW_ROLES = {"Cleaner": "прибиральника", "Former Noble": "колишнього аристократа", "IT President": "IT-президента",
                "Politician": "політика", "TV President": "телепрезидента"}

MANUAL = """
Abyssal King of Avarice	Безодній король скнарості
Adam Kadmon	Адам Кадмон
Adam Kadmon Second Half	Адам Кадмон (друга половина)
Adam Target 1	Ціль Адама 1
Adam Target 2	Ціль Адама 2
Additional Employee	Додатковий працівник
Ambassador of Filth	Посол бруду
Angry Warrior	Розлючений воїн
Angry Wisdom King	Гнівний король мудрості
Apocalyptic Guide	Провідник апокаліпсису
Apprentice in a Jug	Учень у глеку
Arrogant Vulture	Пихатий стерв'ятник
Ascended Feline	Піднесений кіт
Auspicious Pachyderm	Благословенний товстошкірий
Awakened God	Пробуджений бог
Azathoth	Азатот
Azathoth 2	Азатот 2
Battle Fiend	Бойовий демон
Bearer of the Scales	Носій терезів
Beast That Rules the Palace	Звір, що править Палацом
Beast of Human Sacrifice	Звір людських жертвоприношень
Bedside Brute	Нічний громила
Beguiling Girl	Звабна дівчина
Bell of Declaration	Дзвін проголошення
Blazing Giant	Палаючий велетень
Bloated Rotting Meal	Роздута гнила страва
Blood-Thirsty Ogress	Кровожерна людожерка
Bloodthirsty Demoness	Кровожерна демониця
Bloody Goddess	Кривава богиня
Bodyguard-For-Hire	Найманий охоронець
Book of Commandments	Книга заповідей
Bringer of Misfortune	Носій нещастя
Brutal Cavalryman	Жорстокий кавалерист
Burning Giant	Охоплений полум'ям велетень
Captivating Dancer	Чарівна танцівниця
Cavern Snakeman	Печерний змієлюд
Chanting Baboon	Співочий павіан
Chivalrous Fiend	Шляхетний демон
Cleanser of Heaven	Очищувач небес
Coffin-borne God	Бог у труні
Corpse Bird	Трупний птах
Corpse-eating Corpse	Трупоїдний труп
Cruel Leopard	Жорстокий леопард
Crypt-dwelling Pyromaniac	Піроман зі склепу
Dancer of Death	Танцівник смерті
Dancing Lion	Танцюючий лев
Dancing Witch	Танцююча відьма
Dark Sun	Темне сонце
Daydreaming Queen	Мрійлива королева
Debaucherous Demoness	Розпусна демониця
Decadent False God	Занепалий лжебог
Declarer of Anguish	Провісник муки
Defeated Avenger	Переможений месник
Deformed Lion God	Спотворений бог-лев
Delusive Leopard	Оманливий леопард
Destructive Beauty	Руйнівна краса
Dirty Two-Horned Beast	Брудний дворогий звір
Dirty Two-horned Beast	Брудний дворогий звір
Divine Warrior	Божественний воїн
Dragon-slaying Genius	Геній-драконоборець
Dream-Dwelling Skull	Череп, що живе у снах
Drunken Serpents	П'яні змії
EX Kamoshida Color Change	EX Камосіда (інший колір)
Ecstatic Vulture	Екстатичний стерв'ятник
Embittered Blacksmith	Озлоблений коваль
Endless Pulsing Mud	Нескінченна пульсуюча багнюка
Entranced Dancer	Зачарована танцівниця
Envoy of Slumber	Посланець сну
Equine Sage	Кінь-мудрець
Ersatz Fury	Ерзац-лють
Ersatz Joy	Ерзац-радість
Ersatz Mirth	Ерзац-веселощі
Ersatz Sorrow	Ерзац-скорбота
Evil Snowman	Злий сніговик
Evil Synthetic Organism	Злий синтетичний організм
Evil Voracious Dragon	Злий ненажерливий дракон
Ex-Belphegor	Екс-Бельфегор
Ex-Moloch	Екс-Молох
Expressionless Beast	Безвиразний звір
Final Assessor	Останній оцінювач
Fire Assassin	Вогняний убивця
Fly of the Dead	Муха мертвих
Foolish Monk	Нерозумний монах
Funerary Warrior	Похоронний воїн
Fused Ghost	Злитий привид
Gallows-Flower	Шибенична квітка
Gathering Devil	Диявол-збирач
Girl Enthralled by a Dream	Дівчина, зачарована сном
Girl of the Hanging Tree	Дівчина з дерева повішених
God of Control Yaldabaoth	Бог контролю Ялдабаот
Grudging Warrior Arisen	Воскреслий злопам'ятний воїн
Guard Captain	Капітан варти
Guard Dog of Hades	Сторожовий пес Аїду
Guard Dog of Paradise	Сторожовий пес раю
Gun of Execution	Зброя страти
Hallucinating Captain	Капітан у маренні
Harlot of Desire	Блудниця бажання
Haru's Fiancé	Наречений Хару
Heavenly Punisher	Небесний кат
Hedonistic Braggart	Гедоністичний хвалько
Herald of Death	Вісник смерті
Heretic Goat	Цап-єретик
Hero-Gathering Tyrant	Тиран, що збирає героїв
Hitman-For-Hire	Найманий убивця
Holy Grail Tentacle A	Щупальце Святого Грааля A
Holy Grail Tentacle B	Щупальце Святого Грааля B
Holy Grail Tentacle C	Щупальце Святого Грааля C
Human-eating Lady	Пані-людожерка
Hunting Puss in Boots	Кіт у чоботях на полюванні
Hunting Wolf Spirit	Мисливський вовчий дух
Ichiryusai Azazel Madarame	Ітірюсай Азазель Мадараме
Immortal Feline	Безсмертний кіт
Infuriated Wisdom King	Розлючений король мудрості
Insolent Cavalryman	Зухвалий кавалерист
Investigation Team Boy	Хлопець зі Слідчої команди
Inviting Pyromaniac	Привітний піроман
Jade Comb Wielder	Власниця нефритового гребеня
Jealous Lover	Ревнива коханка
Joyful Snake King	Радісний король змій
Junya Bael Kaneshiro	Дзюн'я Баал Канесіро
Killer Teddy Bear	Плюшевий ведмідь-убивця
Kunikazu Mammon Okumura	Кунікадзу Мамона Окумура
Lamenting Sacrifice	Жертва, що оплакує
Laughing Snow King	Сміхотливий сніговий король
Leafy Old Man	Листяний дідуган
Life-Draining Spirit	Дух, що висмоктує життя
Light Guardian	Охоронець світла
Light-Indulgent Messenger	Посланець, що впивається світлом
Lilith's Eldest Daughter	Старша дочка Ліліт
Lilith's Fourth Daughter	Четверта дочка Ліліт
Lilith's Second Daughter	Друга дочка Ліліт
Lilith's Third Daughter	Третя дочка Ліліт
Mad Marsh Horse	Скажений болотяний кінь
Maruki Second Half	Марукі (друга половина)
Masayoshi Samael Shido	Масайосі Самаель Сідо
Menacing Owlman	Загрозлива людина-сова
Merciless Inquisitor	Безжальний інквізитор
Midnight Queen	Опівнічна королева
Militant Elephant	Войовничий слон
Mini Mara	Міні-Мара
Missionary of Depravity	Місіонер розбещеності
Mocking Snowman	Глузливий сніговик
Monarch of Snow	Монарх снігу
Monk of the Valley	Монах з долини
Mountain Girl	Гірська дівчина
Museum Boss All Weakness	Бос музею (усі вразливості)
Museum Boss, Left Eye	Бос музею, ліве око
Museum Boss, Mouth	Бос музею, рот
Museum Boss, Nose	Бос музею, ніс
Museum Boss, Right Eye	Бос музею, праве око
Mysterious Little Girl	Таємнича дівчинка
Night Chimera	Нічна химера
Night Guard Horseman	Вершник нічної варти
Night-Walking Warrior	Нічний воїн-блукач
Nimble Monkey King	Спритний цар мавп
Noisy Mountain Spirit	Галасливий гірський дух
Omniscient Fish of the Sea	Всезнаюча морська риба
P5 Unused	P5 (не використ.)
P6 Unused	P6 (не використ.)
Pagan Savior	Язичницький спаситель
Painter's Left Eye	Ліве око художника
Painter's Mouth	Рот художника
Painter's Nose	Ніс художника
Painter's Right Eye	Праве око художника
Piggyback Demon	Демон на закорках
Piggytron	Свинотрон
Playful Puss in Boots	Грайливий Кіт у чоботях
Pleasant Snowman	Приємний сніговик
Possessing Dog Ghost	Привид пса, що вселяється
Prankster Leader	Ватажок пустунів
Prison Master	Господар в'язниці
Pulsing Mud	Пульсуюча багнюка
Quaking Lady of Shadow	Тремтлива пані тіней
Raging Bird God	Шалений бог-птах
Raging Water Demon	Шалений водяний демон
Raptured Mountain Girl	Захоплена гірська дівчина
Rebellious Elephant	Непокірний слон
Reviled Dictator	Зневажений диктатор
Rhetorician of the Sea	Морський ритор
Rooftop Lion	Лев на даху
S.E.E.S. Boy	Хлопець із S.E.E.S.
Sacred Warrior	Священний воїн
Sacrificial Pyrekeeper	Жертовний хранитель вогнища
Sae Leviathan Niijima	Сае Левіафан Ніїдзіма
Samurai Killer	Самурай-убивця
Satiated Bird God	Ситий бог-птах
Scandalous Queen	Скандальна королева
Security Shadow	Тінь-охоронець
Self-Infatuated Star	Самозакохана зірка
Shadow of God	Тінь бога
Shadowless Pentagram	Пентаграма без тіні
Shadowy Ninja	Тіньовий ніндзя
She of Life and Death	Та, що дарує життя й смерть
Shining Punisher	Сяючий кат
Slithering Snakewoman	Звивиста жінка-змія
Snake King	Король змій
Snakeman in an Ominous Place	Змієлюд у зловісному місці
Snowman Living an Evil Life	Сніговик, що живе лихим життям
Spear-Wielding General	Генерал зі списом
Storm-Invoking Ptarmigan	Куріпка, що кличе бурю
Strumming Veena Player	Музика, що грає на віні
Suguru Asmodeus Kamoshida	Сугуру Асмодей Камосіда
Sword of Conviction	Меч переконання
Teacher Boss Post Aff Change	Вчитель-бос (після зміни спорідн.)
Tentacle of Assistance	Щупальце допомоги
Tentacle of Healing	Щупальце зцілення
Tentacle of Protection	Щупальце захисту
The Black Avenger	Чорний месник
The Blackened Bloom	Почорнілий цвіт
The Blackened Fury	Почорніла лють
The Reaper	Жнець
The Shadowed One	Затьмарений
Thief of Tablets	Викрадач скрижалей
Throbbing King of Desire	Пульсуючий король бажання
Thunder Emperor	Громовий імператор
Tomb of Human Sacrifice	Гробниця людських жертв
Torn King of Desire	Розірваний король бажання
Tornado Devil	Диявол-торнадо
Treasure of Mementos?	Скарб Мементосу?
Trembling Fairy Knight	Тремтливий лицар-фея
Trophy of Obsession	Трофей одержимості
Troublesome Housemaid	Клопітна покоївка
True Masayoshi Samael Shido	Справжній Масайосі Самаель Сідо
Twilight Prostitute	Сутінкова повія
Twin-headed Guardian	Двоголовий вартовий
Unfaithful Dream-King	Невірний король снів
Vampire Moth	Метелик-вампір
Vicious Pentagram	Злісна пентаграма
Vicious Young Warrior	Лютий юний воїн
Viscid Rotting Meat	В'язке гниле м'ясо
Wandering Reviver	Мандрівний воскресник
War-Hungry Horseman	Спраглий війни вершник
Warped Abyss	Викривлена безодня
Waterside Nymph	Прибережна німфа
Wavering Tree Spirit	Хиткий дух дерева
Weak Tomb of Human Sacrifice	Слабка гробниця людських жертв
Wealth-Cultivating Pachyderm	Товстошкірий, що примножує багатство
Wings of Human Sacrifice	Крила людських жертв
Wishless Star	Зірка без бажань
Woman Who Brings Ruin	Жінка, що несе загибель
Zealous Messenger	Ревний посланець
"""


def persona_names():
    out = {}
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        for r in csv.DictReader([l for l in f if l.strip() and not l.startswith("#")], delimiter="\t"):
            if r["category"] == "persona":
                out[r["en"]] = r["uk"]
    out.update({"M. Izanagi": "М. Ідзанагі", "Izanagi-no-Okami Pic.": "Ідзанагі-но-Окамі Пік.",
                "Neo Arsène": "Нео Арсен"})
    return out


def pattern(en, P):
    m = re.fullmatch(r"Shadow (.+)", en)
    if m and (m.group(1) in SURNAMES or m.group(1) in SHADOW_ROLES):
        return f"Тінь {SURNAMES.get(m.group(1)) or SHADOW_ROLES[m.group(1)]}"
    m = re.fullmatch(r"Cognitive (.+)", en)
    if m:
        names = {"Haru Okumura": "Хару Окумура", "Kyoto Nagata": "Кьото Нагата", "Shiho Suzui": "Сіхо Судзуй",
                 "Wakaba Isshiki": "Вакаба Іссікі", "Yuuki Mishima": "Юкі Місіма"}
        g = "Когнітивна" if m.group(1).split()[0] in ("Haru", "Shiho", "Wakaba") else "Когнітивний"
        return f"{g} {names[m.group(1)]}"
    if en == "Izanagi-no-Okami Pic.":
        return P[en]
    m = re.fullmatch(r"(.+) Picaro", en)
    if m and m.group(1) in P:
        return f"{P[m.group(1)]} Пікаро"
    m = re.fullmatch(r"(P[34]) (.+)", en)
    if m and m.group(2) in P:
        return f"{m.group(1)} {P[m.group(2)]}"
    m = re.fullmatch(r"(Corporobo|Execurobo) (MDL-.+)", en)
    if m:
        return f"{'Корпоробот' if m.group(1) == 'Corporobo' else 'Екзекуробот'} {m.group(2)}"
    m = re.fullmatch(r"Azatoth Tendril Second Half (\d)", en)
    if m:
        return f"Щупальце Азатота (друга половина) {m.group(1)}"
    return None


def main():
    P = persona_names()
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    rows = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["category"] in ("enemy", "persona") and r["status"] != "approved" and r["en"] not in main_prop:
                rows.append(r)
    manual = dict(l.split("\t", 1) for l in MANUAL.strip().splitlines())
    out, missing = [], []
    for r in sorted(rows, key=lambda r: r["en"]):
        uk = manual.get(r["en"]) or pattern(r["en"], P)
        (out.append((r["en"], uk, r["category"], "" if r["en"] in manual else "шаблон")) if uk
         else missing.append(r["en"]))
    with open(ROOT / "tools/glossary/proposals_enemies.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for en, uk, cat, note in out:
            f.write(f"{en}\t{uk}\t\t{cat}\t{note}\n")
    print(f"{len(out)} written, {len(missing)} missing: {missing}")


if __name__ == "__main__":
    main()
