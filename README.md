# dice-and-soul

Минимальный text RPG engine на Python с комнатами и dice mechanics.

## Структура

```text
engine/
  game.py
  world.py
  dice.py
  combat.py
  player.py
  item.py

world/
  rooms.py
  enemies.py
```

## Запуск

```bash
python3 rpg_engine.py
```

## Команды

- `look` — осмотреть комнату
- `go <direction>` — перейти (`north/south/east/west`)
- `search` — поиск (бросок d6)
- `attack` — атака врага (попадание через d20, урон d6)
- `take <item>` — поднять предмет из комнаты
- `drop <item>` — выбросить предмет в комнату
- `inventory` — показать инвентарь
- `potion` — выпить зелье
- `status` — текущее состояние персонажа
- `quit` — выход
