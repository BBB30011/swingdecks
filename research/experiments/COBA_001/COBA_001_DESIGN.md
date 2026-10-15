# COBA_001 DESIGN: EXPERIMENTAL DESIGN FREEZE

## 1. PRIMARY RESEARCH QUESTION
**Question:** Does the quantitative signal used by SwingDeck (`arm_a_action == 'ACT'`) possess measurable directional predictive value, independent of downstream effects such as qualitative intelligence filtering and trade-management?

## 2. ESTIMAND
**Primary Estimand:**
The conditional observational difference in future outcomes between signal-exposed setups and control setups under the specified exact stratification. (Note: CAUSALITY = NOT_PROVEN).

## 3. POPULATION
**Dataset Identity:** `DATASET_V2_20260915` (Sourced identically from `reports/zzz14_8_canonical_setup_decision_matrix.csv`).
- **Population Size (N):** 1,760 setups.
- **Inclusion/Exclusion:** All 1,760 setups from ZZZ.14.9 are evaluated for support. No post-outcome filtering is applied.

## 4. TREATMENT / EXPOSURE DEFINITION
- **SIGNAL_PRESENT (Treatment):** Defined deterministically as `arm_a_action == 'ACT'`. This is a pure Agent 1 Quant signal (`mom_score >= 80`, `rel_vol >= 1.2`).
- **SIGNAL_ABSENT (Control):** Defined as `arm_a_action != 'ACT'` (which canonically consists only of `WATCH` and `WAIT` states). 

## 5. STRATIFICATION & COMMON SUPPORT
We use an **EXACT-STRATIFIED COMMON-SUPPORT SAMPLE**.
- **Strata:** `[year, market_regime, sector]`.
- **Method:** Group the population by the defined strata. Retain only strata that contain at least one Treatment observation and at least one Control observation. Keep all observations within those retained strata.
- **Support Definition:** Common-support failure is defined solely based on pre-outcome treatment/control availability. (Future outcomes are strictly prohibited from this step).

## 6. OUTCOMES & MULTIPLE TESTING
The canonical matrix provides multiple pre-calculated, PIT-isolated outcome vectors. These are grouped into two distinct outcome families with different definitions and interpretations:

**Primary Horizon:**
- `H5_PEER_EXCESS`: The canonical primary outcome established in the ZZZ research lineage.

**Secondary Horizons (Exploratory / Multiple-Comparison Subject):**
- **Short-Horizon Absolute Return Family:**
  - `H1_return`
  - `H3_return`
- **Medium/Long-Horizon Peer-Excess Family:**
  - `H10_PEER_EXCESS`
  - `H20_PEER_EXCESS`

## 7. BENCHMARKS & EFFECT SIZE
The peer-excess outcomes naturally incorporate the **Sector Baseline** (Peer Excess).
- **Effect Size Metrics to Report:** Treatment Beta ($\beta$), 95% Confidence Interval, Economically Interpretable Effect Magnitude, Total Treatment Count, Total Control Count, Retained Treatment Count, and Retained Control Count.
- **Minimum Meaningful Effect:** `MINIMUM_EFFECT_SIZE = NOT_PRE_SPECIFIED`. No arbitrary threshold will be invented post-hoc.

## 8. INFERENCE PLAN
- **Primary Inference:** Ordinary Least Squares (OLS) regression of the Outcome vector on the Treatment indicator (`signal_present`), using date-clustered standard errors.
- **Secondary Robustness:** Wild Cluster Bootstrap (Seed=149001).
- **Disagreement Policy:** If primary and secondary inference methods yield contradictory significance, it will be reported as evidence of inference sensitivity (Method Sensitive), not manipulated to force significance.

## 9. HYPOTHESES
- **$H_0$:** There is no systematic directional difference in outcomes between `SIGNAL_PRESENT` setups and `SIGNAL_ABSENT` setups within common strata.
- **$H_1$:** There is a systematic directional difference (Expectation: Positive association with forward returns).

## 10. DECISION RULES (CLASSIFICATION)
- **SIGNAL_SUPPORTED:** The pre-specified primary estimand (`H5_PEER_EXCESS`) shows the pre-specified directional effect and primary inference criteria are satisfied, with supporting evidence from secondary horizons.
- **SIGNAL_NOT_SUPPORTED:** Evidence is sufficiently precise and consistently compatible with the pre-specified null/absence boundary under the frozen decision rule.
- **INCONCLUSIVE:** Triggered by insufficient support, contradictory inference methods, insufficient common support, imprecise estimate, or unresolved methodological limitation.

## 11. PIT & SCIENTIFIC FIREWALL
- **STRICT PROHIBITION:** No Agent 2 live payload (`ide_research_BBCA_live.json`) or non-historical graph data will be used.
- **STRICT PROHIBITION:** MFE/MAE will not be used to define directional alpha.

## 12. STOPPING RULES
The experiment will be HALTED (Status: `BLOCKED`) if:
- Point-in-time leakage is detected.
- The control subset yields insufficient common support based on pre-outcome strata.
- The canonical matrix checksum fails.

## 13. REPRODUCIBILITY
All code for stratification and inference will be parameterized with a fixed random seed (`149001`). The exact execution manifest will be dumped to `COBA_001_MANIFEST.json`.
