from simulator.games.models import GameResource

GAME_CATALOG: dict[str, GameResource] = {
    "game_01": GameResource(
        game_id="game_01",
        critical_bytes=120_000,
        core_bytes=850_000,
        secondary_bytes=2_200_000,
    ),
    "game_02": GameResource(
        game_id="game_02",
        critical_bytes=150_000,
        core_bytes=1_100_000,
        secondary_bytes=1_800_000,
    ),
    "game_03": GameResource(
        game_id="game_03",
        critical_bytes=100_000,
        core_bytes=750_000,
        secondary_bytes=2_600_000,
    ),
    "game_04": GameResource(
        game_id="game_04",
        critical_bytes=180_000,
        core_bytes=950_000,
        secondary_bytes=2_100_000,
    ),
    "game_05": GameResource(
        game_id="game_05",
        critical_bytes=130_000,
        core_bytes=900_000,
        secondary_bytes=2_400_000,
    ),
}
