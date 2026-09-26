# BATCH ZZZ.8.1 — ABLATION & SELECTION ROBUSTNESS EXPERIMENT REPORT

**Document Type:** Scientific Research & Selection Robustness Audit Report  
**Batch ID:** BATCH-ZZZ.8.1  
**As-Of Timestamp:** 2026-09-14T16:30:00+07:00  
**Status:** COMPLETE / FROZEN  
**Final Verdict:** `PASS — PROMISING BUT CONDITIONAL`

---

## 1. Executive Summary & Mission Objective

In Batch ZZZ.8, the 6-layer multi-agent evaluation demonstrated an incremental forward Expected Value (EV) progression:
* **Baseline (Agent 1 Alone):** $H_5 = -0.02\%$ ($N = 1,242$)
* **Layer B (Differential Intelligence):** $H_5 = +0.32\%$ ($N = 252$)
* **Layer E (Full 3-Agent Synthesis):** $H_5 = +1.27\%$ ($N = 73$, full $\Delta EV = +1.30\%$)

However, ZZZ.8 left an essential scientific question unanswered:
> **Which component(s) actually contribute incremental forward EV, and is the Layer E improvement robust or merely a selection/concentration effect?**

Batch ZZZ.8.1 executed a **controlled ablation and selection robustness experiment** across 3,000 historical observations (1,242 Agent 1 candidates, 1,758 controls) without altering Agent 1 indicators, loosening risk gates, or hunting for parameters.

### Core Key Findings:
1. **Flow / Relative Volume ($C_4/C_5$) is the Largest Single EV Contributor:**
   Removing Relative Volume ($> 1.2$) collapses $H_5$ from $+1.27\%$ to $+0.32\%$ ($\Delta H_5 = +0.95\%$) and crashes $H_{10}$ from $+2.20\%$ to $-0.02\%$ ($\Delta H_{10} = +2.23\%$). Volume acceleration is the primary driver of forward follow-through.
2. **Opportunity Score is a Composite Gate (`AGENT3_COMPOSITE_DEPENDENCY = TRUE`):**
   `opportunity_score >= 60.0` is algebraically identical to the conjunction of `(quant_score >= 80) & (rel_vol > 1.2)`. It adds **no independent incremental information** beyond those two upstream features ($\Delta N = 0, \Delta H_5 = 0.00\%$).
3. **Sector Alignment ($C_1$) Prunes Broad Noise:**
   Requiring contextual peer alignment (`SECTOR_WIDE`) removes 211 non-aligned setups, lifting $H_5$ from $+0.75\%$ to $+1.27\%$ ($\Delta H_5 = +0.52\%$).
4. **Heavy Date Concentration Identified:**
   Top 1 date accounts for **29.35%** of total return sum; Top 3 dates account for **69.57%**; Top 5 dates account for **101.88%**. When the top 5 dates are excluded, $H_5$ drops to $-0.03\%$, though $H_{10}$ remains positive at $+0.84\%$.
5. **Matched-Selection Controls Confirm Statistical Outperformance:**
   Layer E ($+1.27\%$) significantly outperforms Random Matched Controls ($p = 0.015$) and Date-Matched Controls ($p = 0.022$), confirming that the result is **not merely a sample-size shrinkage artifact**.

---

## 2. Reconstructed Layer E Contract

To ensure mathematical precision, the selection conditions that generated the 73 Layer E trades were reconstructed directly from the frozen codebase:

```text
LAYER_E_CONTRACT
----------------
sector_alignment    : SECTOR_WIDE (Contextual Peer Harmony, Layer B)
opportunity_score   : >= 60.0 (High Conviction Synthesis Gate)
quant_score         : >= 80.0 (Technical Breakout Readiness)
relative_volume     : > 1.2 (Volume Acceleration Gate)
flow_confirmation   : CONFIRMED (rel_vol > 1.2)
red_team            : CLEAN (Pass time_leakage & logic, no hallucination, not contradicted)
agent3_risk_gate    : BUY + GREEN + R/R >= 2.0 + NOT_PRICED_IN
```

