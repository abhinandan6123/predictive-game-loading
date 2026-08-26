import pytest

from services.cache import CacheState, InMemoryCache


def test_empty_cache_is_miss() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    assert cache.get("game_001") is None

    stats = cache.stats()
    assert stats.misses == 1
    assert stats.hits == 0


def test_put_and_get_ready_entry() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    entry = cache.put("game_001", total_bytes=40)

    assert entry.state == CacheState.READY
    assert entry.cached_bytes == 40
    assert cache.used_bytes == 40

    result = cache.get("game_001")

    assert result is not None
    assert result.state == CacheState.READY
    assert result.coverage == 1.0
    assert cache.stats().hits == 1


def test_partial_entry_tracks_coverage() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    entry = cache.put(
        "game_001",
        total_bytes=100,
        cached_bytes=40,
    )

    assert entry.state == CacheState.PARTIAL
    assert entry.coverage == pytest.approx(0.4)

    result = cache.get("game_001")

    assert result is not None
    assert result.state == CacheState.PARTIAL
    assert cache.stats().partial_hits == 1


def test_lru_eviction() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    cache.put("game_001", total_bytes=40)
    cache.put("game_002", total_bytes=40)

    assert cache.get("game_001") is not None

    cache.put("game_003", total_bytes=40)

    assert cache.contains("game_001")
    assert not cache.contains("game_002")
    assert cache.contains("game_003")
    assert cache.used_bytes == 80
    assert cache.stats().evictions == 1


def test_remove_releases_capacity() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    cache.put("game_001", total_bytes=60)

    assert cache.used_bytes == 60
    assert cache.remove("game_001")
    assert cache.used_bytes == 0
    assert not cache.contains("game_001")


def test_invalid_capacity_is_rejected() -> None:
    with pytest.raises(ValueError):
        InMemoryCache(capacity_bytes=0)


def test_invalid_resource_size_is_rejected() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    with pytest.raises(ValueError):
        cache.put("game_001", total_bytes=0)


def test_resource_larger_than_capacity_is_rejected() -> None:
    cache = InMemoryCache(capacity_bytes=100)

    with pytest.raises(ValueError):
        cache.put("game_001", total_bytes=101)
