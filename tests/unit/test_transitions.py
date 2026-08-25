from ml.features.transitions import TransitionExample
from ml.prediction.transition_predictor import TransitionPredictor


def test_transition_predictor_fit_and_predict() -> None:
    train_data = [
        TransitionExample(prev_game="game_a", next_game="game_b"),
        TransitionExample(prev_game="game_a", next_game="game_b"),
        TransitionExample(prev_game="game_a", next_game="game_c"),
    ]
    model = TransitionPredictor()
    model.fit(train_data)

    predictions = model.predict(current_game="game_a", top_k=2)
    assert len(predictions) == 2
    assert predictions[0] == "game_b"
    assert predictions[1] == "game_c"


def test_transition_predictor_unseen_game() -> None:
    train_data = [
        TransitionExample(prev_game="game_a", next_game="game_b"),
    ]
    model = TransitionPredictor()
    model.fit(train_data)

    predictions = model.predict(current_game="game_unknown", top_k=2)
    assert isinstance(predictions, list)
