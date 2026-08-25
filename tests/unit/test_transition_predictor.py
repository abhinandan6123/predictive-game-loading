import pytest
from ml.features.transitions import TransitionExample

from ml.prediction.transition_predictor import TransitionPredictor


def test_transition_predictor_learns_transition_frequency() -> None:
    predictor = TransitionPredictor()

    predictor.fit(
        [
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_03"),
        ]
    )

    assert predictor.predict_top_k(
        source_game="game_01",
        k=2,
    ) == [
        "game_02",
        "game_03",
    ]


def test_unknown_source_returns_empty_prediction() -> None:
    predictor = TransitionPredictor()

    predictor.fit([TransitionExample("game_01", "game_02")])

    assert predictor.predict_top_k("game_05", 3) == []


def test_transition_predictor_rejects_empty_training_data() -> None:
    predictor = TransitionPredictor()

    with pytest.raises(ValueError):
        predictor.fit([])
