FACTIONS: tuple[str, ...] = (
    "guards",
    "bandits",
    "mages",
    "merchants",
    "cultists",
)


def default_reputation() -> dict[str, int]:
    return {faction: 0 for faction in FACTIONS}


def clamp_reputation(value: int) -> int:
    return max(-100, min(100, value))


def hostility_from_reputation(reputation: int) -> str:
    if reputation <= -20:
        return "hostile"
    if reputation >= 20:
        return "friendly"
    return "neutral"
