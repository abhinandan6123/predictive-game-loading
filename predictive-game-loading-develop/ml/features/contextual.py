"""Contextual feature extraction module.

Extracts session position, switch frequency, and lag transitions.
"""

from __future__ import annotations

from typing import Any


def extract_contextual_features(sessions: list[Any]) -> list[dict[str, Any]]:
    """Extracts contextual features from session sequences."""
    features: list[dict[str, Any]] = []

    for session in sessions:
        games = getattr(session, "game_ids", getattr(session, "games", []))
        if not games or len(games) < 2:
            continue

        for i in range(len(games) - 1):
            features.append(
                {
                    "prev_game": games[i],
                    "target_game": games[i + 1],
                    "position": i,
                    "session_len": len(games),
                    "is_first": i == 0,
                }
            )

    return features