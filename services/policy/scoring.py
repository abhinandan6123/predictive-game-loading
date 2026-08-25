from services.policy.models import PolicyInputs, PolicyScore

REFERENCE_BANDWIDTH_MBPS = 20.0
BYTES_PER_MB = 1_000_000


def calculate_policy_score(inputs: PolicyInputs) -> PolicyScore:
    if not 0.0 <= inputs.probability <= 1.0:
        raise ValueError("probability must be between 0 and 1.")

    if inputs.latency_benefit_ms < 0:
        raise ValueError("latency_benefit_ms must be non-negative.")

    if inputs.resource_cost_bytes <= 0:
        raise ValueError("resource_cost_bytes must be positive.")

    if inputs.bandwidth_mbps <= 0:
        raise ValueError("bandwidth_mbps must be positive.")

    if not 0.0 <= inputs.cache_pressure <= 1.0:
        raise ValueError("cache_pressure must be between 0 and 1.")

    expected_benefit_ms = inputs.probability * inputs.latency_benefit_ms

    resource_cost_mb = inputs.resource_cost_bytes / BYTES_PER_MB

    bandwidth_factor = REFERENCE_BANDWIDTH_MBPS / inputs.bandwidth_mbps

    cache_factor = 1.0 + inputs.cache_pressure

    denominator = resource_cost_mb * bandwidth_factor * cache_factor

    score = expected_benefit_ms / denominator

    explanation = (
        f"expected_benefit={expected_benefit_ms:.3f}ms; "
        f"resource_cost={resource_cost_mb:.3f}MB; "
        f"bandwidth_factor={bandwidth_factor:.3f}; "
        f"cache_factor={cache_factor:.3f}"
    )

    return PolicyScore(
        score=score,
        expected_benefit_ms=expected_benefit_ms,
        resource_cost_mb=resource_cost_mb,
        bandwidth_factor=bandwidth_factor,
        cache_factor=cache_factor,
        explanation=explanation,
    )
