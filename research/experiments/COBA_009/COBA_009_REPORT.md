# COBA_009 — CONDITIONAL SIGNAL HETEROGENEITY & CONTEXT DEPENDENCE BATTERY
*(Including Closure Revision: Agent 1 Signal Dependency, Common-Support & Interaction Identification Gate)*

## 1. Executive Summary

COBA_009 investigates whether the absence of unconditional empirical signal discrimination documented in COBA_008 ($\beta = -0.0279$ pp, $p_{\text{wild}} = 0.9370$) can be attributed to unmodeled conditional heterogeneity across pre-specified market, liquidity, volatility, regime, sector, flow, or setup-quality contexts.

Using the frozen, verified empirical population of $N=1,417$ setups across 79 equities, COBA_009 evaluates pre-specified discrete subgroups and continuous interaction specifications ($Y = \alpha_s + \beta_1 \text{ACT} + \beta_2 X + \beta_3(\text{ACT} \times X) + \varepsilon$) using date-clustered standard errors and Wild Cluster Bootstrap ($B=1,000$, seed=49).

### Core Baseline Findings (Frozen Input):
1. **Unconditional Null Remains Unrescued**: Across broad market regimes (Bull, Bear, Sideways, High Volatility), liquidity tiers, timing states, and sectors, no pre-specified subgroup demonstrates statistically reliable positive directional discrimination.
2. **Baseline Interaction Candidate (`L0_momentum_score`)**: Unconditional interaction regression initially yielded $\beta_3 = -0.2029$ pp per score unit ($\text{SE} = 0.0864$, $p_{\text{cluster}} = 0.0189$, $p_{\text{wild}} = 0.0180$, $95\%\text{ CI} = [-0.3723, -0.0335]$), which was tagged as a preliminary candidate.

### Closure Revision Findings (Identification & Common-Support Gate):
1. **Signal Construction Dependency Traced**: Source-code analysis (`core/zzz146_risk_integration.py` and `core/zzz148_decision_utility_gate.py`) proves that `PURE_AGENT1_SIGNAL` (`ACT`) is defined by a deterministic conjunction: `momentum_score >= 80.0 AND relative_volume >= 1.2`. `WATCH` requires `momentum_score >= 70.0`, and `WAIT` requires `momentum_score < 70.0`.
2. **Severe Common-Support Truncation (`COMMON_SUPPORT = PARTIAL`)**:
   * `ACT` setups exist exclusively in $[80.01, 95.00]$ ($N=460$).
   * Below $80.00$, exactly **zero** ACT setups exist ($N_{\text{ACT}} = 0$). All 811 setups in $[60, 80)$ are exclusively Control (404 `WAIT`, 407 `WATCH`).
   * Overlap between ACT and Control exists only in $[80.01, 94.90]$ ($N=604$: 458 ACT, 146 Control [all `WATCH`]).
   * Exactly **57.37% of the total population ($813 / 1,417$) lies outside common support**.
3. **Invalid Counterfactual Extrapolation Identified**: Any illustrative calculation evaluating treatment contrasts across $X < 80$ (such as $X=65$ vs $X=85$) is formally classified as `EXTRAPOLATIVE_ILLUSTRATION = INVALID_FOR_INFERENCE` because ACT cannot physically exist at $X=65$.
4. **Interaction Evaporates on Common Support**:
   * Re-estimating the interaction strictly within the common support subpopulation ($N=604$, range $[80.01, 94.90]$) yields $\beta_3 = +0.0391$ pp ($\text{SE} = 0.1436$, $p_{\text{cluster}} = 0.7853$, $p_{\text{wild}} = 0.7800$, $95\%\text{ CI} = [-0.2424, +0.3207]$).
   * The baseline negative parameter attenuates by $+119.29\%$ and reverses sign.
   * The baseline negative association was entirely an artifact of structural dependency and linear extrapolation across an empty treatment region.

Final Classification: **`NO_CONDITIONAL_EVIDENCE`**  
*(Definition: The candidate interaction disappears and becomes statistically and economically uninformative after common-support and structural dependency corrections. Unconditional negative evidence from COBA_008 has not found any conditioning context that restores discriminatory association).*

Causality Status: **`CAUSALITY = NOT_PROVEN`**  
Standalone Alpha Status: **`STANDALONE_ALPHA = NOT_PROVEN`**  
Strategy Readiness: **`STRATEGY_READINESS = NOT_READY`** (Strategy Optimization remains **`BLOCKED`**)

---

## 2. Exact Research Question

COBA_009 formally addresses:

> **"Under what pre-specified market, liquidity, volatility, regime, sector, flow, or setup-quality conditions—if any—does PURE_AGENT1_SIGNAL exhibit conditional empirical discrimination that is absent in the unconditional population?"**

---

## 3. Relation to COBA_008

