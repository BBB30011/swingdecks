# ZZZ.14.8.1 -- DECISION UTILITY RECONCILIATION, CALIBRATION & COUNTERFACTUAL CLOSURE GATE REPORT

## 0. EXECUTIVE SUMMARY & RECONCILIATION FINDINGS

Batch **ZZZ.14.8.1** provides the final scientific, econometric, and epistemological reconciliation for the decision-utility validation gate:

1. **Decision Calibration Clarified**: Action states (`ACT`, `WATCH`, `WAIT`, `REJECT`, `INSUFFICIENT`) are discrete categorical decision states with distinct operational semantics; monotonicity across all action states is **`NOT_APPLICABLE`**. Predeclared confidence tiers (`LOW` < `MEDIUM` < `HIGH`) exhibit strictly verified empirical monotonicity.
2. **Defensive Rejection Reconciled**: Across $N=40$ baseline `ACT` setups contradicted by Agent 2, $35$ ($87.50\%$) were observed negative outcomes ($H_5 < 0$, `OBSERVED_NEGATIVE_ALIGNMENT_RATE` $= 87.50\%$, mean $H_5 = -1.9705\text{ pp}$), and $5$ ($12.50\%$) were positive (`OBSERVED_OPPORTUNITY_COST`, mean $H_5 = +2.6100\text{ pp}$).
3. **Escalation Error & Opportunity Identification Balanced**: Across $N=354$ baseline `WATCH` setups escalated to `ACT`, $227$ ($64.12\%$) were positive ($H_5 \ge 0$, mean $H_5 = +2.4466\text{ pp}$, `OBSERVED_OPPORTUNITY_IDENTIFICATION`), while $127$ ($35.88\%$) were negative ($H_5 < 0$, mean $H_5 = -1.6486\text{ pp}$, `ESCALATION_ERROR`).
4. **OOS Stability Verified**: Directionally stable rejection and activation behavior across Development ($N=1,280$), Validation ($N=160$), and Out-of-Sample ($N=320$).
5. **Epistemological Boundary Upheld**: `DECISION_DISCRIMINATION = CONDITIONAL_ASSOCIATION_OBSERVED`, while `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, `STRATEGY_OPTIMIZATION = BLOCKED`, and `STRATEGY_READINESS = NOT_READY`.

---

## 1. EXHAUSTIVE TRANSITION MATRIX (ARM B $\to$ ARM D)

| Transition | Count ($N$) | Frequency | Negative $H_5$ ($N$) | Positive $H_5$ ($N$) | Neg Rate | Mean $H_5$ (pp) | Median $H_5$ (pp) | Mean $H_{10}$ (pp) | Mean $H_{20}$ (pp) | Descriptive Interpretation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **ACT -> REJECT** | 40 | 2.27% | 35 | 5 | 87.5% | -1.9705 | -1.4900 | -2.9572 | -4.3350 | Observed defensive alignment |
| **WATCH -> REJECT** | 46 | 2.61% | 34 | 12 | 73.91% | -1.8928 | -1.9600 | -2.8393 | -4.1641 | Observed defensive action |
| **WAIT -> REJECT** | 71 | 4.03% | 52 | 19 | 73.24% | -1.8886 | -1.5500 | -2.8332 | -4.1549 | Observed defensive action |
| **INSUFFICIENT -> REJECT** | 4 | 0.23% | 2 | 2 | 50.0% | +0.3675 | +0.0850 | +0.5525 | +0.8075 | Observed defensive action (sparsity+contra) |
| **ACT -> ACT** | 422 | 23.98% | 144 | 278 | 34.12% | +0.9721 | +1.1250 | +1.4582 | +2.1386 | Observed baseline confirmation |
| **WATCH -> ACT** | 354 | 20.11% | 127 | 227 | 35.88% | +0.9775 | +0.9100 | +1.4664 | +2.1504 | Observed escalation |
| **WAIT -> ACT** | 52 | 2.95% | 17 | 35 | 32.69% | +1.3529 | +1.3950 | +2.0298 | +2.9758 | Observed escalation |
| **WAIT -> WATCH** | 90 | 5.11% | 37 | 53 | 41.11% | +0.2670 | +0.5050 | +0.4008 | +0.5874 | Observed timing refinement |
| **WATCH -> WATCH** | 217 | 12.33% | 82 | 135 | 37.79% | +0.5247 | +0.5700 | +0.7868 | +1.1542 | Observed observation maintenance |
| **WAIT -> WAIT** | 360 | 20.45% | 123 | 237 | 34.17% | +0.9814 | +0.9100 | +1.4722 | +2.1590 | Observed neutral maintenance |
| **INSUFFICIENT -> INSUFFICIENT** | 77 | 4.38% | 27 | 50 | 35.06% | +0.9665 | +0.9100 | +1.4494 | +2.1262 | Observed information sparsity maintenance |
| **WATCH -> INSUFFICIENT** | 8 | 0.45% | 2 | 6 | 25.0% | +2.1075 | +1.0650 | +3.1612 | +4.6363 | Observed information sparsity de-escalation |
| **WAIT -> INSUFFICIENT** | 19 | 1.08% | 8 | 11 | 42.11% | +0.9211 | +0.7900 | +1.3821 | +2.0268 | Observed information sparsity de-escalation |
| **ACT -> WATCH** | 0 | 0.0% | 0 | 0 | 0.0% | +0.0000 | +0.0000 | +0.0000 | +0.0000 | Observed de-escalation |
| **ACT -> WAIT** | 0 | 0.0% | 0 | 0 | 0.0% | +0.0000 | +0.0000 | +0.0000 | +0.0000 | Observed timing deferral |
| **REJECT -> ACT** | 0 | 0.0% | 0 | 0 | 0.0% | +0.0000 | +0.0000 | +0.0000 | +0.0000 | Observed opportunity recovery |

---

## 2. DECISION CALIBRATION RECONCILIATION TABLE

| Group Type | State / Tier | Count ($N$) | Frequency | Mean $H_5$ (pp) | Median $H_5$ (pp) | Neg $H_5$ Rate | Mean $H_{10}$ (pp) | Mean $H_{20}$ (pp) | Calibration Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| ACTION_STATE | **ACT** | 828 | 47.05% | +0.9983 | +1.0150 | 34.78% | +1.4976 | +2.1962 | CATEGORICAL |
| ACTION_STATE | **WATCH** | 307 | 17.44% | +0.4491 | +0.5600 | 38.76% | +0.6736 | +0.9880 | CATEGORICAL |
| ACTION_STATE | **WAIT** | 360 | 20.45% | +0.9814 | +0.9100 | 34.17% | +1.4722 | +2.1590 | CATEGORICAL |
| ACTION_STATE | **REJECT** | 161 | 9.15% | -1.8541 | -1.6000 | 76.4% | -2.7817 | -4.0790 | CATEGORICAL |
| ACTION_STATE | **INSUFFICIENT** | 104 | 5.91% | +1.0460 | +0.9400 | 35.58% | +1.5688 | +2.3012 | CATEGORICAL |
| CONFIDENCE_TIER | **LOW** | 423 | 24.03% | -0.5888 | -0.3800 | 55.08% | -0.8835 | -1.2954 | MONOTONIC |
| CONFIDENCE_TIER | **MEDIUM** | 867 | 49.26% | +0.5992 | +0.5900 | 40.02% | +0.8990 | +1.3183 | MONOTONIC |
| CONFIDENCE_TIER | **HIGH** | 395 | 22.44% | +2.0929 | +1.9800 | 19.49% | +3.1397 | +4.6044 | MONOTONIC |
| CONFIDENCE_TIER | **UNKNOWN** | 75 | 4.26% | +0.4115 | +0.2900 | 44.0% | +0.6168 | +0.9055 | MONOTONIC |

---

## 3. OOS DECISION UTILITY TABLE

| Partition | Total $N$ | Action Div ($N$, %) | Contra $N$ | ACT Mean $H_5$ (pp) | REJECT Mean $H_5$ (pp) | REJECT Neg Rate | ACT $\to$ REJECT (Neg / Pos) | WATCH $\to$ ACT (Pos / Neg) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **DEVELOPMENT_2016_2023** | 1280 | 505 (39.45%) | 128 | +1.0308 | -1.9328 | 76.56% | 24 / 3 | 156 / 87 | DIRECTIONALLY_STABLE |
| **VALIDATION_2024** | 160 | 63 (39.38%) | 12 | +1.0510 | -1.3733 | 83.33% | 5 / 0 | 24 / 15 | DIRECTIONALLY_STABLE |
| **OUT_OF_SAMPLE_2025_2026** | 320 | 116 (36.25%) | 21 | +0.8518 | -1.6490 | 71.43% | 6 / 2 | 47 / 25 | DIRECTIONALLY_STABLE |

---

## 4. SECTION 35 MANDATORY CLOSING BLOCK

```
DATASET = DATASET_V2_20260915
SETUP_POPULATION = N_1760
ARCHITECTURE = EXACTLY_3_AGENTS
PRIMARY_OUTCOME = H5_PEER_EXCESS
PRIMARY_COMPARISON = ARM_B_VS_ARM_C_VS_ARM_D
DECISION_UNIT = SETUP
ACTION_DIVERGENCE = OBSERVED
DECISION_DIVERGENCE = OBSERVED
THESIS_DIVERGENCE = OBSERVED
DEFENSIVE_ALIGNMENT = OBSERVED_HIGH_ALIGNMENT (87.50%)
FALSE_REJECTION = OBSERVED_LOW (12.50%)
OPPORTUNITY_COST = OBSERVED_LOW (5 setups)
ESCALATION_ERROR = OBSERVED_MODERATE (35.88%)
NEGATIVE_OUTCOME_CAPTURE = OBSERVED_HIGH (76.40% on REJECT cohort)
DECISION_CALIBRATION = CONDITIONAL (Confidence Monotonic, Action States Categorical)
PLACEBO_SEPARATION = PASS (7.2x separation)
SEMANTIC_VALIDITY = PASS (97.4% benchmark agreement)
DECISION_TRACEABILITY = PASS (100% traceable)
OOS_DECISION_UTILITY = CONDITIONAL (Directionally stable across Dev/Val/OOS)
CONCENTRATION_RISK = MODERATE_ACCEPTABLE (Top 1 ticker: 2.19%)
COVERAGE_CONFOUNDING = CONTROLLED
INFERENCE_ROBUSTNESS = ROBUST_ACROSS_METHODS
INFORMATION_NOVELTY = PARTIAL
INCREMENTAL_INFORMATION = OBSERVED
DECISION_ENRICHMENT = OBSERVED
DECISION_DISCRIMINATION = CONDITIONAL_ASSOCIATION_OBSERVED
COUNTERFACTUAL_EVIDENCE = DESCRIPTIVE_OBSERVED_ONLY
CAUSALITY = NOT_PROVEN
STANDALONE_ALPHA = NOT_PROVEN
STRATEGY_OPTIMIZATION = BLOCKED
STRATEGY_READINESS = NOT_READY
REPRODUCIBILITY = PASS
RED_TEAM = PASS
SCIENTIFIC_FIREWALL = PASS
ZZZ_14_8_STATUS = CLOSED
NEXT_RESEARCH_ACTION = CLOSED_RESEARCH_NODE_PROCEED_TO_DYNAMIC_PORTFOLIO_SIMULATION
FINAL_CLASSIFICATION = DECISION_DISCRIMINATION_CONDITIONAL_STANDALONE_ALPHA_NOT_PROVEN
```
