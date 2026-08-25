def recall_at_k(
    predictions: list[list[str]],
    targets: list[str],
) -> float:
    if len(predictions) != len(targets):
        raise ValueError("predictions and targets must have equal length.")

    if not targets:
        return 0.0

    hits = sum(target in predicted for predicted, target in zip(predictions, targets, strict=True))

    return hits / len(targets)
