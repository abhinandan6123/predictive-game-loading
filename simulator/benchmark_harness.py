import csv
from pathlib import Path

from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES
from simulator.scenarios.baseline import simulate_baseline_load

RESULTS_PATH = Path("simulator/results/benchmark_results.csv")
RUNS = 10


def run_benchmark() -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "game_id",
                "network",
                "run",
                "run_type",
                "critical_ms",
                "playable_ms",
                "total_ms",
            ],
        )

        writer.writeheader()

        for network in NETWORK_PROFILES.values():
            for game in GAME_CATALOG.values():
                for run in range(RUNS):
                    result = simulate_baseline_load(game, network)
                    writer.writerow(
                        {
                            "game_id": result.game_id,
                            "network": result.network,
                            "run": run,
                            "run_type": "cold" if run == 0 else "warm",
                            "critical_ms": round(result.critical_load_ms, 2),
                            "playable_ms": round(result.playable_ms, 2),
                            "total_ms": round(result.total_load_ms, 2),
                        }
                    )


if __name__ == "__main__":
    run_benchmark()
