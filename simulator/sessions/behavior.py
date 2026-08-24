import random
from dataclasses import dataclass


@dataclass(frozen=True)
class UserBehavior:
    user_id: str
    primary_game: str
    secondary_game: str
    exploration_rate: float
    switch_rate: float


def generate_behavior(
    user_id: str,
    game_ids: list[str],
    rng: random.Random,
) -> UserBehavior:
    if len(game_ids) < 2:
        raise ValueError("At least two games are required.")

    primary_game = rng.choice(game_ids)

    secondary_candidates = [game_id for game_id in game_ids if game_id != primary_game]

    secondary_game = rng.choice(secondary_candidates)

    exploration_rate = rng.uniform(0.05, 0.25)
    switch_rate = rng.uniform(0.20, 0.60)

    return UserBehavior(
        user_id=user_id,
        primary_game=primary_game,
        secondary_game=secondary_game,
        exploration_rate=exploration_rate,
        switch_rate=switch_rate,
    )


def choose_next_game(
    behavior: UserBehavior,
    current_game: str,
    game_ids: list[str],
    rng: random.Random,
) -> str:
    roll = rng.random()

    if roll < behavior.exploration_rate:
        candidates = [
            game_id
            for game_id in game_ids
            if game_id
            not in {
                behavior.primary_game,
                behavior.secondary_game,
                current_game,
            }
        ]

        if candidates:
            return rng.choice(candidates)

    if current_game == behavior.primary_game:
        if rng.random() > behavior.switch_rate:
            return current_game

        return behavior.secondary_game

    if current_game == behavior.secondary_game:
        if rng.random() > behavior.switch_rate:
            return current_game

        return behavior.primary_game

    preference_roll = rng.random()

    if preference_roll < 0.70:
        return behavior.primary_game

    return behavior.secondary_game
