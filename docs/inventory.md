# Инвентаризация текстовых и контейнерных файлов P5R (PC/Steam)

Сгенерировано `tools/scripts/inventory.py`. Полный список — [inventory.tsv](inventory.tsv) (колонки: cpk, path, ext, size, magic, nested, inner, overridden).

- `path` с `::` — файл внутри контейнера (PAK/PAC/BIN), напр. `INIT/X.PAK::Y.BMD`.
- `magic` — тип по сигнатуре (`bmd` = MSG1, `bf` = FLW0), независимо от расширения.
- `overridden=yes` — файл BASE.CPK, перекрытый одноимённым файлом из EN.CPK (игра берёт EN).
- `inner` — число записей внутри контейнера.

Источники: `C:\SteamLibrary\steamapps\common\P5R\CPK\EN.CPK` (целиком) и `BASE.CPK` (только bmd/bf/tbl/ftd/ctd/pak/pac/arc/fnt/msg). Оглавления всех CPK — [cpk_lists/](cpk_lists/).

## Сводка по типам

| CPK | уровень | тип | файлов | размер, КБ |
|---|---|---|---:|---:|
| EN | в контейнере | ftd | 133 | 185 |
| EN | в контейнере | bf | 114 | 469 |
| EN | в контейнере | ctd | 75 | 277 |
| EN | в контейнере | bmd | 72 | 731 |
| EN | в контейнере | tbl | 12 | 2098 |
| EN | в контейнере | fnt | 2 | 566 |
| EN | файл | bf | 5182 | 71356 |
| EN | файл | bmd | 2019 | 9237 |
| EN | файл | pak | 57 | 187159 |
| EN | файл | bin | 21 | 786956 |
| EN | файл | ftd | 16 | 188 |
| EN | файл | pac | 9 | 70927 |
| EN | файл | tbl | 3 | 210 |
| EN | файл | fnt | 1 | 8948 |
| BASE | в контейнере | bf | 1 | 27 |
| BASE | файл | bmd | 1779 | 7394 |
| BASE | файл | bf | 261 | 3839 |
| BASE | файл | pac | 123 | 400283 |
| BASE | файл | ftd | 80 | 287 |
| BASE | файл | pak | 39 | 152236 |
| BASE | файл | tbl | 13 | 2040 |
| BASE | файл | fnt | 5 | 5828 |
| BASE | файл | arc | 1 | 1696 |

## Текстовые скрипты (BMD/BF), которые реально использует игра

Без учёта BASE-файлов, перекрытых EN. Группировка по верхней папке.

