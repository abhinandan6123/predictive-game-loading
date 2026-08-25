from dataclasses import dataclass


@dataclass(frozen=True)
class SessionEvent:
    session_id: str
    user_id: str
    timestamp_ms: int
    event_type: str
    game_id: str
