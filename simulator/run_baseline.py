from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES
from simulator.scenarios.baseline import simulate_baseline_load


def main() -> None:
    for network in NETWORK_PROFILES.values():
        print(f"\n=== {network.name.upper()} NETWORK ===")

        for game in GAME_CATALOG.values():
            result = simulate_baseline_load(
                game,
                network,
            )

            print(
                f"{game.game_id}: "
                f"playable={result.playable_ms:.2f}ms, "
                f"total={result.total_load_ms:.2f}ms"
            )


if __name__ == "__main__":
    main()
