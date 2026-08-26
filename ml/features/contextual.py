"""Contextual feature extraction module."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from simulator.games.catalog import GAME_CATALOG


def compute_user_affinities(sessions: list[Any]) -> dict[str, dict[str, float]]:
    """Computes normalized play frequency (affinity) for each user and game."""
    user_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for session in sessions:
        user_id = str(getattr(session, "user_id", ""))
        if not user_id:
            continue

        games: list[str] = []
        if hasattr(session, "events"):
            for ev in session.events:
                gid = getattr(ev, "game_id", None)
                if gid:
                    games.append(str(gid))
        elif hasattr(session, "games"):
            games = [str(g) for g in session.games]

        for g in games:
            user_counts[user_id][g] += 1

    user_affinities: dict[str, dict[str, float]] = {}
    for uid, counter in user_counts.items():
        total = sum(counter.values())
        user_affinities[uid] = (
            {gid: count / total for gid, count in counter.items()} if total > 0 else {}
        )

    return user_affinities


def extract_contextual_features(
    sessions: list[Any],
    catalog: dict[str, Any] | None = None,
    history_window: int = 3,
) -> list[dict[str, Any]]:
    """Extracts comprehensive contextual transition features from session events."""
    if catalog is None:
        catalog = GAME_CATALOG

    user_affinities = compute_user_affinities(sessions)
    features: list[dict[str, Any]] = []

    for session in sessions:
        games: list[str] = []
        timestamps: list[float] = []

        if hasattr(session, "events"):
            for ev in session.events:
                game_id = getattr(ev, "game_id", None)
                if game_id:
                    games.append(str(game_id))
                    timestamps.append(float(getattr(ev, "timestamp_ms", 0.0)))
        elif hasattr(session, "games"):
            games = [str(g) for g in session.games]
            timestamps = [0.0] * len(games)

        if len(games) < 2:
            continue

        total_len = len(games)
        session_id = str(getattr(session, "session_id", ""))
        user_id = str(getattr(session, "user_id", ""))
        u_aff = user_affinities.get(user_id, {})

        for i in range(total_len - 1):
            curr_game = games[i]
            prev_game = "START" if i == 0 else games[i - 1]
            target_game = games[i + 1]

            unique_so_far = len(set(games[: i + 1]))
            exploration_rate = float(unique_so_far / (i + 1))
            switch_rate = exploration_rate
            session_pos = float(i / (total_len - 1)) if total_len > 1 else 0.0

            start_hist = max(0, i - history_window)
            recent_game_history = tuple(games[start_hist:i])

            game_obj = catalog.get(curr_game)
            game_category = getattr(game_obj, "category", "unknown") if game_obj else "unknown"

            user_affinity = float(u_aff.get(curr_game, 0.0))

            time_delta = 0.0
            if len(timestamps) > i + 1 and timestamps[i + 1] >= timestamps[i]:
                time_delta = timestamps[i + 1] - timestamps[i]

            record: dict[str, Any] = {
                "session_id": session_id,
                "user_id": user_id,
                "current_game": curr_game,
                "previous_game": prev_game,
                "target_game": target_game,
                "next_game": target_game,
                "position": i,
                "session_position": session_pos,
                "recent_game_history": recent_game_history,
                "game_category": game_category,
                "user_affinity": user_affinity,
                "exploration_rate": exploration_rate,
                "switch_rate": switch_rate,
                "time_since_last_launch_ms": time_delta,
                "session_len": total_len,
                "is_first": i == 0,
            }
            features.append(record)

    return features
