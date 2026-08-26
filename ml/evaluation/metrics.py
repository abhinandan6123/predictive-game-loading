import numpy as np


def recall_at_k(predictions: list[list[str]], targets: list[str]) -> float:
    """Calculates Recall@K. Does the target appear in the top-K predictions?"""
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets must have equal length.")
    if not targets:
        return 0.0

    hits = sum(target in predicted for predicted, target in zip(predictions, targets, strict=True))
    return hits / len(targets)


def precision_at_k(predictions: list[list[str]], targets: list[str], k: int) -> float:
    """Calculates Precision@K. What fraction of the top-K predictions is the target?"""
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets must have equal length.")
    if not targets or k == 0:
        return 0.0

    # Since there's only 1 target per row, precision is just 1/k if it's a hit, 0 otherwise
    hits = sum(
        target in predicted[:k] for predicted, target in zip(predictions, targets, strict=True)
    )
    return hits / (len(targets) * k)


def mean_reciprocal_rank(predictions: list[list[str]], targets: list[str]) -> float:
    """Calculates MRR: Mean of 1 / rank (where rank is 1-indexed)."""
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets must have equal length.")
    if not targets:
        return 0.0

    reciprocal_ranks = []
    for predicted, target in zip(predictions, targets, strict=True):
        try:
            # list.index is 0-indexed, so rank is index + 1
            rank = predicted.index(target) + 1
            reciprocal_ranks.append(1.0 / rank)
        except ValueError:
            reciprocal_ranks.append(0.0)

    return sum(reciprocal_ranks) / len(targets)


def expected_calibration_error(
    probabilities: list[float], targets: list[str], top_predicted_games: list[str], n_bins: int = 10
) -> float:
    """Calculates Expected Calibration Error (ECE)."""
    if not targets:
        return 0.0

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    binned_indices = np.digitize(probabilities, bins) - 1

    ece = 0.0
    total_samples = len(probabilities)

    for i in range(n_bins):
        bin_samples = np.where(binned_indices == i)[0]
        if len(bin_samples) == 0:
            continue

        bin_probs = np.array(probabilities)[bin_samples]
        bin_targets = np.array(targets)[bin_samples]
        bin_preds = np.array(top_predicted_games)[bin_samples]

        # Empirical accuracy of this bin
        bin_acc = np.mean(bin_targets == bin_preds)
        # Average predicted probability of this bin
        bin_conf = np.mean(bin_probs)

        weight = len(bin_samples) / total_samples
        ece += weight * np.abs(bin_acc - bin_conf)

    return ece