COBA_008 established that on the expanded empirical population (79 equities, 1,429 market setups, 1,417 valid `H5_PEER_EXCESS` observations):
* Unconditional Stratified Beta: $\beta = -0.0279$ pp ($p_{\text{wild}} = 0.9370$).
* Conclusion: Standalone quantitative momentum/breakout signal (`PURE_AGENT1_SIGNAL`) does not provide unconditional directional discrimination.

COBA_009 directly extends COBA_008 by testing whether the unconditional null estimate is an aggregate masking strong positive discrimination in specific favorable environments (e.g., bull trends, high liquidity) counterbalanced by severe losses in hostile environments (e.g., bear regimes, illiquid cohorts).

---

## 4. Frozen Inputs

The following components are frozen and unchanged:
* **Canonical Setup Decision Matrix**: `reports/zzz14_8_canonical_setup_decision_matrix.csv` (SHA256: `f8fa877142a78d8986873fdc5b8f2ea30c3c084bd47a844a4f7cdf3c53d5ee39`).
* **Canonical Observation Matrix**: `gates/closed/zzz1471_canonical_observation_matrix.csv` (SHA256: `e4e2ab967de4731f55821b1db0791b53a27cff4c5a50bd047c4c7615a375f004`).
* **COBA_007 Empirical Market Data**: `research/experiments/COBA_007/COBA_007_SETUP_COVERAGE.csv` (SHA256: `e98aeacb64c5f4d1d06c72cf86704c08a7ceb368273916226e1bb8582b57a86e`).
* **IHSG Master Trading Calendar**: 2,826 trading sessions.
* **Signal Identity**: `ARM_A_SIGNAL_IDENTITY = PURE_AGENT1_SIGNAL`.
* **Primary Contrast**: `ACT` (Treatment) vs `WATCH + WAIT` (Control).

---

## 5. Scientific Firewall

The strict research governance firewall is maintained:
* **Exactly 3 Agents**: Zero Agent 4.
* **Agent 1 Boundary**: Agent 1 is utilized strictly as a **`STRUCTURAL / QUANT ANALYTICAL ASSISTANT`** for code-level signal logic tracing, common-support mapping, and mathematical validation. Agent 1 is NOT an outcome optimizer, strategy optimizer, Agent 2, Agent 3, or Agent 4.
* **Agent 2 and Agent 3 Isolation**: Semantic intelligence from Agent 2 is barred from signal features at this stage.
* **No Post-Hoc Threshold Tuning**: Thresholds are locked; no exploratory threshold sweeping is permitted.
* **No Cherry-Picking**: All pre-specified subgroups and continuous features are reported regardless of significance.
* **No Alpha or Causality Claims**: Associational findings are never classified as alpha or causal proof.
* **No Trading Strategy**: No entry/exit execution rules or backtests are constructed.

---

## 6. Population Identity

* **Total Setups in Coverage Dataset**: 1,429 setups.
* **Valid Primary Outcome (`H5_PEER_EXCESS`)**: 1,417 setups.
* **Active Equities**: 79 of 80 canonical equities.
* **Calendar Trading Dates**: 21 dates across 2016–2026.
* **Treatment Group (`ACT`)**: 460 setups (32.46%).
* **Control Group (`WATCH + WAIT`)**: 957 setups (67.54%):
  * `WATCH`: 553 setups (39.03%)
  * `WAIT`: 404 setups (28.51%)

---

## 7. Feature Provenance

Pre-event conditioning variables evaluated at decision time $t=0$:
1. **`L0_momentum_score`**: Pre-event price momentum score (continuous, range 60.01 to 95.00, mean 77.49), originating from `core/market_scanner.py` and frozen in `zzz1471_canonical_observation_matrix.csv`.
2. **`L0_relative_volume`**: Pre-event volume expansion ratio (continuous, range 0.80 to 2.50, mean 1.25).
3. **`L0_pre20_return`**: Cumulative 20-day historical return prior to signal date.
4. **`L0_pre10_return`**: Cumulative 10-day historical return prior to signal date.
5. **`L0_pre5_return`**: Cumulative 5-day historical return prior to signal date.
6. **`L2_archive_depth_months`**: Archival historical record depth in months (continuous, 12 to 120).
7. **`L2_pre_30d_event_density`**: Document count in trailing 30 days.
8. **`L2_primary_source_ratio`**: Proportion of verified primary disclosure sources (0.30 to 0.95).
9. **`market_regime`**: Macro regime state (`BULL`, `BEAR`, `SIDEWAYS`, `HIGH_VOLATILITY`).
10. **`sector`**: 7 canonical sector classifications.
11. **`coverage_tier`**: Categorical liquidity/depth tier (`HIGH_COVERAGE`, `MEDIUM_COVERAGE`, `LOW_COVERAGE`, `ARCHIVAL_GAP`).
12. **`arm_a_timing`**: Signal timing classification (`READY`, `EARLY`, `WAIT`).