### Architectural Decomposition Audit:
* `AGENT3_COMPOSITE_DEPENDENCY = TRUE`
* `OpportunityRanker.score_candidate` combines Technical Factor ($quant \ge 80 \rightarrow 18.0\text{ pts}$ + timing bonus $1.8\text{ pts}$), Flow Factor ($rel\_vol > 1.2 \rightarrow 14.0\text{ pts}$), and Fixed Base Components ($31.9\text{ pts}$) yielding $65.7 \ge 60.0$.
* If $rel\_vol \le 1.2$, score drops to $58.7 < 60.0$. If $quant < 80$, score drops to $\le 56.4 < 60.0$.
* Therefore, Opportunity Score is a **weighted composite conjunction filter** rather than an independent alpha model.

---

## 3. Experiment 1 — Single Component Ablation

Starting from Layer D ($N = 252$), each Layer E component was tested independently:

| Configuration | N | Selection Rate | H1 Mean | H3 Mean | H5 Mean | H10 Mean | H20 Mean | H5 Win Rate | Incremental H5 vs D |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Layer D (Reference)** | 252 | 20.29% | +0.11% | +0.33% | **+0.32%** | +0.04% | -0.72% | 52.21% | +0.00% |
| **D + Opportunity Score (C2 ≥ 60.0)** | 73 | 5.88% | +0.01% | +0.97% | **+1.27%** | +2.20% | +0.95% | 53.42% | **+0.95%** |
| **D + Quant Score (C3 ≥ 80.0)** | 146 | 11.76% | +0.09% | +0.34% | **+0.32%** | -0.02% | -1.80% | 47.59% | +0.00% |
| **D + Relative Volume (C4 > 1.2)** | 102 | 8.21% | +0.04% | +0.67% | **+0.77%** | +0.75% | -0.21% | 52.94% | **+0.45%** |
| **D + Flow Confirmation (C5 CONFIRMED)**| 102 | 8.21% | +0.04% | +0.67% | **+0.77%** | +0.75% | -0.21% | 52.94% | **+0.45%** |
| **D + Sector Alignment (C1)** | 252 | 20.29% | +0.11% | +0.33% | **+0.32%** | +0.04% | -0.72% | 52.21% | +0.00% |

---

## 4. Experiment 2 — Leave-One-Component-Out (Primary Ablation)

Starting from FULL Layer E ($N = 73$), each component was removed one at a time:

| Configuration | Full N | Ablated N | $\Delta N$ | H5 Full | H5 Ablated | $\Delta H_5$ (Contrib) | H10 Full | H10 Ablated | $\Delta H_{10}$ (Contrib) | Interpretation |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **FULL (All Layer E Conditions)** | 73 | 73 | 0 | +1.27% | +1.27% | 0.00% | +2.20% | +2.20% | 0.00% | Reference |
| **FULL - C1 (Sector Alignment)** | 73 | 284 | +211 | +1.27% | +0.75% | **+0.52%** | +2.20% | +2.11% | +0.09% | **VALUE** (Filters divergent noise) |
| **FULL - C2 (Opportunity Score)** | 73 | 73 | 0 | +1.27% | +1.27% | **0.00%** | +2.20% | +2.20% | 0.00% | **REDUNDANT** (Captured by C3+C4) |
| **FULL - C3 (Quant Score ≥ 80)** | 73 | 102 | +29 | +1.27% | +0.77% | **+0.50%** | +2.20% | +0.75% | **+1.45%** | **VALUE** (Enhances persistence) |
| **FULL - C4 (RelVol > 1.2)** | 73 | 146 | +73 | +1.27% | +0.32% | **+0.95%** | +2.20% | -0.02% | **+2.23%** | **VALUE** (Primary Return Driver) |
| **FULL - C5 (Flow Confirmation)** | 73 | 146 | +73 | +1.27% | +0.32% | **+0.95%** | +2.20% | -0.02% | **+2.23%** | **VALUE** (Primary Return Driver) |
| **FULL - C6 (Red Team Gate)** | 73 | 73 | 0 | +1.27% | +1.27% | **0.00%** | +2.20% | +2.20% | 0.00% | **GOVERNANCE_CONTROL** (0 fails in sector) |
| **FULL - C7 (Agent 3 Risk Gate)** | 73 | 73 | 0 | +1.27% | +1.27% | **0.00%** | +2.20% | +2.20% | 0.00% | **GOVERNANCE_CONTROL** (Passed all green) |

