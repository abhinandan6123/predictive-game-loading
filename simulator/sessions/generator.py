import random

from simulator.games.catalog import GAME_CATALOG
from simulator.sessions.behavior import choose_next_game, generate_behavior
from simulator.sessions.events import SessionEvent
from simulator.sessions.session import Session

GAME_IDS = list(GAME_CATALOG)


def generate_sessions(
    count: int,
    seed: int = 42,
    min_events: int = 3,
    max_events: int = 6,
) -> list[Session]:
    if count < 1:
        raise ValueError("count must be greater than zero.")

    if min_events < 2:
        raise ValueError("min_events must be at least 2.")

    if max_events < min_events:
        raise ValueError("max_events must be >= min_events.")

    rng = random.Random(seed)

    sessions: list[Session] = []

    for session_index in range(count):
        session_id = f"session_{session_index:05d}"
        user_id = f"user_{session_index % 100:03d}"

        behavior = generate_behavior(
            user_id=user_id,
            game_ids=GAME_IDS,
            rng=rng,
        )

        event_count = rng.randint(min_events, max_events)

        current_game = rng.choice(GAME_IDS)

        events: list[SessionEvent] = [
            SessionEvent(
                session_id=session_id,
                user_id=user_id,
                timestamp_ms=0,
                event_type="launch",
                game_id=current_game,
            )
        ]

        for event_index in range(1, event_count):
            current_game = choose_next_game(
                behavior=behavior,
                current_game=current_game,
                game_ids=GAME_IDS,
                rng=rng,
            )

            events.append(
                SessionEvent(
                    session_id=session_id,
                    user_id=user_id,
                    timestamp_ms=event_index * 1_000,
                    event_type="launch",
                    game_id=current_game,
                )
            )

        sessions.append(
            Session(
                session_id=session_id,
                user_id=user_id,
                events=tuple(events),
            )
        )

    return sessions
