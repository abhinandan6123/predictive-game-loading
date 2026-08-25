from dataclasses import dataclass


@dataclass(frozen=True)
class GameResource:
    game_id: str
    critical_bytes: int
    core_bytes: int
    secondary_bytes: int

    @property
    def total_bytes(self) -> int:
        return self.critical_bytes + self.core_bytes + self.secondary_bytes
