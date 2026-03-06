from engine.dice import roll


def player_attack(player, room) -> tuple[list[str], bool]:
    messages: list[str] = []
    enemy = room.enemy
    if enemy is None:
        return ["There is nothing to attack."], False

    hit_roll = roll(20) + player.attack_bonus
    messages.append(f"You roll d20 + bonus: {hit_roll}")

    if hit_roll >= enemy.defense:
        damage = roll(6)
        enemy.hp -= damage
        messages.append(f"Hit! You deal {damage} damage.")
        if enemy.hp <= 0:
            messages.append(f"{enemy.name} is defeated!")
            return messages, True
    else:
        messages.append("Miss!")

    enemy_damage = roll(enemy.attack)
    player.hp -= enemy_damage
    messages.append(f"{enemy.name} strikes back for {enemy_damage} damage. Your HP: {player.hp}")
    return messages, False
