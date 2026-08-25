from dataclasses import dataclass

from simulator.games.models import GameResource
from simulator.network.profiles import NetworkProfile
from simulator.network.transfer import transfer_time_ms


@dataclass(frozen=True)
class BaselineResult:
    game_id: str
    network: str
    request_latency_ms: float
    critical_load_ms: float
    core_load_ms: float
    secondary_load_ms: float
    total_load_ms: float
    playable_ms: float


def simulate_baseline_load(
    game: GameResource,
    network: NetworkProfile,
) -> BaselineResult:
    critical_ms = transfer_time_ms(
        game.critical_bytes,
        network,
    )

    core_ms = transfer_time_ms(
        game.core_bytes,
        network,
    )

    secondary_ms = transfer_time_ms(
        game.secondary_bytes,
        network,
    )

    total_ms = critical_ms + core_ms + secondary_ms

    playable_ms = critical_ms + core_ms

    return BaselineResult(
        game_id=game.game_id,
        network=network.name,
        request_latency_ms=network.latency_ms,
        critical_load_ms=critical_ms,
        core_load_ms=core_ms,
        secondary_load_ms=secondary_ms,
        total_load_ms=total_ms,
        playable_ms=playable_ms,
    )
