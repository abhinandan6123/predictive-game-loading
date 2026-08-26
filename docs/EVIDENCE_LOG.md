# PulseLoad Evidence Log

## Final architecture

Client → FastAPI → Predictor → Adaptive Policy → Prefetch Executor →
Hierarchical Cache → Progressive Loader → Telemetry → Metrics → Dashboard.

## Completed engineering evidence

### Prediction
- Transition prediction service implemented.
- `/predict` exposes ranked next-game probabilities.
- Existing unit tests validate prediction behavior.

### Policy
- Constraint-aware scoring combines probability, latency benefit,
  resource cost, bandwidth and cache pressure.
- Policy produces FULL, PARTIAL or SKIP decisions.

### Prefetch execution
- Policy decisions are executed against the game catalog.
- FULL and PARTIAL execution paths are supported.
- Repeated requests can produce deterministic cache-hit behavior.
- Invalid resource/action parameters are rejected.

### Cache
- Hierarchical cache supports critical, core and secondary resource tiers.
- Executor uses cache state to avoid redundant loading.

### Progressive loading
- Critical bytes form the first stage.
- Critical + core bytes form the playable stage.
- Secondary bytes complete the total resource.

### API integration
Implemented API surface includes:
- `/health`
- `/predict`
- `/decide`
- `/prefetch`
- `/prefetch/execute`
- `/metrics`
- `/dashboard`
- `/predict-prefetch`

### Telemetry
Telemetry records:
- prediction requests
- prefetch requests
- execution status
- cache hits/misses
- load events
- playable events

Metrics expose:
- request counts
- prefetch accuracy
- cache hit rate
- load count
- time-to-playable
- p50
- p95

### Responsible play
An independent safety guard evaluates responsible-play permission,
restricted sessions and explicit safety blocks before speculative behavior.

### Deployment
Repository contains:
- Dockerfile
- docker-compose.yml
- render.yaml
- CI workflow
- dashboard

### Quality
Final local validation:
- Ruff check: PASS
- Ruff format check: PASS
- Pytest: PASS
- Git diff check: PASS

The final repository state should remain clean after all changes are committed.

## Known environment limitation

Docker was not available in the local Windows Git Bash environment during
the final local validation. Docker build/configuration therefore remains
validated by repository configuration and CI/deployment configuration rather
than by a local Docker daemon.

## Evidence artifacts

- `evidence/results.csv`
- `evidence/metrics_summary.csv`
- `evidence/METRICS_SUMMARY.md`
- `docs/FAILURE_MATRIX.md`
- `docs/ARCHITECTURE_FREEZE.md`