---

## 5. Experiment 3 — Component Contribution Analysis

Decomposing the incremental return contributions:
* **Relative Volume / Flow Confirmation ($C_4/C_5$):** $+0.95\%$ at $H_5$, $+2.23\%$ at $H_{10}$.
* **Sector Alignment ($C_1$):** $+0.52\%$ at $H_5$, $+0.09\%$ at $H_{10}$.
* **Quant Score $\ge 80$ ($C_3$):** $+0.50\%$ at $H_5$, $+1.45\%$ at $H_{10}$.
* **Opportunity Score ($C_2$):** $0.00\%$ at $H_5$, $0.00\%$ at $H_{10}$ (Fully redundant with $C_3 + C_4$).
* **Red Team ($C_6$) & Risk Gate ($C_7$):** $0.00\%$ direct return addition (Governance gates).

---

## 6. Experiment 4 — Sequential Build-Up Funnel

| Stage | N | % Baseline | H5 Mean | H10 Mean | Incremental H5 | H5 Win Rate |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Baseline (Agent 1 Alone)** | 1,242 | 100.00% | -0.02% | -0.03% | +0.00% | 48.91% |
| **+ Peer Context (Layer A)** | 1,162 | 93.56% | +0.07% | +0.09% | +0.09% | 49.55% |
| **+ Sector Alignment (Layer B)** | 252 | 20.29% | +0.32% | +0.04% | +0.25% | 52.21% |
| **+ Red Team Gate (Layer C)** | 252 | 20.29% | +0.32% | +0.04% | +0.00% | 52.21% |
| **+ Agent 3 Risk Gate (Layer D)** | 252 | 20.29% | +0.32% | +0.04% | +0.00% | 52.21% |
| **+ Quant Score ≥ 80** | 146 | 11.76% | +0.32% | -0.02% | +0.00% | 47.59% |
| **+ Relative Volume / Flow > 1.2** | 73 | 5.88% | **+1.27%** | **+2.20%** | **+0.95%** | **53.42%** |
| **+ Opportunity Score ≥ 60.0 (Layer E)**| 73 | 5.88% | **+1.27%** | **+2.20%** | +0.00% | **53.42%** |

---

## 7. Experiment 5 — Matched-Selection Control Analysis

To verify whether selecting $N = 73$ setups produces an advantage merely due to sample shrinkage:

| Control Type | Iterations | Matched N | H5 Mean | 95% Confidence Interval | H5 p-value vs Layer E | H10 Mean | H10 p-value | Verdict |
| :--- | ---: | ---: | ---: | :---: | ---: | ---: | :--- |
| **Layer E (Observed)** | — | 73 | **+1.27%** | — | — | **+2.20%** | — | **Target** |
| **Uniform Random Matched** | 2,000 | 73 | -0.02% | [-1.26%, +1.16%] | **p = 0.015** | -0.05% | **p = 0.009** | **PASSED** (Statistically distinct) |
| **Date-Matched Control** | 2,000 | 73 | +0.23% | [-0.81%, +1.25%] | **p = 0.022** | +0.29% | **p = 0.009** | **PASSED** (Outperforms same dates) |
| **Ticker-Matched Control** | 2,000 | 73 | +0.38% | [-0.92%, +1.70%] | **p = 0.091** | +0.59% | **p = 0.068** | **BORDERLINE** (Ticker bias present) |

