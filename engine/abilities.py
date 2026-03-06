from dataclasses import dataclass
from typing import Callable

from engine.dice import roll


@dataclass(frozen=True)
class Ability:
    name: str
    description: str
    cooldown: int
    executor: Callable

    def execute(self, player, target) -> tuple[int, str]:
        return self.executor(player, target)


def _power_attack(player, target) -> tuple[int, str]:
    damage = max(1, roll(8) + player.str_mod)
    target.hp -= damage
    return damage, f"Power Attack hits for {damage} damage!"


def _backstab(player, target) -> tuple[int, str]:
    damage = max(1, roll(10) + player.dex_mod)
    if target.hp > (getattr(target, "max_hp", target.hp) / 2):
        damage += 3
    target.hp -= damage
    return damage, f"Backstab strikes for {damage} damage!"


def _firebolt(player, target) -> tuple[int, str]:
    damage = max(1, roll(10) + player.int_mod)
    target.hp -= damage
    return damage, f"Firebolt burns for {damage} damage!"


POWER_ATTACK = Ability(
    name="power_attack",
    description="A stronger melee attack.",
    cooldown=2,
    executor=_power_attack,
)

BACKSTAB = Ability(
    name="backstab",
    description="Deals higher damage when target HP is above 50%.",
    cooldown=2,
    executor=_backstab,
)

FIREBOLT = Ability(
    name="firebolt",
    description="A ranged magic bolt of fire.",
    cooldown=2,
    executor=_firebolt,
)


ABILITIES_BY_NAME = {
    POWER_ATTACK.name: POWER_ATTACK,
    BACKSTAB.name: BACKSTAB,
    FIREBOLT.name: FIREBOLT,
}


def get_ability(name: str):
    return ABILITIES_BY_NAME.get(name.strip().lower())
