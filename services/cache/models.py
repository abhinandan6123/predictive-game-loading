from dataclasses import dataclass
from enum import StrEnum


class CacheState(StrEnum):
    MISS = "MISS"
    PARTIAL = "PARTIAL"
    READY = "READY"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class CacheEntry:
    game_id: str
    total_bytes: int
    cached_bytes: int
    state: CacheState
    last_access: int

    @property
    def remaining_bytes(self) -> int:
        return max(self.total_bytes - self.cached_bytes, 0)

    @property
    def coverage(self) -> float:
        if self.total_bytes <= 0:
            return 0.0
        return self.cached_bytes / self.total_bytes


@dataclass(frozen=True)
class CacheStats:
    hits: int
    misses: int
    partial_hits: int
    evictions: int

    @property
    def requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.hits / self.requests
