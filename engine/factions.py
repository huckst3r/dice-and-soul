FACTIONS: tuple[str, ...] = (
    "guards",
    "bandits",
    "mages",
    "merchants",
    "cultists",
)

FRIENDLY_THRESHOLD = 25
HOSTILE_THRESHOLD = -25


def default_reputation() -> dict[str, int]:
    return {faction: 0 for faction in FACTIONS}


def clamp_reputation(value: int) -> int:
    return max(-100, min(100, value))


def hostility_from_reputation(reputation: int) -> str:
    if reputation <= HOSTILE_THRESHOLD:
        return "hostile"
    if reputation >= FRIENDLY_THRESHOLD:
        return "friendly"
    return "neutral"


def reputation_tier(reputation: int) -> str:
    return hostility_from_reputation(reputation)
