"""Contextual feature extraction module."""

from __future__ import annotations

from typing import Any


def extract_contextual_features(sessions: list[Any]) -> list[dict[str, Any]]:
    """Extracts comprehensive contextual transition features from session events."""
    features: list[dict[str, Any]] = []

    for session in sessions:
        events_list: list[Any] = []
        games: list[str] = []
        timestamps: list[float] = []

        if hasattr(session, "events"):
            for ev in session.events:
                game_id = getattr(ev, "game_id", None)
                if game_id:
                    games.append(str(game_id))
                    events_list.append(ev)
                    timestamps.append(float(getattr(ev, "timestamp_ms", 0.0)))
        elif hasattr(session, "games"):
            games = [str(g) for g in session.games]
            timestamps = [0.0] * len(games)

        if len(games) < 2:
            continue

        total_len = len(games)
        session_id = str(getattr(session, "session_id", ""))
        user_id = str(getattr(session, "user_id", ""))

        for i in range(total_len - 1):
            unique_so_far = len(set(games[: i + 1]))
            switch_rate = float(unique_so_far / (i + 1))
            session_pos = float(i / (total_len - 1)) if total_len > 1 else 0.0

            time_delta = 0.0
            if len(timestamps) > i + 1 and timestamps[i + 1] >= timestamps[i]:
                time_delta = timestamps[i + 1] - timestamps[i]

            record: dict[str, Any] = {
                "session_id": session_id,
                "user_id": user_id,
                "current_game": games[i],
                "previous_game": "START" if i == 0 else games[i - 1],
                "target_game": games[i + 1],
                "next_game": games[i + 1],
                "position": i,
                "session_position": session_pos,
                "switch_rate": switch_rate,
                "time_since_last_launch_ms": time_delta,
                "session_len": total_len,
                "is_first": i == 0,
            }
            features.append(record)

    return features
