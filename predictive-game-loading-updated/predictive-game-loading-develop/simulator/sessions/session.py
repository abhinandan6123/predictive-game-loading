from dataclasses import dataclass

from simulator.sessions.events import SessionEvent


@dataclass(frozen=True)
class Session:
    session_id: str
    user_id: str
    events: tuple[SessionEvent, ...]
