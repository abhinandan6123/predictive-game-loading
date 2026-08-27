# PulseLoad Failure Matrix

## Purpose

The failure matrix documents expected failure modes across the end-to-end
predictive loading pipeline and the intended safe behavior.

| Failure scenario | Expected behavior | Safety / fallback |
|---|---|---|
| Prediction unavailable | Do not prefetch speculative target | Fall back to normal loading |
| Low-confidence prediction | Policy may choose SKIP | No speculative resource consumption |
| Cache miss | Execute permitted prefetch | Load through cache hierarchy |
| Cache pressure high | Reduce/skip prefetch according to policy | Protect cache capacity |
| Invalid game resource | Reject execution request | Return controlled API error |
| Invalid partial fraction | Reject request | No cache mutation |
| Invalid full fraction | Reject request | No cache mutation |
| Responsible-play block | Do not permit speculative action | Safety guard takes precedence |
| Restricted session | Block prefetch | Normal loading path remains available |
| API failure | Preserve deterministic service error | Client can retry/fallback |
| Telemetry unavailable | Core execution remains deterministic | Metrics degradation is observable |
| Dashboard unavailable | API remains available | Dashboard is observational only |
| Docker unavailable locally | Continue source-level validation | CI performs container validation |
| Cold start | Normal application startup | Health endpoint verifies readiness |

## Required invariants

1. Safety decisions are independent from prediction confidence.
2. A safety block must never be converted into a prefetch action.
3. Invalid execution parameters must not mutate cache state.
4. Prediction failure must not prevent normal loading.
5. Observability must not become a hard dependency for core execution.
6. Dashboard failure must not prevent API operation.
7. Deployment failures must have a local reproducibility path.

## Validation evidence

The repository validation suite covers the implemented runtime components,
including prediction, policy, cache, executor, API, telemetry, and safety guard.
