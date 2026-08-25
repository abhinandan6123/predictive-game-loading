"""Unit tests for transition feature extraction and counts."""

from __future__ import annotations

from ml.features.transitions import extract_transitions, transition_counts
from simulator.sessions.generator import Session, SessionEvent


def test_extract_transitions() -> None:
    events = (
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_a",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=110.0,
            event_type="launch",
            game_id="game_b",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=120.0,
            event_type="launch",
            game_id="game_c",
        ),
    )
    sessions = [Session(session_id="s1", user_id="u1", events=events)]
    transitions = extract_transitions(sessions)

    assert len(transitions) == 2
    assert transitions[0].prev_game == "game_a"
    assert transitions[0].next_game == "game_b"
    assert transitions[1].prev_game == "game_b"
    assert transitions[1].next_game == "game_c"


def test_transition_counts() -> None:
    events1 = (
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_a",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=110.0,
            event_type="launch",
            game_id="game_b",
        ),
    )
    events2 = (
        SessionEvent(
            session_id="s2",
            user_id="u2",
            timestamp_ms=200.0,
            event_type="launch",
            game_id="game_a",
        ),
        SessionEvent(
            session_id="s2",
            user_id="u2",
            timestamp_ms=210.0,
            event_type="launch",
            game_id="game_b",
        ),
    )
    sessions = [
        Session(session_id="s1", user_id="u1", events=events1),
        Session(session_id="s2", user_id="u2", events=events2),
    ]
    transitions = extract_transitions(sessions)
    counts = transition_counts(transitions)

    assert counts[("game_a", "game_b")] == 2
