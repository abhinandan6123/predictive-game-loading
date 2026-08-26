from fastapi.testclient import TestClient

from ml.features.transitions import TransitionExample
from services.api.main import app, predictor

client = TestClient(app)


def setup_predictor() -> None:
    predictor.fit(
        [
            TransitionExample("game_01", "game_002"),
            TransitionExample("game_01", "game_002"),
            TransitionExample("game_01", "game_003"),
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
    assert list(data["probabilities"]) == ["game_002", "game_003"]
    assert round(data["probabilities"]["game_002"], 2) == 0.67


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
    assert data["recommendations"][0]["target_game_id"] == "game_002"
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


def test_prefetch_execute_full() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_002",
            "action": "FULL",
            "fraction": 1.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "executed"
    assert data["action"] == "FULL"
    assert data["fraction"] == 1.0
    assert data["requested_bytes"] > 0
    assert data["loaded_bytes"] > 0
    assert data["cache_state"] == "READY"


def test_prefetch_execute_partial() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_003",
            "action": "PARTIAL",
            "fraction": 0.5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "executed"
    assert data["action"] == "PARTIAL"
    assert data["fraction"] == 0.5
    assert data["requested_bytes"] > 0
    assert data["loaded_bytes"] == data["requested_bytes"]
    assert data["cache_state"] == "PARTIAL"


def test_prefetch_execute_skips_without_loading() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_002",
            "action": "SKIP",
            "fraction": 0.0,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "skipped"
    assert data["action"] == "SKIP"
    assert data["fraction"] == 0.0
    assert data["requested_bytes"] == 0
    assert data["loaded_bytes"] == 0
    assert data["cache_state"] is None


def test_prefetch_execute_repeated_full_is_cache_hit() -> None:
    payload = {
        "current_game_id": "game_01",
        "target_game_id": "game_004",
        "action": "FULL",
        "fraction": 1.0,
    }

    first = client.post("/prefetch/execute", json=payload)
    second = client.post("/prefetch/execute", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200

    first_data = first.json()
    second_data = second.json()

    assert first_data["status"] == "executed"
    assert first_data["loaded_bytes"] > 0

    assert second_data["status"] == "cache_hit"
    assert second_data["loaded_bytes"] == 0
    assert second_data["requested_bytes"] == first_data["requested_bytes"]
    assert second_data["cache_state"] == "READY"


def test_prefetch_execute_unknown_game_is_rejected() -> None:
    response = client.post(
        "/prefetch/execute",
        json={
            "current_game_id": "game_01",
            "target_game_id": "game_999",
            "action": "FULL",
            "fraction": 1.0,
        },
    )

    assert response.status_code == 400


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


def test_dashboard_endpoint() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PulseLoad Runtime Dashboard" in response.text
