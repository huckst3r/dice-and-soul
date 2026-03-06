from dataclasses import dataclass


@dataclass
class ParsedCommand:
    command: str
    args: list[str]


ALIASES = {
    "n": "go north",
    "s": "go south",
    "e": "go east",
    "w": "go west",
    "i": "inventory",
}


def parse_command(raw_input: str) -> ParsedCommand:
    normalized = raw_input.strip().lower()
    if not normalized:
        return ParsedCommand(command="", args=[])

    normalized = ALIASES.get(normalized, normalized)
    parts = normalized.split()
    return ParsedCommand(command=parts[0], args=parts[1:])