---

## 8. Experiment 6 — Ticker Concentration & Leave-One-Ticker-Out

Breakdown of the 73 Layer E trades across the 12 pilot tickers:

| Ticker | N | % Trades | H5 Mean | H10 Mean | H5 Sum | Contribution Pct H5 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **ITMG** | 13 | 17.81% | +3.26% | +2.64% | +0.4243 | **45.67%** |
| **INCO** | 10 | 13.70% | +3.63% | +3.08% | +0.3630 | **39.07%** |
| **ANTM** | 7 | 9.59% | +1.81% | +5.95% | +0.1266 | **13.63%** |
| **PTBA** | 10 | 13.70% | +0.95% | +5.93% | +0.0951 | **10.24%** |
| **UNTR** | 6 | 8.22% | +1.24% | +1.47% | +0.0745 | **8.02%** |
| **BMRI** | 2 | 2.74% | +1.27% | -3.41% | +0.0255 | +2.74% |
| **ASII** | 4 | 5.48% | -0.12% | +0.26% | -0.0048 | -0.52% |
| **BBCA** | 2 | 2.74% | -0.96% | -1.74% | -0.0193 | -2.07% |
| **BBNI** | 4 | 5.48% | -0.77% | -0.58% | -0.0308 | -3.32% |
| **BBRI** | 4 | 5.48% | -0.97% | +1.30% | -0.0388 | -4.18% |
| **ADRO** | 11 | 15.07% | -0.78% | -1.66% | -0.0862 | -9.28% |
| **TLKM** | 0 | 0.00% | — | — | 0.0000 | 0.00% |

### Leave-One-Ticker-Out Worst Case:
* **Worst-Case Exclusion:** Exclude `ITMG` ($N = 60$ remaining).
* **Remaining $H_5$ Mean:** **+0.84%** (10% Trimmed Mean: $+0.48\%$).
* **Remaining $H_{10}$ Mean:** **+2.10%**.
* **Verdict:** Layer E **survives** removal of any single ticker; the edge does not collapse to zero when the top ticker is removed.

---

## 9. Experiment 7 — Sector Concentration & Leave-One-Sector-Out

| Sector Group | Constituent Tickers | N | % Trades | H5 Mean | H10 Mean | Contribution Pct H5 |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **MINING_METALS** | ANTM, INCO | 17 | 23.29% | +2.88% | +4.26% | **52.70%** |
| **ENERGY_COAL** | ADRO, ITMG, PTBA | 34 | 46.58% | +1.27% | +1.89% | **46.63%** |
| **HEAVY_EQUIPMENT** | UNTR | 6 | 8.22% | +1.24% | +1.47% | **8.02%** |
| **AUTOMOTIVE_CONGLOMERATE** | ASII | 4 | 5.48% | -0.12% | +0.26% | **-0.52%** |
| **BANKING_FINANCIAL** | BBCA, BBNI, BBRI, BMRI | 12 | 16.44% | -0.53% | -0.61% | **-6.83%** |
| **TELCO** | TLKM | 0 | 0.00% | — | — | **0.00%** |

### Leave-One-Sector-Out Worst Case:
* **Worst-Case Exclusion:** Exclude `MINING_METALS` ($N = 56$ remaining).
* **Remaining $H_5$ Mean:** **+0.78%** (10% Trimmed Mean: $+0.23\%$).
* **Remaining $H_{10}$ Mean:** **+1.54%**.
* **Second Worst-Case:** Exclude `ENERGY_COAL` ($N = 39$ remaining): $H_5 = \mathbf{+1.27\%}$.
* **Verdict:** Commodities (Mining/Metals + Coal) account for **99.33%** of total return contribution. Banking generates negative excess return. The edge is **heavily commodity-tilted**, classified as `SECTOR_CONCENTRATION_RISK`.

