from dataclasses import dataclass, field

from engine.item import Item


@dataclass
class Player:
    hp: int = 20
    attack_bonus: int = 2
    current_room: str = "hall"
    inventory: list[Item] = field(default_factory=lambda: [Item(name="rusty sword", description="Old but usable blade")])
