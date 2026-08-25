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
                    games.append(str(game_id))
        elif hasattr(session, "games"):
            games = [str(g) for g in session.games]

        if len(games) < 2:
            continue

        total_len = len(games)
        session_id = getattr(session, "session_id", "")
        user_id = getattr(session, "user_id", "")

        for i in range(total_len - 1):
            features.append(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "current_game": games[i],
                    "previous_game": "START" if i == 0 else games[i - 1],
                    "target_game": games[i + 1],
                    "next_game": games[i + 1],
                    "position": i,
                    "session_position": float(i / (total_len - 1)) if total_len > 1 else 0.0,
                    "session_len": total_len,
                    "is_first": i == 0,
                }
            )

    return features
