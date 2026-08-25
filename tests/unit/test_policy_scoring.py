import pytest

from services.policy.models import PolicyInputs
from services.policy.scoring import calculate_policy_score


def make_inputs(**overrides) -> PolicyInputs:
    values = {
        "probability": 0.8,
        "latency_benefit_ms": 1000.0,
        "resource_cost_bytes": 10_000_000,
        "bandwidth_mbps": 20.0,
        "cache_pressure": 0.0,
    }
    values.update(overrides)
    return PolicyInputs(**values)


def test_score_is_positive_for_useful_prefetch() -> None:
    score = calculate_policy_score(make_inputs())

    assert score.score > 0
    assert score.expected_benefit_ms == 800.0
    assert score.resource_cost_mb == 10.0


def test_higher_probability_increases_score() -> None:
    low = calculate_policy_score(make_inputs(probability=0.2))
    high = calculate_policy_score(make_inputs(probability=0.8))

    assert high.score > low.score


def test_greater_latency_benefit_increases_score() -> None:
    low = calculate_policy_score(make_inputs(latency_benefit_ms=500.0))
    high = calculate_policy_score(make_inputs(latency_benefit_ms=1500.0))

    assert high.score > low.score


def test_larger_resource_cost_decreases_score() -> None:
    small = calculate_policy_score(make_inputs(resource_cost_bytes=5_000_000))
    large = calculate_policy_score(make_inputs(resource_cost_bytes=20_000_000))

    assert small.score > large.score


def test_lower_bandwidth_decreases_score() -> None:
    fast = calculate_policy_score(make_inputs(bandwidth_mbps=100.0))
    slow = calculate_policy_score(make_inputs(bandwidth_mbps=5.0))

    assert fast.score > slow.score


def test_higher_cache_pressure_decreases_score() -> None:
    low = calculate_policy_score(make_inputs(cache_pressure=0.1))
    high = calculate_policy_score(make_inputs(cache_pressure=0.9))

    assert low.score > high.score


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("probability", -0.1),
        ("probability", 1.1),
        ("latency_benefit_ms", -1.0),
        ("resource_cost_bytes", 0),
        ("bandwidth_mbps", 0),
        ("cache_pressure", -0.1),
        ("cache_pressure", 1.1),
    ],
)
def test_invalid_inputs_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        calculate_policy_score(make_inputs(**{field: value}))
