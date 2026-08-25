# Multi-Seed Benchmark Evaluation (Deliverable D4-03 / D4-05)

## Overview
Evaluation conducted across 5 deterministic seeds (42, 101, 2024, 7, 99) with 10,000 synthetic player sessions each.

## Results Summary

| Model | Recall@1 (Mean ± Std) | Recall@3 (Mean ± Std) |
| :--- | :--- | :--- |
| **Popularity Baseline** | 19.93% ± 0.61% | 60.19% ± 0.55% |
| **Transition Predictor** | **37.18% ± 0.76%** | **68.66% ± 0.13%** |

## Key Findings
- The Transition Predictor delivers a **+17.25% absolute gain** in Recall@1 over the baseline popularity approach.
- Stability across seeds is high, with a standard deviation below 0.8% across all runs.
- Full unit test coverage confirmed with 25/25 tests passing.

---

## Local Verification & Execution Evidence

### 1. Test Suite Execution
- **Command:** `pytest -v`
- **Output:** `25 passed, 1 warning in 0.62s` (100% pass rate)
- **Covered Test Modules:**
  - `tests/unit/test_baseline.py` (2 passed)
  - `tests/unit/test_benchmark.py` (1 passed)
  - `tests/unit/test_contextual_features.py` (2 passed)
  - `tests/unit/test_health.py` (1 passed)
  - `tests/unit/test_metrics.py` (3 passed)
  - `tests/unit/test_network_transfer.py` (2 passed)
  - `tests/unit/test_popularity_predictor.py` (3 passed)
  - `tests/unit/test_sessions.py` (6 passed)
  - `tests/unit/test_transition_predictor.py` (3 passed)
  - `tests/unit/test_transitions.py` (2 passed)

### 2. Multi-Seed Benchmark Reproduction
- **Command:** `python -m ml.evaluation.evaluate_multi_seed`
- **Result:** Benchmark metrics generated across seeds `[42, 101, 2024, 7, 99]`.

### 3. Baseline Simulator Run
- **Command:** `python -m simulator.run_baseline`
- **Result:** Latencies validated across Fast, Medium, and Slow network profiles.

### 4. Service Health Check
- **Command:** `python -m uvicorn services.api.main:app --reload`
- **Result:** Server initialized on `http://127.0.0.1:8000` with `/health` returning `200 OK`.