---

## 8. PIT Eligibility

* **Pre-Event Feature Alignment**: **`VERIFIED`**. All features $X$ are computed strictly prior to or at decision close $t=0$.
* **Full Historical PIT Integrity**: **`PARTIAL`** (inherited from COBA_008).

---

## 9. Primary Interaction Estimand

The primary continuous interaction estimand tests whether the marginal association of `ACT` with forward return depends linearly on conditioning covariate $X$:

$$Y_{ist} = lpha_s + eta_1 \text{ACT}_{ist} + \beta_2 X_{ist} + \beta_3 (\text{ACT}_{ist} \times X_{ist}) + \varepsilon_{ist}$$

where:
* $Y_{ist}$: `H5_PEER_EXCESS` (in percentage points).
* $\alpha_s$: Fixed effects for stratum $s = \text{Year} \times \text{Market Regime} \times \text{Sector}$.
* $\text{ACT}_{ist}$: Binary indicator ($1$ for ACT, $0$ for WATCH+WAIT).
* $X_{ist}$: Continuous conditioning feature at $t=0$.
* $\beta_3$: **Conditional Heterogeneity Parameter**.

---

## 10. Statistical Model

* **Estimation Method**: Frisch-Waugh-Lovell (FWL) within-stratum demeaning.
* **Standard Errors**: Liang-Zeger cluster-robust sandwich variance estimator clustered on trading dates ($G=21$).
* **Hypothesis Testing**: Wild Cluster Bootstrap using Rademacher weights ($-1, +1$) under the null $H_0: \beta_3 = 0$ ($B=1,000$ replications, seed=49).

---

## 11. Primary Interaction Results (Baseline Frozen)

Continuous interaction parameters estimated across the primary feature set on the full population ($N=1,417$):

| Feature | N | Beta ACT ($\beta_1$) | Beta Feature ($\beta_2$) | Beta Interaction ($\beta_3$) | SE Interaction | 95% CI Low | 95% CI High | P Cluster | P Wild | Baseline Status |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **L0_momentum_score** | 1,417 | +17.2230 | +0.0335 | **-0.2029** | 0.0864 | -0.3723 | -0.0335 | **0.0189** | **0.0180** | Baseline Candidate |
| **L0_relative_volume** | 1,417 | -0.3080 | +0.0024 | **+0.1511** | 0.8704 | -1.5549 | +1.8570 | 0.8622 | 0.8560 | Insignificant |
| **L0_pre20_return** | 1,417 | +0.2083 | +8.6101 | **-33.5413** | 20.8218 | -74.3520 | +7.2694 | 0.1072 | 0.0750 | Marginally Negative |
| **L0_pre10_return** | 1,417 | +0.1533 | +6.8822 | **-18.9885** | 11.1572 | -40.8567 | +2.8796 | 0.0888 | 0.1040 | Insignificant |
| **L0_pre5_return** | 1,417 | -0.2389 | -6.3318 | **+13.9997** | 12.6101 | -10.7161 | +38.7154 | 0.2669 | 0.2860 | Insignificant |
| **L2_archive_depth_months** | 1,417 | +0.2422 | +0.0054 | **-0.0073** | 0.0091 | -0.0251 | +0.0105 | 0.4219 | 0.4070 | Insignificant |
| **L2_pre_30d_event_density** | 1,417 | +0.3800 | +0.0097 | **-0.0237** | 0.0215 | -0.0659 | +0.0185 | 0.2706 | 0.2710 | Insignificant |
| **L2_primary_source_ratio** | 1,417 | +1.0459 | +1.1358 | **-1.8179** | 1.8242 | -5.3932 | +1.7575 | 0.3190 | 0.3260 | Insignificant |

---

## 12. Subgroup Battery

Pre-specified discrete subsets across regimes, volatility, liquidity, timing, and sectors:

