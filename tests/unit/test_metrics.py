import pytest

from ml.evaluation.metrics import recall_at_k


def test_recall_at_k() -> None:
    predictions = [
        ["game_01", "game_02", "game_03"],
        ["game_04", "game_01", "game_02"],
        ["game_05"],
    ]

    targets = [
        "game_02",
        "game_03",
        "game_01",
    ]

    assert recall_at_k(predictions, targets) == pytest.approx(1 / 3)


def test_recall_at_k_requires_equal_lengths() -> None:
    with pytest.raises(ValueError):
        recall_at_k(
            [["game_01"]],
            [],
        )


def test_empty_targets_return_zero() -> None:
    assert recall_at_k([], []) == 0.0
