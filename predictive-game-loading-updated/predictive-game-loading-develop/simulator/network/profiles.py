from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkProfile:
    name: str
    bandwidth_mbps: float
    latency_ms: float


NETWORK_PROFILES: dict[str, NetworkProfile] = {
    "fast": NetworkProfile(
        name="fast",
        bandwidth_mbps=100.0,
        latency_ms=20.0,
    ),
    "medium": NetworkProfile(
        name="medium",
        bandwidth_mbps=20.0,
        latency_ms=80.0,
    ),
    "slow": NetworkProfile(
        name="slow",
        bandwidth_mbps=5.0,
        latency_ms=200.0,
    ),
}
