# Batch ZZZ.6.2 — Directional Alpha Validation (Corrected Execution)

> **Audit Notice**: The original Batch ZZZ.6 execution was invalidated due to a confirmed `STATE_EXTRACTION_DEFECT` (diagnosed in Batch ZZZ.6.1). This document represents the corrected execution (Batch ZZZ.6.2) evaluating the frozen Agent 1 quantitative signal under strict Point-in-Time (PIT) isolation.

---

## 1. Executive Summary

Batch ZZZ.6.2 successfully repaired the state extraction defect in `Agent1HistoricalReplay` and re-executed the historical directional alpha validation across 3,000 observations (250 trading days × 12 pilot stocks). 

The corrected execution confirms:
1. **Defect Repaired**: Agent 1 generated **1,242 valid signal observations** (41.4% signal rate with scanner score $\ge 60$, comprising 702 `WATCH` and 540 `EARLY_WATCH` states) across the 3,000 observations, which are now correctly extracted and recognized by the research validator.
2. **Directional Lift Result**: The frozen quantitative momentum/breakout signals **do not demonstrate positive forward directional alpha** over the eligible historical control group (1,758 observations).
3. **Forward Drift**: Forward returns from $Close(T)$ to $Close(T+h)$ show neutral to negative excess drift versus control:
   - **H1**: Signal $-0.01\%$ vs Control $+0.07\%$ (Diff: $-0.08\%$, Clustered 95% CI: $[-0.38\%, +0.18\%]$, $p=0.4320$)
   - **H3**: Signal $+0.01\%$ vs Control $+0.15\%$ (Diff: $-0.14\%$, Clustered 95% CI: $[-0.63\%, +0.31\%]$, $p=0.3460$)
   - **H5**: Signal $-0.02\%$ vs Control $+0.31\%$ (Diff: $-0.33\%$, Clustered 95% CI: $[-0.96\%, +0.26\%]$, $p=0.1010$)
   - **H10**: Signal $-0.03\%$ vs Control $+0.52\%$ (Diff: $-0.55\%$, Clustered 95% CI: $[-1.37\%, +0.31\%]$, $p=0.0440$)
   - **H20**: Signal $-0.35\%$ vs Control $+0.97\%$ (Diff: $-1.32\%$, Clustered 95% CI: $[-2.37\%, -0.38\%]$, $p=0.0020$)
4. **Final Status**: **FAIL** (The tested standalone quantitative momentum/breakout signal fails to provide positive forward directional alpha over the historical control).

---

## 2. ZZZ.6 Original Failure

During the initial execution of Batch ZZZ.6, the validation harness erroneously reported **0 signals** across 3,000 historical observations, resulting in an inconclusive/untestable status. The pipeline appeared dormant because all observations were routed into the control group.

---

## 3. ZZZ.6.1 Root Cause

Batch ZZZ.6.1 investigated the inactivity anomaly and discovered that the dormancy was an artifact of `STATE_EXTRACTION_DEFECT`:
- In `core/historical_replay.py` -> `replay_agent1()`, the engine extracted `candidate.get("status")`, which returned `"READY_FOR_RESEARCH"`.
- `"READY_FOR_RESEARCH"` is an internal raw status of the `MarketScanner`, NOT an official `SignalState` enum.
- The official state was maintained by `SignalStateTracker` (e.g. `WATCH`, `EARLY_WATCH`).
- The downstream research validator filtered for `df["signal_state"].isin(["WATCH", "EARLY_WATCH", "ENTRY_READY", ...])`, which silently rejected 100% of valid candidates.

---

## 4. Fix Applied

In `core/historical_replay.py`:
- Separated `raw_scanner_status` (e.g. `"READY_FOR_RESEARCH"`, `"REJECT"`) from `official_signal_state`.
- Queried `self.pipeline.state_tracker.get_state(snapshot.symbol)` when a candidate is selected, returning the official `SignalState` string (`"WATCH"` or `"EARLY_WATCH"`).
- Assigned `"REJECTED"` to `signal_state` when no candidate is selected.
- Preserved both fields in the return payload for auditability without modifying any scanner thresholds, indicator formulas, or ranking logic.

