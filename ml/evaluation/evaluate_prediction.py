"""Evaluation script comparing Popularity, Transition, and Contextual prediction models."""

from __future__ import annotations

import csv
from pathlib import Path

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import recall_at_k
from ml.features.contextual import extract_contextual_features
from ml.features.transitions import extract_transitions
from ml.prediction.contextual_predictor import ContextualPredictor
from ml.prediction.transition_predictor import TransitionPredictor
from simulator.sessions.generator import generate_sessions

RESULTS_PATH = Path("ml/evaluation/results/prediction_comparison.csv")


def evaluate() -> None:
    print("Generating simulated sessions...")
    sessions = generate_sessions(count=10_000, seed=42)

    split_index = int(len(sessions) * 0.8)
    train_sessions = sessions[:split_index]
    test_sessions = sessions[split_index:]

    # Extract transition and contextual datasets
    train_transitions = extract_transitions(train_sessions)
    test_transitions = extract_transitions(test_sessions)

    train_contextual = extract_contextual_features(train_sessions)
    test_contextual = extract_contextual_features(test_sessions)

    test_targets = [t.target_game for t in test_transitions]

    print("Fitting models...")
    # 1. Popularity Baseline
    popularity = PopularityPredictor()
    popularity.fit([t.target_game for t in train_transitions])

    # 2. Markov Transition Predictor
    transition = TransitionPredictor()
    transition.fit(train_transitions)

    # 3. Contextual Probabilistic Predictor
    contextual = ContextualPredictor()
    contextual.fit(train_contextual)

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    print("\nEvaluating Recall@K across models...")
    for k in (1, 3, 5):
        popularity_preds = [popularity.predict_top_k(k) for _ in test_transitions]
        transition_preds = [transition.predict_top_k(t.source_game, k) for t in test_transitions]
        contextual_preds = [contextual.predict_top_k(ctx, k) for ctx in test_contextual]

        pop_recall = recall_at_k(popularity_preds, test_targets)
        trans_recall = recall_at_k(transition_preds, test_targets)
        ctx_recall = recall_at_k(contextual_preds, test_targets)

        rows.extend(
            [
                {"model": "popularity", "k": k, "recall": pop_recall},
                {"model": "transition", "k": k, "recall": trans_recall},
                {"model": "contextual", "k": k, "recall": ctx_recall},
            ]
        )

    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["model", "k", "recall"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTraining transitions: {len(train_transitions)}")
    print(f"Test transitions:     {len(test_transitions)}")
    print("-" * 40)
    for row in rows:
        print(f"{row['model']:>12} | Recall@{row['k']}: {row['recall'] * 100:.2f}%")


if __name__ == "__main__":
    evaluate()
