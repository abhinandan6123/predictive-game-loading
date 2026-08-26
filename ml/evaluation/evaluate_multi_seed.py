"""Multi-seed evaluation pipeline comparing Popularity, Transition, and Contextual models."""

from __future__ import annotations

import numpy as np

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import recall_at_k
from ml.features.contextual import extract_contextual_features
from ml.features.transitions import extract_transitions
from ml.prediction.contextual_predictor import ContextualPredictor
from ml.prediction.transition_predictor import TransitionPredictor
from simulator.sessions.generator import generate_sessions


def evaluate_across_seeds(
    seeds: list[int] | None = None,
    session_count: int = 10000,
) -> dict[str, dict[str, float]]:
    if seeds is None:
        seeds = [42, 101, 2024, 7, 99]

    pop_r1_list: list[float] = []
    pop_r3_list: list[float] = []
    trans_r1_list: list[float] = []
    trans_r3_list: list[float] = []
    ctx_r1_list: list[float] = []
    ctx_r3_list: list[float] = []

    for seed in seeds:
        sessions = generate_sessions(count=session_count, seed=seed)
        split_idx = int(len(sessions) * 0.8)
        train_sessions = sessions[:split_idx]
        test_sessions = sessions[split_idx:]

        train_trans = extract_transitions(train_sessions)
        test_trans = extract_transitions(test_sessions)
        train_ctx = extract_contextual_features(train_sessions)
        test_ctx = extract_contextual_features(test_sessions)

        test_targets = [t.target_game for t in test_trans]

        pop_model = PopularityPredictor()
        pop_model.fit([t.target_game for t in train_trans])

        trans_model = TransitionPredictor()
        trans_model.fit(train_trans)

        ctx_model = ContextualPredictor()
        ctx_model.fit(train_ctx)

        # Generate top-k predictions
        pop_preds_k1 = [pop_model.predict_top_k(1) for _ in test_trans]
        pop_preds_k3 = [pop_model.predict_top_k(3) for _ in test_trans]

        trans_preds_k1 = [trans_model.predict_top_k(t.source_game, 1) for t in test_trans]
        trans_preds_k3 = [trans_model.predict_top_k(t.source_game, 3) for t in test_trans]

        ctx_preds_k1 = [ctx_model.predict_top_k(ctx, 1) for ctx in test_ctx]
        ctx_preds_k3 = [ctx_model.predict_top_k(ctx, 3) for ctx in test_ctx]

        pop_r1_list.append(recall_at_k(pop_preds_k1, test_targets))
        pop_r3_list.append(recall_at_k(pop_preds_k3, test_targets))
        trans_r1_list.append(recall_at_k(trans_preds_k1, test_targets))
        trans_r3_list.append(recall_at_k(trans_preds_k3, test_targets))
        ctx_r1_list.append(recall_at_k(ctx_preds_k1, test_targets))
        ctx_r3_list.append(recall_at_k(ctx_preds_k3, test_targets))

    results = {
        "popularity_recall@1": {
            "mean": float(np.mean(pop_r1_list) * 100),
            "std": float(np.std(pop_r1_list) * 100),
        },
        "transition_recall@1": {
            "mean": float(np.mean(trans_r1_list) * 100),
            "std": float(np.std(trans_r1_list) * 100),
        },
        "contextual_recall@1": {
            "mean": float(np.mean(ctx_r1_list) * 100),
            "std": float(np.std(ctx_r1_list) * 100),
        },
        "popularity_recall@3": {
            "mean": float(np.mean(pop_r3_list) * 100),
            "std": float(np.std(pop_r3_list) * 100),
        },
        "transition_recall@3": {
            "mean": float(np.mean(trans_r3_list) * 100),
            "std": float(np.std(trans_r3_list) * 100),
        },
        "contextual_recall@3": {
            "mean": float(np.mean(ctx_r3_list) * 100),
            "std": float(np.std(ctx_r3_list) * 100),
        },
    }

    print("\n--- Multi-Seed (5 Seeds) Evaluation Results ---")
    for metric, stats in results.items():
        print(f"{metric:25s}: {stats['mean']:.2f}% (std: {stats['std']:.2f}%)")

    return results


if __name__ == "__main__":
    evaluate_across_seeds()
