from dataclasses import dataclass, field


@dataclass
class NPC:
    name: str
    description: str
    dialogue: list[str]
    offered_quests: list[str] = field(default_factory=list)
    memory: dict[str, int | bool] = field(
        default_factory=lambda: {
            "talk_count": 0,
            "player_attacked": False,
            "player_helped": False,
        }
    )

    def record_talk(self) -> None:
        self.memory["talk_count"] = int(self.memory.get("talk_count", 0)) + 1

    def record_attack(self) -> None:
        self.memory["player_attacked"] = True

    def record_help(self) -> None:
        self.memory["player_helped"] = True

    def get_contextual_dialogue(self) -> str:
        talk_count = int(self.memory.get("talk_count", 0))
        attacked = bool(self.memory.get("player_attacked", False))
        helped = bool(self.memory.get("player_helped", False))

        if attacked:
            return "I won't forget what you did. Keep your distance."
        if helped:
            return "You helped me before — you have my trust."
        if talk_count <= 1:
            return "Greetings, traveler."
        if talk_count >= 4:
            return "Ah, my old friend, back again."
        return "Good to see you again."
