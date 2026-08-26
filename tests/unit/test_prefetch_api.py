from fastapi.testclient import TestClient

from ml.features.transitions import TransitionExample
from services.api.main import app, predictor


def test_predict_prefetch_endpoint() -> None:
    client = TestClient(app)

    # Populate predictor with sample transitions
    predictor.fit(
        [
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_03"),
        ]
    )

    payload = {
        "current_game_id": "game_01",
        "bandwidth_mbps": 20.0,
        "cache_pressure": 0.0,
        "estimated_latency_benefit_ms": 2000.0,
        "resource_cost_bytes": 1_000_000,
        "top_k": 2,
    }

    response = client.post("/predict-prefetch", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["current_game_id"] == "game_01"
    assert len(data["recommendations"]) == 2

    first_rec = data["recommendations"][0]
    assert first_rec["target_game_id"] == "game_02"
    assert round(first_rec["probability"], 2) == 0.67
    assert first_rec["action"] in ["FULL", "PARTIAL", "SKIP"]
