from dataclasses import dataclass

from engine.equipment import EquipmentSlot


@dataclass
class Item:
    name: str
    description: str = ""
    slot: EquipmentSlot | None = None
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    hp_bonus: int = 0
