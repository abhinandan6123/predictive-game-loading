"""
Unit tests for contextual feature extraction pipeline.
"""

from ml.features.contextual import extract_contextual_features
from simulator.sessions.events import SessionEvent
from simulator.sessions.session import Session


def test_extract_contextual_features_structure() -> None:
    events = (
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_01",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=110.0,
            event_type="launch",
            game_id="game_02",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=120.0,
            event_type="launch",
            game_id="game_03",
        ),
    )
    session = Session(session_id="s1", user_id="u1", events=events)

    records = extract_contextual_features([session])
    assert len(records) == 2

    first_record = records[0]
    assert first_record["current_game"] == "game_01"
    assert first_record["previous_game"] == "START"
    assert first_record["target_game"] == "game_02"
    assert 0.0 <= first_record["session_position"] <= 1.0
    assert 0.0 <= first_record["switch_rate"] <= 1.0


def test_extract_contextual_features_short_session() -> None:
    events = (
        SessionEvent(
            session_id="s2",
            user_id="u2",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_01",
        ),
    )
    session = Session(session_id="s2", user_id="u2", events=events)
    records = extract_contextual_features([session])
    assert len(records) == 0
