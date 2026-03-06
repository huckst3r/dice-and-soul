from engine.combat import player_attack
from engine.dice import roll
from engine.player import Player
from engine.world import create_world


class Game:
    def __init__(self) -> None:
        self.rooms = create_world()
        self.player = Player()
        self.chest_opened = False

    def describe_room(self) -> None:
        room = self.rooms[self.player.current_room]
        print(f"\n== {room.name} ==")
        print(room.description)
        if room.enemy and room.enemy_hp > 0:
            print(f"Enemy here: {room.enemy} (HP: {room.enemy_hp})")
        print("Exits:", ", ".join(room.exits.keys()))

    def move(self, direction: str) -> None:
        room = self.rooms[self.player.current_room]
        target = room.exits.get(direction)
        if not target:
            print("You cannot go that way.")
            return
        self.player.current_room = target
        self.describe_room()

    def search(self) -> None:
        room_id = self.player.current_room
        check = roll(6)
        print(f"You roll d6 for search: {check}")
        if room_id == "armory" and not self.chest_opened and check >= 4:
            self.chest_opened = True
            self.player.inventory.append("healing potion")
            print("Success! You find a healing potion in the chest.")
        elif room_id == "armory" and not self.chest_opened:
            print("You hear only creaking wood. Nothing found.")
        else:
            print("You find nothing useful.")

    def attack(self) -> None:
        room = self.rooms[self.player.current_room]
        if not room.enemy or room.enemy_hp <= 0:
            print("There is nothing to attack.")
            return

        messages, _ = player_attack(self.player, room)
        for message in messages:
            print(message)

    def use_potion(self) -> None:
        if "healing potion" not in self.player.inventory:
            print("You do not have a healing potion.")
            return
        self.player.inventory.remove("healing potion")
        heal = roll(8)
        self.player.hp = min(20, self.player.hp + heal)
        print(f"You drink a potion and restore {heal} HP. Current HP: {self.player.hp}")

    def status(self) -> None:
        print(f"HP: {self.player.hp}")
        print("Inventory:", ", ".join(self.player.inventory) if self.player.inventory else "empty")

    def won(self) -> bool:
        crypt = self.rooms["crypt"]
        return crypt.enemy_hp <= 0

    def run(self) -> None:
        print("Welcome to Dice & Soul (minimal text RPG).")
        print("Commands: look, go <north/south/east/west>, search, attack, potion, status, quit")
        self.describe_room()

        while self.player.hp > 0:
            if self.won():
                print("\nYou have cleansed the crypt. Victory!")
                break

            raw = input("\n> ").strip().lower()
            if not raw:
                continue

            if raw == "quit":
                print("Game over.")
                break
            if raw == "look":
                self.describe_room()
            elif raw.startswith("go "):
                self.move(raw.split(maxsplit=1)[1])
            elif raw == "search":
                self.search()
            elif raw == "attack":
                self.attack()
            elif raw == "potion":
                self.use_potion()
            elif raw == "status":
                self.status()
            else:
                print("Unknown command.")

        if self.player.hp <= 0:
            print("\nYou fall in battle. Defeat.")
