from simulator.games.models import GameResource

CATEGORIES = (
    "action",
    "arcade",
    "card",
    "casual",
    "puzzle",
    "racing",
    "sports",
    "strategy",
    "table",
    "adventure",
)


def _build_game(index: int) -> GameResource:
    category = CATEGORIES[(index - 1) % len(CATEGORIES)]

    critical_mb = 8 + ((index * 7) % 18)
    core_mb = 16 + ((index * 11) % 36)
    secondary_mb = 24 + ((index * 13) % 72)

    return GameResource(
        game_id=f"game_{index:03d}",
        category=category,
        critical_bytes=critical_mb * 1_000_000,
        core_bytes=core_mb * 1_000_000,
        secondary_bytes=secondary_mb * 1_000_000,
    )


GAME_CATALOG: dict[str, GameResource] = {
    game.game_id: game for game in (_build_game(index) for index in range(1, 101))
}
