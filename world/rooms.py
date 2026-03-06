from dataclasses import dataclass, field

from engine.equipment import EquipmentSlot
from engine.item import Item
from engine.npc import NPC
from world.enemies import (
    Enemy,
    create_ancient_golem,
    create_necromancer,
    create_skeleton,
)


@dataclass
class Room:
    name: str
    description: str
    exits: dict[str, str]
    enemy: Enemy | None = None
    enemies: list[Enemy] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)
    npcs: list[NPC] = field(default_factory=list)


def build_rooms() -> dict[str, Room]:
    return {
        "hall": Room(
            name="Hall",
            description="Cold stone hall with old banners.",
            exits={"north": "armory", "east": "crypt"},
            items=[Item(name="torch", description="A wooden torch for dark places")],
            npcs=[
                NPC(
                    name="old guard",
                    description="An old guard leaning on a chipped spear.",
                    dialogue=[
                        "The crypt to the east is cursed.",
                        "Keep your blade high and your fear low.",
                        "If you find herbs, keep them. The dark bites hard.",
                    ],
                    offered_quests=["skeleton bounty"],
                )
            ],
        ),
        "armory": Room(
            name="Armory",
            description="Dusty racks with broken spears. A chest stands in the corner.",
            exits={"south": "hall"},
            items=[Item(name="dagger", description="A short steel dagger", slot=EquipmentSlot.WEAPON, dex_bonus=1)],
            npcs=[
                NPC(
                    name="quartermaster",
                    description="A stern quartermaster counting rusty bolts.",
                    dialogue=[
                        "Take what you need, leave what you can.",
                        "Steel wins fights, but timing wins wars.",
                    ],
                )
            ],
        ),
        "crypt": Room(
            name="Crypt",
            description="Dark chamber with cracked sarcophagus.",
            exits={"west": "hall"},
            enemy=create_skeleton(),
        ),
        "hidden_sanctum": Room(
            name="Hidden Sanctum",
            description="A secret chamber with faded runes and a faint golden glow.",
            exits={"down": "forgotten_vault", "east": "obsidian_nexus"},
            items=[
                Item(name="ancient coin", description="An old coin with unknown symbols"),
                Item(name="silver ring", description="A ring etched with tiny runes.", slot=EquipmentSlot.RING, int_bonus=1),
            ],
            npcs=[
                NPC(
                    name="whispering spirit",
                    description="A translucent spirit murmuring ancient words.",
                    dialogue=[
                        "Names fade, but choices remain.",
                        "The walls remember every oath.",
                    ],
                )
            ],
        ),
        "forgotten_vault": Room(
            name="Forgotten Vault",
            description="A sealed chamber crowded with funerary statues and green mist.",
            exits={"up": "hidden_sanctum"},
            enemy=create_necromancer(),
        ),
        "obsidian_nexus": Room(
            name="Obsidian Nexus",
            description="A cavern of black crystal pulsing with old defensive magic.",
            exits={"west": "hidden_sanctum"},
            enemy=create_ancient_golem(),
        ),
    }
