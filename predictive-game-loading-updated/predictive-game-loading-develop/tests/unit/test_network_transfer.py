from simulator.network.profiles import NETWORK_PROFILES
from simulator.network.transfer import transfer_time_ms


def test_transfer_time_increases_with_resource_size() -> None:
    network = NETWORK_PROFILES["fast"]

    small = transfer_time_ms(100_000, network)
    large = transfer_time_ms(1_000_000, network)

    assert large > small


def test_slow_network_is_slower_than_fast_network() -> None:
    resource_size = 1_000_000

    fast = transfer_time_ms(
        resource_size,
        NETWORK_PROFILES["fast"],
    )

    slow = transfer_time_ms(
        resource_size,
        NETWORK_PROFILES["slow"],
    )

    assert slow > fast
