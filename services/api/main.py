from fastapi import FastAPI
from pydantic import BaseModel, Field

from ml.prediction.transition_predictor import TransitionPredictor
from services.policy.decision import make_prefetch_decision
from services.policy.models import PolicyConfig, PolicyInputs, PrefetchAction
from services.policy.scoring import calculate_policy_score

app = FastAPI(
    title="PulseLoad API",
    description="Predictive adaptive game loading system",
    version="0.1.0",
)

# Global or lazily loaded predictor instance for the API service
predictor = TransitionPredictor()


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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "pulseload-api",
        "status": "running",
    }


@app.post("/predict-prefetch", response_model=PrefetchResponse)
async def predict_prefetch(request: PrefetchRequest) -> PrefetchResponse:
    probabilities = predictor.predict_probabilities(request.current_game_id)
    sorted_candidates = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[
        : request.top_k
    ]

    recommendations: list[PrefetchRecommendation] = []
    config = PolicyConfig()

    for game_id, prob in sorted_candidates:
        inputs = PolicyInputs(
            probability=prob,
            latency_benefit_ms=request.estimated_latency_benefit_ms,
            resource_cost_bytes=request.resource_cost_bytes,
            bandwidth_mbps=request.bandwidth_mbps,
            cache_pressure=request.cache_pressure,
        )
        score = calculate_policy_score(inputs)
        decision = make_prefetch_decision(score, config=config)

        recommendations.append(
            PrefetchRecommendation(
                target_game_id=game_id,
                probability=prob,
                action=decision.action,
                score=decision.score,
                fraction=decision.fraction,
                explanation=decision.explanation,
            )
        )

    return PrefetchResponse(
        current_game_id=request.current_game_id,
        recommendations=recommendations,
    )