| CPK | папка | BMD | BF |
|---|---|---:|---:|
| EN | EVENT_DATA/MESSAGE | 1922 | 0 |
| EN | CAMP/CHAT | 0 | 1239 |
| EN | EVENT_DATA/SCRIPT | 0 | 934 |
| EN | SCRIPT/FIELD | 0 | 904 |
| EN | FIELD/KF_EVENT | 0 | 457 |
| EN | TUTORIAL | 0 | 256 |
| EN | FIELD/INIT | 0 | 254 |
| EN | FIELD/HIT | 0 | 228 |
| EN | FIELD/MY_PALACE | 1 | 226 |
| EN | BATTLE/EVENT | 0 | 204 |
| EN | FIELD/NPC | 0 | 161 |
| EN | FIELD/DOOR | 0 | 130 |
| EN | FIELD/OBJECT_HIT | 0 | 126 |
| EN | FIELD/BOX | 0 | 121 |
| EN | MINIGAME/CROSSWORD | 41 | 0 |
| EN | BATTLE/TALK | 0 | 28 |
| EN | INIT | 27 | 0 |
| EN | COMMUNITY/EVENT | 25 | 0 |
| EN | FIELD/PANEL | 10 | 7 |
| EN | FACILITY | 8 | 5 |
| EN | FIELD/ENEMY | 13 | 0 |
| EN | MINIGAME/FUGOU | 12 | 1 |
| EN | BATTLE/MESSAGE | 9 | 0 |
| EN | MINIGAME | 8 | 0 |
| EN | FIELD/ETC | 0 | 4 |
| EN | FIELD/SAFETY_ROOM | 0 | 4 |
| EN | NETWORK | 4 | 0 |
| EN | DEVICE/SAVELOAD | 3 | 0 |
| EN | FIELD/PARTY | 0 | 3 |
| EN | MYPALACE/PALACEMAKER | 2 | 0 |
| EN | TITLE | 0 | 2 |
| EN | FIELD/SCRIPT | 0 | 1 |
| EN | FIELD/TELOP | 1 | 0 |
| EN | FIELD/TV | 0 | 1 |
| EN | GAME | 1 | 0 |
| EN | MYPALACE/AWARD | 1 | 0 |
| EN | MYPALACE/GALLERY | 1 | 0 |
| EN | MYPALACE/MOVIE | 1 | 0 |
| EN | MYPALACE/SOUND | 1 | 0 |
| BASE | BATTLE/SCRIPT | 0 | 145 |
| BASE | FIELD/VOICE_HIT | 0 | 37 |
| BASE | SCRIPT/FIELD | 0 | 35 |
| BASE | EVENT_DATA/MESSAGE | 31 | 0 |
| BASE | EVENT_DATA/SCRIPT | 0 | 20 |
| BASE | SCHEDULER | 0 | 13 |
| BASE | CAMP | 2 | 0 |
| BASE | FIELD/PANEL | 1 | 1 |
| BASE | MISSION/SCRIPT | 0 | 2 |
| BASE | BATTLE | 0 | 1 |
| BASE | BATTLE/RESULT | 1 | 0 |
| BASE | CAMP/CHAT | 0 | 1 |
| BASE | FIELD/SAFETY_ROOM | 0 | 1 |
| BASE | FONT/CHECK | 1 | 0 |
| BASE | SCRIPT | 0 | 1 |

**Итого:** BMD — 2127, BF — 5553.

## Таблицы (.tbl / .ctd / .ftd)

