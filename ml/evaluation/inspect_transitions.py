from ml.features.transitions import extract_transitions, transition_counts
from simulator.sessions.generator import generate_sessions


def main() -> None:
    sessions = generate_sessions(
        count=10_000,
        seed=42,
    )

    transitions = extract_transitions(sessions)
    counts = transition_counts(transitions)

    print(f"Sessions: {len(sessions)}")
    print(f"Transitions: {len(transitions)}")
    print()

    for source_game in sorted(counts):
        print(f"{source_game}:")
        total = sum(counts[source_game].values())

        for target_game, count in counts[source_game].most_common():
            probability = count / total

            print(f"  {target_game}: {count:5d} ({probability:.3f})")

        print()


if __name__ == "__main__":
    main()
