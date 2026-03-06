from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class StatusEffect:
    name: str
    duration: int
    tick_effect: Callable[[object], str | None]


def _damage_tick(entity: object, damage: int, label: str) -> str:
    entity.hp -= damage
    return f"{label} deals {damage} damage."


def poison_tick(entity: object) -> str:
    return _damage_tick(entity, 2, "Poison")


def burn_tick(entity: object) -> str:
    return _damage_tick(entity, 3, "Burn")


def bleed_tick(entity: object) -> str:
    return _damage_tick(entity, 1, "Bleed")


def stun_tick(entity: object) -> str:
    return "Stun prevents action this turn."


def shielded_tick(entity: object) -> str:
    return "Shield block is active."


def create_poison(duration: int = 3) -> StatusEffect:
    return StatusEffect(name="poison", duration=duration, tick_effect=poison_tick)


def create_burn(duration: int = 2) -> StatusEffect:
    return StatusEffect(name="burn", duration=duration, tick_effect=burn_tick)


def create_bleed(duration: int = 3) -> StatusEffect:
    return StatusEffect(name="bleed", duration=duration, tick_effect=bleed_tick)


def create_stun(duration: int = 1) -> StatusEffect:
    return StatusEffect(name="stun", duration=duration, tick_effect=stun_tick)


def create_shielded(duration: int = 1) -> StatusEffect:
    return StatusEffect(name="shielded", duration=duration, tick_effect=shielded_tick)


def get_effect_factory(name: str):
    factories = {
        "poison": create_poison,
        "burn": create_burn,
        "bleed": create_bleed,
        "stun": create_stun,
        "shielded": create_shielded,
    }
    return factories.get(name)


def serialize_effect(effect: StatusEffect) -> dict[str, int | str]:
    return {"name": effect.name, "duration": effect.duration}


def deserialize_effect(data: dict) -> StatusEffect | None:
    name = str(data.get("name", "")).strip().lower()
    duration = int(data.get("duration", 0))
    if duration <= 0:
        return None
    factory = get_effect_factory(name)
    if not factory:
        return None
    return factory(duration=duration)


def apply_status_effect(entity: object, effect: StatusEffect, messages: list[str], owner_label: str) -> None:
    active_effects = getattr(entity, "active_effects", None)
    if active_effects is None:
        return

    for existing in active_effects:
        if existing.name == effect.name:
            existing.duration = max(existing.duration, effect.duration)
            messages.append(f"{owner_label} already has {effect.name}; duration refreshed.")
            return

    active_effects.append(effect)
    messages.append(f"{owner_label} is afflicted with {effect.name} ({effect.duration} turn(s)).")


def process_status_effects(entity: object, owner_label: str) -> tuple[list[str], bool]:
    active_effects = getattr(entity, "active_effects", None)
    if not active_effects:
        return [], False

    messages: list[str] = []
    stunned = False
    remaining = []

    for effect in active_effects:
        if effect.name == "shielded":
            remaining.append(effect)
            continue

        tick_text = effect.tick_effect(entity)
        if tick_text:
            messages.append(f"{owner_label}: {tick_text}")
        if effect.name == "stun":
            stunned = True

        effect.duration -= 1
        if effect.duration > 0:
            remaining.append(effect)
        else:
            messages.append(f"{owner_label} is no longer affected by {effect.name}.")

    setattr(entity, "active_effects", remaining)
    return messages, stunned
