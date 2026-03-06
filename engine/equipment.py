from enum import Enum


class EquipmentSlot(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    RING = "ring"
