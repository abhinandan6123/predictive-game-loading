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