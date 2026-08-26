# PulseLoad 60-Second Demo Script

## 0–10 seconds — Problem

Game loading traditionally waits for the user to tap before loading resources. PulseLoad predicts the likely next game and prepares it proactively.

## 10–20 seconds — Prediction

Call POST /predict and show the ranked next-game probabilities.

Narrate: The transition predictor identifies the most likely next game.

## 20–30 seconds — Adaptive Policy

Call POST /prefetch and show the FULL, PARTIAL or SKIP recommendation.

Narrate: The policy combines prediction confidence with latency benefit, resource cost, bandwidth and cache pressure.

## 30–40 seconds — Execution

Call POST /prefetch/execute and show action, fraction, requested bytes, loaded bytes and cache state.

Narrate: The executor converts the policy decision into an actual cache/loading operation.

## 40–48 seconds — Cache Hit

Repeat the same execution request and show status=cache_hit with loaded_bytes=0.

Narrate: The second request is served from cache instead of repeating the full load.

## 48–54 seconds — Responsible Play

Send an execution request with safety_block=true.

Expected result: HTTP 403 — responsible-play restriction active.

Narrate: Responsible-play restrictions are enforced independently of prediction and optimization.

## 54–58 seconds — Observability

Call GET /metrics and show prefetch accuracy, cache hit rate, load count, time-to-playable, p50 and p95.

## 58–60 seconds — Dashboard

Open /dashboard.

Close: PulseLoad combines prediction, adaptive policy, caching, progressive loading, responsible-play controls and runtime observability into one end-to-end loading pipeline.
