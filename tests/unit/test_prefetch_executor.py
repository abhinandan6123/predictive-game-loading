import pytest

from services.cache import CacheHierarchy, CacheState
from services.policy.models import PrefetchAction, PrefetchDecision
from services.prefetch import ExecutionStatus, PrefetchExecutor
from simulator.games.catalog import GAME_CATALOG


def make_executor() -> PrefetchExecutor:
    return PrefetchExecutor(
        cache=CacheHierarchy(
            critical_capacity_bytes=100_000_000,
            core_capacity_bytes=100_000_000,
            secondary_capacity_bytes=200_000_000,
        ),
        catalog=GAME_CATALOG,
    )


def test_skip_does_not_mutate_cache() -> None:
    executor = make_executor()

    result = executor.execute(
        "game_001",
        PrefetchDecision(
            action=PrefetchAction.SKIP,
            score=0.1,
            fraction=0.0,
            explanation="test",
        ),
    )

    assert result.status is ExecutionStatus.SKIPPED
    assert result.loaded_bytes == 0
    assert result.requested_bytes == 0
    assert result.cache_state is None
    assert executor.cache.get_critical("game_001") is None


def test_partial_prefetch_loads_requested_fraction() -> None:
    executor = make_executor()
    resource = GAME_CATALOG["game_001"]

    result = executor.execute(
        "game_001",
        PrefetchDecision(
            action=PrefetchAction.PARTIAL,
            score=0.5,
            fraction=0.5,
            explanation="test",
        ),
    )

    expected_bytes = int(resource.critical_bytes * 0.5)

    assert result.status is ExecutionStatus.EXECUTED
    assert result.cache_state is CacheState.PARTIAL
    assert result.requested_bytes == expected_bytes
    assert result.loaded_bytes == expected_bytes

    entry = executor.cache.get_critical("game_001")

    assert entry is not None
    assert entry.cached_bytes == expected_bytes
    assert entry.state is CacheState.PARTIAL


def test_repeating_partial_prefetch_is_cache_hit() -> None:
    executor = make_executor()

    decision = PrefetchDecision(
        action=PrefetchAction.PARTIAL,
        score=0.5,
        fraction=0.5,
        explanation="test",
    )

    first = executor.execute("game_001", decision)
    second = executor.execute("game_001", decision)

    assert first.status is ExecutionStatus.EXECUTED
    assert second.status is ExecutionStatus.CACHE_HIT
    assert second.loaded_bytes == 0


def test_full_prefetch_populates_all_cache_levels() -> None:
    executor = make_executor()
    resource = GAME_CATALOG["game_001"]

    result = executor.execute(
        "game_001",
        PrefetchDecision(
            action=PrefetchAction.FULL,
            score=1.5,
            fraction=1.0,
            explanation="test",
        ),
    )

    assert result.status is ExecutionStatus.EXECUTED
    assert result.cache_state is CacheState.READY
    assert result.requested_bytes == resource.total_bytes
    assert result.loaded_bytes == resource.total_bytes

    critical = executor.cache.get_critical("game_001")
    core = executor.cache.get_core("game_001")
    secondary = executor.cache.get_secondary("game_001")

    assert critical is not None
    assert core is not None
    assert secondary is not None

    assert critical.state is CacheState.READY
    assert core.state is CacheState.READY
    assert secondary.state is CacheState.READY


def test_full_prefetch_after_partial_only_loads_remaining_bytes() -> None:
    executor = make_executor()
    resource = GAME_CATALOG["game_001"]

    partial_decision = PrefetchDecision(
        action=PrefetchAction.PARTIAL,
        score=0.5,
        fraction=0.5,
        explanation="test",
    )

    full_decision = PrefetchDecision(
        action=PrefetchAction.FULL,
        score=1.5,
        fraction=1.0,
        explanation="test",
    )

    partial = executor.execute("game_001", partial_decision)
    full = executor.execute("game_001", full_decision)

    assert partial.loaded_bytes == int(resource.critical_bytes * 0.5)
    assert full.status is ExecutionStatus.EXECUTED
    assert full.loaded_bytes == resource.total_bytes - partial.loaded_bytes


def test_repeating_full_prefetch_is_cache_hit() -> None:
    executor = make_executor()

    decision = PrefetchDecision(
        action=PrefetchAction.FULL,
        score=1.5,
        fraction=1.0,
        explanation="test",
    )

    first = executor.execute("game_001", decision)
    second = executor.execute("game_001", decision)

    assert first.status is ExecutionStatus.EXECUTED
    assert second.status is ExecutionStatus.CACHE_HIT
    assert second.loaded_bytes == 0


def test_unknown_game_is_rejected() -> None:
    executor = make_executor()

    with pytest.raises(ValueError, match="unknown game_id"):
        executor.execute(
            "game_999",
            PrefetchDecision(
                action=PrefetchAction.FULL,
                score=1.5,
                fraction=1.0,
                explanation="test",
            ),
        )


def test_partial_fraction_must_be_valid() -> None:
    executor = make_executor()

    with pytest.raises(
        ValueError,
        match="partial prefetch fraction must be between 0 and 1",
    ):
        executor.execute(
            "game_001",
            PrefetchDecision(
                action=PrefetchAction.PARTIAL,
                score=0.5,
                fraction=1.0,
                explanation="invalid",
            ),
        )
