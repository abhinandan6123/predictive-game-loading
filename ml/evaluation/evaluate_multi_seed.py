"""Multi-seed evaluation pipeline for transition predictions."""

from __future__ import annotations

import numpy as np

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import recall_at_k
from ml.features.transitions import extract_transitions
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

    for seed in seeds:
        sessions = generate_sessions(n_sessions=session_count, seed=seed)
        transitions = extract_transitions(sessions)

        split_idx = int(len(transitions) * 0.8)
        train_data = transitions[:split_idx]
        test_data = transitions[split_idx:]

        pop_model = PopularityPredictor()
        pop_model.fit(train_data)
        trans_model = TransitionPredictor()
        trans_model.fit(train_data)

        pop_r1_list.append(recall_at_k(pop_model, test_data, k=1))
        pop_r3_list.append(recall_at_k(pop_model, test_data, k=3))
        trans_r1_list.append(recall_at_k(trans_model, test_data, k=1))
        trans_r3_list.append(recall_at_k(trans_model, test_data, k=3))

    pop_r1_m, pop_r1_s = float(np.mean(pop_r1_list) * 100), float(np.std(pop_r1_list) * 100)
    trans_r1_m, trans_r1_s = float(np.mean(trans_r1_list) * 100), float(np.std(trans_r1_list) * 100)
    pop_r3_m, pop_r3_s = float(np.mean(pop_r3_list) * 100), float(np.std(pop_r3_list) * 100)
    trans_r3_m, trans_r3_s = float(np.mean(trans_r3_list) * 100), float(np.std(trans_r3_list) * 100)

    return {
        "popularity_recall@1": {"mean": pop_r1_m, "std": pop_r1_s},
        "transition_recall@1": {"mean": trans_r1_m, "std": trans_r1_s},
        "popularity_recall@3": {"mean": pop_r3_m, "std": pop_r3_s},
        "transition_recall@3": {"mean": trans_r3_m, "std": trans_r3_s},
    }


if __name__ == "__main__":
    evaluate_across_seeds()
