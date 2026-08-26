"""
Unit tests for contextual feature extraction pipeline.
"""

from ml.features.contextual import compute_user_affinities, extract_contextual_features
from simulator.sessions.events import SessionEvent
from simulator.sessions.session import Session


def test_extract_contextual_features_structure() -> None:
    events = (
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_001",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=110.0,
            event_type="launch",
            game_id="game_002",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=120.0,
            event_type="launch",
            game_id="game_003",
        ),
    )
    session = Session(session_id="s1", user_id="u1", events=events)

    records = extract_contextual_features([session])
    assert len(records) == 2

    first_record = records[0]
    assert first_record["current_game"] == "game_001"
    assert first_record["previous_game"] == "START"
    assert first_record["target_game"] == "game_002"
    assert first_record["recent_game_history"] == ()
    assert first_record["game_category"] == "action"
    assert 0.0 <= first_record["session_position"] <= 1.0
    assert 0.0 <= first_record["user_affinity"] <= 1.0
    assert 0.0 <= first_record["exploration_rate"] <= 1.0
    assert 0.0 <= first_record["switch_rate"] <= 1.0

    second_record = records[1]
    assert second_record["current_game"] == "game_002"
    assert second_record["previous_game"] == "game_001"
    assert second_record["target_game"] == "game_003"
    assert second_record["recent_game_history"] == ("game_001",)


def test_compute_user_affinities() -> None:
    events = (
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_001",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=110.0,
            event_type="launch",
            game_id="game_001",
        ),
        SessionEvent(
            session_id="s1",
            user_id="u1",
            timestamp_ms=120.0,
            event_type="launch",
            game_id="game_002",
        ),
    )
    session = Session(session_id="s1", user_id="u1", events=events)
    affinities = compute_user_affinities([session])

    assert "u1" in affinities
    assert round(affinities["u1"]["game_001"], 2) == 0.67
    assert round(affinities["u1"]["game_002"], 2) == 0.33


def test_extract_contextual_features_short_session() -> None:
    events = (
        SessionEvent(
            session_id="s2",
            user_id="u2",
            timestamp_ms=100.0,
            event_type="launch",
            game_id="game_001",
        ),
    )
    session = Session(session_id="s2", user_id="u2", events=events)
    records = extract_contextual_features([session])
    assert len(records) == 0
