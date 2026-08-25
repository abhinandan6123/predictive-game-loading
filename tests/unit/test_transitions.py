from ml.features.transitions import extract_transitions, transition_counts
from simulator.sessions.generator import Session


def test_extract_transitions() -> None:
    sessions = [
        Session(session_id="s1", games=["game_a", "game_b", "game_c"]),
    ]
    transitions = extract_transitions(sessions)

    assert len(transitions) == 2
    assert transitions[0].prev_game == "game_a"
    assert transitions[0].next_game == "game_b"
    assert transitions[1].prev_game == "game_b"
    assert transitions[1].next_game == "game_c"


def test_transition_counts() -> None:
    sessions = [
        Session(session_id="s1", games=["game_a", "game_b"]),
        Session(session_id="s2", games=["game_a", "game_b"]),
    ]
    transitions = extract_transitions(sessions)
    counts = transition_counts(transitions)

    assert counts[("game_a", "game_b")] == 2