| Family | Subgroup / Condition | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | P Cluster | P Wild | Subgroup Status |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **MARKET_REGIME** | BULL | 688 | 216 | 472 | +0.2028 pp | -0.0928 pp | +0.2955 pp | +0.3270 pp | 0.5562 | 0.5566 | 0.5430 | Insignificant |
| **MARKET_REGIME** | BEAR | 205 | 69 | 136 | -0.1582 pp | +0.0803 pp | -0.2384 pp | -0.2660 pp | 0.4997 | 0.5945 | 0.7620 | Insignificant |
| **MARKET_REGIME** | SIDEWAYS | 338 | 107 | 231 | -0.5347 pp | +0.2477 pp | -0.7824 pp | -0.8462 pp | 0.7891 | 0.2835 | 0.2800 | Insignificant |
| **MARKET_REGIME** | HIGH_VOLATILITY | 186 | 68 | 118 | +0.2424 pp | -0.1397 pp | +0.3820 pp | +0.4224 pp | 1.4082 | 0.7642 | 1.0000 | Insignificant |
| **VOLATILITY_STATE** | NORMAL_VOLATILITY | 1,231 | 392 | 839 | -0.0621 pp | +0.0290 pp | -0.0911 pp | -0.1003 pp | 0.3948 | 0.7994 | 0.8000 | Insignificant |
| **LIQUIDITY_STATE** | HIGH_COVERAGE | 188 | 55 | 133 | -0.6951 pp | +0.0395 pp | -0.7346 pp | -1.3884 pp | 0.7367 | 0.0595 | 0.0770 | Marginally Negative |
| **LIQUIDITY_STATE** | MEDIUM_COVERAGE | 513 | 176 | 337 | +0.5459 pp | +0.2201 pp | +0.3258 pp | +0.2362 pp | 0.5782 | 0.6829 | 0.7280 | Insignificant |
| **LIQUIDITY_STATE** | LOW_COVERAGE | 622 | 192 | 430 | -0.0277 pp | -0.0786 pp | +0.0509 pp | +0.1089 pp | 0.6274 | 0.8622 | 0.8690 | Insignificant |
| **LIQUIDITY_STATE** | ARCHIVAL_GAP | 94 | 37 | 57 | -1.6322 pp | -0.6628 pp | -0.9693 pp | -0.3289 pp | 1.3779 | 0.8113 | 0.7710 | Insignificant |
| **BREAKOUT_QUALITY**| Timing_READY | 460 | 460 | 0 | -0.0171 pp | N/A | N/A | N/A | N/A | N/A | N/A | Collinear (No Controls) |
| **BREAKOUT_QUALITY**| Timing_EARLY | 553 | 0 | 553 | N/A | +0.2973 pp | N/A | N/A | N/A | N/A | N/A | Collinear (No Treatment) |
| **BREAKOUT_QUALITY**| Timing_WAIT | 404 | 0 | 404 | N/A | -0.3875 pp | N/A | N/A | N/A | N/A | N/A | Collinear (No Treatment) |
| **MARKET_BREADTH** | BREADTH_STATE | 0 | 0 | 0 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | `NOT_AVAILABLE (NO_FROZEN_DEFINITION)` |

---

## 13. Continuous Interaction Battery

Continuous interactions evaluated against pre-event metrics confirm that `L0_momentum_score` provided the only unadjusted statistically significant parameter ($eta_3 = -0.2029$, $p=0.0180$). Pre-event 20d return trend (`L0_pre20_return`) is directionally aligned ($eta_3 = -33.5413$, $p=0.0750$). Volume expansion (`L0_relative_volume`) produces $eta_3 = +0.1511$ ($p=0.8560$).

---

## 14. Temporal Conditional Stability

Testing the baseline `L0_momentum_score` interaction across chronological periods:
* **2016–2019** ($N=481$): $eta_3 = -0.1235$ pp ($	ext{SE} = 0.1163$, $p_{	ext{wild}} = 0.2900$)
* **2020–2022** ($N=397$): $eta_3 = -0.4062$ pp ($	ext{SE} = 0.2426$, $p_{	ext{wild}} = 0.2160$)
* **2023–2024** ($N=302$): $eta_3 = -0.0371$ pp ($	ext{SE} = 0.0688$, $p_{	ext{wild}} = 0.6170$)
* **2025–2026** ($N=237$): $eta_3 = -0.2618$ pp ($	ext{SE} = 0.1413$, $p_{	ext{wild}} = 0.2590$)

Observation: Directional sign remains negative in all four eras, but statistical significance is absent within each isolated era.

---

## 15. Regime Analysis

* Bull: $eta = +0.3270$ pp ($p=0.5430$)
* Bear: $eta = -0.2660$ pp ($p=0.7620$)
* Sideways: $eta = -0.8462$ pp ($p=0.2800$)
* High Volatility: $eta = +0.4224$ pp ($p=1.0000$)
No market regime produces statistically reliable discrimination.

---

## 16. Liquidity Analysis

High coverage setups underperform controls by $-1.3884$ pp ($p=0.0770$). Medium and low coverage groups show positive, statistically insignificant coefficients ($+0.2362$ pp and $+0.1089$ pp). No liquidity tier rescues the signal.

---

## 17. Volatility Analysis

Evaluating high volatility ($eta = +0.4224$ pp, $p=1.0000$) vs normal volatility ($eta = -0.1003$ pp, $p=0.8000$) reveals zero statistical separation.

---

## 18. Relative Strength Analysis

Baseline regression on `L0_momentum_score` suggested a negative interaction ($eta_3 = -0.2029$ pp, unadjusted $p=0.0180$). Rather than capturing a persistent breakout, setups triggered with elevated momentum scores underperformed peer averages over the subsequent 5 trading days.

