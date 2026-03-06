from dataclasses import dataclass


@dataclass
class Enemy:
    name: str
    hp: int
    attack: int
    defense: int
    description: str


def create_skeleton() -> Enemy:
    return Enemy(
        name="Skeleton",
        hp=10,
        attack=4,
        defense=12,
        description="Animated bones held together by dark magic.",
    )