---

## 10. Experiment 8 — Date Concentration & Leave-One-Date-Out

### Top Dates Analysis:
* **Distinct Dates in Layer E:** 56 trading dates.
* **Top 1 Date (2026-01-05: ANTM, INCO):** $+0.2727$ return sum (**29.35%** of total return).
* **Top 3 Dates (2026-01-05, 2026-08-27, 2026-03-02):** $+0.6463$ return sum (**69.57%** of total return).
* **Top 5 Dates:** $+0.9465$ return sum (**101.88%** of total return).

### Date Exclusion Impact:

| Exclusion Filter | N Remaining | H5 Mean | H5 Trimmed Mean | H10 Mean | H10 Trimmed Mean |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Full Sample (No Exclusions)** | 73 | **+1.27%** | +0.83% | **+2.20%** | +1.33% |
| **Exclude Top 1 Date** | 71 | **+0.92%** | +0.57% | **+1.78%** | +1.18% |
| **Exclude Top 3 Dates** | 66 | **+0.43%** | +0.36% | **+1.22%** | +0.76% |
| **Exclude Top 5 Dates** | 63 | **-0.03%** | +0.10% | **+0.84%** | +0.48% |
| **Exclude Top 10 Dates** | 55 | **-0.82%** | -0.60% | **-0.74%** | -0.45% |

* **Verdict:** The $H_5$ return edge is **heavily clustered in a handful of high-momentum swing dates**. When the top 5 dates are removed, $H_5$ becomes flat ($-0.03\%$), though $H_{10}$ retains $+0.84\%$.

---

## 11. Experiment 9 — Regime Robustness

* **Regime Column Status:** `stock_regime` across the historical pilot is labeled `UNKNOWN`.
* **Action:** In strict adherence to AGENTS.md Constitution, **NO synthetic regime labels were fabricated**.
* **Classification:** `INSUFFICIENT_SAMPLE_OR_UNPOPULATED_REGIME`.

---

## 12. Experiment 10 — Complete Horizon Profile Shape

| Horizon | N | Mean Return | Median Return | 10% Trimmed Mean | Win Rate | Mean MFE | Mean MAE | Excess vs Benchmark |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **H1** | 73 | +0.01% | -0.38% | -0.14% | 39.73% | +2.07% | -1.95% | +0.01% |
| **H3** | 73 | +0.97% | +0.37% | +0.70% | 56.16% | +3.82% | -2.85% | +0.97% |
| **H5** | 73 | **+1.27%** | **+0.79%** | **+0.83%** | **53.42%** | **+5.17%** | **-3.85%** | **+1.27%** |
| **H10** | 70 | **+2.20%** | **+0.51%** | **+1.33%** | **52.86%** | **+7.43%** | **-5.32%** | **+2.20%** |
| **H20** | 59 | +0.95% | +0.45% | +1.02% | 50.85% | +9.39% | -7.55% | +0.95% |

* **Observation:** The profile shows classic swing characteristics: friction at $H_1$, strong expansion from $H_3$ to $H_{10}$ (peaking at $H_{10} = +2.20\%$), and partial mean-reversion at $H_{20}$.

---

## 13. Statistical Validation (Bootstrap & Permutation)

Date-clustered bootstrap ($B = 10,000$) and permutation testing ($P = 5,000$) evaluating Layer E vs Layer D:

| Horizon | Full $\Delta$ | 95% Cluster CI | Cluster p-value | Permutation p-value | Trimmed $\Delta$ | Status |
| :--- | ---: | :---: | ---: | ---: | ---: | :--- |
| **H1** | -0.10% | [-0.71%, +0.53%] | 0.3856 | 0.3996 | -0.14% | `NOT_SIGNIFICANT` |
| **H3** | +0.63% | [-0.30%, +1.57%] | 0.0896 | 0.1416 | +0.49% | `BORDERLINE` |
| **H5** | **+0.95%** | [-0.36%, +2.31%] | **0.0770** | **0.1040** | **+0.64%** | `BORDERLINE` |
| **H10** | **+2.16%** | **[+0.28%, +4.21%]** | **0.0113** | **0.0282** | **+1.52%** | `SIGNIFICANT` |
| **H20** | +1.66% | [-0.49%, +3.82%] | 0.0630 | 0.1318 | +1.43% | `BORDERLINE` |

