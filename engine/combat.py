from engine.dice import roll
from world.enemies import ENEMIES


def player_attack(player, room) -> tuple[list[str], bool]:
    messages: list[str] = []

    hit_roll = roll(20) + player.attack_bonus
    messages.append(f"You roll d20 + bonus: {hit_roll}")

    if hit_roll >= 12:
        damage = roll(6)
        room.enemy_hp -= damage
        messages.append(f"Hit! You deal {damage} damage.")
        if room.enemy_hp <= 0:
            messages.append(f"{room.enemy} is defeated!")
            return messages, True
    else:
        messages.append("Miss!")

    enemy_damage = roll(ENEMIES.get(room.enemy, {"attack_die": 4})["attack_die"])
    player.hp -= enemy_damage
    messages.append(f"{room.enemy} strikes back for {enemy_damage} damage. Your HP: {player.hp}")
    return messages, False
