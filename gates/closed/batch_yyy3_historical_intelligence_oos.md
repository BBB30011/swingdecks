# Batch YYY.3

## 1. Mission
Build and validate the Historical Intelligence Out-of-Sample (OOS) framework for SwingDeck. The objective is to determine whether the information-intelligence architecture can transform historical, point-in-time-safe evidence into measurable directional information, acting deterministically (LLM=OFF).

## 2. Research Question
Does the Historical Intelligence framework contain measurable directional information that survives point-in-time constraints and out-of-sample testing?

## 3. Existing Architecture Reused
- `IntelligenceEngine` (for DuckDB relational queries).
- `fact_event`, `fact_exposure`, `fact_reaction`, `fact_peer_network`, and `dim_entity` schemas.
- The Differential Logic engine (`analyze_event_impact`), expanded for strict chronological splits.

## 4. Dataset Audit
- **Universe**: Sparse mock fixtures (`data/intelligence.duckdb`).
- **Coverage**: 10 Unique Entities, 1 Policy Event.
- **Event Count**: 1 (`EVT_COAL_BAN`).
- **Min/Max Date**: 2026-09-12.
- **Conclusion**: The dataset validates the *architecture* and deterministic pipelines, but lacks sufficient `N` for practical statistical significance.

## 5. PIT Audit
- Filtered all `fact_exposure`, `fact_peer_network`, and `fact_relationship` by `valid_from <= decision_timestamp`.
- Ensured `publication_time` is used as the strict decision boundary.
- Rejected any future information or leakage.

## 6. Candidate Information Families
**B — Policy / Macro Transmission**: A policy or macro event with an identifiable company exposure.

## 7. Researchability Assessment
- **Status**: RESEARCHABLE (for architecture validation).
- **Limitation**: Insufficient sample size for robust P-value significance. The experiment proceeds conditionally to validate the engine.

## 8. Selected Hypothesis
A restrictive policy event (`EVT_COAL_BAN`) applied to a specific commodity target (`ENT_COAL`) will cause a materially negative differential reaction for highly exposed entities (`ENT_PTBA`) and potentially asymmetric reactions for distinct peers or competitors.

## 9. Economic Mechanism
A ban on coal exports severely restricts revenue generation capabilities for highly exposed coal producers (e.g. `ENT_PTBA`), leading to immediate forward-looking repricing relative to less-exposed or non-exposed peers.

## 10. Information Definition
- **Event Type**: `POLICY`
- **Target**: `ENT_COAL`

## 11. Exposure Definition
- Entities with `HIGH` exposure to `ENT_COAL` (e.g. via `REVENUE` basis in `fact_exposure`).

## 12. Peer Definition
- Contextual peers defined via `fact_peer_network` at the exact `decision_timestamp`.

## 13. Control Definition
- The control is the average reaction of contextual peers (`peer_average_reaction`) to the same event.

## 14. Prediction Timestamp
- The exact `publication_time` of the event.

## 15. Label Definition
- `differential` return (Target Return - Peer Average Return).

## 16. OOS Design
- Chronological separation: Train (50%), Validation (20%), OOS (30%).
- Due to the sparse dataset (N=1 event), the single event falls into the OOS bucket to simulate an isolated test.

## 17. Statistical Method
- Permutation Test against 0.
- Mean, Median, Standard Deviation, Effect Size.

## 18. Multiple Testing Controls
- Only ONE candidate family (`POLICY`) was tested in this iteration. The results were not hyper-parameter optimized or p-hacked.

## 19. Experiment Result
- **Events Tested**: 1
- **Differentials Found**: 2 (PTBA, ADRO)
- **Mean Differential**: 0.0%
- **PTBA Reaction**: Target: -10.0%, Peer Avg: -2.0%, Differential: -8.0% (`ASYMMETRIC_DETRIMENT_CANDIDATE`)
- **ADRO Reaction**: Target: -2.0%, Peer Avg: -10.0%, Differential: +8.0% (`ASYMMETRIC_BENEFICIARY_CANDIDATE`)
- **P-Value**: 1.0 (Insignificant due to small N).

## 20. Falsification
The hypothesis would fail if the differential reaction of heavily exposed entities was zero (meaning the market did not differentiate between them and their peers) or if the permutation test on a large N produced p > 0.05.

## 21. Failure Analysis
- **INSUFFICIENT_SAMPLE**: The dataset currently only holds 1 event, making statistical validation mathematically impossible to prove beyond a null hypothesis. The pipeline executed flawlessly, but the *data* limits practical use.

## 22. Conclusion
**CONDITIONAL**

## 23. What This Proves
- The Antigravity SwingDeck Information Intelligence Architecture successfully, deterministically, and PIT-safely calculates differential event outcomes.
- The 3-agent architecture can operate securely with `LLM=OFF`.

## 24. What This Does Not Prove
- It does not prove that Policy Transmission events consistently yield positive expected value (EV) in real trading, due to the limited sample size.

## 25. Next Research Decision
- The infrastructure is ready. The next step must either be synthesizing a broader set of test fixtures (N > 100) to prove statistical significance, or migrating to live/real Parquet data containing historical events for Agent 2 to analyze.