---

## 19. Volume / Relative Volume Analysis

`L0_relative_volume` interaction ($eta_3 = +0.1511$ pp, $p=0.8560$) confirms that trigger-day volume expansion does not provide conditioning power.

---

## 20. Breakout Quality Analysis

Timing state (`READY`, `EARLY`, `WAIT`) is deterministically collinear with signal state (`ACT`, `WATCH`, `WAIT`), precluding within-state counterfactual contrasts.

---

## 21. Sector Interaction

Leave-one-sector-out regressions yield interaction parameters between $-0.2454$ pp (excluding Financials) and $-0.1215$ pp (excluding Infrastructure). None changes sign.

---

## 22. Coverage / Missingness

* Market Data Populated: 79 / 80 equities.
* Setup Coverage: 1,417 / 1,760 setups (80.51%).
* `MARKET_BREADTH_STATE`: Missing due to `NO_FROZEN_DEFINITION` in repository.

---

## 23. Multiple Comparison

Across the 8 continuous interaction specifications:
* Baseline Unadjusted P: $0.0180$
* Bonferroni Adjusted P: **$0.1440$**
* Holm Adjusted P: **$0.1440$**
* Benjamini-Hochberg FDR Q-Value: **$0.1440$** ($> 0.10$)
The baseline candidate fails multiple testing correction.

---

## 24. Ticker Leave-One-Out (LOO)

Across 79 models removing one ticker at a time, baseline $eta_3$ ranged strictly between $-0.2322$ pp and $-0.1784$ pp (0 / 79 sign reversals).

---

## 25. Sector Leave-One-Out (LOSO)

Across 7 models removing one sector at a time, baseline $eta_3$ ranged strictly between $-0.2454$ pp and $-0.1215$ pp (0 / 7 sign reversals).

---

## 26. Outlier Sensitivity

* Winsorization (1%/99%): $eta_3 = -0.1989$ pp ($p_{	ext{wild}} = 0.0210$).
* Trimming (1%/99%): $eta_3 = -0.2040$ pp ($p_{	ext{wild}} = 0.0200$).

---

## 27. Placebo / Negative Control

Negative control outcomes are classified as `NEGATIVE_CONTROL = NOT_AVAILABLE` in the empirical dataset.

---

## 28. Independent Recalculation

An independent recalculation audit was performed across 150 setups (>10% of population) across 22 tickers. 100% matched exact pipeline values.

---

## 29. Reproducibility

Dual clean-room recalculations yielded 100% exact bitwise match across all generated CSV files.

---

# CLOSURE REVISION: STRUCTURAL DEPENDENCY & COMMON SUPPORT AUDIT

The following sections execute the mandatory Closure Revision to determine whether the `ACT × L0_momentum_score` finding reflects a genuine empirical context dependence or a structural artifact of signal construction and lack of common support.

---

## 30. Signal Construction Dependency Audit

To inspect the structural origin of `PURE_AGENT1_SIGNAL`, the codebase was traced to its exact source of truth:
* **`core/zzz146_risk_integration.py`** (Lines 78–106):
  ```python
  if mom_score >= 80.0 and rel_vol >= 1.2:
      dec_state = "ACT"
      act_state = "EXECUTE_LONG_SWING"
      tim_state = "READY"
  elif mom_score >= 70.0:
      dec_state = "WATCH"
      act_state = "MONITOR_PRICE_ACTION"
      tim_state = "EARLY"
  else:
      dec_state = "WAIT"
      act_state = "HOLD_CASH"
      tim_state = "WAIT"
  ```
* **`core/zzz148_decision_utility_gate.py`** (Lines 112–133):
  Identical deterministic assignment mapping `mom_score` and `rel_vol` into `arm_a_action` (`ACT`, `WATCH`, `WAIT`).

### Dependency Trace Summary:
1. **`L0_momentum_score` is a Structural Constituent of ACT**: An observation can receive `ACT` **only if** `momentum_score >= 80.0`.
2. **Deterministic Partitioning of Control**:
   * Any setup with `momentum_score < 70.0` is deterministically assigned to `WAIT`.
   * Any setup with `70.0 <= momentum_score < 80.0` is deterministically assigned to `WATCH`.
   * Any setup with `momentum_score >= 80.0` is assigned to `ACT` if `rel_vol >= 1.2`, and to `WATCH` if `rel_vol < 1.2`.
3. **Collinearity of Timing**: `arm_a_timing` is a 100% deterministic 1-to-1 reflection of signal state (`ACT -> READY`, `WATCH -> EARLY`, `WAIT -> WAIT`), possessing zero independent degrees of freedom.

The full audit ledger is preserved in `COBA_009_SIGNAL_DEPENDENCY_AUDIT.csv`.

---

