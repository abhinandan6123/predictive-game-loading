import pytest

from services.policy.decision import make_prefetch_decision
from services.policy.models import (
    PolicyConfig,
    PolicyScore,
    PrefetchAction,
)


def make_score(value: float) -> PolicyScore:
    return PolicyScore(
        score=value,
        expected_benefit_ms=100.0,
        resource_cost_mb=10.0,
        bandwidth_factor=1.0,
        cache_factor=1.0,
        explanation="test",
    )


def test_high_score_produces_full_prefetch() -> None:
    decision = make_prefetch_decision(make_score(1.5))

    assert decision.action is PrefetchAction.FULL
    assert decision.fraction == 1.0


def test_middle_score_produces_partial_prefetch() -> None:
    decision = make_prefetch_decision(make_score(0.5))

    assert decision.action is PrefetchAction.PARTIAL
    assert decision.fraction == 0.5


def test_low_score_produces_skip() -> None:
    decision = make_prefetch_decision(make_score(0.1))

    assert decision.action is PrefetchAction.SKIP
    assert decision.fraction == 0.0


def test_full_threshold_is_inclusive() -> None:
    config = PolicyConfig(
        full_threshold=1.0,
        partial_threshold=0.25,
    )

    decision = make_prefetch_decision(
        make_score(1.0),
        config,
    )

    assert decision.action is PrefetchAction.FULL


def test_partial_threshold_is_inclusive() -> None:
    config = PolicyConfig(
        full_threshold=1.0,
        partial_threshold=0.25,
    )

    decision = make_prefetch_decision(
        make_score(0.25),
        config,
    )

    assert decision.action is PrefetchAction.PARTIAL


def test_decision_contains_explanation() -> None:
    decision = make_prefetch_decision(make_score(0.5))

    assert "score=" in decision.explanation
    assert "action=PARTIAL" in decision.explanation


def test_invalid_threshold_order_is_rejected() -> None:
    config = PolicyConfig(
        full_threshold=0.25,
        partial_threshold=1.0,
    )

    with pytest.raises(ValueError):
        make_prefetch_decision(make_score(0.5), config)


def test_invalid_partial_fraction_is_rejected() -> None:
    config = PolicyConfig(partial_fraction=1.0)

    with pytest.raises(ValueError):
        make_prefetch_decision(make_score(0.5), config)
