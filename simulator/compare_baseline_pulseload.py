from services.loading.progressive import progressive_load
from simulator.games.catalog import GAME_CATALOG
from simulator.network.profiles import NETWORK_PROFILES
from simulator.network.transfer import transfer_time_ms
from simulator.scenarios.baseline import simulate_baseline_load


def main() -> None:
    for network in NETWORK_PROFILES.values():
        print(f"\n=== {network.name.upper()} NETWORK ===")

        for game in GAME_CATALOG.values():
            baseline = simulate_baseline_load(game, network)
            pulse = progressive_load(game)

            pulse_critical_ms = transfer_time_ms(
                pulse.critical_bytes,
                network,
            )

            pulse_playable_ms = transfer_time_ms(
                pulse.playable_bytes,
                network,
            )

            pulse_total_ms = transfer_time_ms(
                pulse.total_bytes,
                network,
            )

            print(f"\n{game.game_id}")
            print(
                f"  Baseline: "
                f"playable={baseline.playable_ms:.2f}ms, "
                f"total={baseline.total_load_ms:.2f}ms"
            )
            print(
                f"  PulseLoad: "
                f"critical={pulse_critical_ms:.2f}ms, "
                f"playable={pulse_playable_ms:.2f}ms, "
                f"total={pulse_total_ms:.2f}ms"
            )


if __name__ == "__main__":
    main()