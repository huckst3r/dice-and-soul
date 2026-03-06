# dice-and-soul

Минимальный text RPG engine на Python с комнатами и dice mechanics.

## Структура

```text
engine/
  game.py
  world.py
  dice.py
  combat.py
  abilities.py
  classes.py
  player.py
  item.py
  npc.py
  quest.py
  narrative.py

world/
  rooms.py
  enemies.py
```

## Запуск

```bash
python3 rpg_engine.py
```

При старте новой игры движок предлагает выбрать класс: `warrior`, `rogue` или `mage`.
Если найден `savegame.json`, можно загрузить существующее сохранение, и тогда класс берется из сейва.

## Команды

- `look` — осмотреть комнату
- `look <npc>` — осмотреть NPC в текущей комнате
- `talk <npc>` — поговорить с NPC (реплика зависит от памяти + случайная фраза)
- `help <npc>` — помочь NPC (влияет на память NPC)
- `go <direction>` — перейти (`north/south/east/west`, а также `secret/back` при открытии)
- `search` — поиск (бросок d6)
- `attack` — атака врага (попадание через d20 против defense, урон d6)
- `attack <npc>` — атаковать NPC (меняет отношение NPC)
- `take <item>` — поднять предмет из комнаты
- `drop <item>` — выбросить предмет в комнату
- `inventory` — показать инвентарь
- `quests` — показать принятые квесты
- `accept <quest>` — принять квест от NPC в текущей комнате
- `complete <quest>` — завершить квест при выполненной цели
- `use <ability> <target>` — применить способность по цели
- `potion` — выпить зелье
- `save` — сохранить игру в `savegame.json`
- `load` — загрузить игру из `savegame.json`
- `status` — текущее состояние персонажа
- `quit` — выход

Алиасы:
- `n` → `go north`
- `s` → `go south`
- `e` → `go east`
- `w` → `go west`
- `i` → `inventory`

## Случайные события при перемещении

При каждом успешном `go` есть шанс на событие:
- встреча с врагом;
- находка предмета;
- обнаружение скрытой комнаты.

## Narrative

- Добавлена функция `describe_event(event_context)` для текстового описания событий.
- Сейчас она возвращает статические шаблоны, но интерфейс подготовлен для будущего вызова LLM.

## Атрибуты игрока

- У игрока есть характеристики: `STR`, `DEX`, `INT`, `CHA`.
- Они применяются как модификаторы бросков: атака/урон, уклонение от урона, поиск и случайные события при перемещении.

## NPC

- В комнатах могут находиться несколько NPC.
- У каждого NPC есть память взаимодействий: количество разговоров, факт атаки, факт помощи.
- Команда `talk <npc>` учитывает память NPC: первое знакомство, более дружелюбный тон после нескольких разговоров, реакция на помощь/атаку.
- Команда `look <npc>` показывает описание NPC.
- Память NPC сохраняется и загружается через `save`/`load`.

## Quests

- Добавлен класс `Quest`: `name`, `description`, `objective`, `reward`, `status` (`active`/`completed`).
- NPC могут выдавать квесты (пример: `skeleton bounty` от `old guard` — убить скелета в крипте).
- Завершение квеста выдает награду предметом.
- Прогресс квестов сохраняется/загружается через `save`/`load`.

## Procedural rooms

- Если при `go <direction>` нет заранее заданной комнаты, движок создаёт новую процедурную комнату.
- Сгенерированная комната получает случайные `name` и `description`, может содержать врага и/или предмет.
- Связи двусторонние: всегда создаётся обратный выход, чтобы можно было вернуться.
- Процедурные комнаты сохраняются в состоянии мира и восстанавливаются через `save`/`load`.
- Для новых комнат используется narrative-событие `describe_event({"type": "room_generated", ...})`.

## Parser examples

- `attack skeleton` → command: `attack`, args: `["skeleton"]`
- `take torch` → command: `take`, args: `["torch"]`
- `go north` → command: `go`, args: `["north"]`
- `look old guard` → command: `look`, args: `["old", "guard"]`

## Character classes

- Добавлен модуль `engine/classes.py` с классом `CharacterClass`.
- Классы:
  - `Warrior`: `STR +2`, способность `power_attack`
  - `Rogue`: `DEX +2`, способность `backstab`
  - `Mage`: `INT +2`, способность `firebolt`
- У игрока есть поле `character_class`, бонусы класса применяются при создании персонажа.
- `status` показывает класс и стартовые способности.
- Класс игрока сохраняется/загружается через `save`/`load`.

## Abilities

- Добавлен модуль `engine/abilities.py` с классом `Ability` (`name`, `description`, `cooldown`, `execute`).
- Способности:
  - `power_attack` — сильный удар, `d8 + STR mod`
  - `backstab` — высокий урон при HP цели > 50%, `d10 + DEX mod`
  - `firebolt` — магический удар, `d10 + INT mod`
- Новая команда: `use <ability> <target>` (например, `use firebolt skeleton`).
- Кулдауны способностей хранятся у игрока и отображаются в `status`.
- Кулдауны и класс персонажа сохраняются/загружаются через `save`/`load`.
