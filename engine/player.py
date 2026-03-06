from dataclasses import dataclass, field


@dataclass
class Player:
    hp: int = 20
    attack_bonus: int = 2
    current_room: str = "hall"
    inventory: list[str] = field(default_factory=lambda: ["rusty sword"])
