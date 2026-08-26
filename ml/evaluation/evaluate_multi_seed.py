"""Multi-seed evaluation pipeline with Recall@K, Precision@K, MRR, and Calibration (ECE)."""

from __future__ import annotations

import numpy as np

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import (
    expected_calibration_error,
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)
from ml.features.transitions import extract_transitions
from ml.prediction.transition_predictor import TransitionPredictor
from simulator.sessions.generator import generate_sessions


def evaluate_across_seeds(
    seeds: list[int] | None = None,
    session_count: int = 10000,
) -> dict[str, dict[str, float]]:
    if seeds is None:
        seeds = [42, 101, 2024, 7, 99]

    metrics_tracker: dict[str, list[float]] = {
        "popularity_recall@1": [],
        "transition_recall@1": [],
        "popularity_recall@3": [],
        "transition_recall@3": [],
        "popularity_precision@1": [],
        "transition_precision@1": [],
        "popularity_mrr": [],
        "transition_mrr": [],
        "popularity_ece": [],
        "transition_ece": [],
    }

    for seed in seeds:
        sessions = generate_sessions(count=session_count, seed=seed)
        transitions = extract_transitions(sessions)

        split_idx = int(len(transitions) * 0.8)
        train_data = transitions[:split_idx]
        test_data = transitions[split_idx:]

        train_targets = [t.target_game for t in train_data]
        test_targets = [t.target_game for t in test_data]

        pop_model = PopularityPredictor()
        pop_model.fit(train_targets)

        trans_model = TransitionPredictor()
        trans_model.fit(train_data)

        # Generate top-k predictions
        pop_preds_k1 = [pop_model.predict_top_k(1) for _ in test_data]
        pop_preds_k3 = [pop_model.predict_top_k(3) for _ in test_data]

        trans_preds_k1 = [trans_model.predict_top_k(t.source_game, 1) for t in test_data]
        trans_preds_k3 = [trans_model.predict_top_k(t.source_game, 3) for t in test_data]

        # Single top predictions & confidence for ECE
        pop_top_games = [p[0] if p else "" for p in pop_preds_k1]
        pop_top_probs = [pop_model.predict_probabilities().get(g, 0.0) for g in pop_top_games]

        trans_top_games = [p[0] if p else "" for p in trans_preds_k1]
        trans_top_probs = [
            trans_model.predict_probabilities(t.source_game).get(g, 0.0)
            for t, g in zip(test_data, trans_top_games, strict=True)
        ]

        # Recalls
        metrics_tracker["popularity_recall@1"].append(recall_at_k(pop_preds_k1, test_targets))
        metrics_tracker["transition_recall@1"].append(recall_at_k(trans_preds_k1, test_targets))
        metrics_tracker["popularity_recall@3"].append(recall_at_k(pop_preds_k3, test_targets))
        metrics_tracker["transition_recall@3"].append(recall_at_k(trans_preds_k3, test_targets))

        # Precisions
        metrics_tracker["popularity_precision@1"].append(
            precision_at_k(pop_preds_k1, test_targets, k=1)
        )
        metrics_tracker["transition_precision@1"].append(
            precision_at_k(trans_preds_k1, test_targets, k=1)
        )

        # MRR
        metrics_tracker["popularity_mrr"].append(mean_reciprocal_rank(pop_preds_k3, test_targets))
        metrics_tracker["transition_mrr"].append(mean_reciprocal_rank(trans_preds_k3, test_targets))

        # Calibration (ECE)
        metrics_tracker["popularity_ece"].append(
            expected_calibration_error(pop_top_probs, test_targets, pop_top_games)
        )
        metrics_tracker["transition_ece"].append(
            expected_calibration_error(trans_top_probs, test_targets, trans_top_games)
        )

    results = {}
    for metric_name, values in metrics_tracker.items():
        scale = 100.0 if "ece" not in metric_name else 1.0
        results[metric_name] = {
            "mean": float(np.mean(values) * scale),
            "std": float(np.std(values) * scale),
        }

    print("\n=======================================================")
    print("       MULTI-SEED EVALUATION RESULTS (5 SEEDS)        ")
    print("=======================================================")
    for metric, stats in results.items():
        unit = "%" if "ece" not in metric else ""
        print(f"{metric:25s}: {stats['mean']:.4f}{unit} (std: {stats['std']:.4f}{unit})")
    print("=======================================================\n")

    return results


if __name__ == "__main__":
    evaluate_across_seeds()
