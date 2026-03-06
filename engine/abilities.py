from dataclasses import dataclass
from typing import Callable

from engine.dice import roll
from engine.status_effects import apply_status_effect, create_poison, create_stun


@dataclass(frozen=True)
class Ability:
    name: str
    description: str
    cooldown: int
    executor: Callable
    requires_target: bool = True

    def execute(self, player, target_or_targets) -> tuple[int, str]:
        return self.executor(player, target_or_targets)


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


def _shield_block(player, _target) -> tuple[int, str]:
    messages: list[str] = []
    # add / refresh custom shielded effect using generic status helper
    from engine.status_effects import create_shielded

    apply_status_effect(player, create_shielded(1), messages, "Player")
    return 0, " ".join(messages) or "You raise your shield for the next incoming attack."


def _whirlwind(player, targets) -> tuple[int, str]:
    if not targets:
        return 0, "No enemies are in range for Whirlwind."
    total = 0
    hits = []
    for enemy in targets:
        damage = max(1, roll(6) + player.str_mod)
        enemy.hp -= damage
        total += damage
        hits.append(f"{enemy.name}({damage})")
    return total, f"Whirlwind hits all enemies: {', '.join(hits)}"


def _poison_strike(player, target) -> tuple[int, str]:
    damage = max(1, roll(8) + player.dex_mod)
    target.hp -= damage
    messages = [f"Poison Strike hits for {damage} damage."]
    apply_status_effect(target, create_poison(3), messages, target.name)
    return damage, " ".join(messages)


def _stealth_attack(player, target) -> tuple[int, str]:
    damage = max(1, roll(8) + player.dex_mod)
    if target.hp > (getattr(target, "max_hp", target.hp) / 2):
        damage += 5
    target.hp -= damage
    return damage, f"Stealth Attack deals {damage} damage!"


def _ice_shard(player, target) -> tuple[int, str]:
    damage = max(1, roll(8) + player.int_mod)
    target.hp -= damage
    messages = [f"Ice Shard hits for {damage} damage."]
    if roll(100) <= 35:
        apply_status_effect(target, create_stun(1), messages, target.name)
    return damage, " ".join(messages)


def _chain_lightning(player, targets) -> tuple[int, str]:
    if not targets:
        return 0, "No enemies are in range for Chain Lightning."
    total = 0
    arcs = []
    for enemy in targets:
        damage = max(1, roll(6) + player.int_mod)
        enemy.hp -= damage
        total += damage
        arcs.append(f"{enemy.name}({damage})")
    return total, f"Chain Lightning arcs through enemies: {', '.join(arcs)}"


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

SHIELD_BLOCK = Ability(
    name="shield_block",
    description="Reduces damage from the next incoming attack.",
    cooldown=3,
    executor=_shield_block,
    requires_target=False,
)

WHIRLWIND = Ability(
    name="whirlwind",
    description="Attack all enemies in the room.",
    cooldown=3,
    executor=_whirlwind,
    requires_target=False,
)

POISON_STRIKE = Ability(
    name="poison_strike",
    description="Deals damage and applies poison.",
    cooldown=3,
    executor=_poison_strike,
)

STEALTH_ATTACK = Ability(
    name="stealth_attack",
    description="High damage if target HP is above 50%.",
    cooldown=3,
    executor=_stealth_attack,
)

ICE_SHARD = Ability(
    name="ice_shard",
    description="Ice damage with chance to stun.",
    cooldown=2,
    executor=_ice_shard,
)

CHAIN_LIGHTNING = Ability(
    name="chain_lightning",
    description="Lightning arc that damages multiple enemies.",
    cooldown=4,
    executor=_chain_lightning,
    requires_target=False,
)

ABILITIES_BY_NAME = {
    POWER_ATTACK.name: POWER_ATTACK,
    BACKSTAB.name: BACKSTAB,
    FIREBOLT.name: FIREBOLT,
    SHIELD_BLOCK.name: SHIELD_BLOCK,
    WHIRLWIND.name: WHIRLWIND,
    POISON_STRIKE.name: POISON_STRIKE,
    STEALTH_ATTACK.name: STEALTH_ATTACK,
    ICE_SHARD.name: ICE_SHARD,
    CHAIN_LIGHTNING.name: CHAIN_LIGHTNING,
}


def get_ability(name: str):
    return ABILITIES_BY_NAME.get(name.strip().lower())
