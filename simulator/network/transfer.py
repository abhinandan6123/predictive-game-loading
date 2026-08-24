from simulator.network.profiles import NetworkProfile


def transfer_time_ms(
    resource_bytes: int,
    network: NetworkProfile,
) -> float:
    bits = resource_bytes * 8
    bandwidth_bits_per_second = network.bandwidth_mbps * 1_000_000

    transfer_seconds = bits / bandwidth_bits_per_second

    return network.latency_ms + (transfer_seconds * 1000)