* **Multiple Testing Risk Disclosure:** `MULTIPLE_TESTING_RISK = PRESENT`.

---

## 14. Special Assessments

### Red Team ($C_6$) Assessment:
* **Function:** Governance & Safety Control.
* **Result:** Rejection count within `SECTOR_WIDE` candidates = 0.
* **Finding:** Red Team is not a return-generating alpha filter; its purpose is ensuring zero PIT leakage, consistent logic, and verified entity relationships.

### Agent 3 Risk Engine ($C_7$) Assessment:
* **Status:** `AGENT3_COMPOSITE_DEPENDENCY = TRUE`.
* **Finding:** `opportunity_score >= 60.0` is a composite ranking gate that collapses mathematically into $(quant \ge 80) \land (rel\_vol > 1.2)$. Agent 3 provides portfolio-level sizing and risk gating rather than independent predictive alpha.

---

## 15. Component Classification Matrix

| Component | Identifier | Role in Architecture | Classification | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Sector Alignment** | C1 | Contextual Peer Harmony | `VALUE` | Removes 211 divergent candidates, lifting $H_5$ by $+0.52\%$. |
| **Opportunity Score** | C2 | Composite Ranking Gate | `REDUNDANT` | $\Delta N = 0, \Delta H_5 = 0.00\%$ once C3 & C4 are present. |
| **Quant Score ≥ 80** | C3 | Technical Breakout Readiness | `VALUE` | Enhances swing follow-through ($\Delta H_5 = +0.50\%, \Delta H_{10} = +1.45\%$). |
| **Relative Volume > 1.2**| C4 | Volume Acceleration Gate | `VALUE` | Primary single contributor ($\Delta H_5 = +0.95\%, \Delta H_{10} = +2.23\%$). |
| **Flow Confirmation** | C5 | Flow State Confirmation | `VALUE` | Identical to C4 under current mapping. |
| **Red Team Gate** | C6 | Adversarial Audit & Safety | `GOVERNANCE_CONTROL` | Zero return drag, enforces PIT & contradiction checks. |
| **Agent 3 Risk Gate** | C7 | Structural Risk & R/R Gate | `GOVERNANCE_CONTROL` | Enforces $R/R \ge 2.0$ and green portfolio state. |

---

## 16. Answers to Required Final Questions (A through O)

### A. What component contributes the most incremental EV?
**Relative Volume / Flow Confirmation ($C_4/C_5$)** contributes the most incremental EV ($+0.95\%$ at $H_5$ and $+2.23\%$ at $H_{10}$). Removing it causes $H_{10}$ to collapse from $+2.20\%$ to $-0.02\%$.

### B. Does Sector Alignment survive ablation?
**Yes.** Removing Sector Alignment ($C_1$) admits 211 non-sector aligned trades, causing $H_5$ to drop from $+1.27\%$ to $+0.75\%$ ($\Delta H_5 = +0.52\%$).

### C. Does Opportunity Score add independent value?
**No.** `opportunity_score >= 60.0` is mathematically redundant with the conjunction of $(quant \ge 80) \land (rel\_vol > 1.2)$. `AGENT3_COMPOSITE_DEPENDENCY = TRUE`.

### D. Does Relative Volume add independent value?
**Yes.** Adding Relative Volume $> 1.2$ to Layer D lifts $H_5$ from $+0.32\%$ to $+0.77\%$ and is the primary driver of $H_{10}$ follow-through.

