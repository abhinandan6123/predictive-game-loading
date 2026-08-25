import csv
from pathlib import Path

from ml.baselines.popularity import PopularityPredictor
from ml.evaluation.metrics import recall_at_k
from ml.features.transitions import extract_transitions
from ml.prediction.transition_predictor import TransitionPredictor
from simulator.sessions.generator import generate_sessions

RESULTS_PATH = Path("ml/evaluation/results/prediction_baseline.csv")


def build_examples(
    sessions,
) -> tuple[list[str], list[str]]:
    sources: list[str] = []
    targets: list[str] = []

    for session in sessions:
        launches = [event.game_id for event in session.events if event.event_type == "launch"]

        for index in range(len(launches) - 1):
            sources.append(launches[index])
            targets.append(launches[index + 1])

    return sources, targets


def evaluate() -> None:
    sessions = generate_sessions(
        count=10_000,
        seed=42,
    )

    split_index = int(len(sessions) * 0.8)

    train_sessions = sessions[:split_index]
    test_sessions = sessions[split_index:]

    train_sources, train_targets = build_examples(train_sessions)
    test_sources, test_targets = build_examples(test_sessions)

    popularity = PopularityPredictor()
    popularity.fit(train_targets)

    transition = TransitionPredictor()
    transition.fit(extract_transitions(train_sessions))

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    for k in (1, 3, 5):
        popularity_predictions = [popularity.predict_top_k(k) for _ in test_targets]

        transition_predictions = [transition.predict_top_k(source, k) for source in test_sources]

        rows.extend(
            [
                {
                    "model": "popularity",
                    "k": k,
                    "recall": recall_at_k(
                        popularity_predictions,
                        test_targets,
                    ),
                },
                {
                    "model": "transition",
                    "k": k,
                    "recall": recall_at_k(
                        transition_predictions,
                        test_targets,
                    ),
                },
            ]
        )

    with RESULTS_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["model", "k", "recall"],
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Training sessions: {len(train_sessions)}")
    print(f"Test sessions: {len(test_sessions)}")
    print(f"Training transitions: {len(train_targets)}")
    print(f"Test transitions: {len(test_targets)}")
    print()

    for row in rows:
        print(f"{row['model']:>10} Recall@{row['k']}: {row['recall']:.4f}")


if __name__ == "__main__":
    evaluate()
