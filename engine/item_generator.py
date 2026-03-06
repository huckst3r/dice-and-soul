from __future__ import annotations

from dataclasses import dataclass

from engine.dice import roll
from engine.equipment import EquipmentSlot
from engine.item import Item


@dataclass(frozen=True)
class PrefixMod:
    name: str
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    attack_bonus: int = 0


@dataclass(frozen=True)
class BaseItem:
    name: str
    slot: EquipmentSlot | None = None
    description: str = ""
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    attack_bonus: int = 0


@dataclass(frozen=True)
class SuffixMod:
    name: str
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    attack_bonus: int = 0
    special_effect: str | None = None


PREFIXES: tuple[PrefixMod, ...] = (
    PrefixMod(name="Rusty", attack_bonus=-1),
    PrefixMod(name="Ancient", attack_bonus=2),
    PrefixMod(name="Shadow", dex_bonus=2),
)

BASE_ITEMS: tuple[BaseItem, ...] = (
    BaseItem(name="Sword", slot=EquipmentSlot.WEAPON, description="A balanced blade.", str_bonus=1, attack_bonus=1),
    BaseItem(name="Dagger", slot=EquipmentSlot.WEAPON, description="A fast stabbing weapon.", dex_bonus=1),
    BaseItem(name="Staff", slot=EquipmentSlot.WEAPON, description="A carved wooden staff.", int_bonus=1),
)

SUFFIXES: tuple[SuffixMod, ...] = (
    SuffixMod(name="of Fire", special_effect="fire_chance"),
    SuffixMod(name="of Venom", special_effect="venom_chance"),
    SuffixMod(name="of Giants", str_bonus=2),
)


def _pick(sequence):
    return sequence[roll(len(sequence)) - 1]


def generate_item() -> Item:
    prefix = _pick(PREFIXES)
    base = _pick(BASE_ITEMS)
    suffix = _pick(SUFFIXES)

    name = f"{prefix.name} {base.name} {suffix.name}".strip()
    effects: list[str] = []
    if suffix.special_effect:
        effects.append(suffix.special_effect)

    return Item(
        name=name,
        description=f"A procedurally generated {base.name.lower()}.",
        slot=base.slot,
        str_bonus=base.str_bonus + prefix.str_bonus + suffix.str_bonus,
        dex_bonus=base.dex_bonus + prefix.dex_bonus + suffix.dex_bonus,
        int_bonus=base.int_bonus + prefix.int_bonus + suffix.int_bonus,
        attack_bonus=base.attack_bonus + prefix.attack_bonus + suffix.attack_bonus,
        special_effects=effects,
    )
