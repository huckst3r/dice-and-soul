from engine.dice import roll


def player_attack(player, room) -> tuple[list[str], bool]:
    messages: list[str] = []
    enemy = room.enemy
    if enemy is None:
        return ["There is nothing to attack."], False

    hit_roll = roll(20) + player.attack_bonus + player.str_mod
    messages.append(f"You roll d20 + attack bonuses (ATK+STR): {hit_roll}")

    if hit_roll >= enemy.defense:
        damage = max(1, roll(6) + player.str_mod)
        enemy.hp -= damage
        messages.append(f"Hit! You deal {damage} damage.")
        if enemy.hp <= 0:
            messages.append(f"{enemy.name} is defeated!")
            return messages, True
    else:
        messages.append("Miss!")

    enemy_damage = max(0, roll(enemy.attack) - player.dex_mod)
    player.hp -= enemy_damage
    messages.append(
        f"{enemy.name} strikes back for {enemy_damage} damage (reduced by DEX). Your HP: {player.hp}"
    )
    return messages, False
