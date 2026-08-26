from dataclasses import dataclass

from services.cache import CacheHierarchy
from services.policy.decision import make_prefetch_decision
from services.policy.models import PolicyScore
from services.prefetch import ExecutionStatus, PrefetchExecutor
from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES
from simulator.scenarios.baseline import simulate_baseline_load

DEMO_CURRENT_GAME = "game_001"
DEMO_TARGET_GAME = "game_002"
DEMO_NETWORK = "medium"
DEMO_PROBABILITY = 0.90
DEMO_LATENCY_BENEFIT_MS = 1500.0
DEMO_CACHE_PRESSURE = 0.10


@dataclass(frozen=True)
class DemoResult:
    scenario: str
    network: str
    baseline_playable_ms: float
    baseline_total_ms: float
    predicted_game_id: str
    probability: float
    action: str
    fraction: float
    execution_status: str
    requested_bytes: int
    loaded_bytes: int
    cache_state: str | None
    cache_hit_on_repeat: bool
    repeat_loaded_bytes: int


def run_demo() -> DemoResult:
    current_game = GAME_CATALOG[DEMO_CURRENT_GAME]
    network = NETWORK_PROFILES[DEMO_NETWORK]

    baseline = simulate_baseline_load(current_game, network)

    target_game = GAME_CATALOG[DEMO_TARGET_GAME]

    resource_cost_mb = target_game.total_bytes / 1_000_000
    bandwidth_factor = min(network.bandwidth_mbps / 20.0, 1.0)
    cache_factor = 1.0 / (1.0 - DEMO_CACHE_PRESSURE)

    score = (
        DEMO_PROBABILITY
        * DEMO_LATENCY_BENEFIT_MS
        * bandwidth_factor
        * cache_factor
        / max(resource_cost_mb, 1.0)
    )

    policy_score = PolicyScore(
        score=score,
        expected_benefit_ms=DEMO_LATENCY_BENEFIT_MS,
        resource_cost_mb=resource_cost_mb,
        bandwidth_factor=bandwidth_factor,
        cache_factor=cache_factor,
        explanation=(
            f"demo_probability={DEMO_PROBABILITY:.3f}; "
            f"expected_benefit={DEMO_LATENCY_BENEFIT_MS:.3f}ms; "
            f"resource_cost={resource_cost_mb:.3f}MB"
        ),
    )

    decision = make_prefetch_decision(policy_score)

    cache = CacheHierarchy(
        critical_capacity_bytes=100_000_000,
        core_capacity_bytes=100_000_000,
        secondary_capacity_bytes=200_000_000,
    )
    executor = PrefetchExecutor(cache=cache, catalog=GAME_CATALOG)

    first = executor.execute(DEMO_TARGET_GAME, decision)
    second = executor.execute(DEMO_TARGET_GAME, decision)

    return DemoResult(
        scenario=f"{DEMO_CURRENT_GAME} -> {DEMO_TARGET_GAME}",
        network=network.name,
        baseline_playable_ms=baseline.playable_ms,
        baseline_total_ms=baseline.total_load_ms,
        predicted_game_id=DEMO_TARGET_GAME,
        probability=DEMO_PROBABILITY,
        action=decision.action.value,
        fraction=decision.fraction,
        execution_status=first.status.value,
        requested_bytes=first.requested_bytes,
        loaded_bytes=first.loaded_bytes,
        cache_state=first.cache_state.value if first.cache_state else None,
        cache_hit_on_repeat=second.status is ExecutionStatus.CACHE_HIT,
        repeat_loaded_bytes=second.loaded_bytes,
    )


def main() -> None:
    result = run_demo()

    print("=" * 64)
    print("PulseLoad Baseline vs PulseLoad Demo")
    print("=" * 64)
    print()
    print(f"Scenario: {result.scenario}")
    print(f"Network:  {result.network}")
    print()
    print("BASELINE")
    print(f"  playable_ms: {result.baseline_playable_ms:.2f}")
    print(f"  total_ms:    {result.baseline_total_ms:.2f}")
    print()
    print("PULSELOAD")
    print(f"  predicted_game: {result.predicted_game_id}")
    print(f"  probability:    {result.probability:.2f}")
    print(f"  policy:         {result.action}")
    print(f"  fraction:       {result.fraction:.2f}")
    print(f"  status:         {result.execution_status}")
    print(f"  requested_bytes:{result.requested_bytes}")
    print(f"  loaded_bytes:   {result.loaded_bytes}")
    print(f"  cache_state:    {result.cache_state}")
    print(f"  repeat_cache_hit:{result.cache_hit_on_repeat}")
    print(f"  repeat_loaded_bytes:{result.repeat_loaded_bytes}")
    print()
    print("COMPARISON")
    print(f"  baseline_playable_ms: {result.baseline_playable_ms:.2f}")
    print("  PulseLoad: deterministic demo transition through real policy/executor")
    print()
    print("Note: the demo transition is deterministic because the runtime")
    print("TransitionPredictor requires fitted transition examples.")
    print("=" * 64)


if __name__ == "__main__":
    main()
