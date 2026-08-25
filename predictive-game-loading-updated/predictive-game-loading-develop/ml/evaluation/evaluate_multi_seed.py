"""
Multi-Seed Evaluation Harness (Deliverable D4-03)
Runs repeated experiments across multiple seeds and computes mean +/- std dev.
"""

import numpy as np

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import recall_at_k
from ml.features.transitions import extract_transitions
from ml.prediction.transition_predictor import TransitionPredictor
from simulator.sessions.generator import generate_sessions


def build_examples(sessions):
    sources = []
    targets = []
    for session in sessions:
        launches = [event.game_id for event in session.events if event.event_type == "launch"]
        for index in range(len(launches) - 1):
            sources.append(launches[index])
            targets.append(launches[index + 1])
    return sources, targets


def evaluate_across_seeds(seeds: list[int] = [42, 101, 2024, 7, 99], session_count: int = 10000):
    pop_r1_list, pop_r3_list = [], []
    trans_r1_list, trans_r3_list = [], []

    print(f"Running Multi-Seed Evaluation across {len(seeds)} seeds...")

    for seed in seeds:
        sessions = generate_sessions(count=session_count, seed=seed)
        split_idx = int(0.8 * len(sessions))
        train_sessions = sessions[:split_idx]
        test_sessions = sessions[split_idx:]

        train_sources, train_targets = build_examples(train_sessions)
        test_sources, test_targets = build_examples(test_sessions)

        # 1. Popularity Baseline
        pop_model = PopularityPredictor()
        pop_model.fit(train_targets)

        pop_preds_1 = [pop_model.predict_top_k(1) for _ in test_targets]
        pop_preds_3 = [pop_model.predict_top_k(3) for _ in test_targets]
        pop_r1_list.append(recall_at_k(pop_preds_1, test_targets))
        pop_r3_list.append(recall_at_k(pop_preds_3, test_targets))

        # 2. Transition Predictor
        trans_model = TransitionPredictor()
        trans_model.fit(extract_transitions(train_sessions))

        trans_preds_1 = [trans_model.predict_top_k(src, 1) for src in test_sources]
        trans_preds_3 = [trans_model.predict_top_k(src, 3) for src in test_sources]
        trans_r1_list.append(recall_at_k(trans_preds_1, test_targets))
        trans_r3_list.append(recall_at_k(trans_preds_3, test_targets))

    print("\n================ MULTI-SEED BENCHMARK RESULTS ================")
    print(f"Popularity  Recall@1: {np.mean(pop_r1_list)*100:.2f}% +/- {np.std(pop_r1_list)*100:.2f}%")
    print(f"Transition  Recall@1: {np.mean(trans_r1_list)*100:.2f}% +/- {np.std(trans_r1_list)*100:.2f}%")
    print(f"Popularity  Recall@3: {np.mean(pop_r3_list)*100:.2f}% +/- {np.std(pop_r3_list)*100:.2f}%")
    print(f"Transition  Recall@3: {np.mean(trans_r3_list)*100:.2f}% +/- {np.std(trans_r3_list)*100:.2f}%")
    print("==============================================================")


if __name__ == "__main__":
    evaluate_across_seeds()