import csv

import simulator.benchmark as benchmark
from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES


def test_benchmark_generates_expected_rows(tmp_path) -> None:
    original_path = benchmark.RESULTS_PATH

    try:
        benchmark.RESULTS_PATH = tmp_path / "baseline_results.csv"

        benchmark.run_benchmark()

        with benchmark.RESULTS_PATH.open(
            newline="",
            encoding="utf-8",
        ) as file:
            rows = list(csv.DictReader(file))

        expected_rows = len(GAME_CATALOG) * len(NETWORK_PROFILES)

        assert len(rows) == expected_rows
        assert {
            "game_id",
            "network",
            "critical_ms",
            "playable_ms",
            "total_ms",
        } == set(rows[0])

    finally:
        benchmark.RESULTS_PATH = original_path
