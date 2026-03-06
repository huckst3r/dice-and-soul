from dataclasses import dataclass


@dataclass
class Room:
    name: str
    description: str
    exits: dict[str, str]
    enemy: str | None = None
    enemy_hp: int = 0


def build_rooms() -> dict[str, Room]:
    return {
        "hall": Room(
            name="Hall",
            description="Cold stone hall with old banners.",
            exits={"north": "armory", "east": "crypt"},
        ),
        "armory": Room(
            name="Armory",
            description="Dusty racks with broken spears. A chest stands in the corner.",
            exits={"south": "hall"},
        ),
        "crypt": Room(
            name="Crypt",
            description="Dark chamber with cracked sarcophagus.",
            exits={"west": "hall"},
            enemy="Skeleton",
            enemy_hp=10,
        ),
    }
