from engine.dice import roll
from engine.status_effects import (
    apply_status_effect,
    create_bleed,
    create_burn,
    create_poison,
    create_stun,
    process_status_effects,
)


def _try_apply_enemy_status(enemy, player, messages: list[str]) -> None:
    enemy_name = enemy.name.lower()
    if "skeleton" in enemy_name and roll(100) <= 25:
        apply_status_effect(player, create_bleed(3), messages, "Player")
    elif "bat" in enemy_name and roll(100) <= 20:
        apply_status_effect(player, create_burn(2), messages, "Player")
    elif "goblin" in enemy_name and roll(100) <= 15:
        apply_status_effect(player, create_stun(1), messages, "Player")


def player_attack(player, room) -> tuple[list[str], bool]:
    messages: list[str] = []
    enemy = room.enemy
    if enemy is None:
        return ["There is nothing to attack."], False

    player_effect_messages, player_stunned = process_status_effects(player, "Player")
    messages.extend(player_effect_messages)
    if player.hp <= 0:
        messages.append("You collapse from status effects.")
        return messages, False

    if player_stunned:
        messages.append("You are stunned and cannot attack this turn.")
    else:
        hit_roll = roll(20) + player.attack_bonus + player.str_mod
        messages.append(f"You roll d20 + attack bonuses (ATK+STR): {hit_roll}")

        if hit_roll >= enemy.defense:
            damage = max(1, roll(6) + player.str_mod)
            enemy.hp -= damage
            messages.append(f"Hit! You deal {damage} damage.")
            if roll(100) <= 20:
                apply_status_effect(enemy, create_bleed(3), messages, enemy.name)
            if enemy.hp <= 0:
                messages.append(f"{enemy.name} is defeated!")
                return messages, True
        else:
            messages.append("Miss!")

    enemy_effect_messages, enemy_stunned = process_status_effects(enemy, enemy.name)
    messages.extend(enemy_effect_messages)
    if enemy.hp <= 0:
        messages.append(f"{enemy.name} is defeated by status effects!")
        return messages, True

    if enemy_stunned:
        messages.append(f"{enemy.name} is stunned and cannot act.")
        return messages, False

    enemy_damage = max(0, roll(enemy.attack) - player.dex_mod)
    player.hp -= enemy_damage
    messages.append(
        f"{enemy.name} strikes back for {enemy_damage} damage (reduced by DEX). Your HP: {player.hp}"
    )
    _try_apply_enemy_status(enemy, player, messages)
    return messages, False


def resolve_effects_before_ability(player, enemy) -> tuple[list[str], bool, bool]:
    messages: list[str] = []
    player_effect_messages, player_stunned = process_status_effects(player, "Player")
    messages.extend(player_effect_messages)
    if player.hp <= 0:
        messages.append("You collapse from status effects.")
        return messages, True, True

    enemy_effect_messages, enemy_stunned = process_status_effects(enemy, enemy.name)
    messages.extend(enemy_effect_messages)
    if enemy.hp <= 0:
        messages.append(f"{enemy.name} is defeated by status effects!")
        return messages, False, True

    return messages, player_stunned, enemy_stunned


def enemy_counterattack(enemy, player, messages: list[str], enemy_stunned: bool = False) -> None:
    if enemy_stunned:
        messages.append(f"{enemy.name} is stunned and cannot act.")
        return

    enemy_damage = max(0, roll(enemy.attack) - player.dex_mod)
    shield_effect = next((effect for effect in player.active_effects if effect.name == "shielded"), None)
    if shield_effect:
        reduced_damage = enemy_damage // 2
        messages.append(f"Shield Block reduces incoming damage from {enemy_damage} to {reduced_damage}.")
        enemy_damage = reduced_damage
        shield_effect.duration -= 1
        if shield_effect.duration <= 0:
            player.active_effects = [effect for effect in player.active_effects if effect is not shield_effect]
            messages.append("Player is no longer affected by shielded.")
    player.hp -= enemy_damage
    messages.append(
        f"{enemy.name} strikes back for {enemy_damage} damage (reduced by DEX). Your HP: {player.hp}"
    )
    _try_apply_enemy_status(enemy, player, messages)


def try_apply_ability_status(ability_name: str, enemy, messages: list[str]) -> None:
    name = ability_name.strip().lower()
    if name == "firebolt" and roll(100) <= 45:
        apply_status_effect(enemy, create_burn(2), messages, enemy.name)
    elif name == "backstab" and roll(100) <= 35:
        apply_status_effect(enemy, create_bleed(3), messages, enemy.name)
    elif name == "power_attack" and roll(100) <= 25:
        apply_status_effect(enemy, create_stun(1), messages, enemy.name)
    elif name == "poison_strike" and roll(100) <= 75:
        apply_status_effect(enemy, create_poison(3), messages, enemy.name)
    elif name == "ice_shard" and roll(100) <= 35:
        apply_status_effect(enemy, create_stun(1), messages, enemy.name)
    elif name == "stealth_attack" and roll(100) <= 30:
        apply_status_effect(enemy, create_bleed(2), messages, enemy.name)
    elif name == "chain_lightning" and roll(100) <= 20:
        apply_status_effect(enemy, create_stun(1), messages, enemy.name)
    elif roll(100) <= 10:
        apply_status_effect(enemy, create_poison(3), messages, enemy.name)
