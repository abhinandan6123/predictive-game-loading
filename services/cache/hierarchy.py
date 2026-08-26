from dataclasses import dataclass

from services.cache.cache import InMemoryCache
from services.cache.models import CacheEntry, CacheState, CacheStats
from simulator.games.models import GameResource


@dataclass(frozen=True)
class CacheHierarchyStats:
    critical: CacheStats
    core: CacheStats
    secondary: CacheStats


class CacheHierarchy:
    """Three-level cache aligned with critical/core/secondary resources."""

    def __init__(
        self,
        critical_capacity_bytes: int,
        core_capacity_bytes: int,
        secondary_capacity_bytes: int,
    ) -> None:
        self.critical = InMemoryCache(critical_capacity_bytes)
        self.core = InMemoryCache(core_capacity_bytes)
        self.secondary = InMemoryCache(secondary_capacity_bytes)

    def put(
        self,
        resource: GameResource,
        *,
        critical: bool = True,
        core: bool = False,
        secondary: bool = False,
    ) -> None:
        if critical:
            self.critical.put(
                resource.game_id,
                resource.critical_bytes,
            )

        if core:
            self.core.put(
                resource.game_id,
                resource.core_bytes,
            )

        if secondary:
            self.secondary.put(
                resource.game_id,
                resource.secondary_bytes,
            )

    def get_critical(self, game_id: str) -> CacheEntry | None:
        return self.critical.get(game_id)

    def get_core(self, game_id: str) -> CacheEntry | None:
        return self.core.get(game_id)

    def get_secondary(self, game_id: str) -> CacheEntry | None:
        return self.secondary.get(game_id)

    def preload_partial(
        self,
        resource: GameResource,
        fraction: float,
    ) -> None:
        if not 0.0 < fraction < 1.0:
            raise ValueError("fraction must be between 0 and 1.")

        critical_bytes = int(resource.critical_bytes * fraction)

        if critical_bytes > 0:
            self.critical.put(
                resource.game_id,
                resource.critical_bytes,
                cached_bytes=critical_bytes,
                state=CacheState.PARTIAL,
            )

    def mark_ready(self, resource: GameResource) -> None:
        self.critical.put(
            resource.game_id,
            resource.critical_bytes,
            state=CacheState.READY,
        )

        self.core.put(
            resource.game_id,
            resource.core_bytes,
            state=CacheState.READY,
        )

        self.secondary.put(
            resource.game_id,
            resource.secondary_bytes,
            state=CacheState.READY,
        )

    def stats(self) -> CacheHierarchyStats:
        return CacheHierarchyStats(
            critical=self.critical.stats(),
            core=self.core.stats(),
            secondary=self.secondary.stats(),
        )
