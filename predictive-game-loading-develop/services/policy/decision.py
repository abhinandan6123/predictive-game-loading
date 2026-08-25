from services.policy.models import (
    PolicyConfig,
    PolicyScore,
    PrefetchAction,
    PrefetchDecision,
)


def make_prefetch_decision(
    score: PolicyScore,
    config: PolicyConfig | None = None,
) -> PrefetchDecision:
    config = config or PolicyConfig()

    if config.partial_threshold < 0:
        raise ValueError("partial_threshold must be non-negative.")

    if config.full_threshold <= config.partial_threshold:
        raise ValueError("full_threshold must be greater than partial_threshold.")

    if not 0.0 < config.partial_fraction < 1.0:
        raise ValueError("partial_fraction must be between 0 and 1.")

    if score.score >= config.full_threshold:
        action = PrefetchAction.FULL
        fraction = 1.0
    elif score.score >= config.partial_threshold:
        action = PrefetchAction.PARTIAL
        fraction = config.partial_fraction
    else:
        action = PrefetchAction.SKIP
        fraction = 0.0

    explanation = (
        f"score={score.score:.4f}; "
        f"action={action.value}; "
        f"fraction={fraction:.2f}; "
        f"score_components=({score.explanation})"
    )

    return PrefetchDecision(
        action=action,
        score=score.score,
        fraction=fraction,
        explanation=explanation,
    )