### E. Does Flow add independent value?
**Yes.** Flow Confirmation (defined as $rel\_vol > 1.2$) provides the primary momentum confirmation in the 3-agent pipeline.

### F. Does Agent 3 Risk Gate add independent value?
**No direct return value.** It functions as a structural execution filter ($R/R \ge 2.0$, Green Risk) rather than an alpha generator.

### G. Does Red Team add return value or governance value?
**Governance value.** Red Team does not generate return lift ($\Delta H_5 = 0.00\%$), but successfully audited and guaranteed zero time-leakage and zero unverified relationship claims.

### H. Does Layer E survive matched-selection controls?
**Yes.** Layer E ($+1.27\%$) significantly outperforms Random Matched Controls ($p = 0.015$) and Date-Matched Controls ($p = 0.022$).

### I. Does Layer E survive ticker concentration?
**Yes.** In the worst-case Leave-One-Ticker-Out test (excluding ITMG), remaining $H_5$ is $+0.84\%$ and $H_{10}$ is $+2.10\%$.

### J. Does Layer E survive sector concentration?
**Conditionally.** In the worst-case Leave-One-Sector-Out test (excluding Mining/Metals), remaining $H_5$ is $+0.78\%$. However, Commodities (Mining + Coal) account for $99.33\%$ of total return contribution, while Banking is negative ($-0.53\%$).

### K. Does Layer E survive date concentration?
**Conditionally.** Top 5 dates account for $101.88\%$ of total return sum. Excluding the top 5 dates drops $H_5$ to $-0.03\%$, though $H_{10}$ remains $+0.84\%$.

### L. Does Layer E survive trimming?
**Yes.** The 10% trimmed mean of Layer E is $+0.83\%$ at $H_5$ and $+1.33\%$ at $H_{10}$, remaining substantially above Baseline ($-0.02\%$).

### M. Does the effect persist across H3/H5/H10?
**Yes.** Return profile expands from $H_1 (+0.01\%) \rightarrow H_3 (+0.97\%) \rightarrow H_5 (+1.27\%) \rightarrow H_{10} (+2.20\%)$ before mean-reverting at $H_{20} (+0.95\%)$.

### N. Is the effect likely information, filtering, concentration, redundancy, selection effect, or UNKNOWN?
The effect is a **combination of Filtering (Sector Alignment + Volume Acceleration) and Concentration (Commodity Sector + Clustered Momentum Dates)**, while Opportunity Score is **Redundant**.

### O. Is there sufficient evidence to call this alpha?
**No.** While the statistical evidence is promising ($H_{10}$ date-clustered $p = 0.0113$), the heavy concentration in commodity tickers (ITMG, INCO, ANTM) and specific momentum dates, combined with the small pilot universe ($N=12$), warrants conservative classification. It represents **Promising Research Evidence with Conditional Robustness**, not proven general alpha.

---

## 17. Final Acceptance Verdict

```text
================================================================================
FINAL VERDICT: PASS — PROMISING BUT CONDITIONAL
================================================================================
- Point-in-Time Integrity: VALID (Zero lookahead leakage)
- Component Isolation: COMPLETE (C1-C7 isolated)
- Matched Controls: SURVIVED (p = 0.015 vs Random, p = 0.022 vs Date-matched)
- Ticker/Sector Robustness: SURVIVED with Sector Concentration Warning (Commodity Tilted)
- Horizon Shape: ROBUST (H3 -> H5 -> H10 progression)
- Parameter Tuning: ZERO (Frozen baseline maintained)
================================================================================
```

---

## 18. Recommended Next Steps for Batch ZZZ.9

1. **Do NOT modify Agent 1 logic or optimize thresholds.**
2. **Expand Historical Semantic & Graph Substrate:** Ingest broader multi-year PIT company news, corporate actions, and commodity macro data into DuckDB.
3. **Controlled Paper Trading Pilot:** Prepare a zero-risk simulated forward-testing runner tracking the 3-agent pipeline on live daily data.
