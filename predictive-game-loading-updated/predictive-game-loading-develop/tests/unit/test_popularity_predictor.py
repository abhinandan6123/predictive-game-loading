import pytest

from ml.baselines.popularity import PopularityPredictor


def test_popularity_predictor_returns_most_frequent_games() -> None:
    predictor = PopularityPredictor()

    predictor.fit(
        [
            "game_01",
            "game_02",
            "game_02",
            "game_03",
            "game_03",
            "game_03",
        ]
    )

    assert predictor.predict_top_k(2) == [
        "game_03",
        "game_02",
    ]


def test_popularity_rejects_empty_training_data() -> None:
    predictor = PopularityPredictor()

    with pytest.raises(ValueError):
        predictor.fit([])


def test_popularity_rejects_invalid_k() -> None:
    predictor = PopularityPredictor()
    predictor.fit(["game_01"])

    with pytest.raises(ValueError):
        predictor.predict_top_k(0)
