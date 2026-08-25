from simulator.games.catalog import CATEGORIES, GAME_CATALOG


def test_catalog_contains_100_games() -> None:
    assert len(GAME_CATALOG) == 100


def test_game_ids_are_unique() -> None:
    assert len(GAME_CATALOG) == len(set(GAME_CATALOG))


def test_all_games_have_valid_categories() -> None:
    assert all(game.category in CATEGORIES for game in GAME_CATALOG.values())


def test_resource_components_sum_to_total() -> None:
    for game in GAME_CATALOG.values():
        resource_sum = game.critical_bytes + game.core_bytes + game.secondary_bytes

        assert resource_sum == game.total_bytes


def test_all_resource_sizes_are_positive() -> None:
    for game in GAME_CATALOG.values():
        assert game.total_bytes > 0
        assert game.critical_bytes > 0
        assert game.core_bytes > 0
        assert game.secondary_bytes > 0


def test_categories_are_distributed() -> None:
    categories = {game.category for game in GAME_CATALOG.values()}

    assert categories == set(CATEGORIES)
