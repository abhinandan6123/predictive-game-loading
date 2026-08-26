from collections import Counter

from ml.features.transitions import TransitionExample, transition_counts


class TransitionPredictor:
    def __init__(self) -> None:
        self._counts: dict[str, Counter[str]] = {}

    def fit(
        self,
        examples: list[TransitionExample],
    ) -> None:
        if not examples:
            raise ValueError("examples must not be empty.")

        self._counts = transition_counts(examples)

    def predict_top_k(
        self,
        source_game: str,
        k: int,
    ) -> list[str]:
        if k < 1:
            raise ValueError("k must be at least 1.")

        counts = self._counts.get(source_game)

        if not counts:
            return []

        return [game_id for game_id, _ in counts.most_common(k)]

    def predict_probabilities(
        self,
        source_game: str,
    ) -> dict[str, float]:
        counts = self._counts.get(source_game)
        if not counts:
            return {}

        total = sum(counts.values())
        if total == 0:
            return {}

        return {game_id: count / total for game_id, count in counts.items()}
