from dataclasses import dataclass


@dataclass
class Quest:
    name: str
    description: str
    objective: str
    reward: str
    xp_reward: int = 50
    status: str = "active"  # active | completed
