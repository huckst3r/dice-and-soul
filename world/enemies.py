from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from engine.dice import roll
from engine.loot import LootEntry, LootTable

if TYPE_CHECKING:
    from engine.status_effects import StatusEffect


@dataclass
class Enemy:
    name: str
    hp: int
    attack: int
    defense: int
    description: str
    faction: str = "bandits"
    xp_reward: int = 35
    max_hp: int | None = None
    active_effects: list[StatusEffect] = field(default_factory=list)
    loot_table: LootTable | None = None

    def __post_init__(self) -> None:
        if self.max_hp is None:
            self.max_hp = self.hp


@dataclass
class Boss(Enemy):
    unique_abilities: tuple[str, ...] = ()
    unique_loot: tuple[str, ...] = ()
    is_boss: bool = True


def create_skeleton() -> Enemy:
    return Enemy(
        name="Skeleton",
        hp=10,
        attack=4,
        defense=12,
        description="Animated bones held together by dark magic.",
        faction="cultists",
        xp_reward=75,
        loot_table=LootTable(
            entries=(
                LootEntry(item_id="bones", weight=60),
                LootEntry(item_id="rusty_sword", weight=25),
                LootEntry(item_id="potion", weight=10),
                LootEntry(item_id="rare_ring", weight=5),
            )
        ),
    )


def create_wandering_enemy() -> Enemy:
    variants = [
        Enemy(
            name="Cave Bat",
            hp=6,
            attack=3,
            defense=10,
            description="A screeching bat dives from the darkness.",
            faction="bandits",
            xp_reward=30,
            loot_table=LootTable(
                entries=(
                    LootEntry(item_id="bones", weight=50),
                    LootEntry(item_id="coin_pouch", weight=35),
                    LootEntry(item_id="potion", weight=15),
                )
            ),
        ),
        Enemy(
            name="Goblin Scout",
            hp=8,
            attack=4,
            defense=11,
            description="A sneaky goblin appears from a side corridor.",
            faction="bandits",
            xp_reward=40,
            loot_table=LootTable(
                entries=(
                    LootEntry(item_id="rusty_sword", weight=45),
                    LootEntry(item_id="coin_pouch", weight=40),
                    LootEntry(item_id="potion", weight=15),
                )
            ),
        ),
    ]
    return variants[roll(len(variants)) - 1]


def create_necromancer() -> Boss:
    return Boss(
        name="Necromancer",
        hp=34,
        attack=7,
        defense=14,
        description="A robed sorcerer channels grave-magic and whispers to the dead.",
        faction="cultists",
        xp_reward=220,
        unique_abilities=("bone_storm", "soul_drain"),
        unique_loot=("necromancer's staff", "black grimoire"),
        loot_table=LootTable(
            entries=(
                LootEntry(item_id="arcane_shard", weight=60),
                LootEntry(item_id="rare_ring", weight=25),
                LootEntry(item_id="potion", weight=15),
            )
        ),
    )


def create_crypt_lord() -> Boss:
    return Boss(
        name="Crypt Lord",
        hp=40,
        attack=8,
        defense=15,
        description="An armored death-knight rises from an ancient throne.",
        faction="cultists",
        xp_reward=280,
        unique_abilities=("grave_cleave", "fear_roar"),
        unique_loot=("lord's sigil", "crypt plate"),
        loot_table=LootTable(
            entries=(
                LootEntry(item_id="bones", weight=45),
                LootEntry(item_id="rare_ring", weight=35),
                LootEntry(item_id="potion", weight=20),
            )
        ),
    )


def create_ancient_golem() -> Boss:
    return Boss(
        name="Ancient Golem",
        hp=50,
        attack=9,
        defense=16,
        description="A colossal stone guardian awakens with thunderous steps.",
        faction="mages",
        xp_reward=320,
        unique_abilities=("stone_skin", "seismic_slam"),
        unique_loot=("golem core", "runed stone"),
        loot_table=LootTable(
            entries=(
                LootEntry(item_id="arcane_shard", weight=50),
                LootEntry(item_id="rare_ring", weight=30),
                LootEntry(item_id="potion", weight=20),
            )
        ),
    )


def create_random_boss() -> Boss:
    bosses = [create_necromancer(), create_crypt_lord(), create_ancient_golem()]
    return bosses[roll(len(bosses)) - 1]
