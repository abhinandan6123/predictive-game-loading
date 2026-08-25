"""
Contextual Feature Engineering Pipeline (PulseLoad)
Extracts session position, switch frequency, and lag transitions.
"""
from typing import Any


def extract_contextual_features(sessions: list[Any]) -> list[dict[str, Any]]:
    """
    Extracts contextual features from session sequences.

    Computed metrics:
    - current_game: Source game in transition
    - previous_game: Preceding game (lag-1)
    - session_position: Progress within the session (0.0 to 1.0)
    - switch_rate: Ratio of unique games explored to steps taken
    - target_game: The actual next game launched
    """
    records = []

    for session in sessions:
        events = getattr(session, "events", [])
        total_events = len(events)
        if total_events < 2:
            continue

        unique_seen_games = set()

        for idx in range(total_events - 1):
            curr_event = events[idx]
            target_event = events[idx + 1]

            curr_game = getattr(curr_event, "game_id", str(curr_event))
            target_game = getattr(target_event, "game_id", str(target_event))

            unique_seen_games.add(curr_game)

            prev_game = (
                getattr(events[idx - 1], "game_id", str(events[idx - 1]))
                if idx > 0
                else "START"
            )

            session_position = round((idx + 1) / total_events, 4)
            switch_rate = round(len(unique_seen_games) / (idx + 1), 4)

            records.append(
                {
                    "session_id": getattr(session, "session_id", "sim_session"),
                    "current_game": curr_game,
                    "previous_game": prev_game,
                    "session_position": session_position,
                    "switch_rate": switch_rate,
                    "target_game": target_game,
                }
            )

    return records