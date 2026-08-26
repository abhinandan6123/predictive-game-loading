import pytest

from services.cache import CacheHierarchy, CacheState
from simulator.games.catalog import GAME_CATALOG


def test_hierarchy_stores_critical_core_and_secondary() -> None:
    resource = GAME_CATALOG["game_001"]

    cache = CacheHierarchy(
        critical_capacity_bytes=100_000_000,
        core_capacity_bytes=100_000_000,
        secondary_capacity_bytes=200_000_000,
    )

    cache.put(
        resource,
        critical=True,
        core=True,
        secondary=True,
    )

    critical = cache.get_critical(resource.game_id)
    core = cache.get_core(resource.game_id)
    secondary = cache.get_secondary(resource.game_id)

    assert critical is not None
    assert core is not None
    assert secondary is not None

    assert critical.cached_bytes == resource.critical_bytes
    assert core.cached_bytes == resource.core_bytes
    assert secondary.cached_bytes == resource.secondary_bytes

    assert critical.state == CacheState.READY
    assert core.state == CacheState.READY
    assert secondary.state == CacheState.READY


def test_partial_preload_only_prefetches_partial_critical_resource() -> None:
    resource = GAME_CATALOG["game_001"]

    cache = CacheHierarchy(
        critical_capacity_bytes=100_000_000,
        core_capacity_bytes=100_000_000,
        secondary_capacity_bytes=200_000_000,
    )

    cache.preload_partial(resource, fraction=0.5)

    critical = cache.get_critical(resource.game_id)

    assert critical is not None
    assert critical.state == CacheState.PARTIAL
    assert critical.coverage == pytest.approx(0.5)

    assert cache.get_core(resource.game_id) is None
    assert cache.get_secondary(resource.game_id) is None


def test_mark_ready_populates_all_resource_levels() -> None:
    resource = GAME_CATALOG["game_001"]

    cache = CacheHierarchy(
        critical_capacity_bytes=100_000_000,
        core_capacity_bytes=100_000_000,
        secondary_capacity_bytes=200_000_000,
    )

    cache.mark_ready(resource)

    assert cache.get_critical(resource.game_id).state == CacheState.READY
    assert cache.get_core(resource.game_id).state == CacheState.READY
    assert cache.get_secondary(resource.game_id).state == CacheState.READY


def test_partial_fraction_must_be_between_zero_and_one() -> None:
    resource = GAME_CATALOG["game_001"]

    cache = CacheHierarchy(
        critical_capacity_bytes=100_000_000,
        core_capacity_bytes=100_000_000,
        secondary_capacity_bytes=200_000_000,
    )

    with pytest.raises(ValueError):
        cache.preload_partial(resource, fraction=0.0)

    with pytest.raises(ValueError):
        cache.preload_partial(resource, fraction=1.0)
