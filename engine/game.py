import json
from pathlib import Path

from engine.abilities import get_ability
from engine.classes import CLASSES_BY_NAME, get_character_class
from engine.command_parser import parse_command
from engine.combat import player_attack
from engine.dice import roll
from engine.equipment import EquipmentSlot
from engine.item import Item
from engine.narrative import describe_event
from engine.player import Player
from engine.quest import Quest
from engine.world import create_world
from world.enemies import Enemy, create_wandering_enemy
from world.rooms import Room


class Game:
    SAVE_PATH = Path("savegame.json")
    CLASS_UNLOCKS: dict[str, dict[int, str]] = {
        "warrior": {3: "backstab"},
        "rogue": {3: "firebolt"},
        "mage": {3: "power_attack"},
    }

    def __init__(self) -> None:
        self.rooms = create_world()
        self.player = Player()
        self.chest_opened = False
        self.hidden_room_discovered = False
        self.victory_announced = False
        self.generated_room_counter = 0
        self.class_selected = False

        self.quests: dict[str, Quest] = {}
        self.quest_templates: dict[str, Quest] = {
            "skeleton bounty": Quest(
                name="skeleton bounty",
                description="Old guard asks you to clear the crypt.",
                objective="kill_skeleton_in_crypt",
                reward="guard's charm",
                xp_reward=100,
                status="active",
            )
        }

    @staticmethod
    def _find_item_by_name(items: list[Item], item_name: str) -> Item | None:
        item_name = item_name.strip().lower()
        for item in items:
            if item.name.lower() == item_name:
                return item
        return None

    def _find_npc_by_name(self, npc_name: str):
        room = self.rooms[self.player.current_room]
        npc_name = npc_name.strip().lower()
        for npc in room.npcs:
            if npc.name.lower() == npc_name:
                return npc
        return None

    @staticmethod
    def _random_loot_item() -> Item:
        loot_table = [
            Item(name="bandage", description="Simple wrap that might be useful later"),
            Item(name="iron shard", description="A jagged piece of iron"),
            Item(name="mysterious key", description="Could open something important"),
        ]
        return loot_table[roll(len(loot_table)) - 1]

    @staticmethod
    def _item_to_dict(item: Item) -> dict:
        return {
            "name": item.name,
            "description": item.description,
            "slot": item.slot.value if item.slot else None,
            "str_bonus": item.str_bonus,
            "dex_bonus": item.dex_bonus,
            "int_bonus": item.int_bonus,
            "hp_bonus": item.hp_bonus,
        }

    @staticmethod
    def _item_from_dict(data: dict) -> Item:
        slot_value = data.get("slot")
        slot = None
        if slot_value:
            try:
                slot = EquipmentSlot(slot_value)
            except ValueError:
                slot = None
        return Item(
            name=data.get("name", "unknown item"),
            description=data.get("description", ""),
            slot=slot,
            str_bonus=int(data.get("str_bonus", 0)),
            dex_bonus=int(data.get("dex_bonus", 0)),
            int_bonus=int(data.get("int_bonus", 0)),
            hp_bonus=int(data.get("hp_bonus", 0)),
        )

    @staticmethod
    def _enemy_to_dict(enemy: Enemy | None) -> dict | None:
        if enemy is None:
            return None
        return {
            "name": enemy.name,
            "hp": enemy.hp,
            "attack": enemy.attack,
            "defense": enemy.defense,
            "description": enemy.description,
            "xp_reward": enemy.xp_reward,
            "max_hp": enemy.max_hp,
        }

    @staticmethod
    def _enemy_from_dict(data: dict | None) -> Enemy | None:
        if data is None:
            return None
        return Enemy(
            name=data.get("name", "Unknown Enemy"),
            hp=int(data.get("hp", 1)),
            attack=int(data.get("attack", 1)),
            defense=int(data.get("defense", 10)),
            description=data.get("description", ""),
            xp_reward=int(data.get("xp_reward", 35)),
            max_hp=int(data.get("max_hp", data.get("hp", 1))),
        )

    @staticmethod
    def _quest_to_dict(quest: Quest) -> dict[str, str]:
        return {
            "name": quest.name,
            "description": quest.description,
            "objective": quest.objective,
            "reward": quest.reward,
            "xp_reward": quest.xp_reward,
            "status": quest.status,
        }

    @staticmethod
    def _quest_from_dict(data: dict) -> Quest:
        return Quest(
            name=data.get("name", "unknown quest"),
            description=data.get("description", ""),
            objective=data.get("objective", ""),
            reward=data.get("reward", ""),
            xp_reward=int(data.get("xp_reward", 50)),
            status=data.get("status", "active"),
        )

    def _serialize_npc_memory(self, room_id: str) -> dict[str, dict[str, int | bool]]:
        room = self.rooms[room_id]
        return {npc.name: dict(npc.memory) for npc in room.npcs}

    def _restore_npc_memory(self, room_id: str, saved_memory: dict[str, dict]) -> None:
        room = self.rooms[room_id]
        for npc in room.npcs:
            if npc.name in saved_memory:
                npc.memory.update(saved_memory[npc.name])

    @staticmethod
    def _opposite_direction(direction: str) -> str:
        return {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
            "up": "down",
            "down": "up",
            "secret": "back",
            "back": "secret",
        }.get(direction, "back")

    def _generate_room_id(self) -> str:
        self.generated_room_counter += 1
        return f"generated_{self.generated_room_counter}"

    def _build_generated_room(self) -> Room:
        names = ["Forgotten Cellar", "Echo Chamber", "Dust Gallery", "Broken Shrine", "Collapsed Hall"]
        descriptions = [
            "A damp space with dripping water and crumbling stone.",
            "Every step echoes here like distant whispers.",
            "Dust swirls in old torchlight over cracked tiles.",
            "Faded carvings line the walls, barely visible.",
            "The ceiling sags, but a narrow path remains open.",
        ]

        room = Room(
            name=names[roll(len(names)) - 1],
            description=descriptions[roll(len(descriptions)) - 1],
            exits={},
        )

        if roll(100) <= 35:
            room.enemy = create_wandering_enemy()
        if roll(100) <= 45:
            room.items.append(self._random_loot_item())

        return room

    def _generate_room_for_direction(self, direction: str) -> str:
        current_room_id = self.player.current_room
        current_room = self.rooms[current_room_id]

        new_room_id = self._generate_room_id()
        new_room = self._build_generated_room()
        back_direction = self._opposite_direction(direction)

        current_room.exits[direction] = new_room_id
        new_room.exits[back_direction] = current_room_id
        self.rooms[new_room_id] = new_room

        print(describe_event({"type": "room_generated", "room_name": new_room.name, "direction": direction}))
        return new_room_id

    def save_game(self) -> None:
        data = {
            "player": {
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "attack_bonus": self.player.attack_bonus,
                "level": self.player.level,
                "xp": self.player.xp,
                "current_room": self.player.current_room,
                "character_class": self.player.character_class.name,
                "ability_cooldowns": self.player.ability_cooldowns,
                "known_abilities": self.player.known_abilities,
                "equipment": {slot.value: self._item_to_dict(item) if item else None for slot, item in self.player.equipment.items()},
                "str_stat": self.player.str_stat,
                "dex_stat": self.player.dex_stat,
                "int_stat": self.player.int_stat,
                "cha_stat": self.player.cha_stat,
                "inventory": [self._item_to_dict(item) for item in self.player.inventory],
            },
            "flags": {
                "chest_opened": self.chest_opened,
                "hidden_room_discovered": self.hidden_room_discovered,
                "victory_announced": self.victory_announced,
            },
            "generated_room_counter": self.generated_room_counter,
            "quests": {name: self._quest_to_dict(quest) for name, quest in self.quests.items()},
            "rooms": {
                room_id: {
                    "name": room.name,
                    "description": room.description,
                    "exits": room.exits,
                    "items": [self._item_to_dict(item) for item in room.items],
                    "enemy": self._enemy_to_dict(room.enemy),
                    "npcs_memory": self._serialize_npc_memory(room_id),
                }
                for room_id, room in self.rooms.items()
            },
        }

        self.SAVE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(describe_event({"type": "save"}))
        print(f"Game saved to {self.SAVE_PATH}.")

    def load_game(self) -> None:
        if not self.SAVE_PATH.exists():
            print("No save file found.")
            return

        data = json.loads(self.SAVE_PATH.read_text())
        self.rooms = create_world()

        player_data = data.get("player", {})
        self.player.hp = int(player_data.get("hp", 20))
        self.player.max_hp = int(player_data.get("max_hp", 20))
        self.player.attack_bonus = int(player_data.get("attack_bonus", 2))
        self.player.level = int(player_data.get("level", 1))
        self.player.xp = int(player_data.get("xp", 0))
        self.player.current_room = player_data.get("current_room", "hall")
        self.player.assign_class(get_character_class(player_data.get("character_class", "warrior")))
        self.player.ability_cooldowns = {
            k: int(v) for k, v in player_data.get("ability_cooldowns", {}).items()
        }
        self.player.known_abilities = list(player_data.get("known_abilities", self.player.character_class.starting_abilities))
        self.player.str_stat = int(player_data.get("str_stat", 12))
        self.player.dex_stat = int(player_data.get("dex_stat", 11))
        self.player.int_stat = int(player_data.get("int_stat", 10))
        self.player.cha_stat = int(player_data.get("cha_stat", 9))
        self.player.inventory = [self._item_from_dict(it) for it in player_data.get("inventory", [])]
        equipment_data = player_data.get("equipment", {})
        self.player.equipment = {
            EquipmentSlot.WEAPON: None,
            EquipmentSlot.ARMOR: None,
            EquipmentSlot.RING: None,
        }
        for slot_name, item_data in equipment_data.items():
            try:
                slot = EquipmentSlot(slot_name)
            except ValueError:
                continue
            if item_data:
                self.player.equipment[slot] = self._item_from_dict(item_data)

        flags = data.get("flags", {})
        self.chest_opened = bool(flags.get("chest_opened", False))
        self.hidden_room_discovered = bool(flags.get("hidden_room_discovered", False))
        self.victory_announced = bool(flags.get("victory_announced", False))
        self.class_selected = True

        self.generated_room_counter = int(data.get("generated_room_counter", 0))
        self.quests = {name: self._quest_from_dict(q) for name, q in data.get("quests", {}).items()}

        room_data = data.get("rooms", {})

        for room_id, saved_room in room_data.items():
            if room_id not in self.rooms:
                self.rooms[room_id] = Room(
                    name=saved_room.get("name", "Generated Room"),
                    description=saved_room.get("description", "A newly discovered chamber."),
                    exits={},
                )

        for room_id, room in self.rooms.items():
            saved_room = room_data.get(room_id)
            if not saved_room:
                continue
            room.name = saved_room.get("name", room.name)
            room.description = saved_room.get("description", room.description)
            room.exits = dict(saved_room.get("exits", room.exits))
            room.items = [self._item_from_dict(it) for it in saved_room.get("items", [])]
            room.enemy = self._enemy_from_dict(saved_room.get("enemy"))
            self._restore_npc_memory(room_id, saved_room.get("npcs_memory", {}))

        print(describe_event({"type": "load"}))
        print(f"Game loaded from {self.SAVE_PATH}.")
        self.describe_room()

    def describe_room(self) -> None:
        room = self.rooms[self.player.current_room]
        print(f"\n== {room.name} ==")
        print(room.description)
        if room.enemy and room.enemy.hp > 0:
            print(f"Enemy here: {room.enemy.name} (HP: {room.enemy.hp})")
            print(room.enemy.description)
        if room.npcs:
            print("NPCs:", ", ".join(npc.name for npc in room.npcs))
        if room.items:
            print("Items:", ", ".join(item.name for item in room.items))
        print("Exits:", ", ".join(room.exits.keys()))

    def look_npc(self, npc_name: str) -> None:
        npc = self._find_npc_by_name(npc_name)
        if not npc:
            print(f"There is no '{npc_name}' here.")
            return
        print(f"{npc.name}: {npc.description}")
        if npc.offered_quests:
            print("Offers quests:", ", ".join(npc.offered_quests))

    def talk_npc(self, npc_name: str) -> None:
        npc = self._find_npc_by_name(npc_name)
        if not npc:
            print(f"There is no '{npc_name}' here.")
            return

        npc.record_talk()
        talk_count = int(npc.memory.get("talk_count", 0))
        memory_context = {
            "talk_count": talk_count,
            "player_attacked": bool(npc.memory.get("player_attacked", False)),
            "player_helped": bool(npc.memory.get("player_helped", False)),
        }
        print(describe_event({"type": "npc_talk", "npc": npc.name, **memory_context}))

        contextual_line = npc.get_contextual_dialogue()
        if npc.dialogue:
            random_line = npc.dialogue[roll(len(npc.dialogue)) - 1]
            print(f"{npc.name} says: \"{contextual_line} {random_line}\"")
        else:
            print(f"{npc.name} says: \"{contextual_line}\"")

    def help_npc(self, npc_name: str) -> None:
        npc = self._find_npc_by_name(npc_name)
        if not npc:
            print(f"There is no '{npc_name}' here.")
            return
        npc.record_help()
        print(describe_event({"type": "npc_help", "npc": npc.name, "talk_count": npc.memory.get("talk_count", 0)}))
        print(f"You help {npc.name}.")

    def attack_npc(self, npc_name: str) -> None:
        npc = self._find_npc_by_name(npc_name)
        if not npc:
            print(f"There is no '{npc_name}' here.")
            return
        npc.record_attack()
        print(describe_event({"type": "npc_attack", "npc": npc.name, "talk_count": npc.memory.get("talk_count", 0)}))
        print(f"You attack {npc.name}. They recoil and avoid you.")

    def list_quests(self) -> None:
        if not self.quests:
            print("No active quests.")
            return
        print("Quests:")
        for quest in self.quests.values():
            print(f"- {quest.name} [{quest.status}] -> {quest.description} | objective: {quest.objective}")

    def accept_quest(self, quest_name: str) -> None:
        quest_name = quest_name.strip().lower()
        if quest_name in self.quests:
            print(f"Quest '{quest_name}' already accepted.")
            return

        room = self.rooms[self.player.current_room]
        if not any(quest_name in [q.lower() for q in npc.offered_quests] for npc in room.npcs):
            print(f"No NPC here offers quest '{quest_name}'.")
            return

        template = self.quest_templates.get(quest_name)
        if not template:
            print(f"Quest '{quest_name}' does not exist.")
            return

        self.quests[quest_name] = Quest(
            name=template.name,
            description=template.description,
            objective=template.objective,
            reward=template.reward,
            xp_reward=template.xp_reward,
            status="active",
        )
        print(f"Quest accepted: {template.name}")

    def _is_quest_objective_completed(self, quest: Quest) -> bool:
        if quest.objective == "kill_skeleton_in_crypt":
            crypt = self.rooms["crypt"]
            return bool(crypt.enemy and crypt.enemy.hp <= 0)
        return False

    def xp_needed_for_next_level(self) -> int:
        return self.player.level * 100

    def _try_unlock_ability(self) -> None:
        class_name = self.player.character_class.name.lower()
        unlocks_for_class = self.CLASS_UNLOCKS.get(class_name, {})
        unlocked_ability = unlocks_for_class.get(self.player.level)
        if unlocked_ability and unlocked_ability not in self.player.known_abilities:
            self.player.known_abilities.append(unlocked_ability)
            print(f"New ability unlocked: {unlocked_ability}")

    def _level_up(self) -> None:
        self.player.level += 1
        self.player.max_hp += 5
        self.player.hp = self.player.max_hp

        stat_choices = ["str_stat", "dex_stat", "int_stat", "cha_stat"]
        chosen_stat = stat_choices[roll(len(stat_choices)) - 1]
        setattr(self.player, chosen_stat, getattr(self.player, chosen_stat) + 1)

        stat_name = chosen_stat.replace("_stat", "").upper()
        print(f"*** Level up! You reached level {self.player.level}. ***")
        print(f"Max HP increased to {self.player.max_hp}. HP fully restored.")
        print(f"{stat_name} increased by 1.")

        self._try_unlock_ability()

    def gain_xp(self, amount: int, source: str) -> None:
        if amount <= 0:
            return
        self.player.xp += amount
        print(f"You gain {amount} XP from {source}. (Total XP: {self.player.xp})")
        while self.player.xp >= self.xp_needed_for_next_level():
            self.player.xp -= self.xp_needed_for_next_level()
            self._level_up()

    def complete_quest(self, quest_name: str) -> None:
        quest_name = quest_name.strip().lower()
        quest = self.quests.get(quest_name)
        if not quest:
            print(f"Quest '{quest_name}' not found.")
            return
        if quest.status == "completed":
            print(f"Quest '{quest.name}' already completed.")
            return
        if not self._is_quest_objective_completed(quest):
            print(f"Objective not completed for quest '{quest.name}'.")
            return

        quest.status = "completed"
        reward_item = Item(name=quest.reward, description=f"Reward from quest: {quest.name}")
        self.player.inventory.append(reward_item)
        print(f"Quest completed: {quest.name}")
        print(f"You receive reward: {quest.reward}")
        self.gain_xp(quest.xp_reward, f"completing quest '{quest.name}'")

    @staticmethod
    def _format_item_bonuses(item: Item) -> str:
        bonuses = []
        if item.str_bonus:
            bonuses.append(f"STR {item.str_bonus:+d}")
        if item.dex_bonus:
            bonuses.append(f"DEX {item.dex_bonus:+d}")
        if item.int_bonus:
            bonuses.append(f"INT {item.int_bonus:+d}")
        if item.hp_bonus:
            bonuses.append(f"HP {item.hp_bonus:+d}")
        return f" ({', '.join(bonuses)})" if bonuses else ""

    def _apply_item_bonuses(self, item: Item) -> None:
        self.player.str_stat += item.str_bonus
        self.player.dex_stat += item.dex_bonus
        self.player.int_stat += item.int_bonus
        self.player.max_hp += item.hp_bonus
        self.player.hp += item.hp_bonus

    def _remove_item_bonuses(self, item: Item) -> None:
        self.player.str_stat -= item.str_bonus
        self.player.dex_stat -= item.dex_bonus
        self.player.int_stat -= item.int_bonus
        self.player.max_hp -= item.hp_bonus
        if self.player.hp > self.player.max_hp:
            self.player.hp = self.player.max_hp

    def equip_item(self, item_name: str) -> None:
        item = self._find_item_by_name(self.player.inventory, item_name)
        if not item:
            print(f"You do not have '{item_name}'.")
            return
        if item.slot is None:
            print(f"{item.name} cannot be equipped.")
            return

        current = self.player.equipment.get(item.slot)
        if current:
            self._remove_item_bonuses(current)
            self.player.inventory.append(current)
            print(f"You unequip {current.name} from {item.slot.value}.")

        self.player.inventory.remove(item)
        self.player.equipment[item.slot] = item
        self._apply_item_bonuses(item)
        print(f"You equip {item.name} to {item.slot.value}{self._format_item_bonuses(item)}.")

    def unequip_item(self, slot_name: str) -> None:
        try:
            slot = EquipmentSlot(slot_name.strip().lower())
        except ValueError:
            print("Unknown equipment slot. Use: weapon, armor, ring.")
            return

        item = self.player.equipment.get(slot)
        if not item:
            print(f"Nothing is equipped in {slot.value}.")
            return

        self.player.equipment[slot] = None
        self._remove_item_bonuses(item)
        self.player.inventory.append(item)
        print(f"You unequip {item.name} from {slot.value}.")

    def show_equipment(self) -> None:
        print("Equipment:")
        for slot in (EquipmentSlot.WEAPON, EquipmentSlot.ARMOR, EquipmentSlot.RING):
            equipped = self.player.equipment.get(slot)
            if equipped:
                print(f"- {slot.value}: {equipped.name}{self._format_item_bonuses(equipped)}")
            else:
                print(f"- {slot.value}: empty")

    def look_object(self, object_name: str) -> None:
        room = self.rooms[self.player.current_room]
        npc = self._find_npc_by_name(object_name)
        if npc:
            self.look_npc(object_name)
            return

        item = self._find_item_by_name(room.items, object_name)
        if item:
            print(f"{item.name}: {item.description}{self._format_item_bonuses(item)}")
            return

        inv_item = self._find_item_by_name(self.player.inventory, object_name)
        if inv_item:
            print(f"{inv_item.name} (inventory): {inv_item.description}{self._format_item_bonuses(inv_item)}")
            return

        print(f"You see no '{object_name}' here.")

    def attack_target(self, target_name: str) -> None:
        room = self.rooms[self.player.current_room]
        if room.enemy and room.enemy.hp > 0 and room.enemy.name.lower() != target_name.lower():
            print(f"There is no '{target_name}' to attack here.")
            return
        self.attack()

    def use_ability(self, ability_name: str, target_name: str) -> None:
        ability = get_ability(ability_name)
        if not ability:
            print(f"Unknown ability '{ability_name}'.")
            return

        if ability.name not in self.player.known_abilities:
            print(f"Your class cannot use '{ability.name}'.")
            return

        cooldown = self.player.cooldown_for(ability.name)
        if cooldown > 0:
            print(f"Ability '{ability.name}' is on cooldown for {cooldown} more turn(s).")
            return

        room = self.rooms[self.player.current_room]
        enemy = room.enemy
        if not enemy or enemy.hp <= 0:
            print("There is nothing to target.")
            return

        if enemy.name.lower() != target_name.lower():
            print(f"No target named '{target_name}' is here.")
            return

        damage, message = ability.execute(self.player, enemy)
        self.player.set_cooldown(ability.name, ability.cooldown)
        print(message)
        if enemy.hp <= 0:
            print(f"{enemy.name} is defeated!")
            self.gain_xp(enemy.xp_reward, f"defeating {enemy.name}")
            return

        enemy_damage = max(0, roll(enemy.attack) - self.player.dex_mod)
        self.player.hp -= enemy_damage
        print(f"{enemy.name} strikes back for {enemy_damage} damage (reduced by DEX). Your HP: {self.player.hp}")

    def trigger_random_encounter(self) -> None:
        room = self.rooms[self.player.current_room]

        enemy_check = roll(20) + self.player.dex_mod
        if enemy_check <= 8:
            if not room.enemy or room.enemy.hp <= 0:
                room.enemy = create_wandering_enemy()
                print(describe_event({"type": "enemy_encounter", "enemy": room.enemy.name}))
                print(f"A random encounter! {room.enemy.name} appears.")
            return

        item_check = roll(20) + self.player.cha_mod
        if item_check >= 17:
            found_item = self._random_loot_item()
            room.items.append(found_item)
            print(describe_event({"type": "item_found", "item": found_item.name}))
            print(f"You found an item on the way: {found_item.name}.")
            return

        hidden_check = roll(20) + self.player.int_mod
        if hidden_check >= 19 and not self.hidden_room_discovered and self.player.current_room != "hidden_sanctum":
            current_room = self.rooms[self.player.current_room]
            hidden_room = self.rooms["hidden_sanctum"]
            current_room.exits["secret"] = "hidden_sanctum"
            hidden_room.exits["back"] = self.player.current_room
            self.hidden_room_discovered = True
            print(describe_event({"type": "hidden_room", "room": "hidden_sanctum"}))
            print("You discovered a hidden room! New exit available: secret.")

    def move(self, direction: str) -> None:
        room = self.rooms[self.player.current_room]
        target = room.exits.get(direction)

        if not target:
            target = self._generate_room_for_direction(direction)

        self.player.current_room = target
        self.trigger_random_encounter()
        self.describe_room()

    def search(self) -> None:
        room = self.rooms[self.player.current_room]
        raw_check = roll(6)
        check = raw_check + self.player.int_mod
        print(f"You roll d6 + INT modifier: {raw_check} + {self.player.int_mod} = {check}")
        if self.player.current_room == "armory" and not self.chest_opened and check >= 4:
            self.chest_opened = True
            room.items.append(Item(name="healing potion", description="Restores HP when used"))
            print(describe_event({"type": "search_success", "item": "healing potion"}))
            print("Success! You find a healing potion in the chest.")
        elif self.player.current_room == "armory" and not self.chest_opened:
            print(describe_event({"type": "search_fail"}))
            print("You hear only creaking wood. Nothing found.")
        else:
            print(describe_event({"type": "search_fail"}))
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
        if not room.enemy or room.enemy.hp <= 0:
            print("There is nothing to attack.")
            return

        enemy_name = room.enemy.name
        enemy_xp = room.enemy.xp_reward
        messages, defeated = player_attack(self.player, room)
        for message in messages:
            print(message)
        if defeated:
            self.gain_xp(enemy_xp, f"defeating {enemy_name}")

    def use_potion(self) -> None:
        potion = self._find_item_by_name(self.player.inventory, "healing potion")
        if not potion:
            print("You do not have a healing potion.")
            return
        self.player.inventory.remove(potion)
        heal = roll(8)
        self.player.hp = min(self.player.max_hp, self.player.hp + heal)
        print(f"You drink a potion and restore {heal} HP. Current HP: {self.player.hp}")

    def status(self) -> None:
        print(f"Level: {self.player.level} | XP: {self.player.xp}/{self.xp_needed_for_next_level()}")
        print(f"HP: {self.player.hp}/{self.player.max_hp}")
        abilities = ", ".join(self.player.known_abilities)
        cooldown_info = ", ".join(
            f"{name}:{self.player.cooldown_for(name)}"
            for name in self.player.known_abilities
            if self.player.cooldown_for(name) > 0
        ) or "none"
        print(
            f"Class: {self.player.character_class.name} | "
            f"Abilities: {abilities} | Cooldowns: {cooldown_info}"
        )
        print(
            "Attributes: "
            f"STR {self.player.str_stat} ({self.player.str_mod:+d}), "
            f"DEX {self.player.dex_stat} ({self.player.dex_mod:+d}), "
            f"INT {self.player.int_stat} ({self.player.int_mod:+d}), "
            f"CHA {self.player.cha_stat} ({self.player.cha_mod:+d})"
        )
        self.show_equipment()
        self.show_inventory()

    def _prompt_class_selection(self) -> None:
        print("Choose your class:")
        for class_name in ("warrior", "rogue", "mage"):
            cc = CLASSES_BY_NAME[class_name]
            bonuses = []
            if cc.str_bonus:
                bonuses.append(f"STR {cc.str_bonus:+d}")
            if cc.dex_bonus:
                bonuses.append(f"DEX {cc.dex_bonus:+d}")
            if cc.int_bonus:
                bonuses.append(f"INT {cc.int_bonus:+d}")
            if cc.cha_bonus:
                bonuses.append(f"CHA {cc.cha_bonus:+d}")
            bonus_text = ", ".join(bonuses) if bonuses else "no bonuses"
            print(f"- {cc.name.lower()}: {cc.description} ({bonus_text}), ability: {', '.join(cc.starting_abilities)}")

        while True:
            raw = input("Class (warrior/rogue/mage): ").strip().lower()
            selected = CLASSES_BY_NAME.get(raw)
            if selected:
                self.player.assign_class(selected)
                self.class_selected = True
                print(f"You chose {selected.name}.")
                return
            print("Invalid class. Choose warrior, rogue, or mage.")

    def _startup_class_or_load(self) -> bool:
        if self.class_selected:
            return False

        if self.SAVE_PATH.exists():
            choice = input("Load existing save? (y/n): ").strip().lower()
            if choice in {"y", "yes"}:
                self.load_game()
                return True

        self._prompt_class_selection()
        return False

    def won(self) -> bool:
        crypt = self.rooms["crypt"]
        return bool(crypt.enemy and crypt.enemy.hp <= 0)

    def run(self) -> None:
        print("Welcome to Dice & Soul (minimal text RPG).")
        print(
            "Commands: look [object], talk <npc>, help <npc>, attack [enemy|npc], go <direction>, "
            "search, take <item>, drop <item>, inventory, equip <item>, unequip <slot>, equipment, "
            "quests, accept <quest>, complete <quest>, use <ability> <target>, potion, save, load, status, quit"
        )
        print("Aliases: n/s/e/w -> go north/south/east/west, i -> inventory")
        loaded_at_start = self._startup_class_or_load()
        if not self.class_selected:
            # load may have failed; fallback to class prompt
            self._prompt_class_selection()
        if not loaded_at_start:
            self.describe_room()

        while self.player.hp > 0:
            if self.won() and not self.victory_announced:
                print("\nYou have cleansed the crypt. Victory! You can still finish quests or quit.")
                self.victory_announced = True

            parsed = parse_command(input("\n> "))
            command = parsed.command
            args = parsed.args

            if not command:
                continue

            if command == "quit":
                print("Game over.")
                break
            if command == "look":
                if args:
                    self.look_object(" ".join(args))
                else:
                    self.describe_room()
            elif command == "talk":
                if not args:
                    print("Talk to whom?")
                else:
                    self.talk_npc(" ".join(args))
            elif command == "help":
                if not args:
                    print("Help whom?")
                else:
                    self.help_npc(" ".join(args))
            elif command == "attack":
                if not args:
                    room = self.rooms[self.player.current_room]
                    if not room.enemy or room.enemy.hp <= 0:
                        print("Attack what?")
                    else:
                        self.attack()
                else:
                    target = " ".join(args)
                    npc = self._find_npc_by_name(target)
                    if npc:
                        self.attack_npc(target)
                    else:
                        self.attack_target(target)
            elif command == "go":
                if not args:
                    print("Go where?")
                else:
                    self.move(args[0])
            elif command == "search":
                self.search()
            elif command == "take":
                if not args:
                    print("Take what?")
                else:
                    self.take_item(" ".join(args))
            elif command == "drop":
                if not args:
                    print("Drop what?")
                else:
                    self.drop_item(" ".join(args))
            elif command == "inventory":
                self.show_inventory()
            elif command == "equip":
                if not args:
                    print("Equip what?")
                else:
                    self.equip_item(" ".join(args))
            elif command == "unequip":
                if not args:
                    print("Unequip which slot?")
                else:
                    self.unequip_item(args[0])
            elif command == "equipment":
                self.show_equipment()
            elif command == "quests":
                self.list_quests()
            elif command == "accept":
                if not args:
                    print("Accept which quest?")
                else:
                    self.accept_quest(" ".join(args))
            elif command == "complete":
                if not args:
                    print("Complete which quest?")
                else:
                    self.complete_quest(" ".join(args))
            elif command == "use":
                if len(args) < 2:
                    print("Use what on whom?")
                else:
                    self.use_ability(args[0], " ".join(args[1:]))
            elif command == "potion":
                self.use_potion()
            elif command == "save":
                self.save_game()
            elif command == "load":
                self.load_game()
            elif command == "status":
                self.status()
            else:
                print("Unknown command.")

            self.player.tick_cooldowns()

        if self.player.hp <= 0:
            print("\nYou fall in battle. Defeat.")
