from ml.evaluation.metrics import (
    expected_calibration_error,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)


def test_recall_at_k():
    predictions = [["game_1", "game_2"], ["game_3", "game_4"]]
    targets = ["game_1", "game_5"]
    assert recall_at_k(predictions, targets) == 0.5


def test_precision_at_k():
    predictions = [["game_1", "game_2"], ["game_3", "game_4"]]
    targets = ["game_1", "game_5"]
    assert precision_at_k(predictions, targets, k=2) == 0.25


def test_mean_reciprocal_rank():
    predictions = [["game_1", "game_2"], ["game_2", "game_3"], ["game_1", "game_2"]]
    targets = ["game_1", "game_3", "game_99"]
    assert mean_reciprocal_rank(predictions, targets) == 0.5


def test_expected_calibration_error():
    probs = [0.8, 0.8, 0.2, 0.2]
    targets = ["game_1", "game_1", "game_2", "game_3"]
    preds = ["game_1", "game_1", "game_2", "game_2"]
    ece = expected_calibration_error(probs, targets, preds, n_bins=2)
    assert isinstance(ece, float)
    assert 0.0 <= ece <= 1.0
