from dataclasses import dataclass

from engine.dice import roll


@dataclass
class Enemy:
    name: str
    hp: int
    attack: int
    defense: int
    description: str
    xp_reward: int = 35
    max_hp: int | None = None

    def __post_init__(self) -> None:
        if self.max_hp is None:
            self.max_hp = self.hp


def create_skeleton() -> Enemy:
    return Enemy(
        name="Skeleton",
        hp=10,
        attack=4,
        defense=12,
        description="Animated bones held together by dark magic.",
        xp_reward=75,
    )


def create_wandering_enemy() -> Enemy:
    variants = [
        Enemy(
            name="Cave Bat",
            hp=6,
            attack=3,
            defense=10,
            description="A screeching bat dives from the darkness.",
            xp_reward=30,
        ),
        Enemy(
            name="Goblin Scout",
            hp=8,
            attack=4,
            defense=11,
            description="A sneaky goblin appears from a side corridor.",
            xp_reward=40,
        ),
    ]
    return variants[roll(len(variants)) - 1]
