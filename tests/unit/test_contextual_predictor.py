"""Unit tests for ContextualPredictor model."""

import pytest

from ml.prediction.contextual_predictor import ContextualPredictor


def test_contextual_predictor_fit_and_predict() -> None:
    records = [
        {
            "current_game": "game_001",
            "target_game": "game_002",
            "game_category": "action",
            "user_affinity": 0.5,
            "exploration_rate": 0.2,
        },
        {
            "current_game": "game_001",
            "target_game": "game_002",
            "game_category": "action",
            "user_affinity": 0.5,
            "exploration_rate": 0.2,
        },
        {
            "current_game": "game_001",
            "target_game": "game_003",
            "game_category": "action",
            "user_affinity": 0.2,
            "exploration_rate": 0.5,
        },
    ]

    predictor = ContextualPredictor()
    predictor.fit(records)

    context = {
        "current_game": "game_001",
        "game_category": "action",
        "user_affinity": 0.5,
        "exploration_rate": 0.2,
    }

    top_1 = predictor.predict_top_k(context, k=1)
    assert top_1 == ["game_002"]

    top_2 = predictor.predict_top_k(context, k=2)
    assert len(top_2) == 2
    assert top_2[0] == "game_002"

    probs = predictor.predict_probabilities(context)
    assert "game_002" in probs
    assert probs["game_002"] > probs["game_003"]
    assert pytest.approx(sum(probs.values()), 0.01) == 1.0


def test_contextual_predictor_empty_fit_raises() -> None:
    predictor = ContextualPredictor()
    with pytest.raises(ValueError, match="feature_records must not be empty"):
        predictor.fit([])
