from services.telemetry import (
    TelemetryCollector,
    TelemetryEvent,
    TelemetryEventType,
)


def test_records_events() -> None:
    collector = TelemetryCollector()

    collector.record(
        TelemetryEvent(
            event_type=TelemetryEventType.PREDICTION,
            game_id="game_001",
            timestamp_ms=100.0,
        )
    )

    assert collector.count(TelemetryEventType.PREDICTION) == 1
    assert collector.metrics()["events_total"] == 1


def test_calculates_cache_hit_rate() -> None:
    collector = TelemetryCollector()

    collector.record(
        TelemetryEvent(
            event_type=TelemetryEventType.CACHE,
            game_id="game_001",
            timestamp_ms=100.0,
            status="hit",
        )
    )
    collector.record(
        TelemetryEvent(
            event_type=TelemetryEventType.CACHE,
            game_id="game_002",
            timestamp_ms=110.0,
            status="miss",
        )
    )

    assert collector.metrics()["cache_hit_rate"] == 0.5


def test_calculates_prefetch_accuracy() -> None:
    collector = TelemetryCollector()

    for status in ("executed", "cache_hit", "skipped"):
        collector.record(
            TelemetryEvent(
                event_type=TelemetryEventType.PREFETCH,
                game_id="game_001",
                timestamp_ms=100.0,
                status=status,
            )
        )

    assert collector.metrics()["prefetch_accuracy"] == 2 / 3


def test_calculates_load_percentiles() -> None:
    collector = TelemetryCollector()

    for index, latency in enumerate((100.0, 200.0, 300.0, 400.0, 500.0)):
        collector.record(
            TelemetryEvent(
                event_type=TelemetryEventType.LOAD,
                game_id=f"game_{index:03d}",
                timestamp_ms=float(index),
                value=latency,
            )
        )

    metrics = collector.metrics()

    assert metrics["time_to_playable_ms"] == 300.0
    assert metrics["p50_load_ms"] == 300.0
    assert metrics["p95_load_ms"] == 480.0


def test_load_event_without_latency_does_not_fake_timing_metrics() -> None:
    collector = TelemetryCollector()

    collector.record(
        TelemetryEvent(
            event_type=TelemetryEventType.LOAD,
            game_id="game_001",
            timestamp_ms=100.0,
            metadata={"loaded_bytes": 110_000_000},
        )
    )

    metrics = collector.metrics()

    assert metrics["load_count"] == 0
    assert metrics["time_to_playable_ms"] == 0.0
    assert metrics["p50_load_ms"] == 0.0
    assert metrics["p95_load_ms"] == 0.0
