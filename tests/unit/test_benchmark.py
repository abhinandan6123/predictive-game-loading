import csv

import simulator.benchmark as benchmark


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

        assert len(rows) == 15
        assert {
            "game_id",
            "network",
            "critical_ms",
            "playable_ms",
            "total_ms",
        } == set(rows[0])

    finally:
        benchmark.RESULTS_PATH = original_path