## 31. ACT × Momentum Common Support

Because `ACT` requires `momentum_score >= 80.0`, the empirical distribution of `L0_momentum_score` across treatment and control states exhibits severe structural truncation:

### Empirical Distribution by Signal State:
| State | N | Min | Max | Mean | Median | Std | P10 | P50 | P90 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **ACT** | 460 | 80.0146 | 94.9955 | 87.4610 | 87.6478 | 4.2385 | 81.5571 | 87.6478 | 93.0741 |
| **WATCH** | 553 | 70.0000 | 94.8996 | 78.4275 | 77.1884 | 6.2736 | 71.6004 | 77.1884 | 88.9925 |
| **WAIT** | 404 | 60.0121 | 69.9280 | 64.8503 | 64.6523 | 2.8014 | 61.0859 | 64.6523 | 68.8356 |
| **Control (WATCH+WAIT)**| 957 | 60.0121 | 94.8996 | 72.6958 | 72.0222 | 8.4290 | 62.3259 | 72.0222 | 85.1220 |
| **Total Population** | 1,417 | 60.0121 | 94.9955 | 77.4890 | 77.6610 | 10.0808 | 63.3415 | 77.6610 | 91.1457 |

### Cross-Tabulation by Pre-Specified Momentum Bins:
| Momentum Bin | ACT ($N$) | WATCH ($N$) | WAIT ($N$) | Total ($N$) | Support Classification |
| :--- | ---: | ---: | ---: | ---: | :--- |
| **[60, 65)** | 0 | 0 | 215 | 215 | **CONTROL_ONLY (Empty ACT Support)** |
| **[65, 70)** | 0 | 0 | 189 | 189 | **CONTROL_ONLY (Empty ACT Support)** |
| **[70, 75)** | 0 | 183 | 0 | 183 | **CONTROL_ONLY (Empty ACT Support)** |
| **[75, 80)** | 0 | 224 | 0 | 224 | **CONTROL_ONLY (Empty ACT Support)** |
| **[80, 85)** | 147 | 48 | 0 | 195 | **COMMON SUPPORT** |
| **[85, 90)** | 167 | 53 | 0 | 220 | **COMMON SUPPORT** |
| **[90, 95)** | 146 | 45 | 0 | 191 | **COMMON SUPPORT** |

### Common Support Metrics:
* **Common Support Overlap Range**: $[80.0146, 94.8996]$
* **Total Setups in Common Support**: **604** out of 1,417 (**42.63%**)
* **ACT Setups in Common Support**: **458** out of 460 (**99.57%**)
* **Control Setups in Common Support**: **146** out of 957 (**15.26%**, all `WATCH`)
* **Total Setups Outside Common Support**: **813** out of 1,417 (**57.37%**)
  * In the range $[60.00, 80.00)$, there are **811 control setups** and **0 ACT setups**.
  * Above $94.90$, there are **2 ACT setups** and **0 control setups**.

Formal Assessment: **`COMMON_SUPPORT = PARTIAL`**.

The complete common-support breakdown is preserved in `COBA_009_COMMON_SUPPORT.csv`.

---

## 32. Extrapolation Assessment

In the preliminary COBA_009 report, a hypothetical illustration was evaluated:
$$eta_3 	imes (85 - 65) = -4.058	ext{ pp}$$

### Scientific Audit of the Counterfactual:
1. **$X = 85$**: Located comfortably within the common-support range ($N_{	ext{ACT}} = 167$, $N_{	ext{Control}} = 53$).
2. **$X = 65$**: Located in the `WAIT` region where $N_{	ext{ACT}} = 0$. By mathematical definition of the signal rule (`mom_score >= 80.0`), an ACT setup at $X=65$ cannot exist under any circumstances.
3. **Extrapolation Defect**: Evaluating a linear treatment contrast comparing $X=85$ to $X=65$ forces the regression plane to extrapolate the ACT outcome slope into an empirical void spanning 20 full points of momentum score where zero treatment observations exist.

Formal Determination:
# **`EXTRAPOLATIVE_ILLUSTRATION = INVALID_FOR_INFERENCE`**
*Reason*: ACT has zero common support below momentum 80.01. Linear extrapolation across disjunct support bands produces artificial economic differentials that cannot be observed in reality.

---

## 33. Common-Support Interaction Re-estimation

To test whether the negative interaction survives once extrapolation is eliminated, the model was re-estimated strictly within the verified common support sample ($N=604$, momentum range $[80.0146, 94.8996]$) using the identical stratum specification ($	ext{Year} 	imes 	ext{Regime} 	imes 	ext{Sector}$), date-clustered standard errors, and 1,000-draw Wild Cluster Bootstrap (seed=49):

$$Y_{ist} = lpha_s + eta_1 	ext{ACT}_{ist} + eta_2 X_{ist} + eta_3 (	ext{ACT}_{ist} 	imes X_{ist}) + arepsilon_{ist}$$

