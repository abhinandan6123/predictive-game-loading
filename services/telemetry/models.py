from dataclasses import dataclass
from enum import StrEnum


class TelemetryEventType(StrEnum):
    PREDICTION = "prediction"
    PREFETCH = "prefetch"
    CACHE = "cache"
    LOAD = "load"
    PLAYABLE = "playable"


@dataclass(frozen=True)
class TelemetryEvent:
    event_type: TelemetryEventType
    game_id: str
    timestamp_ms: float
    value: float | None = None
    status: str | None = None
    metadata: dict[str, str | int | float | bool] | None = None
