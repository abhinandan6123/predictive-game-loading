from dataclasses import dataclass
from enum import StrEnum


class PrefetchAction(StrEnum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    SKIP = "SKIP"


@dataclass(frozen=True)
class PolicyInputs:
    probability: float
    latency_benefit_ms: float
    resource_cost_bytes: int
    bandwidth_mbps: float
    cache_pressure: float


@dataclass(frozen=True)
class PolicyScore:
    score: float
    expected_benefit_ms: float
    resource_cost_mb: float
    bandwidth_factor: float
    cache_factor: float
    explanation: str


@dataclass(frozen=True)
class PolicyConfig:
    full_threshold: float = 1.0
    partial_threshold: float = 0.25
    partial_fraction: float = 0.5


@dataclass(frozen=True)
class PrefetchDecision:
    action: PrefetchAction
    score: float
    fraction: float
    explanation: str
