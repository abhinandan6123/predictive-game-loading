from ml.features.transitions import extract_transitions, transition_counts

from simulator.sessions.generator import generate_sessions


def test_transitions_are_extracted() -> None:
    sessions = generate_sessions(20, seed=42)

    transitions = extract_transitions(sessions)

    assert transitions


def test_transition_counts_are_positive() -> None:
    sessions = generate_sessions(20, seed=42)
    transitions = extract_transitions(sessions)
    counts = transition_counts(transitions)

    assert counts

    for source_counts in counts.values():
        assert all(count > 0 for count in source_counts.values())