| CPK | путь | размер |
|---|---|---:|
| EN | `BATTLE/TABLE.PAC::AICALC.TBL` | 129248 |
| EN | `BATTLE/TABLE.PAC::ELSAI.TBL` | 625200 |
| EN | `BATTLE/TABLE.PAC::ENCOUNT.TBL` | 54672 |
| EN | `BATTLE/TABLE.PAC::EXIST.TBL` | 9840 |
| EN | `BATTLE/TABLE.PAC::ITEM.TBL` | 168416 |
| EN | `BATTLE/TABLE.PAC::NAME.TBL` | 102912 |
| EN | `BATTLE/TABLE.PAC::PERSONA.TBL` | 73040 |
| EN | `BATTLE/TABLE.PAC::PLAYER.TBL` | 5360 |
| EN | `BATTLE/TABLE.PAC::SKILL.TBL` | 65520 |
| EN | `BATTLE/TABLE.PAC::TALKINFO.TBL` | 560 |
| EN | `BATTLE/TABLE.PAC::UNIT.TBL` | 128464 |
| EN | `BATTLE/TABLE.PAC::VISUAL.TBL` | 786048 |
| EN | `BATTLE/TABLE/NAME.TBL` | 102912 |
| EN | `CALENDAR/GOODGAUGE.PAC::cldCommentTable.ftd` | 60384 |
| EN | `CALENDAR/GOODGAUGE.PAC::cldEvtCommentTable.ftd` | 7920 |
| EN | `CALENDAR/GOODGAUGE.PAC::cldGoodGauge.ftd` | 864 |
| EN | `CALENDAR/GOODGAUGE.PAC::cldGoodGaugeComment.ftd` | 96 |
| EN | `CALENDAR/GOODGAUGE.PAC::cldGoodGaugeLevel.ftd` | 80 |
| EN | `FIELD/FTD/FLDACTIONNAME.FTD` | 1632 |
| EN | `FIELD/FTD/FLDARCANANAME.FTD` | 96 |
| EN | `FIELD/FTD/FLDASSISTLISTNAME_SOCIAL.FTD` | 208 |
| EN | `FIELD/FTD/FLDASSISTLISTNAME_TRAIN.FTD` | 64 |
| EN | `FIELD/FTD/FLDCHECKNAME.FTD` | 8304 |
| EN | `FIELD/FTD/FLDDNGCHECKNAME.FTD` | 8960 |
| EN | `FIELD/FTD/FLDKFECHECKNAME.FTD` | 464 |
| EN | `FIELD/FTD/FLDNPCNAME.FTD` | 10352 |
| EN | `FIELD/FTD/FLDPARAMUPFUNCNAME.FTD` | 2784 |
| EN | `FIELD/FTD/FLDPLACENAME.FTD` | 17136 |
| EN | `FIELD/FTD/FLDSAVEDATAPLACE.FTD` | 4208 |
| EN | `FIELD/FTD/FLDSCRIPTNAME.FTD` | 2480 |
| EN | `FIELD/PANEL/FLDWHOLEMAPTABLE.FTD` | 106832 |
| EN | `FIELD/PANEL/FLDWHOLEMAPTABLEDNG.FTD` | 12416 |
| EN | `FIELD/PANEL/LMAP/FLDLMAPLOCKEDCORPNAME.FTD` | 1648 |
| EN | `FIELD/PANEL/LMAP/FLDLMAPSTATION.FTD` | 15024 |
| EN | `FIELD/PANEL/MISSION_LIST/MISSION_LIST.TBL` | 66988 |
| EN | `FIELD/PANEL/ROADMAP/ROADMAP.TBL` | 45560 |
| EN | `INIT/CMM.BIN::cmmArbeit.ctd` | 224 |
| EN | `INIT/CMM.BIN::cmmArcanaSPHelp.ctd` | 2112 |
| EN | `INIT/CMM.BIN::cmmAreaName.ctd` | 768 |
| EN | `INIT/CMM.BIN::cmmBookTable.ctd` | 2112 |
| EN | `INIT/CMM.BIN::cmmCall.ctd` | 416 |
| EN | `INIT/CMM.BIN::cmmClubName.ctd` | 384 |
| EN | `INIT/CMM.BIN::cmmCommunityStatus.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmEventBGM.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmEventNo.ctd` | 17216 |
| EN | `INIT/CMM.BIN::cmmFishCaptureFishBaitRate.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmFishCaptureRate.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmFishingGauge.ctd` | 192 |
| EN | `INIT/CMM.BIN::cmmFishingOthers.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmFishingTable.ctd` | 128 |
| EN | `INIT/CMM.BIN::cmmFishTrade.ctd` | 160 |
| EN | `INIT/CMM.BIN::cmmFishWeaponRate.ctd` | 64 |
| EN | `INIT/CMM.BIN::cmmFixString.ctd` | 672 |
| EN | `INIT/CMM.BIN::cmmFormat.ctd` | 7200 |
| EN | `INIT/CMM.BIN::cmmFunctionInfoTable.ctd` | 2368 |
| EN | `INIT/CMM.BIN::cmmFunctionName.ctd` | 18624 |
| EN | `INIT/CMM.BIN::cmmFunctionOpenSPTable.ctd` | 544 |
| EN | `INIT/CMM.BIN::cmmFunctionTable.ctd` | 4608 |
| EN | `INIT/CMM.BIN::cmmHelp.ctd` | 960 |
| EN | `INIT/CMM.BIN::cmmHelpMember.ctd` | 736 |
| EN | `INIT/CMM.BIN::cmmHelpMember_EXTRA.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmHelp_EXTRA.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmLockCheckTable.ctd` | 8416 |
| EN | `INIT/CMM.BIN::cmmMailOrder.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmMailOrder_Name.ctd` | 2944 |
| EN | `INIT/CMM.BIN::cmmMailOrder_Text.ctd` | 4352 |
| EN | `INIT/CMM.BIN::cmmMemberName.ctd` | 2496 |
| EN | `INIT/CMM.BIN::cmmName.ctd` | 2496 |
| EN | `INIT/CMM.BIN::cmmName_EXTRA.ctd` | 192 |
| EN | `INIT/CMM.BIN::cmmNetReportTable.ctd` | 11712 |
| EN | `INIT/CMM.BIN::cmmNotInvite.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmPC_PARAM_EXP.ctd` | 96 |
| EN | `INIT/CMM.BIN::cmmPC_PARAM_Help.ctd` | 576 |
| EN | `INIT/CMM.BIN::cmmPC_PARAM_Name.ctd` | 160 |
| EN | `INIT/CMM.BIN::cmmPhantomThiefName.ctd` | 768 |
| EN | `INIT/CMM.BIN::cmmSpDataTable.ctd` | 64 |
| EN | `INIT/CMPTABLE.BIN::chatDataTable.ctd` | 2752 |
| EN | `INIT/CMPTABLE.BIN::chatOpenTable.ctd` | 48288 |
| EN | `INIT/CMPTABLE.BIN::chatTitleName.ctd` | 85824 |
| EN | `INIT/CMPTABLE.BIN::cmpAlsnSkillQuestTable.ctd` | 96 |
| EN | `INIT/CMPTABLE.BIN::cmpArbeitName.ctd` | 384 |
| EN | `INIT/CMPTABLE.BIN::cmpArbeitTable.ctd` | 288 |
| EN | `INIT/CMPTABLE.BIN::cmpCalArbeitDrawOffTable.ctd` | 384 |
| EN | `INIT/CMPTABLE.BIN::cmpCalName.ctd` | 4544 |
| EN | `INIT/CMPTABLE.BIN::cmpCalTable.ctd` | 3328 |
| EN | `INIT/CMPTABLE.BIN::cmpCmuDressTable.ctd` | 64 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigHelp.ctd` | 3136 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigHelpNx.ctd` | 1216 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigHelpPs5.ctd` | 1216 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigHelpSteam.ctd` | 5952 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigHelpXbox.ctd` | 1216 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigItem.ctd` | 1536 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigItemNx.ctd` | 704 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigItemPs5.ctd` | 704 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigItemSteam.ctd` | 6720 |
| EN | `INIT/CMPTABLE.BIN::cmpConfigItemXbox.ctd` | 704 |
| EN | `INIT/CMPTABLE.BIN::cmpDailySkillTable.ctd` | 480 |
| EN | `INIT/CMPTABLE.BIN::cmpDifficultName.ctd` | 384 |
| EN | `INIT/CMPTABLE.BIN::cmpFriendPsSpSkillTable.ctd` | 128 |
| EN | `INIT/CMPTABLE.BIN::cmpMoneyPanelString.ctd` | 128 |
| EN | `INIT/CMPTABLE.BIN::cmpPersonaParam.ctd` | 384 |
| EN | `INIT/CMPTABLE.BIN::cmpPsCoopChgPersonalTable.ctd` | 128 |
| EN | `INIT/CMPTABLE.BIN::cmpPsCoopSkillTable.ctd` | 544 |
| EN | `INIT/CMPTABLE.BIN::cmpPsSkillAddTable.ctd` | 256 |
| EN | `INIT/CMPTABLE.BIN::cmpPsSkillOverWriteTable.ctd` | 64 |
| EN | `INIT/CMPTABLE.BIN::cmpQuestData.ctd` | 3648 |
| EN | `INIT/CMPTABLE.BIN::cmpQuestName.ctd` | 6400 |
| EN | `INIT/CMPTABLE.BIN::cmpQuestSortTable.ctd` | 192 |
| EN | `INIT/CMPTABLE.BIN::cmpQuestTargetName.ctd` | 6400 |
| EN | `INIT/CMPTABLE.BIN::cmpSystemHelp.ctd` | 512 |
| EN | `INIT/CMPTABLE.BIN::cmpSystemMenu.ctd` | 448 |
| EN | `INIT/FCLTABLE.BIN::allAttrTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::autoAttrTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::buturiAttrTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::CmbCmmCheckTbl.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::ComuAchieve.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::ElectricSkillTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclBookBonus.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclBookHelp.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclBookOwner.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclBookStore_OKINA.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclBookStore_YOMENAI.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCardTradeTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCmbBurstLvUp.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclCmbBurstPoint.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclCmbBurstSkill.ftd` | 6240 |
| EN | `INIT/FCLTABLE.BIN::fclCmbComText.ftd` | 288 |
| EN | `INIT/FCLTABLE.BIN::fclCmbElectAccidentTable.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::fclCmbGallowsTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCmbHelpTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCmbIkenieExpRate.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclCmbPsInfo.ftd` | 672 |
| EN | `INIT/FCLTABLE.BIN::fclCmbSpSettingTable.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclCmbSpSklSetTable_ACC.ftd` | 288 |
| EN | `INIT/FCLTABLE.BIN::fclCmbSpSklSetTable_ASP.ftd` | 352 |
| EN | `INIT/FCLTABLE.BIN::fclCmbSpTimeDayTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCmmRankMsgNo.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclCombCellMainSkill.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::fclCombCellRandSkill.ftd` | 864 |
| EN | `INIT/FCLTABLE.BIN::fclCombElectItemTable.ftd` | 5632 |
| EN | `INIT/FCLTABLE.BIN::fclCombineBirthTable.ftd` | 256 |
| EN | `INIT/FCLTABLE.BIN::fclCombineLift.ftd` | 544 |
| EN | `INIT/FCLTABLE.BIN::fclCombineSkillAffinity.ftd` | 800 |
| EN | `INIT/FCLTABLE.BIN::fclCombineSkillLimit.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclCombineTable_HighSpread.ftd` | 992 |
| EN | `INIT/FCLTABLE.BIN::fclCombineTable_Normal.ftd` | 960 |
| EN | `INIT/FCLTABLE.BIN::fclCombineTable_NormalHouma.ftd` | 960 |
| EN | `INIT/FCLTABLE.BIN::fclCombineTable_NormalSP.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::fclCombPublicFailPs.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclCombPublicRareSkill.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclComuLvMessage.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclConstTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCorpRankBuyTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCostumeHelp.ftd` | 288 |
| EN | `INIT/FCLTABLE.BIN::fclCostumeLineupTable.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclCostumeSetTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclCostumeTalk.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclCostumeTopMenu.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclCustomPartsName.ftd` | 448 |
| EN | `INIT/FCLTABLE.BIN::fclCustomTypeTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclGunTypeName.ftd` | 480 |
| EN | `INIT/FCLTABLE.BIN::fclHelpMsgTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_CELL.ftd` | 608 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_CELL_HELP.ftd` | 608 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMBINE_G.ftd` | 608 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMBINE_G_HELP.ftd` | 1312 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMBINE_HELP.ftd` | 1728 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMBINE_ROOT.ftd` | 480 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMBINE_SUB.ftd` | 608 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMPEND.ftd` | 480 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMPEND_HELP.ftd` | 352 |
| EN | `INIT/FCLTABLE.BIN::fclHelpTable_COMPEND_HELP_L.ftd` | 352 |
| EN | `INIT/FCLTABLE.BIN::fclInjectionName.ftd` | 1024 |
| EN | `INIT/FCLTABLE.BIN::fclInjectionTable.ftd` | 256 |
| EN | `INIT/FCLTABLE.BIN::fclItemHelp.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclItemLineUpAccTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclItemLineUpTable.ftd` | 224 |
| EN | `INIT/FCLTABLE.BIN::fclItemTalk.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclItemTopMenu.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::fclLogConjunctionText.ftd` | 1824 |
| EN | `INIT/FCLTABLE.BIN::fclLogFormatText.ftd` | 4704 |
| EN | `INIT/FCLTABLE.BIN::fclLogInitTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclMarketTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclMatRareTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclMementosShopFlagTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclMementosShopTable.ftd` | 4032 |
| EN | `INIT/FCLTABLE.BIN::fclMmtShopNumHeroMessage.ftd` | 256 |
| EN | `INIT/FCLTABLE.BIN::fclMmtShopSelMessage.ftd` | 640 |
| EN | `INIT/FCLTABLE.BIN::fclMovieTable.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclNotSellTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclPackageTable.ftd` | 1088 |
| EN | `INIT/FCLTABLE.BIN::fclPersonaAccMinMax.ftd` | 1472 |
| EN | `INIT/FCLTABLE.BIN::fclPersonaSkillAddNrmTable.ftd` | 224 |
| EN | `INIT/FCLTABLE.BIN::fclPersonaSkillAddPerTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclPersonaSkillAddRareTable.ftd` | 224 |
| EN | `INIT/FCLTABLE.BIN::fclPersonaSkillPowerUp.ftd` | 1248 |
| EN | `INIT/FCLTABLE.BIN::fclPSCoinTable.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclPsToSklCardTable.ftd` | 992 |
| EN | `INIT/FCLTABLE.BIN::fclPSTuriBoriTable.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclPSVintageTable.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclPublicShopDataTable.ftd` | 416 |
| EN | `INIT/FCLTABLE.BIN::fclPublicShopItemPrevTable.ftd` | 18464 |
| EN | `INIT/FCLTABLE.BIN::fclPublicShopItemTable.ftd` | 23648 |
| EN | `INIT/FCLTABLE.BIN::fclPublicShopJuiceTable.ftd` | 128 |
| EN | `INIT/FCLTABLE.BIN::fclPublicShopName.ftd` | 4320 |
| EN | `INIT/FCLTABLE.BIN::fclRecoverySkillRank.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclReqBonusTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclSaleTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::fclSearchText.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclSetItemName.ftd` | 2112 |
| EN | `INIT/FCLTABLE.BIN::fclSimpleHelp.ftd` | 12352 |
| EN | `INIT/FCLTABLE.BIN::fclSklCardAttrTable.ftd` | 224 |
| EN | `INIT/FCLTABLE.BIN::fclSpreadText.ftd` | 448 |
| EN | `INIT/FCLTABLE.BIN::fclSuggestTypeName.ftd` | 384 |
| EN | `INIT/FCLTABLE.BIN::fclTradeTalk.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclViewTypeText.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponCategoryName.ftd` | 192 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponHelp.ftd` | 256 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponSellList.ftd` | 160 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponTalk.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponTalkCmm.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponTalkMat.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponTopMenu.ftd` | 384 |
| EN | `INIT/FCLTABLE.BIN::fclWeaponTypeName.ftd` | 384 |
| EN | `INIT/FCLTABLE.BIN::FlameSkillTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::FreezeSkillTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::magicAttrTable.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::MarguriteCmmTbl.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::pWeatherBonus.ftd` | 1024 |
| EN | `INIT/FCLTABLE.BIN::pWeatherCondition.ftd` | 2176 |
| EN | `INIT/FCLTABLE.BIN::Rank0MesDat.ftd` | 416 |
| EN | `INIT/FCLTABLE.BIN::recoveryAttrTable.ftd` | 64 |
| EN | `INIT/FCLTABLE.BIN::RecoverySkillTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::SupportSkillTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::teamNameEntryNGWord.ftd` | 320 |
| EN | `INIT/FCLTABLE.BIN::WeatherBonusTbl.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::WeatherCommuBonus.ftd` | 96 |
| EN | `INIT/FCLTABLE.BIN::WeatherUnconditionalBonus.ftd` | 224 |
| EN | `INIT/FCLTABLE.BIN::WindSkillTbl.ftd` | 96 |
| BASE | `BATTLE/TABLE/AICALC.TBL` | 129248 |
| BASE | `BATTLE/TABLE/ELSAI.TBL` | 625200 |
| BASE | `BATTLE/TABLE/ENCOUNT.TBL` | 54672 |
| BASE | `BATTLE/TABLE/EXIST.TBL` | 9840 |
| BASE | `BATTLE/TABLE/ITEM.TBL` | 168416 |
| BASE | `BATTLE/TABLE/PERSONA.TBL` | 73040 |
| BASE | `BATTLE/TABLE/PLAYER.TBL` | 5360 |
| BASE | `BATTLE/TABLE/SKILL.TBL` | 65520 |
| BASE | `BATTLE/TABLE/TALKINFO.TBL` | 560 |
| BASE | `BATTLE/TABLE/UNIT.TBL` | 128464 |
| BASE | `BATTLE/TABLE/VISUAL.TBL` | 786048 |
| BASE | `FIELD/NPC/CORPTBL.TBL` | 41160 |
| BASE | `RESOURCE/RESRCMAPTARGET.TBL` | 2176 |