---

## 5. Regression Test

A dedicated regression test suite was implemented in `tests/test_batch_zzz62_state_extraction_regression.py` covering:
1. `MarketScanner` produces `READY_FOR_RESEARCH`.
2. `READY_FOR_RESEARCH` is validated to NOT be a member of `SignalState` enum.
3. `SignalStateTracker` tracks and produces official `SignalState` enums.
4. `Agent1HistoricalReplay` returns both `official_signal_state` and `raw_scanner_status` separately.
5. Research validator filter correctly identifies replayed signals.
6. Graceful handling of rejected symbols.

All 6 regression tests passed cleanly.

---

## 6. PIT Validation

The Point-in-Time (PIT) boundary established in Batch ZZZ.5 remained strictly enforced throughout ZZZ.6.2:
- Market data is truncated at decision timestamp $T$ before being ingested by `Agent1QuantPipeline`.
- Zero future bars $(T+1 \dots T+20)$ are accessible to Agent 1 during signal generation.
- Future prices are accessed strictly post-signal by the research evaluation harness solely for forward return calculation.

---

## 7. Dataset

- **Universe**: 12 pilot IDX equities (`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`).
- **Benchmark**: IHSG (cross-sectional market reference).
- **Timeframe**: Last 250 trading days (2025-09-03 to 2026-09-14).
- **Total Observations**: 3,000 stock-days.

---

## 8. Signal Inventory

- **Total Signals Generated ($N_{signal}$)**: **1,242** (41.4% signal rate)
  - `WATCH` (Quant Score $\ge 80$): **702** (56.5% of signals)
  - `EARLY_WATCH` (Quant Score $60-79$): **540** (43.5% of signals)
- **Score Distribution**: Mean = 82.04, Median = 83.0, IQR = [70.0, 93.0].
- **Symbol Breakdown**:
  - `UNTR`: 133
  - `ADRO`: 133
  - `ASII`: 122
  - `INCO`: 115
  - `ITMG`: 115
  - `ANTM`: 110
  - `BMRI`: 99
  - `BBNI`: 94
  - `PTBA`: 89
  - `BBRI`: 88
  - `TLKM`: 80
  - `BBCA`: 64

---

## 9. Control Definition

- **Control Group ($N_{control}$)**: **1,758** observations.
- **Definition**: All valid historical observations within the same 12-symbol universe and 250-day window that failed the scanner qualification ($Score < 60$ or rejected at liquidity/quant gates).
- The control represents the eligible opportunity set that Agent 1 decided *not* to select.

---

## 10. H1/H3/H5/H10/H20 Results

### Primary Forward Return: $Close(T) \to Close(T+h)$

| Horizon | $N_{sig}$ | $N_{ctrl}$ | Signal Mean | Control Mean | Diff (Sig - Ctrl) | Signal Median | Control Median | Win Rate (Sig / Ctrl) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **H1** | 1,236 | 1,752 | -0.01% | +0.07% | **-0.08%** | 0.00% | 0.00% | 44.3% / 44.3% |
| **H3** | 1,218 | 1,746 | +0.01% | +0.15% | **-0.14%** | 0.00% | 0.00% | 47.7% / 48.2% |
| **H5** | 1,198 | 1,742 | -0.02% | +0.31% | **-0.33%** | 0.00% | 0.00% | 48.9% / 48.6% |
| **H10** | 1,150 | 1,730 | -0.03% | +0.52% | **-0.55%** | 0.00% | +0.35% | 48.9% / 51.4% |
| **H20** | 1,087 | 1,683 | -0.35% | +0.97% | **-1.32%** | -0.33% | +0.33% | 47.8% / 50.6% |

### MFE / MAE & Excursion Metrics

