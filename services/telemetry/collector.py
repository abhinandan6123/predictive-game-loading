from dataclasses import dataclass, field

from services.telemetry.models import TelemetryEvent, TelemetryEventType


@dataclass
class TelemetryCollector:
    events: list[TelemetryEvent] = field(default_factory=list)

    def record(self, event: TelemetryEvent) -> None:
        self.events.append(event)

    def count(self, event_type: TelemetryEventType) -> int:
        return sum(event.event_type is event_type for event in self.events)

    def metrics(self) -> dict[str, object]:
        prefetch_events = [
            event for event in self.events if event.event_type is TelemetryEventType.PREFETCH
        ]

        cache_events = [
            event for event in self.events if event.event_type is TelemetryEventType.CACHE
        ]

        load_events = [
            event
            for event in self.events
            if event.event_type is TelemetryEventType.LOAD and event.value is not None
        ]

        cache_hits = sum(event.status == "hit" for event in cache_events)
        cache_total = len(cache_events)

        executed_prefetches = sum(event.status == "executed" for event in prefetch_events)
        successful_prefetches = sum(
            event.status in {"executed", "cache_hit"} for event in prefetch_events
        )

        latencies = [event.value for event in load_events if event.value is not None]

        return {
            "events_total": len(self.events),
            "prediction_requests": self.count(TelemetryEventType.PREDICTION),
            "prefetch_requests": len(prefetch_events),
            "prefetch_executed": executed_prefetches,
            "prefetch_accuracy": (
                successful_prefetches / len(prefetch_events) if prefetch_events else 0.0
            ),
            "cache_hits": cache_hits,
            "cache_requests": cache_total,
            "cache_hit_rate": cache_hits / cache_total if cache_total else 0.0,
            "load_count": len(latencies),
            "time_to_playable_ms": (sum(latencies) / len(latencies) if latencies else 0.0),
            "p50_load_ms": _percentile(latencies, 50),
            "p95_load_ms": _percentile(latencies, 95),
        }


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0

    if not 0.0 <= percentile <= 100.0:
        raise ValueError("percentile must be between 0 and 100.")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    rank = (percentile / 100.0) * (len(ordered) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower

    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight
