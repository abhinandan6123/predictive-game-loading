"""Contextual probabilistic game transition predictor."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


class ContextualPredictor:
    """Predicts next-game transitions leveraging contextual, behavioral, and user signals."""

    def __init__(self, alpha: float = 0.5, beta: float = 0.3, gamma: float = 0.2) -> None:
        """Initializes weights for transition, user affinity, and global popularity priors."""
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self._transition_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._category_transitions: dict[str, Counter[str]] = defaultdict(Counter)
        self._global_counts: Counter[str] = Counter()
        self._total_transitions: int = 0

    def fit(self, feature_records: list[dict[str, Any]]) -> None:
        """Fits transition distributions and contextual priors from extracted feature records."""
        if not feature_records:
            raise ValueError("feature_records must not be empty.")

        self._transition_counts.clear()
        self._category_transitions.clear()
        self._global_counts.clear()
        self._total_transitions = len(feature_records)

        for rec in feature_records:
            curr_game = str(rec.get("current_game", ""))
            target_game = str(rec.get("target_game", rec.get("next_game", "")))
            cat = str(rec.get("game_category", "unknown"))

            if not curr_game or not target_game:
                continue

            self._transition_counts[curr_game][target_game] += 1
            self._category_transitions[cat][target_game] += 1
            self._global_counts[target_game] += 1

    def predict_probabilities(
        self,
        context: dict[str, Any] | str,
    ) -> dict[str, float]:
        """Calculates normalized posterior probabilities across candidate games."""
        if isinstance(context, str):
            curr_game = context
            game_category = "unknown"
            user_affinity = 0.0
            exploration_rate = 0.5
        else:
            curr_game = str(context.get("current_game", ""))
            game_category = str(context.get("game_category", "unknown"))
            user_affinity = float(context.get("user_affinity", 0.0))
            exploration_rate = float(context.get("exploration_rate", 0.5))

        if not curr_game or self._total_transitions == 0:
            return {}

        candidate_scores: defaultdict[str, float] = defaultdict(float)

        # 1. Markov Transition Probability
        curr_counts = self._transition_counts.get(curr_game, Counter())
        curr_total = sum(curr_counts.values())
        if curr_total > 0:
            for g, count in curr_counts.items():
                candidate_scores[g] += self.alpha * (count / curr_total)

        # 2. Category Transition Prior
        cat_counts = self._category_transitions.get(game_category, Counter())
        cat_total = sum(cat_counts.values())
        if cat_total > 0:
            for g, count in cat_counts.items():
                candidate_scores[g] += self.beta * (count / cat_total)

        # 3. Global Popularity Fallback
        global_total = sum(self._global_counts.values())
        if global_total > 0:
            for g, count in self._global_counts.items():
                candidate_scores[g] += self.gamma * (count / global_total)

        # 4. Contextual Modulation (User Affinity & Exploration adjustments)
        if user_affinity > 0 and curr_game in candidate_scores:
            candidate_scores[curr_game] *= (1.0 + user_affinity)

        if exploration_rate > 0.7:
            for g in candidate_scores:
                if g not in curr_counts:
                    candidate_scores[g] *= 1.2

        total_score = sum(candidate_scores.values())
        if total_score == 0:
            return {}

        return {g: score / total_score for g, score in candidate_scores.items()}

    def predict_top_k(
        self,
        context: dict[str, Any] | str,
        k: int = 3,
    ) -> list[str]:
        """Returns the top-K highest-probability next games."""
        if k < 1:
            raise ValueError("k must be at least 1.")

        probs = self.predict_probabilities(context)
        if not probs:
            return []

        sorted_games = sorted(probs.items(), key=lambda item: item[1], reverse=True)
        return [game for game, _ in sorted_games[:k]]
