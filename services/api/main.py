from collections import Counter
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml.prediction.transition_predictor import TransitionPredictor
from services.policy.decision import make_prefetch_decision
from services.policy.models import (
    PolicyConfig,
    PolicyInputs,
    PrefetchAction,
    PrefetchDecision,
)
from services.policy.scoring import calculate_policy_score
from services.prefetch import PrefetchExecutor

app = FastAPI(
    title="PulseLoad API",
    description="Predictive adaptive game loading system",
    version="0.2.0",
)

predictor = TransitionPredictor()
prefetch_executor = PrefetchExecutor()

_metrics: Counter[str] = Counter()


class PredictRequest(BaseModel):
    current_game_id: str
    top_k: int = Field(default=3, ge=1)


class PredictResponse(BaseModel):
    current_game_id: str
    probabilities: dict[str, float]


class DecisionRequest(BaseModel):
    probability: float = Field(ge=0.0, le=1.0)
    estimated_latency_benefit_ms: float = Field(default=1500.0, ge=0)
    resource_cost_bytes: int = Field(default=5_000_000, gt=0)
    bandwidth_mbps: float = Field(default=20.0, gt=0)
    cache_pressure: float = Field(default=0.1, ge=0.0, le=1.0)


class DecisionResponse(BaseModel):
    action: PrefetchAction
    score: float
    fraction: float
    explanation: str


class PrefetchRequest(BaseModel):
    current_game_id: str
    bandwidth_mbps: float = Field(default=20.0, gt=0)
    cache_pressure: float = Field(default=0.1, ge=0.0, le=1.0)
    estimated_latency_benefit_ms: float = Field(default=1500.0, ge=0)
    resource_cost_bytes: int = Field(default=5_000_000, gt=0)
    top_k: int = Field(default=3, ge=1)


class PrefetchRecommendation(BaseModel):
    target_game_id: str
    probability: float
    action: PrefetchAction
    score: float
    fraction: float
    explanation: str


class PrefetchResponse(BaseModel):
    current_game_id: str
    recommendations: list[PrefetchRecommendation]


class ExecuteRequest(BaseModel):
    current_game_id: str
    target_game_id: str
    action: PrefetchAction
    fraction: float = Field(ge=0.0, le=1.0)


class ExecuteResponse(BaseModel):
    current_game_id: str
    target_game_id: str
    action: PrefetchAction
    fraction: float
    status: str
    requested_bytes: int
    loaded_bytes: int
    cache_state: str | None


def _record(metric: str) -> None:
    _metrics[metric] += 1


def _calculate_decision(request: DecisionRequest) -> DecisionResponse:
    inputs = PolicyInputs(
        probability=request.probability,
        latency_benefit_ms=request.estimated_latency_benefit_ms,
        resource_cost_bytes=request.resource_cost_bytes,
        bandwidth_mbps=request.bandwidth_mbps,
        cache_pressure=request.cache_pressure,
    )

    score = calculate_policy_score(inputs)
    decision = make_prefetch_decision(score, config=PolicyConfig())

    _record("decisions_total")
    _record(f"decisions_{decision.action.value.lower()}")

    return DecisionResponse(
        action=decision.action,
        score=decision.score,
        fraction=decision.fraction,
        explanation=decision.explanation,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "pulseload-api",
        "status": "running",
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    probabilities = predictor.predict_probabilities(request.current_game_id)

    sorted_probabilities = dict(
        sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        )[: request.top_k]
    )

    _record("predict_requests_total")

    return PredictResponse(
        current_game_id=request.current_game_id,
        probabilities=sorted_probabilities,
    )


@app.post("/decide", response_model=DecisionResponse)
async def decide(request: DecisionRequest) -> DecisionResponse:
    _record("decide_requests_total")
    return _calculate_decision(request)


@app.post("/prefetch", response_model=PrefetchResponse)
async def prefetch(request: PrefetchRequest) -> PrefetchResponse:
    probabilities = predictor.predict_probabilities(request.current_game_id)

    sorted_candidates = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True,
    )[: request.top_k]

    recommendations: list[PrefetchRecommendation] = []

    for game_id, probability in sorted_candidates:
        decision = _calculate_decision(
            DecisionRequest(
                probability=probability,
                latency_benefit_ms=request.estimated_latency_benefit_ms,
                resource_cost_bytes=request.resource_cost_bytes,
                bandwidth_mbps=request.bandwidth_mbps,
                cache_pressure=request.cache_pressure,
            )
        )

        recommendations.append(
            PrefetchRecommendation(
                target_game_id=game_id,
                probability=probability,
                action=decision.action,
                score=decision.score,
                fraction=decision.fraction,
                explanation=decision.explanation,
            )
        )

    _record("prefetch_requests_total")

    return PrefetchResponse(
        current_game_id=request.current_game_id,
        recommendations=recommendations,
    )


@app.post("/prefetch/execute", response_model=ExecuteResponse)
async def execute_prefetch(request: ExecuteRequest) -> ExecuteResponse:
    _record("prefetch_execute_requests_total")

    decision = PrefetchDecision(
        action=request.action,
        score=0.0,
        fraction=request.fraction,
        explanation="API execution request",
    )

    try:
        result = prefetch_executor.execute(
            target_game_id=request.target_game_id,
            decision=decision,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    _record(f"executions_{request.action.value.lower()}")

    if result.status.value == "cache_hit":
        _record("executions_cache_hit")
    elif result.status.value == "executed":
        _record("executions_completed")

    return ExecuteResponse(
        current_game_id=request.current_game_id,
        target_game_id=request.target_game_id,
        action=result.action,
        fraction=result.fraction,
        status=result.status.value,
        requested_bytes=result.requested_bytes,
        loaded_bytes=result.loaded_bytes,
        cache_state=(result.cache_state.value if result.cache_state is not None else None),
    )


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    return {
        "requests": dict(_metrics),
    }


@app.post("/predict-prefetch", response_model=PrefetchResponse)
async def predict_prefetch(request: PrefetchRequest) -> PrefetchResponse:
    return await prefetch(request)
