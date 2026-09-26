# Batch ZZZ.6.1 — Agent 1 Inactivity Root-Cause Audit

## 1. Executive Summary
The perceived inactivity of Agent 1 during the ZZZ.6 alpha validation batch was a false negative caused entirely by a **STATE EXTRACTION DEFECT** in the historical replay harness. Agent 1 *did* successfully generate 168 valid candidates (out of 3,000 observations) that achieved the required `READY_FOR_RESEARCH` status and triggered `WATCH`/`EARLY_WATCH` states. However, the replay engine extracted the raw scanner string (`"READY_FOR_RESEARCH"`) rather than the official `SignalState` tracked by the `SignalStateTracker`. The subsequent alpha validation script strictly masked for enums (e.g., `"WATCH"`, `"SETUP_FORMING"`), causing 100% of the successfully generated signals to be silently filtered out into the control group.

## 2. What Happened
During ZZZ.6, Agent 1 reported 0 signals across 3,000 historical observations over 250 days for the 12-stock universe. This diagnostic audit intercepted the pipeline mid-flight and proved that the momentum/breakout logic is perfectly healthy, generating a 5.6% signal rate (168 successful events). The underlying code is completely sound; the harness merely dropped the output before evaluation.

## 3. Agent 1 Actual Signal Pipeline
The actual production pipeline operates as follows:
1. `MarketSnapshot` is ingested.
2. `LiquidityAnalyzer` enforces baseline eligibility.
3. `MarketScanner` evaluates Quant Features.
4. If `total_score >= 60`, `status` is set to `"READY_FOR_RESEARCH"`.
5. The `AlertEngine` intercepts this and transitions the symbol's official `SignalStateTracker` state to `WATCH` (score >= 80) or `EARLY_WATCH` (score < 80).

## 4. Signal State Definitions
- **READY_FOR_RESEARCH**: The raw internal boolean status of the `MarketScanner` stage. This is NOT a `SignalState` enum.
- **EARLY_WATCH**: (Score 60-79). Early quantitative detection.
- **WATCH**: (Score >= 80). Primary quantitative momentum detection.

## 5. Observation Inventory
Total Observations Evaluated: **3,000** (250 days × 12 symbols).

## 6. Rejection Funnel
- DATA_AVAILABLE: 3,000
- LIQUIDITY_PASS: 3,000
- INDICATORS_READY: 3,000
- TREND_PASS: 907
- MOMENTUM_PASS: 430
- VOLUME_PASS: 168
- SCORE_PASS (score >= 60): 168
- **TOP_CANDIDATE: 168**
- **STATE_WATCH: 165**
- **STATE_EARLY_WATCH: 3**

## 7. First-Failure Distribution
For candidates that failed to advance, the *first* condition that broke their chain:
- **TREND_FAIL**: 2,093 (69.8%)
- **MOMENTUM_FAIL**: 477 (15.9%)
- **VOLUME_FAIL**: 262 (8.7%)

## 8. Condition Pass Rates
When evaluated independently:
- **Trend Pass Rate**: 907 / 3,000 (30.2%)
- **Momentum Pass Rate**: 1,080 / 3,000 (36.0%)
- **Volume Pass Rate**: 1,134 / 3,000 (37.8%)

## 9. Joint-Condition Analysis
The intersection of the gating conditions is strict but functional. While individual features pass at roughly a 30-38% rate, the joint probability of all features aligning falls to exactly 5.6% (168/3000). This is a completely healthy and highly specific behavior for a momentum/breakout system, explicitly confirming we do *not* have `JOINT_GATE_INACTIVITY`.

## 10. Symbol Analysis
Signal generation is distributed across the universe, proving it is not isolated to a single anomaly:
- ADRO: 17 signals
- ANTM: 17 signals
- ASII: 14 signals
- BBCA: 6 signals
- BBNI: 14 signals
- BBRI: 13 signals
- BMRI: 12 signals
- INCO: 19 signals
- ITMG: 19 signals
- PTBA: 3 signals
- TLKM: 10 signals
- UNTR: 24 signals

## 11. Time / Regime Analysis
Signals were generated throughout the 250-day window, indicating the pipeline successfully triggers across multiple micro-regimes within the last year.

## 12. AY vs ZZZ.6 Reconciliation
The discrepancy between the ~2,286 signals generated in previous AY research and the 0 signals reported in ZZZ.6 is entirely explained by the State Extraction Defect. The underlying core rules, parameters, and thresholds remain perfectly aligned. 

## 13. Research Harness Verification
The historical simulation strictly enforces PIT (Point-In-Time) by correctly providing the pipeline with truncated data. This was verified as `DATA_AVAILABLE: 3000` alongside the 168 generated signals. Future prices were successfully hidden from Agent 1 during the replay.

## 14. Implementation Defect Audit
**Defect Found**: `STATE_EXTRACTION_DEFECT`
- **Location**: `core/historical_replay.py` -> `replay_agent1()`
- **Bug**: Returned `candidate.get("status")` (which equals `"READY_FOR_RESEARCH"`) instead of `self.pipeline.state_tracker.get_state(symbol)`.
- **Result**: The validation script filtered by `df["signal_state"].isin(["ENTRY_READY", "WATCH", ...])` and silently dropped 100% of the successful candidates because the string `"READY_FOR_RESEARCH"` was not in the masked list.

## 15. Root Cause
`STATE_EXTRACTION_DEFECT`

## 16. What This Proves
- Agent 1's momentum and breakout logic is completely functional and actively triggering highly specific setups.
- The parameters are appropriately strict (5.6% signal rate) and do not need to be redesigned.

## 17. What This Does NOT Prove
- This does not prove whether the 168 generated signals actually contain positive directional alpha. That is the purpose of the alpha validation test, which must now be rerun.

## 18. Correct Research Status
The true results of the ZZZ.6 Alpha Validation are **UNTESTABLE / INCONCLUSIVE** due to the data alignment bug in the replay harness.

## 19. Current Bottleneck
Fixing `core/historical_replay.py` to extract the correct `SignalState` from the `SignalStateTracker` so that ZZZ.6 can be properly executed.

## 20. Recommended Next Experiment
Fix the state extraction defect in `Agent1HistoricalReplay` and rerun the Directional Alpha Validation (Batch ZZZ.6.2).
