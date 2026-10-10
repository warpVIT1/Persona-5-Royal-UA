"""Generate tools/glossary/proposals_equipment.tsv: accessories, armor, weapons, materials, outfits, traits.

Rules:
  * "<Skill> Belt/Anklet/Crown" reuse the skill's Ukrainian name from the glossary: Пояс «Випад»;
  * element protection items, sin crystals/rings, "Spiral X", "X R" are built from templates;
  * named weapons (Masamune, Mjolnir, parody gun models) — transliteration; descriptive — translation.
Run: python tools/glossary/make_equipment.py   (then tools/scripts/build_glossary.py)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATS = ("accessory", "armor", "melee_weapon", "ranged_weapon", "material", "outfit", "trait")

EL_GEN = {"Fire": "вогню", "Ice": "льоду", "Elec": "електрики", "Wind": "вітру", "Psy": "псі", "Nuke": "ядерної енергії",
          "Bless": "світла", "Curse": "прокляття"}
SIN_GEN = {"Envy": "заздрощів", "Gluttony": "ненажерливості", "Greed": "жадібності", "Lust": "хтивості",
           "Pride": "гордині", "Sorrow": "скорботи", "Vanity": "марнославства", "Wrath": "гніву"}
CARRIER = {"Belt": "Пояс", "Anklet": "Браслет на щиколотку", "Crown": "Корона", "Charm": "Амулет", "Bangle": "Браслет",
           "Ring": "Каблучка"}


def load_skill_uk():
    out = {}
    for name in ("proposals.tsv", "proposals_skills.tsv"):
        with open(ROOT / "tools/glossary" / name, encoding="utf-8") as f:
            for r in csv.DictReader([l for l in f if l.strip() and not l.startswith("#")], delimiter="\t"):
                if r["category"].startswith("skill"):
                    out[r["en"]] = r["uk"]
    return out


MANUAL = """
1st Mate Badge	Значок першого помічника
2nd Mate Badge	Значок другого помічника
ARM PC	Наручний ПК
Ace Cap	Кепка аса
Addle Bangle	Браслет сум'яття
Agitation Crown	Корона збудження
Aid Charm	Амулет допомоги
Alarm Charm	Амулет тривоги
Alluring Belt	Звабний пояс
Almighty Ring	Каблучка всемогутності
Amrita Charm	Амулет амріти
Angel Badge	Значок ангела
Apotropaic Hairpin	Шпилька-оберіг
Ardhanari Band	Пов'язка Ардханарі
Assault Belt	Штурмовий пояс
Astral Crown	Астральна корона
Atom Necklace	Атомне намисто
Atom Ring	Атомна каблучка
Atomic Crown	Атомна корона
Attachment Pearl	Перлина прив'язаності
Babel Headphones	Навушники «Вавилон»
Baisudi Charm	Амулет байсуді
Barrier Break Charm	Амулет пробиття бар'єра
Beast Headphones	Звірині навушники
Black Band	Чорна пов'язка
Black Headband	Чорна стрічка на голову
Black Moon	Чорний місяць
Black Necktie	Чорна краватка
Black Rock	Чорний камінь
Black Tights	Чорні колготки
Blazing Horns	Палаючі роги
Blessing Ring	Каблучка благословення
Blizzard Ring	Каблучка хуртовини
Blue Band	Синя пов'язка
Bold Eyepatch	Зухвала пов'язка на око
Boss Undies	Боса труси
Brain Guard	Захист мозку
Brainwash Bangle	Браслет промивання мізків
Brave Belt	Пояс хоробрості
Bravery Sash	Перев'язь відваги
Brawler Belt	Пояс забіяки
Breath Ring	Каблучка подиху
Breeze Ring	Каблучка бризу
Burn Charm	Амулет опіку
Caffeine Patch	Кофеїновий пластир
Calming Anklet	Заспокійливий браслет на щиколотку
Calming Cape	Заспокійлива накидка
Calming Mask	Заспокійлива маска
Camera Strap	Ремінець фотоапарата
Cape of Hope	Накидка надії
Captain Badge	Значок капітана
Cat Brooch	Брошка-кіт
Chakra Choker	Чокер чакри
Circular Band	Кругла пов'язка
Clarity Cape	Накидка ясності
Clown Mask	Маска клоуна
Compression Socks	Компресійні шкарпетки
Concentration Anklet	Браслет на щиколотку зосередження
Cooling Pack	Охолоджувальний пакет
Corrupting Mask	Маска розбещення
Crimson Necklace	Багряне намисто
Cross Augite	Авгіт хреста
Cross-Shaped Charm	Хрестоподібний амулет
Crown of Death	Корона смерті
Cure Charm	Амулет зцілення
Curse Ring	Каблучка прокляття
Cursed Ribbon	Проклята стрічка
Dandy Mirror	Дзеркальце денді
Dark Flame Band	Пов'язка темного полум'я
Dark Spirit Mirror	Дзеркало темного духу
Darkness Ring	Каблучка темряви
Dazzling Netsuke	Сліпуча нецке
Death Ring	Каблучка смерті
Demonica Device	Пристрій «Демоніка»
Designer Shades	Дизайнерські окуляри
Despair Charm	Амулет відчаю
Diamond Dust Lily	Лілія діамантового пилу
Divine Pillar	Божественний стовп
Divine Ring	Божественна каблучка
Dizzy Bangle	Браслет запаморочення
Dizzy Mask	Маска запаморочення
Dotted Tights	Колготки в горошок
Dragon's Heart	Серце дракона
Drowsy Mask	Сонна маска
Eccentric Belt	Ексцентричний пояс
Ember Ring	Каблучка жару
Emperor's Charm	Амулет імператора
Empowering Anklet	Браслет на щиколотку наснаги
Energy Charm	Амулет енергії
Energy Ring	Каблучка енергії
Engraved Dog Tag	Гравірований армійський жетон
Evoker	Евокер
Expedite Ring	Каблучка прискорення
Fanny Pack	Поясна сумка
Fear Bangle	Браслет страху
Fearless Cape	Накидка безстрашності
Feather Cape	Пір'яна накидка
Featherman Badge	Значок Фезермена
Feeble Anklet	Браслет на щиколотку кволості
Fire Dragon Horn	Ріг вогняного дракона
Fish God's Badge	Значок бога риб
Flame Ring	Каблучка полум'я
Forget Bangle	Браслет забуття
Forgetful Mask	Маска забудькуватості
Forneus Badge	Значок Форнеуса
Freeze Charm	Амулет замороження
Frost Ring	Каблучка морозу
Frozen Crown	Крижана корона
Gale Ring	Каблучка бурі
Gambla Badge	Значок «Гамбла»
Gambler's Ring	Каблучка гравця
Gauntlet	Латна рукавиця
Gloom Bangle	Браслет похмурості
Goddess Horn	Ріг богині
Golfer Badge	Значок гольфіста
Graceful Harp	Граціозна арфа
Grand Slam Charm	Амулет «Великий шолом»
Green Band	Зелена пов'язка
Grudge Ring	Каблучка образи
Hades Harp	Арфа Аїду
Hairpin	Шпилька
Hall of Fame Belt	Пояс зали слави
Hallowed Ring	Освячена каблучка
Hawaiian Ring	Гавайська каблучка
Headphones	Навушники
Heal Charm	Амулет лікування
Healing Augite	Цілющий авгіт
Heavenly Necklace	Небесне намисто
Hell Ring	Пекельна каблучка
Hex Ring	Каблучка пристріту
Hidden Ring	Прихована каблучка
Hip Glasses	Модні окуляри
Holy Ring	Свята каблучка
Holy Stone	Святий камінь
Honu Charm	Амулет хону
Hot Water Pouch	Грілка
Idaten's Belt	Пояс Ідатена
Immortal Charm	Амулет безсмертя
Inferno Horns	Роги інферно
Inferno Ring	Каблучка інферно
Invisible Veil	Невидима вуаль
Jade Wind Necklace	Намисто нефритового вітру
Judgment Cross	Хрест суду
Karma Ring	Каблучка карми
Kugelbein	Кугельбайн
Kuzunoha Tubes	Трубки Кудзунохи
Lambs' Pillow	Подушка ягнят
Lantern Necklace	Намисто-ліхтарик
Leblanc Charm	Амулет «Леблану»
Life Sapping Mask	Маска, що висмоктує життя
Lightning Augite	Авгіт блискавки
Lucky Belt	Щасливий пояс
Lure Keychain	Брелок-приманка
Magic Bullet Belt	Пояс чарівної кулі
Magic Mirror Charm	Амулет магічного дзеркала
Magic Misanga	Чарівна фенечка
Magnetic Necklace	Магнітне намисто
Menehune Dolls	Ляльки менехуне
Midnight Bandana	Опівнічна бандана
Mighty Ring	Могутня каблучка
Mind Choker	Чокер розуму
Miracle Belt	Дивовижний пояс
Moonlight Phones	Навушники «Місячне сяйво»
Mysterious Mask	Таємнича маска
Mystic Ring	Містична каблучка
Night Necklace	Нічне намисто
Notebook	Записник
Nuclear Augite	Ядерний авгіт
Nuclear Ring	Ядерна каблучка
Nuisance Belt	Пояс докучливості
Nuke Brooch	Ядерна брошка
Occult Mask	Окультна маска
Oil Pack	Масляний компрес
Omnipotent Orb	Всемогутня сфера
PI Badge	Значок приватного детектива
Peaceful Potpourri	Мирне попурі
Phys Mirror Charm	Амулет фізичного дзеркала
Picaresque Crown	Пікарескна корона
Picaresque Hat	Пікарескний капелюх
Pick-Me-Up Tie	Підбадьорлива краватка
Portable Battery	Павербанк
Positivity Calendar	Календар позитиву
Prayer Ring	Каблучка молитви
Psy Augite	Псі-авгіт
Psy Necklace	Псі-намисто
Psy Ring	Псі-каблучка
Punch Badge	Значок удару
Purple Bolt Necklace	Намисто фіолетової блискавки
Rage Bangle	Браслет люті
Raging Wristband	Шалений напульсник
Reactor Ring	Каблучка-реактор
Red Band	Червона пов'язка
Red Ribbon	Червона стрічка
Red String	Червона нитка
Rejuvenate Charm	Амулет омолодження
Reprisal Mirror	Дзеркало відплати
Retail Smile Mask	Маска усмішки продавця
Retribution Mirror	Дзеркало розплати
Revenge Mirror	Дзеркало помсти
Revival Charm	Амулет відродження
Ring of Vitality	Каблучка життєвої сили
Rosary of Purity	Вервиця чистоти
Rubber Gloves	Гумові рукавички
Rush Belt	Пояс натиску
S.E.E.S. Armband	Пов'язка S.E.E.S.
Salvation Crown	Корона спасіння
Savior Brooch	Брошка рятівника
Sevens Emblem	Емблема Севенс
Shield Goggles	Захисні окуляри
Shiny Belt	Блискучий пояс
Shockproof Charm	Амулет від шоку
Silver Ice Necklace	Намисто срібного льоду
Silver Key Ring	Срібна в'язка ключів
Sinister Mask	Зловісна маска
Skanda Belt	Пояс Сканди
Skeleton Augite	Авгіт-скелет
Skull Charm	Амулет-череп
Sleep Bangle	Браслет сну
Sleepless Gem	Самоцвіт безсоння
Snow Ring	Снігова каблучка
Soul Choker	Чокер душі
Spark Ring	Каблучка іскри
Special Shot Belt	Пояс особливого пострілу
Spinning Crown	Обертова корона
Spirit Camera	Камера духів
Spirit Sapping Mask	Маска, що висмоктує дух
Spirit Sense Mirror	Дзеркало відчуття духу
St. Hermelin Badge	Значок Св. Гермеліна
Stalling Anklet	Браслет на щиколотку затримки
Star Bracelet	Зірковий браслет
Starlight Glove	Рукавичка зоряного світла
Static Ring	Статична каблучка
Storm Sculpture	Скульптура бурі
Strength Belt	Пояс сили
Sturdy Suspenders	Міцні підтяжки
Supreme Ring	Верховна каблучка
Suspenders	Підтяжки
Team Glasses	Командні окуляри
The Victory Cup	Кубок перемоги
Thief Mask	Маска злодія
Thunder Charm	Амулет грому
Thunder Ring	Каблучка грому
Tiki Keychain	Брелок тікі
Tough Belt	Міцний пояс
Train Badge	Значок потяга
Triple Shot Belt	Пояс потрійного пострілу
Ultimate Augite	Найкращий авгіт
Umi Sachihiko's Belt	Пояс Умі-Сатіхіко
Vacuum Crown	Вакуумна корона
Vajra Anklet	Браслет на щиколотку «Ваджра»
Vajra Belt	Пояс ваджри
Wall Break Charm	Амулет пробиття стіни
Warden's Baton	Кийок наглядача
Weak Anklet	Браслет на щиколотку слабкості
Well-Fed Cape	Накидка ситості
White Band	Біла пов'язка
White Headband	Біла стрічка на голову
Willful Belt	Вольовий пояс
Wind Augite	Авгіт вітру
Wind Ring	Каблучка вітру
Wing Ring	Каблучка-крило
Wood Clappers	Дерев'яні тріскачки
Wooden Clogs	Дерев'яні гета
Yellow Band	Жовта пов'язка
Idaten Anklet	Браслет на щиколотку Ідатена
Rasetsu Anklet	Браслет на щиколотку Расецу
Akashic Shirt	Акашична сорочка
Amulet Shirt	Сорочка-оберіг
Angel's Cape	Накидка ангела
Arcane Robe	Таємнича мантія
Archangel Bra	Бюстгальтер архангела
Armada Collar	Нашийник «Армада»
Army Vest	Армійський жилет
Athletic Shirt	Спортивна футболка
Austere Haori	Суворе хаорі
Baseball Jacket	Бейсбольна куртка
Black Jacket	Чорна куртка
Black Robe	Чорна мантія
Black Wing Robe	Мантія чорних крил
Blood Red Capote	Криваво-червоний капоте
Bloodied Capote	Закривавлений капоте
Bodhi Haori	Хаорі Бодгі
Bottomless Scarf	Бездонний шарф
Brave Scarf	Шарф хоробрості
Breeze Scarf	Шарф бризу
Cat Knight's Collar	Нашийник котячого лицаря
Cat Sweater	Светр з котом
Chaos Undershirt	Майка хаосу
Cone Collar	Конічний комір
Confident Camisole	Упевнена камісоль
Cool Vest	Крутий жилет
Cosmic Undies	Космічні труси
Cozy Dress	Затишна сукня
Dark Jacket	Темна куртка
Dark Undershirt	Темна майка
Death's Black Tights	Чорні колготки смерті
Demon's Jacket	Куртка демона
Dishonored Haori	Зганьблене хаорі
Divine Black Tights	Божественні чорні колготки
Divine Guard	Божественний захист
Dragon Scale Scarf	Шарф із луски дракона
Dress Shirt	Сорочка
Duke's Coat	Пальто герцога
Egoist Shirt	Сорочка егоїста
Elysian Robe	Єлисейська мантія
Fairy Cheongsam	Ципао феї
Fairy Hero Armor	Обладунок героя-феї
Fairy Knight Armor	Обладунок лицаря-феї
Fiery Apron	Вогняний фартух
Fine Silk Dress	Вишукана шовкова сукня
Fine Tapsuan	Вишуканий тапсуан
Fireman Happi	Хаппі пожежника
Fluted Guard	Рифлений захист
Formal Shirt	Офіційна сорочка
Frost Ace Hood	Капюшон морозного аса
Frost Hood	Морозний капюшон
Gambler's Shirt	Сорочка гравця
Ghillie Vest	Маскувальний жилет
Gigas Vest	Жилет гіганта
Glaring Cape	Сліпуча накидка
Godsent Dress	Сукня, послана богом
Golden Dress	Золота сукня
Golden Vest	Золотий жилет
Hard Corset	Жорсткий корсет
Hard Scarf	Жорсткий шарф
Haten Robe	Мантія Хатен
Heavensent Dress	Сукня, послана небом
High Archangel Bra	Бюстгальтер вищого архангела
Hope Shirt	Сорочка надії
Id Collar	Нашийник «Ід»
Immortal Vest	Безсмертний жилет
Immovable Shirt	Непорушна сорочка
Kaiser Vest	Кайзерівський жилет
Kampff Collar	Нашийник «Кампф»
Karna's Robe	Мантія Карни
Khamrai Tao	Кхамрай-тао
King Frost Cape	Накидка Короля Фроста
King Frost Cape EX	Накидка Короля Фроста EX
Lady's Dress	Дамська сукня
Leopard Print Vest	Леопардовий жилет
Light Undershirt	Легка майка
Lightning Blouse	Блуза-блискавка
Lil Devil Undershirt	Майка «Чортеня»
Loose Cutsew	Вільний трикотаж
Lovely Witch's Robe	Мантія милої відьми
Lucky Robe	Щаслива мантія
Lucky Underwear	Щаслива білизна
Lynx Camo Vest	Камуфляжний жилет «Рись»
Lyrical Scarf	Ліричний шарф
Maillot	Купальник-майо
Mandala Vest	Жилет мандали
Measure Collar	Нашийник міри
Memorial Collar	Пам'ятний нашийник
Moonlight Robe	Мантія місячного сяйва
Morose Collar	Похмурий нашийник
Mythical Scarf	Міфічний шарф
Neckerchief	Шийна хустка
Nekomata Coat	Пальто Некомати
Night Shift Haori	Хаорі нічної зміни
Nightwatch Armor	Обладунок нічної варти
Official's Robe	Мантія сановника
Old Angels' Cape	Стара накидка ангелів
Old Black Tights	Старі чорні колготки
Old Cat Collar	Старий котячий нашийник
Old Cheongsam	Старе ципао
Old Coat	Старе пальто
Old Duke's Coat	Старе пальто герцога
Old Fiery Apron	Старий вогняний фартух
Old Ghastly Dress	Стара моторошна сукня
Old Ghillie Vest	Старий маскувальний жилет
Old Haori	Старе хаорі
Old Infinity Scarf	Старий шарф-снуд
Old Khamrai Tao	Старий кхамрай-тао
Old Mythical Scarf	Старий міфічний шарф
Old Pajamas	Стара піжама
Old Primate Vest	Старий жилет примата
Old Pure Collar	Старий чистий нашийник
Old Robe	Стара мантія
Old Scale Scarf	Старий лускатий шарф
Old Shocking Scarf	Старий шокувальний шарф
Old Shroud	Старий саван
Old Sinful Bikini	Старе грішне бікіні
Old Snakeskin Scarf	Старий шарф зі зміїної шкіри
Old Tights	Старі колготки
Old Undershirt	Стара майка
Old Underwear	Стара білизна
Old Vest	Старий жилет
Old Wild Lion Scarf	Старий шарф дикого лева
Old Witch's Robe	Стара мантія відьми
Panzer Dress	Панцерна сукня
Papal Robes	Папське вбрання
Philosophical Scarf	Філософський шарф
Pink Top	Рожевий топ
Pleroma Collar	Нашийник Плероми
Power Camisole	Камісоль сили
Primate Vest	Жилет примата
Print T-Shirt	Футболка з принтом
Pure Collar	Чистий нашийник
Robe of Hatred	Мантія ненависті
Robust Apron	Міцний фартух
Royal Holy Shroud	Королівська свята плащаниця
Rubber Scarf	Гумовий шарф
Rune Vest	Руновий жилет
Saint's Tunic	Туніка святого
Scarf of Mercy	Шарф милосердя
Shikigami Dress	Сукня сікігамі
Shining Vest	Сяйний жилет
Shocking Scarf	Шокувальний шарф
Shoulder Pads	Наплічники
Silk Dress	Шовкова сукня
Sinful Bikini	Грішне бікіні
Sirius Armor	Обладунок «Сіріус»
Sirius Armor EX	Обладунок «Сіріус» EX
Snakeskin Scarf	Шарф зі зміїної шкіри
Sooty Astro Armor	Закіптявілий астрообладунок
Sooty Black Armor	Закіптявілий чорний обладунок
Sooty Bolt Armor	Закіптявілий обладунок блискавки
Sooty Boots	Закіптявілі чоботи
Sooty Cat's Armor	Закіптявілий котячий обладунок
Sooty Cheongsam	Закіптявіле ципао
Sooty Dancer's Garb	Закіптявіле вбрання танцівниці
Sooty Dark Armor	Закіптявілий темний обладунок
Sooty Divine Armor	Закіптявілий божественний обладунок
Sooty Elder's Armor	Закіптявілий обладунок старійшини
Sooty Feather Coat	Закіптявіле пір'яне пальто
Sooty Ghastly Gear	Закіптявіле моторошне спорядження
Sooty Gilded Collar	Закіптявілий позолочений комір
Sooty Grifter's Garb	Закіптявіле вбрання шахрая
Sooty Heavy Armor	Закіптявілий важкий обладунок
Sooty Horn	Закіптявілий ріг
Sooty Ladies' Armor	Закіптявілий жіночий обладунок
Sooty Lion's Mane	Закіптявіла лев'яча грива
Sooty Man's Armor	Закіптявілий чоловічий обладунок
Sooty Monkey Fur	Закіптявіле мавпяче хутро
Sooty Ogress' Gear	Закіптявіле спорядження людожерки
Sooty Regalia	Закіптявілі регалії
Sooty Rogue's Garb	Закіптявіле вбрання пройдисвіта
Sooty Scale Armor	Закіптявілий лускатий обладунок
Sooty Snakeskin	Закіптявіла зміїна шкіра
Sooty Spotted Fur	Закіптявіле плямисте хутро
Sooty Wolf's Coat	Закіптявіле вовче пальто
Sooty Yorishiro	Закіптявілий йорісіро
Space Suit	Скафандр
Sparkly Collar	Блискучий нашийник
Starry Wisdom Vest	Жилет зоряної мудрості
Sublime Collar	Величний нашийник
Succubus Pajamas	Піжама сукуба
Super Lucky Robe	Надщаслива мантія
Survival Vest	Жилет для виживання
Tantric Oath	Тантрична клятва
Tao Robe	Мантія дао
Tapsuan	Тапсуан
Titanium Corset	Титановий корсет
Tomoe's Doumaru	Доумару Томое
Turtleneck	Водолазка
Unio Dress	Сукня «Уніо»
Vest of Life	Жилет життя
Water Crown	Водяна корона
Weird Wrap	Дивна обгортка
Wild Lion Scarf	Шарф дикого лева
Yama Dress	Сукня Ями
Zen Outfit	Дзен-вбрання
Amazon Axe	Сокира амазонки
Answerer	Відповідач
Antique Gunto	Старовинний гунто
Arc Mace	Булава-дуга
Armageddon Rod	Жезл Армагеддону
Arsène's Cane	Тростина Арсена
Athame	Атаме
Axe	Сокира
Baccarat Knuckle	Кастет «Баккара»
Bandit Sword	Меч бандита
Bardiche	Бердиш
Barog Whip	Батіг Барога
Baselard	Базелард
Battle Hammer	Бойовий молот
Bear Gloves	Ведмежі рукавиці
Big Bang Axe	Сокира «Біг Бенг»
Big Bear Gloves	Великі ведмежі рукавиці
Big Sleep Stick	Великий сонний кийок
Black Kogatana	Чорна когатана
Blizz Dagger	Кинджал хуртовини
Blood Scimitar	Кривавий ятаган
Boss Bush Hammer	Бос-бучарда
Bout Gloves	Бійцівські рукавиці
Brass Knuckles	Латунний кастет
Bright Sword	Яскравий меч
Burn Whip	Пекучий батіг
Bush Hammer	Бучарда
Celtis	Кельтис
Chain Whip	Ланцюговий батіг
Champion	Чемпіон
Chief's Cutlass	Кортик шефа
Claiomh Solais	Клівь Солас
Clenched Fist	Стиснутий кулак
Cosmic Sword	Космічний меч
Crescent Axe	Сокира-півмісяць
Crusader	Хрестоносець
Dainaraka Whip	Батіг Дайнарака
Damascus Sword	Дамаський меч
Dark Cutlass	Темний кортик
Death Axe	Сокира смерті
Death Contract	Контракт смерті
Death Promise	Обіцянка смерті
Decisive Rapier	Рішуча рапіра
Decorative Whip	Декоративний батіг
Delta Knuckle	Кастет «Дельта»
Demon Fist	Кулак демона
Demon Pipe	Труба демона
Disciplinary Whip	Дисциплінарний батіг
Dragon God Pole	Жердина бога-дракона
Dread Saber	Шабля жаху
Electromag Whip	Електромагнітний батіг
Envy Chain	Ланцюг заздрощів
Falchion	Фальшіон
Fear of Pain	Страх болю
Fervent Bat	Палка бита
Fine Ruyi Jingu Bang	Вишуканий Жуї Цзіньгу Бан
Flash Punch	Спалах-удар
Fleurs du Mal	Квіти зла
Frenzy Dagger	Кинджал шаленства
Fundo-Kusari	Фундо-кусарі
Gaea Presser	Прес Геї
Gang Star	Гангстар
Gekkou	Гекко
Gilgamesh Axe	Сокира Гільгамеша
Goat Leather Whip	Батіг з козячої шкіри
God Saber	Божественна шабля
Gordios	Гордій
Grand Presser	Великий прес
Grapnel	Гак-кішка
Great Whip Sword	Великий меч-батіг
Guillotine Saber	Шабля-гільйотина
Guilty Whip	Батіг провини
Gunto	Гунто
Hard Branch	Тверда гілка
Headhunter Ladle	Черпак мисливця за головами
Headhunter Ladle EX	Черпак мисливця за головами EX
Heat Whip	Гарячий батіг
Heavy Grip	Важкий хват
Heavy Mace	Важка булава
Heavy Saber	Важка шабля
Heavy Steel Pipe	Важка сталева труба
Hell Knuckles	Пекельні кастети
Hell Slugger	Пекельна бита
Helper Knife	Ніж-помічник
Hero Whip	Батіг героя
Hinokagutsuchi	Хінокагуцуті
Hinokagutsuchi II	Хінокагуцуті II
Hot-Blooded Sword	Гарячий меч
Iai Katana	Катана для іай
Ice Axe	Льодоруб
Igniter	Запальник
Imprisoned Mjolnir	Ув'язнений Мйольнір
Infini-saber	Нескінченна шабля
Iron Fist	Залізний кулак
Iron Pipe	Залізна труба
Jagato	Ягато
Judge Mace	Булава судді
Kaito Ranma	Кайто Ранма
Kaketsushinto	Какецусінто
Kasumi Aid Rapier	Рапіра допомоги Касумі
Kasumi Awaken Rapier	Рапіра пробудження Касумі
Katana	Катана
Killing Scalpel	Смертельний скальпель
Kintaro Axe	Сокира Кінтаро
Knuckle Duster	Кастет
Koedo Sword	Меч Коедо
Kopis	Копіс
Kukri	Кукрі
Last Hammer	Останній молот
Leather Whip	Шкіряний батіг
Lumina Saber	Шабля Люміна
Lunar Cutlass	Місячний кортик
Mach Punch	Мах-удар
Machete	Мачете
Masamune	Масамуне
Masquerade Ribbon	Маскарадна стрічка
Master's Iai Katana	Катана майстра іай
Mega Axe	Мегасокира
Mega Knife	Меганіж
Megistos Sword	Меч Мегістос
Metal Duster	Металевий кастет
Meteor Knuckle	Метеоритний кастет
Mirage Whip	Батіг міражу
Misericorde	Мізерикордія
Mjolnir	Мйольнір
Murasame	Мурасаме
Mut Cutlass	Кортик Мут
Naraka Whip	Батіг Нарака
Normal Rod	Звичайний жезл
Old Man's Fist	Кулак старого
Omega Knuckle	Кастет «Омега»
Orochito	Оротіто
Panic Sword	Меч паніки
Paradise Lost	Втрачений рай
Parrying Dagger	Даги для парирування
Plasma Knife	Плазмовий ніж
Pro Parrying Dagger	Професійна дага для парирування
Pro Skinning Knife	Професійний ніж-шкуродер
Prophet's Hand	Рука пророка
Punish Dagger	Кинджал кари
Quasar Saber	Квазарна шабля
Rapier	Рапіра
Rebel Knife	Ніж бунтаря
Red Demon Blade	Клинок червоного демона
Resting Sword	Спочилий меч
Royal Dagger	Королівський кинджал
Ruyi Jingu Bang	Жуї Цзіньгу Бан
Sabazios	Сабазій
Sanction	Санкція
Saw Saber	Шабля-пила
Scimitar	Ятаган
Seishiki Sword	Меч Сейсікі
Senryou Yakusha	Сенрьо Якуся
Shamshir	Шамшир
Shikomi Kiseru	Сікомі-кісеру
Silver Dagger	Срібний кинджал
Skin Ripper	Шкуродер
Skinning Knife	Ніж-шкуродер
Sleep Stick	Сонний кийок
Sleeper Blade	Сонний клинок
Snow Queen's Whip	Батіг Снігової Королеви
Snow Queen's Whip II	Батіг Снігової Королеви II
Sonic Blade	Звуковий клинок
Spike Rod	Шипований жезл
Spike Whip	Шипований батіг
Strike Tail	Ударний хвіст
Stun Baton	Електрокийок
Stun Dagger	Приголомшливий кинджал
Super Megido Rod	Супермегідо-жезл
Sword of Sinai	Меч Синаю
Sword of Sinai II	Меч Синаю II
Taiji Axe	Сокира тайцзі
Talwar	Тальвар
Ten Ichimonji	Тен-Ітімондзі
The Great Thief Stick	Кийок Великого злодія
Unparalleled Vajra	Неперевершена ваджра
Usumidori	Усумідорі
Vajra	Ваджра
Venture Saber	Шабля авантюриста
Vertical Edge	Вертикальне лезо
Victory Beam	Промінь перемоги
Wakizashi	Вакідзасі
Warrior Whip	Батіг воїна
Whip Sword	Меч-батіг
White Snow Rapier	Рапіра білого снігу
Wicked Iron Pipe	Лиха залізна труба
Yuibitachi	Юібітаті
Zandouto	Дзандото
Zirah Bouk	Зіра-бук
AR-X	AR-X
Ancient Day	Прадавній день
Annihilator	Анігілятор
Balalaika	Балалайка
Baptism	Хрещення
Bianchi SBAS	Б'янкі SBAS
Black Assault	Чорний штурм
Blitz MG	Бліц MG
Brain Shot	Постріл у мозок
Calamity Gun	Зброя лиха
Casino Battle Gun	Казино-бойовий пістолет
Casino Start	Казино-старт
Cat Buster	Котячий бластер
Catnap	Котячий сон
Comet 3	Комета 3
Crimson Gun	Багряна зброя
Doomsday	Судний день
Dreamstone	Камінь мрій
Eliminator	Ліквідатор
Eraser	Ластик
Falcon	Сокіл
Fireworks	Феєрверк
From Heaven	З небес
Fury	Лють
GL Replica	Репліка GL
Governance	Урядування
Granelli M3	Гранеллі M3
Gungnir	Гунгнір
H. Renhappou	Х. Рендзюхо
Heaven's Gate	Брама небес
Heavy Assault	Важкий штурм
Hellfire	Пекельний вогонь
Hizutsu	Хідзуцу
Jig 227	Джиг 227
Judge End	Кінець суду
Judge of Hell	Суддя пекла
K. Gouhou	К. Гохо
K. Gouhou EX	К. Гохо EX
Kiraihou	Кірайхо
Levinson M31	Левінсон M31
Ling Xing	Лін Сін
Makaronov	Макаронов
Masterkey	Майстер-ключ
Mauser	Маузер
Megido Blaster	Мегідо-бластер
Megido Fire	Мегідо-вогонь
Milkor	Мілкор
Mirrirmina	Міррірміна
Mirrirmina EX	Міррірміна EX
Model Gun	Модель пістолета
Moebius	Мебіус
Nataraja	Натараджа
Nataraja EX	Натараджа EX
No Mercy	Без жалю
Northern Light	Північне сяйво
Orochi	Ороті
Pandemonium	Пандемоніум
Paw-omber	Лапомбер
Pawzooka	Лапузука
Peacemaker	Миротворець
Phantom Killer	Фантомний убивця
Pink Buster	Рожевий бластер
Providence	Провидіння
Pumpkin Bomb	Гарбузова бомба
Pumpkin Buster	Гарбузовий бластер
R.I.Pistol	R.I.P.-істолет
Rebel Rifle	Гвинтівка бунтаря
Red Five	Червона п'ятірка
Replica AR	Репліка AR
Replica Revolver	Репліка револьвера
Replica SMG	Репліка пістолета-кулемета
Reversion	Реверсія
Riot Police	Спецназ
Roosevelt	Рузвельт
Ryuraihou	Рюрайхо
Sahasrara	Сахасрара
Sahasrara EX	Сахасрара EX
Sand Hawk	Пісчаний яструб
Scorcher	Спопелювач
Shooting Star	Падаюча зірка
Shrike	Сорокопуд
Sirius	Сіріус
Slingbow	Рогатка-лук
Star Slayer	Вбивця зірок
Star-H	Стар-H
Sterlidge	Стерлідж
Sudarshana	Сударшана
Sudarshana EX	Сударшана EX
Tarantula	Тарантул
Tkachev	Ткачов
Town Burner	Палій міст
Trooper	Солдат
Twilight	Сутінки
Tyrant Pistol	Пістолет тирана
Tyrant Pistol EX	Пістолет тирана EX
Unlimited	Безмежний
Utopia	Утопія
W Rifle Replica	Репліка гвинтівки W
Western SMG	Вестерн-ПК
Wild Hunt	Дике полювання
Wildborn	Дикороджений
Yagrush	Ягруш
Yagrush EX	Ягруш EX
Yellow Girl	Жовта дівчина
Amber Stamp	Бурштинова печатка
Amethyst	Аметист
Animal Brush	Пензель із шерсті
Aquamarine	Аквамарин
Bad Sculpture	Погана скульптура
Bastet Statue	Статуетка Бастет
Bent Staff	Погнута палиця
Blade Flashlight	Ліхтарик-лезо
Blessed Trumpet	Благословенна сурма
Brass Pocket Watch	Латунний кишеньковий годинник
Broken Baton	Зламаний кийок
Broken Handcuffs	Зламані кайданки
Broken Meter Panel	Зламана панель приладів
Broken Telescope	Зламаний телескоп
Broken Thermostat	Зламаний термостат
Bronze Compass	Бронзовий компас
Cameo Brooch	Брошка-камея
Canopic Jar	Канопа
Card Shuffler	Тасувальна машинка
Chipped Glass	Щерблений келих
Copper Chain	Мідний ланцюжок
Copper Hand	Мідна рука
Copper Heart	Мідне серце
Copper Lump	Мідний злиток
Copper Mist	Мідний туман
Copper Moon	Мідний місяць
Copper Star	Мідна зірка
Coral Pendant	Кораловий кулон
Cracked Vase	Тріснута ваза
Crappy Portrait	Жахливий портрет
Crushed Shield	Зім'ятий щит
Damascene Cane	Тростина з насічкою
Dead Solar Panel	Несправна сонячна панель
Dead Surgical Light	Несправна хірургічна лампа
Dealer Ring	Каблучка круп'є
Diamond	Діамант
Diamond Lump	Діамантовий злиток
Dice Shaker	Стакан для кісток
Distorted Lens	Спотворена лінза
Dull Sword	Тупий меч
Ebony Box	Скринька з ебену
Emerald	Смарагд
Faded Silk Hat	Вицвілий циліндр
Fine Washi	Вишуканий васі
Garnet	Гранат
Glory Staff	Палиця слави
Gold Chain	Золотий ланцюжок
Gold Coin	Золота монета
Gold Earrings	Золоті сережки
Gold Emblem	Золота емблема
Gold Hand	Золота рука
Gold Heart	Золоте серце
Gold Lump	Золотий злиток
Gold Mist	Золотий туман
Gold Moon	Золотий місяць
Gold Star	Золота зірка
Gold Uraeus	Золотий урей
Golden Cap Badge	Золота кокарда
Gray Cufflinks	Сірі запонки
Grooved Copper	Рифлена мідь
Grooved Silver	Рифлене срібло
Hanging Scroll	Настінний сувій
Hannya Mask	Маска ханнья
Hi-Fi Megaphone	Hi-Fi мегафон
Hole Copper	Мідь з отвором
Hole Silver	Срібло з отвором
Holey Helmet	Дірявий шолом
Huge Gold Lump	Величезний золотий злиток
Incomplete Deck	Неповна колода
Ink Wash Art	Картина тушшю
Inkless Pen	Ручка без чорнила
Ivory Dice	Кості зі слонової кістки
Jade	Нефрит
Jewel Mummy	Мумія з коштовностями
Large Gold Lump	Великий золотий злиток
Laser Pointer	Лазерна указка
Leather Case	Шкіряний футляр
Locked Collar	Замкнений нашийник
Loose Magnetic Tape	Розмотана магнітна стрічка
Loose Sash	Розв'язаний пояс
Lustrous Iron Ball	Блискуча залізна куля
Luxury Watch	Розкішний годинник
Magician Bowtie	Метелик фокусника
Marble Chessboard	Мармурова шахівниця
Masquerade Mask	Маскарадна маска
Mini Sound Sensor	Міні-датчик звуку
Mirror Ball	Дзеркальна куля
Misprinted Poster	Плакат із браком друку
Money Counter	Лічильник банкнот
Moon Stone	Місячний камінь
Mummy Mask	Маска мумії
Music Box	Музична скринька
Nude Candle Stand	Свічник з оголеною фігурою
Office Calculator	Офісний калькулятор
Old Coin	Стара монета
Old Kaleidoscope	Старий калейдоскоп
Old Projector	Старий проектор
Onyx	Онікс
Opal	Опал
Peacock Fan	Віяло з пір'я павича
Pearl	Перлина
Pearl Necklace	Перлове намисто
Picture Scroll	Сувій з малюнками
Pillar Piece	Уламок колони
Plastic Frame	Пластикова рамка
Platinum	Платина
Platinum Lump	Платиновий злиток
Porcelain Teacup	Порцелянова чашка
Precious Bill	Цінна банкнота
Prison Officer Badge	Значок тюремника
Pro Dart	Професійний дротик
Punctured PCB	Пробита плата
Ra Mural	Фреска Ра
Radar Antenna	Радарна антена
Raden Plate	Тарілка з перламутром
Rainbow Diode	Райдужний діод
Rare Coin	Рідкісна монета
Rare Metal	Рідкісний метал
Ripped Uniform Cap	Порваний форменний кашкет
Robot Arm	Рука робота
Ruby	Рубін
Rusted Ankh	Іржавий анкх
Rusted Handcuffs	Іржаві кайданки
Safe Dial	Диск сейфа
Sage Astrolabe	Астролябія мудреця
Sapphire	Сапфір
Sarcophagus Bit	Уламок саркофага
Scarab Charm	Амулет-скарабей
Scratched Sword	Подряпаний меч
Sekhmet Mural	Фреска Сехмет
Shackles	Кайдани
Sharp Barbed Wire	Гострий колючий дріт
Silent Horn	Німий ріжок
Silver Arm Band	Срібна пов'язка на руку
Silver Chain	Срібний ланцюжок
Silver Cutlery	Срібні столові прибори
Silver Hand	Срібна рука
Silver Heart	Срібне серце
Silver Lump	Срібний злиток
Silver Mist	Срібний туман
Silver Monocle	Срібний монокль
Silver Moon	Срібний місяць
Silver Star	Срібна зірка
Small Gold Lump	Малий золотий злиток
Smoked Cigar	Недопалок сигари
Sooty Kettle	Закіптявілий чайник
Space Food	Космічна їжа
Spaceship Stick	Штурвал космічного корабля
Stock Certificate	Акційний сертифікат
Strange Lantern	Дивний ліхтар
Tangled USB Cord	Заплутаний USB-кабель
Tattered Wallet	Пошарпаний гаманець
Thin Copper	Тонка мідь
Thin Silver	Тонке срібло
Tidy Prison Uniform	Охайна тюремна роба
Topaz	Топаз
Torn Papyrus	Порваний папірус
Tortoise Hairpin	Черепахова шпилька
Turquoise	Бірюза
UFO Drone	Дрон-НЛО
Ukiyo-e	Укійо-е
Unopenable Lock	Замок, що не відмикається
Unsigned Mug	Чашка без підпису
Victor Laurel	Лавр переможця
Voice Recorder	Диктофон
Voltage Converter	Перетворювач напруги
Warped Wheel	Погнуте колесо
Worn Stamp	Стерта печатка
Aigis Costume	Костюм Айгіс
Black Leotard	Чорне трико
Boss's Suit	Костюм боса
Burroughs Costume	Костюм Берроуза
Butler Suit	Костюм дворецького
Catherine's Cami	Камісоль Кетрін
Christmas Outfit	Різдвяний костюм
Cyber Gear	Кіберспорядження
Dancewear	Танцювальний одяг
Dark Suit	Темний костюм
Demonica Head	Шолом «Демоніка»
Demonica Suit	Костюм «Демоніка»
Erica's Uniform	Форма Еріки
Featherman Suit	Костюм Фезермена
Gekkoukan High	Старша школа Гекковкан
Gouto Costume	Костюм Гото
Hazama's Uniform	Форма Хадзами
Imperial Uniform	Імперська форма
Johnny's Coat	Пальто Джонні
Karukozaka High	Старша школа Карукодзака
Kasugayama High	Старша школа Касугаяма
Katherine's Outfit	Вбрання Катерини
Long Nose Outfit	Костюм Довгоносика
Loungewear	Домашній одяг
Maid Uniform	Форма покоївки
Metal Rider	Металевий вершник
Moonlight Outfit	Костюм місячного сяйва
Morgana Classic	Класична Моргана
Musketeer Suit	Костюм мушкетера
New Cinema Outfit	Костюм «Нове кіно»
Orlando's Fashion	Вбрання Орландо
Ouran High	Старша школа Оуран
Outlaw's Attire	Вбрання розбійника
Phantom Suit	Фантомний костюм
Pirate Armor	Піратський обладунок
Prince Suit	Костюм принца
Red Latex Suit	Червоний латексний костюм
Rin's One Piece	Сукня Рін
Samurai Garb	Вбрання самурая
Seven Sisters High	Старша школа Севен Сістерс
Shadow Ops Uniform	Форма тіньових операцій
Shujin Uniform	Форма Сюдзіну
St. Hermelin High	Старша школа Св. Гермеліна
Starlight Outfit	Костюм зоряного світла
Starter Clothes	Початковий одяг
Stray Sheep Suit	Костюм заблудлої вівці
Summer Clothes	Літній одяг
Summer Uniform	Літня форма
Swimsuit	Купальник
Teddie Costume	Костюм Тедді
Toby's Overalls	Комбінезон Тобі
Tracksuit	Спортивний костюм
Trish Costume v1	Костюм Тріш, вар. 1
Trish Costume v2	Костюм Тріш, вар. 2
Ultramarine Outfit	Ультрамариновий костюм
Vincent's Outfit	Вбрання Вінсента
Winter Clothes	Зимовий одяг
Winter Uniform	Зимова форма
Yasogami High	Старша школа Ясоґамі
Yumizuki High	Старша школа Юмідзукі
Ailment Hunter	Мисливець на стани
Allure of Wisdom	Принада мудрості
Atomic Bloodline	Атомний родовід
Atomic Hellscape	Атомне пекло
Ave Maria	Аве Марія
Bargain Bolts	Вигідні блискавки
Blessed Bloodline	Благословенний родовід
Blessed Spirit	Благословенний дух
Bloodstained Eyes	Закривавлені очі
Bolstering Force	Зміцнювальна сила
Chi You's Blessing	Благословення Чию
Circle of Sadness	Коло смутку
Cocytus	Коцит
Cold-Blooded	Холоднокровність
Cool Customer	Холодний розум
Country Maker	Творець країни
Crisis Control	Контроль кризи
Cursed Bloodline	Проклятий родовід
Deathly Illness	Смертельна хвороба
Demon's Bite	Укус демона
Draining Mouth	Висмоктувальна паща
Drunken Passion	П'яна пристрасть
Eccentric Temper	Ексцентричний норов
Electric Bloodline	Електричний родовід
Explosive Scheme	Вибуховий задум
Flawless Spirit	Бездоганний дух
Foul Odor	Сморід
Foul Stench	Сильний сморід
Frenzied Bull	Скажений бик
Frigid Bloodline	Крижаний родовід
Gaia Blessing	Благословення Геї
Gaia Pact	Угода з Геєю
Ghost Nest	Гніздо привидів
Gloomy Child	Похмуре дитя
Gluttonmouth	Ненажерлива паща
God Maker	Творець богів
Grace of Mother	Материнська ласка
Grace of the Olive	Благодать оливи
Hallowed Spirit	Освячений дух
Hazy Presence	Туманна присутність
Heated Bloodline	Гарячий родовід
Hollow Jester	Порожній блазень
Icy Glare	Крижаний погляд
Immunity	Імунітет
Infinite Scheme	Нескінченний задум
Ingenious Spirit	Винахідливий дух
Intense Focus	Глибоке зосередження
Internal Hypnosis	Внутрішній гіпноз
Inviolable Beauty	Непорушна краса
Iron Heart	Залізне серце
Just Die	Просто помри
Linked Bloodline	Пов'язаний родовід
Majestic Presence	Велична присутність
Martyr's Gift	Дар мученика
Mastery of Magic	Опанування магії
Mighty Gaze	Могутній погляд
Mother's Lament	Плач матері
Mouth of Savoring	Паща смакування
Naranari	Наранарі
Omen	Знамення
Pagan Allure	Язичницька принада
Pinch Anchor	Якір у скруті
Pinnacle of Magic	Вершина магії
Positive Thoughts	Позитивні думки
Potent Hypnosis	Сильний гіпноз
Proud Presence	Горда присутність
Psychic Bloodline	Псі-родовід
Raging Temper	Шалений норов
Rare Antibody	Рідкісне антитіло
Relentless	Невблаганний
Relief Bloodline	Цілющий родовід
Retaliating Body	Тіло відплати
Savior Bloodline	Родовід рятівника
Scoundrel Eyes	Очі негідника
Skillful Combo	Вправне комбо
Skillful Technique	Вправна техніка
Static Electricity	Статична електрика
Striking Weight	Ударна вага
Tactical Spirit	Тактичний дух
Tag Team	Командна робота
Thermal Conduct	Теплопровідність
Undying Fury	Невмируща лють
Universal Law	Всесвітній закон
Unparalleled Eyes	Неперевершені очі
Vahana's Wings	Крила вахани
Veil of Midnight	Покров півночі
Veil of Sunrise	Покров світанку
Vitality of the Tree	Життєва сила дерева
Wealth of Lotus	Багатство лотоса
Will of the Sword	Воля меча
Wind Bloodline	Родовід вітру
Brain Shaker Belt	Пояс «Струс мозку»
Cornered Belt	Пояс «Ікло загнаного звіра»
Gatling Belt	Пояс «Гатлінг-удар»
Megaton Belt	Пояс «Мегатонний наліт»
Myriad Slash Belt	Пояс «Міріади розрізів»
Rakshasa Belt	Пояс Ракшаси
"""


def pattern(en, M, S):
    m = re.fullmatch(r"(.+) R", en)
    if m and m.group(1) in M:
        return f"{M[m.group(1)]} R"
    m = re.fullmatch(r"(.+) R", en)
    if m:  # rare Persona-treasure items: "Regent R", "Koh-i-Noor R"
        base = {"Crystal Skull": "Кришталевий череп", "Hope Diamond": "Діамант Хоупа", "Koh-i-Noor": "Кохінур",
                "Orichalcum": "Орихалк", "Orlov": "Орлов", "Queen's Necklace": "Намисто королеви",
                "Regent": "Регент", "Stone of Scone": "Сконський камінь"}.get(m.group(1))
        if base:
            return f"{base} R"
    m = re.fullmatch(r"Spiral (.+)", en)
    if m and m.group(1) in M:
        return f"{M[m.group(1)]} «Спіраль»"
    m = re.fullmatch(r"(Anti-)?(\w+?)(proof)? (Choker|Bracelet)", en)
    if m and m.group(2) in EL_GEN and (m.group(1) or m.group(3)):
        what = "Чокер" if m.group(4) == "Choker" else "Браслет"
        if m.group(1):  # Anti-X is a separate, stronger line than Xproof
            anti = {"Fire": "Антивогонь", "Ice": "Антилід", "Elec": "Антиелектрика", "Wind": "Антивітер",
                    "Psy": "Антипсі", "Nuke": "Антиядро", "Bless": "Антисвітло", "Curse": "Антипрокляття"}
            return f"{what} «{anti[m.group(2)]}»"
        return f"{what} від {EL_GEN[m.group(2)]}"
    m = re.fullmatch(r"(\w+) Breaker Bell", en)
    if m and m.group(1) in EL_GEN:
        return f"Дзвіночок пробиття {EL_GEN[m.group(1)]}"
    m = re.fullmatch(r"(\w+) Augite", en)
    if m and m.group(1) in ("Fire", "Ice"):
        return f"Авгіт {EL_GEN[m.group(1)]}"
    m = re.fullmatch(r"(Crystal|Ring) of (\w+)", en)
    if m and m.group(2) in SIN_GEN:
        return f"{'Кристал' if m.group(1) == 'Crystal' else 'Каблучка'} {SIN_GEN[m.group(2)]}"
    m = re.fullmatch(r"(.+) (Belt|Anklet|Crown)", en)
    if m and m.group(1) in S:
        return f"{CARRIER[m.group(2)]} «{S[m.group(1)]}»"
    m = re.fullmatch(r"(SP Adhesive|Regen Patch) (\d)", en)
    if m:
        return f"{'ОД-пластир' if m.group(1) == 'SP Adhesive' else 'Пластир регенерації'} {m.group(2)}"
    return None


def main():
    S = load_skill_uk()
    with open(ROOT / "tools/glossary/proposals.tsv", encoding="utf-8") as f:
        main_prop = {l.split("\t", 1)[0] for l in f if l.strip() and not l.startswith("#")}
    rows = []
    with open(ROOT / "glossary.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["category"] in CATS and r["status"] != "approved" and r["en"] not in main_prop:
                rows.append(r)
    M = dict(l.split("\t", 1) for l in MANUAL.strip().splitlines())
    out, missing = [], []
    for r in sorted(rows, key=lambda r: r["en"]):
        uk = M.get(r["en"]) or pattern(r["en"], M, S)
        (out.append((r["en"], uk, r["category"], "" if r["en"] in M else "шаблон")) if uk
         else missing.append(r["en"]))
    with open(ROOT / "tools/glossary/proposals_equipment.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("en\tuk\talternatives\tcategory\tnote\n")
        for en, uk, cat, note in out:
            f.write(f"{en}\t{uk}\t\t{cat}\t{note}\n")
    print(f"{len(out)} written, {len(missing)} missing: {missing}")


if __name__ == "__main__":
    main()
