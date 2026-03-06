from dataclasses import dataclass


@dataclass
class Quest:
    name: str
    description: str
    objective: str
    reward: str
    status: str = "active"  # active | completed
