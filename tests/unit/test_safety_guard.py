from services.safety import ResponsiblePlayGuard


def test_allows_normal_responsible_play_session() -> None:
    guard = ResponsiblePlayGuard()

    decision = guard.evaluate()

    assert decision.allowed is True
    assert "allows" in decision.reason


def test_blocks_explicit_safety_block() -> None:
    guard = ResponsiblePlayGuard()

    decision = guard.evaluate(safety_block=True)

    assert decision.allowed is False
    assert decision.reason == "responsible-play restriction active"


def test_blocks_restricted_session() -> None:
    guard = ResponsiblePlayGuard()

    decision = guard.evaluate(restricted_session=True)

    assert decision.allowed is False
    assert decision.reason == "restricted session"


def test_blocks_when_permission_denied() -> None:
    guard = ResponsiblePlayGuard()

    decision = guard.evaluate(responsible_play_allowed=False)

    assert decision.allowed is False
    assert decision.reason == "responsible-play permission denied"


def test_allow_returns_boolean_only() -> None:
    guard = ResponsiblePlayGuard()

    assert guard.allow() is True
    assert guard.allow(safety_block=True) is False
