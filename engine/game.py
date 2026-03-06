from engine.combat import player_attack
from engine.dice import roll
from engine.item import Item
from engine.player import Player
from engine.world import create_world


class Game:
    def __init__(self) -> None:
        self.rooms = create_world()
        self.player = Player()
        self.chest_opened = False

    @staticmethod
    def _find_item_by_name(items: list[Item], item_name: str) -> Item | None:
        item_name = item_name.strip().lower()
        for item in items:
            if item.name.lower() == item_name:
                return item
        return None

    def describe_room(self) -> None:
        room = self.rooms[self.player.current_room]
        print(f"\n== {room.name} ==")
        print(room.description)
        if room.enemy and room.enemy_hp > 0:
            print(f"Enemy here: {room.enemy} (HP: {room.enemy_hp})")
        if room.items:
            print("Items:", ", ".join(item.name for item in room.items))
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
        room = self.rooms[self.player.current_room]
        check = roll(6)
        print(f"You roll d6 for search: {check}")
        if self.player.current_room == "armory" and not self.chest_opened and check >= 4:
            self.chest_opened = True
            room.items.append(Item(name="healing potion", description="Restores HP when used"))
            print("Success! You find a healing potion in the chest.")
        elif self.player.current_room == "armory" and not self.chest_opened:
            print("You hear only creaking wood. Nothing found.")
        else:
            print("You find nothing useful.")

    def take_item(self, item_name: str) -> None:
        room = self.rooms[self.player.current_room]
        item = self._find_item_by_name(room.items, item_name)
        if not item:
            print(f"There is no '{item_name}' here.")
            return
        room.items.remove(item)
        self.player.inventory.append(item)
        print(f"You take {item.name}.")

    def drop_item(self, item_name: str) -> None:
        room = self.rooms[self.player.current_room]
        item = self._find_item_by_name(self.player.inventory, item_name)
        if not item:
            print(f"You do not have '{item_name}'.")
            return
        self.player.inventory.remove(item)
        room.items.append(item)
        print(f"You drop {item.name}.")

    def show_inventory(self) -> None:
        if not self.player.inventory:
            print("Inventory: empty")
            return
        print("Inventory:", ", ".join(item.name for item in self.player.inventory))

    def attack(self) -> None:
        room = self.rooms[self.player.current_room]
        if not room.enemy or room.enemy_hp <= 0:
            print("There is nothing to attack.")
            return

        messages, _ = player_attack(self.player, room)
        for message in messages:
            print(message)

    def use_potion(self) -> None:
        potion = self._find_item_by_name(self.player.inventory, "healing potion")
        if not potion:
            print("You do not have a healing potion.")
            return
        self.player.inventory.remove(potion)
        heal = roll(8)
        self.player.hp = min(20, self.player.hp + heal)
        print(f"You drink a potion and restore {heal} HP. Current HP: {self.player.hp}")

    def status(self) -> None:
        print(f"HP: {self.player.hp}")
        self.show_inventory()

    def won(self) -> bool:
        crypt = self.rooms["crypt"]
        return crypt.enemy_hp <= 0

    def run(self) -> None:
        print("Welcome to Dice & Soul (minimal text RPG).")
        print(
            "Commands: look, go <north/south/east/west>, search, attack, "
            "take <item>, drop <item>, inventory, potion, status, quit"
        )
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
            elif raw.startswith("take "):
                self.take_item(raw.split(maxsplit=1)[1])
            elif raw.startswith("drop "):
                self.drop_item(raw.split(maxsplit=1)[1])
            elif raw == "inventory":
                self.show_inventory()
            elif raw == "potion":
                self.use_potion()
            elif raw == "status":
                self.status()
            else:
                print("Unknown command.")

        if self.player.hp <= 0:
            print("\nYou fall in battle. Defeat.")
