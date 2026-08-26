from dataclasses import dataclass
from enum import StrEnum

from simulator.games.models import GameResource


class LoadStage(StrEnum):
    CRITICAL = "critical"
    PLAYABLE = "playable"
    SECONDARY = "secondary"


@dataclass(frozen=True)
class ProgressiveLoadResult:
    critical_bytes: int
    playable_bytes: int
    secondary_bytes: int
    total_bytes: int


def progressive_load(game: GameResource) -> ProgressiveLoadResult:
    critical_bytes = game.critical_bytes
    core_bytes = game.core_bytes
    secondary_bytes = game.secondary_bytes

    playable_bytes = critical_bytes + core_bytes
    total_bytes = playable_bytes + secondary_bytes

    return ProgressiveLoadResult(
        critical_bytes=critical_bytes,
        playable_bytes=playable_bytes,
        secondary_bytes=secondary_bytes,
        total_bytes=total_bytes,
    )


@dataclass(frozen=True)
class ProgressiveLoadEvent:
    stage: LoadStage
    bytes_loaded: int