| Horizon | Signal Mean MFE | Signal Mean MAE | Signal 5% Trimmed Mean | Control 5% Trimmed Mean |
|:---|:---:|:---:|:---:|:---:|
| **H1** | +1.57% | -1.57% | -0.02% | +0.02% |
| **H3** | +2.94% | -2.91% | -0.04% | +0.12% |
| **H5** | +3.88% | -3.87% | -0.10% | +0.24% |
| **H10** | +5.69% | -5.77% | -0.31% | +0.45% |
| **H20** | +7.82% | -8.26% | -0.57% | +0.55% |

### Signal-Day Price Action (Intraday & Gap)

- **Gap ($Close_{T-1} \to Open_T$)**: Signal Mean = **+0.28%** vs Control Mean = **+0.06%** (Diff: **+0.22%**)
- **Intraday ($Open_T \to Close_T$)**: Signal Mean = **+0.34%** vs Control Mean = **-0.43%** (Diff: **+0.77%**)
- **Total Day ($Close_{T-1} \to Close_T$)**: Signal Mean = **+0.62%** vs Control Mean = **-0.37%** (Diff: **+0.99%**)

---

## 11. Statistical Tests

| Horizon | Mean Difference | IID Bootstrap 95% CI | Date-Clustered 95% CI | Permutation $p$-value |
|:---|:---:|:---:|:---:|:---:|
| **H1** | -0.08% | [-0.26%, +0.11%] | [-0.38%, +0.18%] | 0.4320 |
| **H3** | -0.14% | [-0.42%, +0.18%] | [-0.63%, +0.31%] | 0.3460 |
| **H5** | -0.33% | [-0.72%, +0.08%] | [-0.96%, +0.26%] | 0.1010 |
| **H10** | -0.55% | [-1.12%, +0.02%] | [-1.37%, +0.31%] | 0.0440 |
| **H20** | -1.32% | [-2.13%, -0.54%] | [-2.37%, -0.38%] | 0.0020 |

---

## 12. Date-Clustered Results

- **Unique Signal Dates**: 229 days (out of 250).
- **Signals per Date**: Mean = 5.42, Median = 5.0, Max = 12.0, 90th percentile = 10.0.
- **Robustness Interpretation**: Date-clustered confidence intervals are wider than IID intervals due to cross-sectional correlation on high-momentum market days. The date-clustered CIs confirm that the difference between signal and control is indistinguishable from zero at H1-H5 and turns statistically significantly negative at H20.

---

## 13. Concentration Analysis

- **Top Date Clustering**: Top dates with 11-12 simultaneous signals coincided with broad market gap days (`2026-01-15`, `2026-01-19`, `2025-10-30`, `2025-10-31`, `2025-11-03`).
- **Symbol Concentration (H5 Return)**:
  - Positive contributors: `PTBA` (+2.31%, N=84), `ITMG` (+0.89%, N=110), `INCO` (+0.58%, N=115), `ADRO` (+0.37%, N=130).
  - Negative contributors: `TLKM` (-1.40%, N=76), `BBNI` (-0.77%, N=91), `BBRI` (-0.70%, N=83), `ANTM` (-0.59%, N=106), `UNTR` (-0.48%, N=128), `BMRI` (-0.44%, N=94), `BBCA` (-0.23%, N=61), `ASII` (-0.17%, N=120).
- Trimming the top/bottom 5% does not change the sign of the difference (Trimmed Diff at H5: $-0.34\%$, at H20: $-1.12\%$).

---

## 14. Market Adjustment

- **Raw vs Relative Return**: The signal produces a strong positive return on day $T$ ($+0.62\%$ raw), but subsequent forward returns show no alpha above market drift.
- **Benchmark Relationship**: Standalone index data is `UNAVAILABLE` in the local directory; cross-sectional universe control serves as the market benchmark proxy.
- **Sector Attribution**: `SECTOR_ATTRIBUTION = UNKNOWN_COMPONENT` (no granular sector indexes available; do not fabricate).

---

## 15. Signal Decomposition

