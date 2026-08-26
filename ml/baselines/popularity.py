from collections import Counter


class PopularityPredictor:
    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._total_counts: int = 0

    def fit(self, targets: list[str]) -> None:
        if not targets:
            raise ValueError("targets must not be empty.")

        self._counts = Counter(targets)
        self._total_counts = sum(self._counts.values())

    def predict_top_k(self, k: int) -> list[str]:
        if k < 1:
            raise ValueError("k must be at least 1.")

        return [game_id for game_id, _ in self._counts.most_common(k)]

    def predict_probabilities(self) -> dict[str, float]:
        """Returns the global empirical probability distribution across all games."""
        if self._total_counts == 0:
            return {}

        return {game_id: count / self._total_counts for game_id, count in self._counts.items()}
