from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES
from simulator.scenarios.baseline import simulate_baseline_load


def test_baseline_returns_playable_time() -> None:
    result = simulate_baseline_load(
        GAME_CATALOG["game_01"],
        NETWORK_PROFILES["medium"],
    )

    assert result.playable_ms > 0
    assert result.total_load_ms >= result.playable_ms


def test_all_games_have_positive_resources() -> None:
    for game in GAME_CATALOG.values():
        assert game.total_bytes > 0
        assert game.critical_bytes > 0
        assert game.core_bytes > 0
