from fastapi.testclient import TestClient

from ml.features.transitions import TransitionExample
from services.api.main import app, predictor

client = TestClient(app)


def setup_predictor() -> None:
    predictor.fit(
        [
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_02"),
            TransitionExample("game_01", "game_03"),
        ]
    )


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint() -> None:
    setup_predictor()

    response = client.post(
        "/predict",
        json={
            "current_game_id": "game_01",
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["current_game_id"] == "game_01"
    assert list(data["probabilities"]) == ["game_02", "game_03"]
    assert round(data["probabilities"]["game_02"], 2) == 0.67


def test_decide_endpoint_full() -> None:
    response = client.post(
        "/decide",
        json={
            "probability": 0.9,
            "estimated_latency_benefit_ms": 2000.0,
            "resource_cost_bytes": 1_000_000,
            "bandwidth_mbps": 20.0,
            "cache_pressure": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["action"] == "FULL"
    assert data["fraction"] == 1.0
    assert "score=" in data["explanation"]


def test_decide_endpoint_partial() -> None:
    response = client.post(
        "/decide",
        json={
            "probability": 0.1,
            "estimated_latency_benefit_ms": 150.0,
            "resource_cost_bytes": 30_000_000,
            "bandwidth_mbps": 20.0,
            "cache_pressure": 0.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["action"] == "PARTIAL"
    assert response.json()["fraction"] == 0.5


def test_decide_endpoint_skip() -> None:
    response = client.post(
        "/decide",
        json={
            "probability": 0.1,
            "estimated_latency_benefit_ms": 500.0,
            "resource_cost_bytes": 50_000_000,
            "bandwidth_mbps": 5.0,
            "cache_pressure": 0.9,
        },
    )

    assert response.status_code == 200
    assert response.json()["action"] == "SKIP"
    assert response.json()["fraction"] == 0.0


def test_prefetch_endpoint() -> None:
    setup_predictor()

    response = client.post(
        "/prefetch",
        json={
            "current_game_id": "game_01",
            "bandwidth_mbps": 20.0,
            "cache_pressure": 0.0,
            "estimated_latency_benefit_ms": 2000.0,
            "resource_cost_bytes": 1_000_000,
            "top_k": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["current_game_id"] == "game_01"
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["target_game_id"] == "game_02"
    assert data["recommendations"][0]["action"] == "FULL"


def test_predict_prefetch_compatibility_endpoint() -> None:
    setup_predictor()

    response = client.post(
        "/predict-prefetch",
        json={
            "current_game_id": "game_01",
            "top_k": 2,
        },
    )

    assert response.status_code == 200
    assert len(response.json()["recommendations"]) == 2


def test_prefetch_execute_accepts_full() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_02",
            "action": "FULL",
            "fraction": 1.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "accepted"
    assert data["action"] == "FULL"


def test_prefetch_execute_skips() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_02",
            "action": "SKIP",
            "fraction": 0.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


def test_metrics_endpoint() -> None:
    response = client.get("/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "requests" in data
    assert isinstance(data["requests"], dict)


def test_invalid_decision_input_is_rejected() -> None:
    response = client.post(
        "/decide",
        json={
            "probability": 1.5,
        },
    )

    assert response.status_code == 422
