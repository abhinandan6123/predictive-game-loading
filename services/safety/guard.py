from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str


class ResponsiblePlayGuard:
    """
    Independent responsible-play policy guard.

    The guard is intentionally separate from prediction, policy scoring,
    caching, loading, and execution so that a safety decision cannot be
    bypassed by the optimization pipeline.
    """

    def evaluate(
        self,
        *,
        responsible_play_allowed: bool = True,
        restricted_session: bool = False,
        safety_block: bool = False,
    ) -> SafetyDecision:
        if safety_block:
            return SafetyDecision(
                allowed=False,
                reason="responsible-play restriction active",
            )

        if restricted_session:
            return SafetyDecision(
                allowed=False,
                reason="restricted session",
            )

        if not responsible_play_allowed:
            return SafetyDecision(
                allowed=False,
                reason="responsible-play permission denied",
            )

        return SafetyDecision(
            allowed=True,
            reason="responsible-play policy allows prefetch",
        )

    def allow(
        self,
        *,
        responsible_play_allowed: bool = True,
        restricted_session: bool = False,
        safety_block: bool = False,
    ) -> bool:
        return self.evaluate(
            responsible_play_allowed=responsible_play_allowed,
            restricted_session=restricted_session,
            safety_block=safety_block,
        ).allowed
