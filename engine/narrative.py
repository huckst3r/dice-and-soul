from typing import Any


def describe_event(event_context: dict[str, Any]) -> str:
    """Return narrative text for a gameplay event.

    This is intentionally static for now, but the interface is prepared
    for future LLM-backed generation by passing structured event context.
    """
    event_type = event_context.get("type", "generic")

    # Future extension point:
    # return llm_client.generate(prompt_from_event_context(event_context))
    templates: dict[str, str] = {
        "enemy_encounter": "Shadows shift around you — danger has found you.",
        "item_found": "Something glints in the dust. You pick it up carefully.",
        "hidden_room": "A hidden seam opens in the wall, revealing a secret passage.",
        "save": "You take a moment to record your journey.",
        "load": "Memories of your path settle back into focus.",
        "search_success": "Your careful search pays off with a useful discovery.",
        "search_fail": "You inspect every corner, but find nothing new.",
        "room_generated": "The dungeon shifts and reveals a new path.",
    }

    if event_type == "room_generated":
        room_name = event_context.get("room_name", "Unknown Room")
        direction = event_context.get("direction", "forward")
        return f"You push {direction}, and discover a new place: {room_name}."

    if event_type == "npc_talk":
        npc_name = event_context.get("npc", "someone")
        talk_count = event_context.get("talk_count", 0)
        return f"You and {npc_name} exchange words (conversation #{talk_count})."
    if event_type == "npc_help":
        npc_name = event_context.get("npc", "the stranger")
        return f"You offer help to {npc_name}, and the tension eases."
    if event_type == "npc_attack":
        npc_name = event_context.get("npc", "the stranger")
        return f"You lash out at {npc_name}. Trust shatters instantly."

    return templates.get(event_type, "The dungeon remains silent.")
