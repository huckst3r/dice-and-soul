from __future__ import annotations

from dataclasses import dataclass

from engine.dice import roll
from engine.item import Item


@dataclass(frozen=True)
class LootEntry:
    item_id: str
    weight: int


@dataclass(frozen=True)
class LootTable:
    entries: tuple[LootEntry, ...]

    def roll(self) -> str | None:
        positive_entries = [entry for entry in self.entries if entry.weight > 0]
        if not positive_entries:
            return None

        total_weight = sum(entry.weight for entry in positive_entries)
        threshold = roll(total_weight)

        cumulative = 0
        for entry in positive_entries:
            cumulative += entry.weight
            if threshold <= cumulative:
                return entry.item_id
        return positive_entries[-1].item_id


ITEM_LIBRARY: dict[str, Item] = {
    "bones": Item(name="bones", description="A pile of brittle bones."),
    "rusty_sword": Item(
        name="rusty sword",
        description="Old but usable blade",
    ),
    "potion": Item(name="healing potion", description="Restores HP when used"),
    "rare_ring": Item(
        name="rare ring",
        description="A rare ring humming with old magic.",
        int_bonus=1,
    ),
    "coin_pouch": Item(name="coin pouch", description="A pouch of old coins."),
    "arcane_shard": Item(name="arcane shard", description="A shard infused with arcane energy."),
}


def item_from_id(item_id: str) -> Item | None:
    template = ITEM_LIBRARY.get(item_id)
    if template is None:
        return None
    return Item(
        name=template.name,
        description=template.description,
        slot=template.slot,
        str_bonus=template.str_bonus,
        dex_bonus=template.dex_bonus,
        int_bonus=template.int_bonus,
        hp_bonus=template.hp_bonus,
        attack_bonus=template.attack_bonus,
        special_effects=list(template.special_effects),
    )


def loot_table_to_dict(loot_table: LootTable | None) -> dict | None:
    if loot_table is None:
        return None
    return {
        "entries": [
            {
                "item_id": entry.item_id,
                "weight": entry.weight,
            }
            for entry in loot_table.entries
        ]
    }


def loot_table_from_dict(data: dict | None) -> LootTable | None:
    if not data:
        return None
    entries_raw = data.get("entries", [])
    entries: list[LootEntry] = []
    for raw_entry in entries_raw:
        item_id = str(raw_entry.get("item_id", "")).strip()
        if not item_id:
            continue
        weight = int(raw_entry.get("weight", 0))
        if weight <= 0:
            continue
        entries.append(LootEntry(item_id=item_id, weight=weight))
    if not entries:
        return None
    return LootTable(entries=tuple(entries))