### Score Tier Analysis
- **`WATCH` (Score $\ge 80$, $N=702$)**:
  - H1 Mean: -0.00%, H5 Mean: -0.05%, H20 Mean: -0.46% (Win Rate: 47.1%)
- **`EARLY_WATCH` (Score $60-79$, $N=540$)**:
  - H1 Mean: -0.01%, H5 Mean: +0.01%, H20 Mean: -0.22% (Win Rate: 48.7%)
- **Correlation with H5 Returns**:
  - `quant_score`: $r = -0.008$ ($p = 0.784$, not significant)
  - `rsi14`: $r = -0.026$ ($p = 0.378$, not significant)
  - `macd`: $r = -0.080$ ($p = 0.006$, slightly negative correlation)
  - `atr_pct`: $r = -0.065$ ($p = 0.025$, higher volatility slightly reduces H5 return)
  - `rel_vol`: $r = +0.082$ ($p = 0.004$, modest positive volume confirmation)

---

## 16. Persistence

- **Observed Pattern**: **D. Mean Reversion / Post-Momentum Exhaustion**.
- The quantitative scanner effectively detects momentum that has *already occurred* up to $Close(T)$ (with $+0.99\%$ outperformance on day $T$). However, from $Close(T)$ forward, the price action exhibits mean-reversion and underperforms the control group at H10 and H20.

---

## 17. Specificity

Attribution breakdown of the quantitative momentum signal:
- `MARKET_COMPONENT`: High (signals heavily cluster on broad market breakout days).
- `FACTOR_COMPONENT`: High (momentum/high-beta factor exposure).
- `SECTOR_COMPONENT`: `UNKNOWN_COMPONENT`.
- `COMPANY_SPECIFIC_COMPONENT`: Low / Unconfirmed.
- `UNKNOWN_COMPONENT`: Significant.

---

## 18. Limitations

1. **Universe Size**: Evaluated on 12 large-cap IDX stocks (pilot universe).
2. **Fixed Holding Periods**: Evaluated across static horizons (H1, H3, H5, H10, H20) rather than dynamic trade setups with Agent 3 entry/exit rules.
3. **Execution Assumption**: Evaluated using $Close(T) \to Close(T+h)$. Intraday execution (e.g. limit orders at pullbacks) is not modeled in pure directional alpha validation.

---

## 19. What This Proves

- The state extraction defect is completely resolved and verified by regression testing.
- Agent 1's quantitative market scanner generates signals at a predictable rate (41.4% of universe observations score $\ge 60$).
- Pure unguided quantitative momentum/breakout scores on daily closes do *not* contain positive forward alpha in the tested IDX universe over 1 to 20 day horizons.

---

## 20. What This Does NOT Prove

- This does not prove that swing trading in IDX is impossible.
- This does not prove that Agent 2 (Market Intelligence / Red Team) and Agent 3 (Risk & Timing Engine) cannot create positive Expected Value when filtering candidates.
- It proves specifically that **Agent 1 quantitative signals alone cannot be used as a standalone mechanical BUY trigger**.

---

## 21. Hypothesis Update

- **H0**: Agent 1's historical quantitative signal does not provide practically meaningful directional lift versus the eligible historical control.
- **Decision**: **FAIL TO REJECT H0**. The empirical data provides no evidence of positive directional lift from the standalone quantitative signal.

---

## 22. Final Status

# **FAIL**

*(The tested hypothesis does not demonstrate practically useful forward directional information for standalone trade execution. The quantitative scanner functions as a candidate funnel, not a standalone alpha engine).*

---

## 23. Next Bottleneck

The primary bottleneck is that Agent 1's quantitative scanner is an **attention filter (WHAT is moving)**, not an alpha generator. 

The research must now evaluate whether **Agent 2's Relational Intelligence & Red Team synthesis** combined with **Agent 3's Asymmetric Risk/Reward & Trigger Confirmation** can filter this 1,242-candidate funnel into positive Expected Value swing setups.
