from dataclasses import dataclass
from enum import StrEnum

from services.cache import CacheHierarchy, CacheState
from services.loading.progressive import LoadStage, progressive_load
from services.policy.models import PrefetchAction, PrefetchDecision
from simulator.games.catalog import GAME_CATALOG
from simulator.games.models import GameResource


class ExecutionStatus(StrEnum):
    SKIPPED = "skipped"
    EXECUTED = "executed"
    CACHE_HIT = "cache_hit"


@dataclass(frozen=True)
class PrefetchExecutionResult:
    target_game_id: str
    action: PrefetchAction
    fraction: float
    status: ExecutionStatus
    cache_state: CacheState | None
    requested_bytes: int
    loaded_bytes: int
    playable_bytes: int
    total_bytes: int
    stages: tuple[LoadStage, ...]


class PrefetchExecutor:
    """Execute policy decisions against the game catalog and cache hierarchy."""

    def __init__(
        self,
        cache: CacheHierarchy | None = None,
        catalog: dict[str, GameResource] | None = None,
    ) -> None:
        self.cache = cache or CacheHierarchy(
            critical_capacity_bytes=256_000_000,
            core_capacity_bytes=512_000_000,
            secondary_capacity_bytes=1_024_000_000,
        )
        self.catalog = catalog or GAME_CATALOG

    def execute(
        self,
        target_game_id: str,
        decision: PrefetchDecision,
    ) -> PrefetchExecutionResult:
        resource = self._get_resource(target_game_id)

        load = progressive_load(resource)

        if decision.action is PrefetchAction.SKIP:
            return PrefetchExecutionResult(
                target_game_id=target_game_id,
                action=decision.action,
                fraction=decision.fraction,
                status=ExecutionStatus.SKIPPED,
                cache_state=None,
                requested_bytes=0,
                loaded_bytes=0,
                playable_bytes=load.playable_bytes,
                total_bytes=load.total_bytes,
                stages=(),
            )

        if decision.action is PrefetchAction.PARTIAL:
            return self._execute_partial(resource, decision, load)

        if decision.action is PrefetchAction.FULL:
            return self._execute_full(resource, decision, load)

        raise ValueError(f"Unsupported prefetch action: {decision.action}")

    def _execute_partial(
        self,
        resource: GameResource,
        decision: PrefetchDecision,
        load,
    ) -> PrefetchExecutionResult:
        if not 0.0 < decision.fraction < 1.0:
            raise ValueError("partial prefetch fraction must be between 0 and 1.")

        existing = self.cache.get_critical(resource.game_id)
        requested_bytes = int(resource.critical_bytes * decision.fraction)

        if existing is not None and existing.cached_bytes >= requested_bytes:
            return PrefetchExecutionResult(
                target_game_id=resource.game_id,
                action=decision.action,
                fraction=decision.fraction,
                status=ExecutionStatus.CACHE_HIT,
                cache_state=existing.state,
                requested_bytes=requested_bytes,
                loaded_bytes=0,
                playable_bytes=load.playable_bytes,
                total_bytes=load.total_bytes,
                stages=(LoadStage.CRITICAL,),
            )

        previous_bytes = existing.cached_bytes if existing is not None else 0

        self.cache.preload_partial(
            resource,
            decision.fraction,
        )

        loaded_bytes = max(requested_bytes - previous_bytes, 0)

        entry = self.cache.get_critical(resource.game_id)

        return PrefetchExecutionResult(
            target_game_id=resource.game_id,
            action=decision.action,
            fraction=decision.fraction,
            status=ExecutionStatus.EXECUTED,
            cache_state=entry.state if entry is not None else CacheState.PARTIAL,
            requested_bytes=requested_bytes,
            loaded_bytes=loaded_bytes,
            playable_bytes=load.playable_bytes,
            total_bytes=load.total_bytes,
            stages=(LoadStage.CRITICAL,),
        )

    def _execute_full(
        self,
        resource: GameResource,
        decision: PrefetchDecision,
        load,
    ) -> PrefetchExecutionResult:
        if decision.fraction != 1.0:
            raise ValueError("full prefetch fraction must be 1.0.")

        existing_entries = (
            self.cache.get_critical(resource.game_id),
            self.cache.get_core(resource.game_id),
            self.cache.get_secondary(resource.game_id),
        )

        loaded_before = sum(entry.cached_bytes for entry in existing_entries if entry is not None)

        if all(entry is not None and entry.state is CacheState.READY for entry in existing_entries):
            return PrefetchExecutionResult(
                target_game_id=resource.game_id,
                action=decision.action,
                fraction=decision.fraction,
                status=ExecutionStatus.CACHE_HIT,
                cache_state=CacheState.READY,
                requested_bytes=load.total_bytes,
                loaded_bytes=0,
                playable_bytes=load.playable_bytes,
                total_bytes=load.total_bytes,
                stages=(
                    LoadStage.CRITICAL,
                    LoadStage.PLAYABLE,
                    LoadStage.SECONDARY,
                ),
            )

        self.cache.mark_ready(resource)

        loaded_bytes = max(load.total_bytes - loaded_before, 0)

        return PrefetchExecutionResult(
            target_game_id=resource.game_id,
            action=decision.action,
            fraction=decision.fraction,
            status=ExecutionStatus.EXECUTED,
            cache_state=CacheState.READY,
            requested_bytes=load.total_bytes,
            loaded_bytes=loaded_bytes,
            playable_bytes=load.playable_bytes,
            total_bytes=load.total_bytes,
            stages=(
                LoadStage.CRITICAL,
                LoadStage.PLAYABLE,
                LoadStage.SECONDARY,
            ),
        )

    def _get_resource(self, game_id: str) -> GameResource:
        try:
            return self.catalog[game_id]
        except KeyError as exc:
            raise ValueError(f"unknown game_id: {game_id}") from exc
