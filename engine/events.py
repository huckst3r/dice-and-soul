from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class GameEvent:
    name: str
    context: dict


@dataclass
class EventManager:
    _handlers: dict[str, list[Callable[[GameEvent], None]]] = field(default_factory=dict)

    def register(self, event_name: str, handler: Callable[[GameEvent], None]) -> None:
        handlers = self._handlers.setdefault(event_name, [])
        handlers.append(handler)

    def emit(self, event_name: str, context: dict | None = None) -> GameEvent:
        event = GameEvent(name=event_name, context=context or {})
        for handler in self._handlers.get(event_name, []):
            handler(event)
        return event
