"""Contextual feature extraction module."""

from __future__ import annotations

from typing import Any


def extract_contextual_features(sessions: list[Any]) -> list[dict[str, Any]]:
    """Extracts contextual transition features from session events."""
    features: list[dict[str, Any]] = []

    for session in sessions:
        games: list[str] = []
        if hasattr(session, "events"):
            for ev in session.events:
                game_id = getattr(ev, "game_id", None)
                if game_id:
                    games.append(game_id)
        elif hasattr(session, "games"):
            games = list(session.games)

        if len(games) < 2:
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