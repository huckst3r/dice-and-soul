from dataclasses import dataclass, field

from engine.item import Item


@dataclass
class Room:
    name: str
    description: str
    exits: dict[str, str]
    enemy: str | None = None
    enemy_hp: int = 0
    items: list[Item] = field(default_factory=list)


def build_rooms() -> dict[str, Room]:
    return {
        "hall": Room(
            name="Hall",
            description="Cold stone hall with old banners.",
            exits={"north": "armory", "east": "crypt"},
            items=[Item(name="torch", description="A wooden torch for dark places")],
        ),
        "armory": Room(
            name="Armory",
            description="Dusty racks with broken spears. A chest stands in the corner.",
            exits={"south": "hall"},
            items=[Item(name="dagger", description="A short steel dagger")],
        ),
        "crypt": Room(
            name="Crypt",
            description="Dark chamber with cracked sarcophagus.",
            exits={"west": "hall"},
            enemy="Skeleton",
            enemy_hp=10,
        ),
    }