Плюс 80 .ftd в BASE (в основном параметры полей FIELD/FTD, не текст) — см. tsv.

## Шрифты

| CPK | путь | размер |
|---|---|---:|
| EN | `FONT/FONT0.FNT` | 9163557 |
| EN | `STAFF_ROLL/STAFF_ROLL.PAK::font1.fnt` | 289626 |
| EN | `STAFF_ROLL/STAFF_ROLL.PAK::font2.fnt` | 290867 |
| BASE | `FONT/FONT1.FNT` | 289626 |
| BASE | `FONT/FONT2.FNT` | 290867 |
| BASE | `FONT/KEYTOP_FONT.FNT` | 4807844 |
| BASE | `STAFF_ROLL/FONT1.FNT` | 289626 |
| BASE | `STAFF_ROLL/FONT2.FNT` | 290867 |

## Контейнеры с текстом внутри

Контейнеры верхнего уровня, внутри которых есть BMD/BF/TBL/CTD/FTD.

| CPK | контейнер | BMD | BF | таблиц |
|---|---|---:|---:|---:|
| EN | `BATTLE/TABLE.PAC` | 0 | 0 | 12 |
| EN | `CALENDAR/GOODGAUGE.PAC` | 0 | 0 | 5 |
| EN | `DEVICE/SAVELOAD/SAVELOAD.PAK` | 1 | 0 | 0 |
| EN | `FIELD/MY_PALACE/MP_ALL.PAC` | 0 | 113 | 0 |
| EN | `INIT/CMM.BIN` | 2 | 0 | 40 |
| EN | `INIT/CMPTABLE.BIN` | 3 | 0 | 35 |
| EN | `INIT/DATMSG.PAK` | 21 | 0 | 0 |
| EN | `INIT/FCLTABLE.BIN` | 0 | 0 | 128 |
| EN | `MINIGAME/CROSSWORD.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_00.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_01.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_02.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_03.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_04.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_05.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_06.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_07.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_08.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_09.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_10.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_11.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_12.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_13.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_14.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_15.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_16.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_17.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_18.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_19.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_20.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_21.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_22.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_23.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_24.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_25.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_26.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_27.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_28.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_29.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_30.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_31.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_32.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_33.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_34.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_35.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_36.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_37.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_38.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_39.PAK` | 1 | 0 | 0 |
| EN | `MINIGAME/CROSSWORD/CROSSWORD_40.PAK` | 1 | 0 | 0 |
| EN | `NETWORK/AUDIENCE.PAK` | 1 | 0 | 0 |
| EN | `NETWORK/NET.PAK` | 1 | 0 | 0 |
| EN | `NETWORK/NET_0.PAK` | 1 | 0 | 0 |
| EN | `TITLE/FICTION.PAK` | 0 | 1 | 0 |
| BASE | `BATTLE/RESIDENT_COMMON.PAC` | 0 | 1 | 0 |