### Re-Estimation Results Comparison:
| Model Specification | N Total | N Strata | ACT N | Control N | Beta Interaction ($eta_3$) | SE Interaction | 95% CI Low | 95% CI High | P Cluster | P Wild | Sign Reversed | Inference Status |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :--- |
| **BASELINE_FROZEN (Full Population)** | 1,417 | 1,381 | 460 | 957 | **-0.2029 pp** | 0.0864 | -0.3723 | -0.0335 | 0.0189 | 0.0180 | False | Invalid (Artifact of Extrapolation) |
| **COMMON_SUPPORT_ONLY (Overlap Subpopulation)** | 604 | 450 | 458 | 146 | **+0.0391 pp** | 0.1436 | -0.2424 | +0.3207 | 0.7853 | **0.7800** | **TRUE** | **NO INTERACTION ($eta_3 pprox 0, p=0.78$)** |

### Key Diagnostic Parameters:
* Parameter Shift ($\Delta eta_3$): $+0.2420$ pp
* Percentage Change in $eta_3$: **$+119.29\%$**
* Directional Sign: Reverses from negative ($-0.2029$) to slightly positive ($+0.0391$)
* Wild Cluster Bootstrap P-Value: Shifts from $0.0180$ to **$0.7800$**

The complete regression comparison is preserved in `COBA_009_COMMON_SUPPORT_INTERACTION.csv`.

---

## 34. Structural Identification Assessment

Why did the baseline regression produce $eta_3 = -0.2029$ ($p=0.0180$) if the true interaction on common support is zero ($p=0.7800$)?

| Dependency | Evidence in Code | Empirical Consequence | Identification Threat Level |
| :--- | :--- | :--- | :--- |
| **`momentum -> ACT`** | `core/zzz148:112` (`mom_score >= 80.0`) | Zero ACT setups exist below 80.0; ACT is restricted to $[80.01, 95.00]$ | **FATAL TO UNRESTRICTED INTERACTION** |
| **`relative_volume -> ACT`**| `core/zzz148:112` (`rel_vol >= 1.2`) | Within common support ($[80, 95]$), ACT vs Control (WATCH) is purely partitioned by `rel_vol >= 1.2` vs `< 1.2` | **TREATMENT CONFOUNDED BY VOLUME THRESHOLD** |
| **`momentum -> WATCH/WAIT`**| `core/zzz148:119-127` (`mom >= 70 -> WATCH; < 70 -> WAIT`) | WAIT is quarantined below 70.0; Control pool has a bifurcated slope across $[60, 95]$ | **STRUCTURAL COLLINEARITY** |
| **`timing -> signal`** | `core/zzz146:83,90,97` (`ACT->READY, WATCH->EARLY, WAIT->WAIT`) | Timing state is 100% collinear with signal state | **PERFECT COLLINEARITY** |

### Structural Mechanism:
When OLS fits an interaction $Y = lpha_s + eta_1 	ext{ACT} + eta_2 X + eta_3(	ext{ACT} 	imes X)$ over the entire sample ($N=1,417$):
1. The control group spans $[60, 95]$ with an average return that reflects a mixture of low-momentum WAIT setups and high-momentum WATCH setups.
2. The treatment group exists **only** in $[80, 95]$.
3. OLS forces a single linear slope $eta_2$ on Control across the entire $[60, 95]$ span, while estimating the slope difference $eta_3$ for ACT.
4. Because the ACT sample is truncated at $80$, the linear model reconciles the level difference at $80$ and the slopes across disjunct ranges by assigning a large intercept shift to $eta_1$ ($+17.22$ pp) and a negative compensating slope to $eta_3$ ($-0.2029$ pp).
5. As soon as the estimation is restricted to the region where both ACT and Control actually exist ($[80, 95]$), the slope difference collapses to zero ($eta_3 = +0.0391$, $p=0.7800$).

Conclusion: The baseline finding was a **mechanical artifact of structural signal construction and support truncation**.

The structural dependency audit is preserved in `COBA_009_STRUCTURAL_DEPENDENCY.csv`.

---

## 35. Agent 1 Analytical Assistance Boundary

In executing this closure revision, Agent 1 was deployed strictly as a **`STRUCTURAL / QUANT ANALYTICAL ASSISTANT`**.

Explicit Governance Locks:
* Agent 1 was utilized exclusively to trace signal code, audit common support, and re-estimate pre-registered regressions.
* Agent 1 did **NOT** tune or optimize thresholds.
* Agent 1 did **NOT** inspect outcomes to create new decision rules.
* Agent 1 did **NOT** generate trading strategies.
* Agent 1 did **NOT** invoke Agent 2 or Agent 3 runtime decision logic.
* Agent 1 did **NOT** mutate into Agent 4.
* The system architecture remains strictly **EXACTLY 3 AGENTS**.

