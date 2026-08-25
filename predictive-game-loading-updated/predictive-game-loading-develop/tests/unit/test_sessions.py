import pytest

from simulator.sessions.generator import generate_sessions


def test_session_generation_is_deterministic() -> None:
    first = generate_sessions(10, seed=42)
    second = generate_sessions(10, seed=42)

    assert first == second


def test_different_seeds_produce_different_sessions() -> None:
    first = generate_sessions(10, seed=42)
    second = generate_sessions(10, seed=43)

    assert first != second


def test_session_generation_produces_requested_count() -> None:
    sessions = generate_sessions(25, seed=42)

    assert len(sessions) == 25


def test_sessions_have_multiple_launch_events() -> None:
    sessions = generate_sessions(10, seed=42)

    for session in sessions:
        assert len(session.events) >= 2
        assert all(event.event_type == "launch" for event in session.events)


@pytest.mark.parametrize(
    "count",
    [0, -1],
)
def test_invalid_session_count_is_rejected(count: int) -> None:
    with pytest.raises(ValueError):
        generate_sessions(count)
