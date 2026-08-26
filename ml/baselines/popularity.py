from collections import Counter


class PopularityPredictor:
    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()

    def fit(self, targets: list[str]) -> None:
        if not targets:
            raise ValueError("targets must not be empty.")

        self._counts = Counter(targets)

    def predict_top_k(self, k: int) -> list[str]:
        if k < 1:
            raise ValueError("k must be at least 1.")

        return [game_id for game_id, _ in self._counts.most_common(k)]
