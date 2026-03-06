import random
from dataclasses import dataclass, field


@dataclass
class Room:
    name: str
    description: str
    exits: dict[str, str]
    enemy: str | None = None
    enemy_hp: int = 0


@dataclass
class Player:
    hp: int = 20
    attack_bonus: int = 2
    current_room: str = "hall"
    inventory: list[str] = field(default_factory=lambda: ["rusty sword"])


class Game:
    def __init__(self) -> None:
        self.rooms: dict[str, Room] = {
            "hall": Room(
                name="Hall",
                description="Cold stone hall with old banners.",
                exits={"north": "armory", "east": "crypt"},
            ),
            "armory": Room(
                name="Armory",
                description="Dusty racks with broken spears. A chest stands in the corner.",
                exits={"south": "hall"},
            ),
            "crypt": Room(
                name="Crypt",
                description="Dark chamber with cracked sarcophagus.",
                exits={"west": "hall"},
                enemy="Skeleton",
                enemy_hp=10,
            ),
        }
        self.player = Player()
        self.chest_opened = False

    @staticmethod
    def roll(sides: int) -> int:
        return random.randint(1, sides)

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
        check = self.roll(6)
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

        hit_roll = self.roll(20) + self.player.attack_bonus
        print(f"You roll d20 + bonus: {hit_roll}")

        if hit_roll >= 12:
            damage = self.roll(6)
            room.enemy_hp -= damage
            print(f"Hit! You deal {damage} damage.")
            if room.enemy_hp <= 0:
                print(f"{room.enemy} is defeated!")
                return
        else:
            print("Miss!")

        enemy_damage = self.roll(4)
        self.player.hp -= enemy_damage
        print(f"{room.enemy} strikes back for {enemy_damage} damage. Your HP: {self.player.hp}")

    def use_potion(self) -> None:
        if "healing potion" not in self.player.inventory:
            print("You do not have a healing potion.")
            return
        self.player.inventory.remove("healing potion")
        heal = self.roll(8)
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


if __name__ == "__main__":
    Game().run()
