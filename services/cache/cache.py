from collections import OrderedDict

from services.cache.models import CacheEntry, CacheState, CacheStats


class InMemoryCache:
    """Deterministic byte-capacity cache with LRU eviction."""

    def __init__(self, capacity_bytes: int) -> None:
        if capacity_bytes <= 0:
            raise ValueError("capacity_bytes must be positive.")

        self.capacity_bytes = capacity_bytes
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self._used_bytes = 0
        self._clock = 0

        self._hits = 0
        self._misses = 0
        self._partial_hits = 0
        self._evictions = 0

    @property
    def used_bytes(self) -> int:
        return self._used_bytes

    @property
    def available_bytes(self) -> int:
        return self.capacity_bytes - self._used_bytes

    def get(self, game_id: str) -> CacheEntry | None:
        entry = self._entries.get(game_id)

        if entry is None:
            self._misses += 1
            return None

        if entry.state == CacheState.EXPIRED:
            self._remove(game_id)
            self._misses += 1
            return None

        self._clock += 1
        refreshed = CacheEntry(
            game_id=entry.game_id,
            total_bytes=entry.total_bytes,
            cached_bytes=entry.cached_bytes,
            state=entry.state,
            last_access=self._clock,
        )

        self._entries[game_id] = refreshed
        self._entries.move_to_end(game_id)

        if refreshed.state == CacheState.PARTIAL:
            self._partial_hits += 1
        else:
            self._hits += 1

        return refreshed

    def put(
        self,
        game_id: str,
        total_bytes: int,
        cached_bytes: int | None = None,
        state: CacheState | None = None,
    ) -> CacheEntry:
        if total_bytes <= 0:
            raise ValueError("total_bytes must be positive.")

        if cached_bytes is None:
            cached_bytes = total_bytes

        if cached_bytes < 0:
            raise ValueError("cached_bytes must be non-negative.")

        if cached_bytes > total_bytes:
            raise ValueError("cached_bytes cannot exceed total_bytes.")

        if cached_bytes > self.capacity_bytes:
            raise ValueError("cached resource cannot exceed cache capacity.")

        if state is None:
            if cached_bytes == total_bytes:
                state = CacheState.READY
            elif cached_bytes == 0:
                state = CacheState.MISS
            else:
                state = CacheState.PARTIAL

        if state == CacheState.MISS:
            cached_bytes = 0
        elif state == CacheState.READY:
            cached_bytes = total_bytes
        elif state == CacheState.EXPIRED:
            cached_bytes = 0

        if game_id in self._entries:
            self._remove(game_id)

        self._evict_until_available(cached_bytes)

        self._clock += 1
        entry = CacheEntry(
            game_id=game_id,
            total_bytes=total_bytes,
            cached_bytes=cached_bytes,
            state=state,
            last_access=self._clock,
        )

        self._entries[game_id] = entry
        self._used_bytes += cached_bytes

        return entry

    def remove(self, game_id: str) -> bool:
        if game_id not in self._entries:
            return False

        self._remove(game_id)
        return True

    def contains(self, game_id: str) -> bool:
        return game_id in self._entries

    def clear(self) -> None:
        self._entries.clear()
        self._used_bytes = 0

    def entries(self) -> tuple[CacheEntry, ...]:
        return tuple(self._entries.values())

    def stats(self) -> CacheStats:
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            partial_hits=self._partial_hits,
            evictions=self._evictions,
        )

    def _evict_until_available(self, required_bytes: int) -> None:
        while self.available_bytes < required_bytes and self._entries:
            _, entry = self._entries.popitem(last=False)
            self._used_bytes -= entry.cached_bytes
            self._evictions += 1

    def _remove(self, game_id: str) -> None:
        entry = self._entries.pop(game_id)
        self._used_bytes -= entry.cached_bytes
