from services.loading.progressive import progressive_load
from simulator.games.catalog import GAME_CATALOG


def test_progressive_load_preserves_game_resources() -> None:
    for game in GAME_CATALOG.values():
        result = progressive_load(game)

        assert result.critical_bytes == game.critical_bytes
        assert result.secondary_bytes == game.secondary_bytes


def test_progressive_load_playable_bytes() -> None:
    for game in GAME_CATALOG.values():
        result = progressive_load(game)

        assert result.playable_bytes == (game.critical_bytes + game.core_bytes)


def test_progressive_load_total_bytes() -> None:
    for game in GAME_CATALOG.values():
        result = progressive_load(game)

        assert result.total_bytes == game.total_bytes