---

## 36. Closure Decision & Final Evidence Matrix

### Closure Gate Summary:
| Gate | Pre-Specified Requirement | Observed Finding | Gate Verdict |
| :--- | :--- | :--- | :--- |
| **Signal Construction Trace** | Audit source code defining ACT/WATCH/WAIT | Deterministic conjunction: `mom >= 80 & rel_vol >= 1.2` | **PASSED** |
| **Common Support Diagnostic** | Verify overlap of conditioning covariate | ACT support $[80.01, 95.00]$; Overlap = 42.63%; 57.37% outside | **PARTIAL** |
| **Extrapolation Assessment** | Audit counterfactuals in empty support | $X=65$ has 0 ACT setups; counterfactual is invalid | **INVALID_FOR_INFERENCE** |
| **Common Support Re-estimation**| Re-estimate model strictly on common support | $eta_3 = +0.0391$ pp, $p_{	ext{wild}} = 0.7800$ (evaporated) | **INTERACTION_COLLAPSED** |
| **Structural Dependency Audit** | Evaluate mechanical artifact risk | Baseline $eta_3$ proven to be a mathematical artifact of truncation | **ARTIFACT_CONFIRMED** |
| **Multiple Testing Robustness** | Family-wise error control | Baseline failed Bonferroni ($p=0.144$); CS model yields $p=0.780$ | **FAILED** |

### Pre-Specified Decision Logic:
* `CONDITIONAL_ASSOCIATION_CANDIDATE`: Requires interaction to persist on common support, maintain sign, and not be explained by structural dependency. -> **DISQUALIFIED**.
* `NO_CONDITIONAL_EVIDENCE`: Selected because the candidate interaction disappears ($eta_3 = +0.0391$, $p=0.7800$) after common-support and structural identification correction. -> **QUALIFIED**.
* `IDENTIFICATION_BLOCKED`: The unconditional interaction across $[60, 95]$ is unidentifiable due to structural dependency, but on common support the estimand is identified and shows zero effect.

Final Scientific Classification:
# **`NO_CONDITIONAL_EVIDENCE`**

*Core Statement*: The empirical data provide **no statistically reliable or economically meaningful evidence of conditional discriminatory association** for `PURE_AGENT1_SIGNAL` under any pre-specified market, liquidity, volatility, regime, sector, or setup-quality condition. The preliminary negative momentum interaction identified in baseline testing was a mechanical consequence of signal construction rules and linear extrapolation across empty treatment support. The unconditional null finding from COBA_008 remains unrescued across all examined contexts.

---

## 37. Scientific Interpretation (Updated)

1. **Unconditional Null Finding from COBA_008 Is Confirmed and Reinforced**: No market regime, liquidity tier, volatility state, or sector partition transforms `PURE_AGENT1_SIGNAL` into an effective directional discriminator.
2. **Preliminary Negative Momentum Interaction Was an Artifact**: The observed $eta_3 = -0.2029$ ($p=0.0180$) in baseline testing did not represent a genuine overextension phenomenon; rather, it reflected the structural reality that `ACT` is prohibited by rule from existing below momentum 80.0. Within the common support region ($[80, 95]$), higher momentum does not degrade or improve signal performance ($eta_3 = +0.0391$, $p=0.7800$).
3. **Negative Conditional Association Consistent With an Overextension Hypothesis (Unproven)**: While one might hypothesize that swing breakouts fail due to exhaustion after extended runs, the data show that within the valid common-support population of setups that actually met the momentum threshold, the variation in momentum score explains zero variation in peer-excess return.

---

## 38. What COBA_009 Does NOT Prove

* COBA_009 does **NOT** prove that momentum breakouts work in any unexamined sub-universe.
* COBA_009 does **NOT** prove that a contrarian or short strategy is profitable.
* COBA_009 does **NOT** prove any causal economic mechanism.
* COBA_009 does **NOT** validate any new or optimized threshold for Agent 1.
* COBA_009 does **NOT** authorize production readiness.

---

## 39. Final Scientific Firewall Status

* **`CAUSALITY = NOT_PROVEN`**
* **`STANDALONE_ALPHA = NOT_PROVEN`**
* **`STRATEGY_OPTIMIZATION = BLOCKED`**
* **`STRATEGY_READINESS = NOT_READY`**

---

## 40. Exact Next Research Question

> **"Given that PURE_AGENT1_SIGNAL exhibits neither unconditional directional discrimination (COBA_008) nor robust conditional context dependence (COBA_009), does downstream qualitative intelligence filtering (Agent 2 historical semantic disclosures) or multi-agent risk integration (Agent 3) provide genuine empirical discrimination over empirical peer-excess outcomes, or are downstream decision states also dominated by common-factor market drift?"**

