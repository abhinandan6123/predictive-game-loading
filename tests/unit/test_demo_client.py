from demo.client import (
    DEMO_CURRENT_GAME,
    DEMO_TARGET_GAME,
    run_demo,
)


def test_demo_runs_baseline_and_pulseload_paths() -> None:
    result = run_demo()

    assert result.scenario == f"{DEMO_CURRENT_GAME} -> {DEMO_TARGET_GAME}"
    assert result.network == "medium"

    assert result.baseline_playable_ms > 0
    assert result.baseline_total_ms >= result.baseline_playable_ms

    assert result.predicted_game_id == DEMO_TARGET_GAME
    assert result.probability == 0.90

    assert result.action == "FULL"
    assert result.fraction == 1.0

    assert result.execution_status == "executed"
    assert result.requested_bytes > 0
    assert result.loaded_bytes == result.requested_bytes
    assert result.cache_state == "READY"


def test_demo_repeat_execution_is_cache_hit() -> None:
    result = run_demo()

    assert result.cache_hit_on_repeat is True
    assert result.repeat_loaded_bytes == 0
