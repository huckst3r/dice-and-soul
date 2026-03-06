from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterClass:
    name: str
    description: str
    str_bonus: int = 0
    dex_bonus: int = 0
    int_bonus: int = 0
    cha_bonus: int = 0
    starting_abilities: tuple[str, ...] = ()


WARRIOR = CharacterClass(
    name="Warrior",
    description="Frontline fighter focused on strength.",
    str_bonus=2,
    starting_abilities=("power_attack",),
)

ROGUE = CharacterClass(
    name="Rogue",
    description="Agile trickster focused on precision.",
    dex_bonus=2,
    starting_abilities=("backstab",),
)

MAGE = CharacterClass(
    name="Mage",
    description="Arcane caster focused on intellect.",
    int_bonus=2,
    starting_abilities=("firebolt",),
)


CLASSES_BY_NAME = {
    "warrior": WARRIOR,
    "rogue": ROGUE,
    "mage": MAGE,
}


def get_character_class(name: str | None) -> CharacterClass:
    if not name:
        return WARRIOR
    return CLASSES_BY_NAME.get(name.strip().lower(), WARRIOR)
