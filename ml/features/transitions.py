from collections import Counter
from dataclasses import dataclass

from simulator.sessions.session import Session


@dataclass(frozen=True)
class TransitionExample:
    source_game: str
    target_game: str


def extract_transitions(
    sessions: list[Session],
) -> list[TransitionExample]:
    examples: list[TransitionExample] = []

    for session in sessions:
        launches = [event.game_id for event in session.events if event.event_type == "launch"]

        for index in range(len(launches) - 1):
            examples.append(
                TransitionExample(
                    source_game=launches[index],
                    target_game=launches[index + 1],
                )
            )

    return examples


def transition_counts(
    examples: list[TransitionExample],
) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = {}

    for example in examples:
        counts.setdefault(example.source_game, Counter())
        counts[example.source_game][example.target_game] += 1

    return counts
