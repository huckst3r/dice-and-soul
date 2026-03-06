from dataclasses import dataclass, field

from engine.classes import CharacterClass, WARRIOR
from engine.item import Item

BASE_STR = 12
BASE_DEX = 11
BASE_INT = 10
BASE_CHA = 9


@dataclass
class Player:
    hp: int = 20
    attack_bonus: int = 2
    current_room: str = "hall"
    str_stat: int = BASE_STR
    dex_stat: int = BASE_DEX
    int_stat: int = BASE_INT
    cha_stat: int = BASE_CHA
    character_class: CharacterClass = field(default_factory=lambda: WARRIOR)
    ability_cooldowns: dict[str, int] = field(default_factory=dict)
    inventory: list[Item] = field(
        default_factory=lambda: [Item(name="rusty sword", description="Old but usable blade")]
    )

    def __post_init__(self) -> None:
        self.assign_class(self.character_class)

    def assign_class(self, character_class: CharacterClass) -> None:
        self.character_class = character_class
        self.str_stat = BASE_STR + character_class.str_bonus
        self.dex_stat = BASE_DEX + character_class.dex_bonus
        self.int_stat = BASE_INT + character_class.int_bonus
        self.cha_stat = BASE_CHA + character_class.cha_bonus
        self.ability_cooldowns = {
            name: turns
            for name, turns in self.ability_cooldowns.items()
            if name in character_class.starting_abilities
        }

    @staticmethod
    def modifier(stat_value: int) -> int:
        return (stat_value - 10) // 2

    @property
    def str_mod(self) -> int:
        return self.modifier(self.str_stat)

    @property
    def dex_mod(self) -> int:
        return self.modifier(self.dex_stat)

    @property
    def int_mod(self) -> int:
        return self.modifier(self.int_stat)

    @property
    def cha_mod(self) -> int:
        return self.modifier(self.cha_stat)

    def tick_cooldowns(self) -> None:
        updated: dict[str, int] = {}
        for ability, turns_left in self.ability_cooldowns.items():
            new_turns = turns_left - 1
            if new_turns > 0:
                updated[ability] = new_turns
        self.ability_cooldowns = updated

    def set_cooldown(self, ability_name: str, cooldown: int) -> None:
        if cooldown > 0:
            self.ability_cooldowns[ability_name] = cooldown

    def cooldown_for(self, ability_name: str) -> int:
        return self.ability_cooldowns.get(ability_name, 0)
