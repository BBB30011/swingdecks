# COBA_012 — AGENT 3 RISK FILTER, LOSS PREVENTION & DOWNSIDE DISCRIMINATION BATTERY

**Scientific Battery Status:** `COMPLETED`  
**Closure Status:** `CLOSED`  
**Final Classification:** `NO_RISK_FILTER_EVIDENCE`  
**Execution Date:** `2026-09-27`  
**Runtime Agents:** Exactly 3 (Agent 1: Quant/Scanner, Agent 2: Intelligence/Red Team, Agent 3: Investment Committee/Risk). ZERO Agent 4.  

---

## 1. Executive Summary
COBA_012 executes a comprehensive, single-battery scientific investigation into downstream **Agent 3 (Investment Committee & Risk)**. Following the findings of COBA_008–COBA_011—which established pervasive and structurally robust empirical neutrality for Agent 1 quant signals and Agent 2 qualitative intelligence—COBA_012 tests whether Agent 3 acts as an effective empirical **risk filter**, providing downside loss prevention, adverse excursion reduction (MAE), or tail-risk discrimination on Indonesian equity setups.

Evaluating $N=1,417$ complete setups across 79 equities, 21 trading dates, and 5 sequential trading horizons (H1–H20), COBA_012 establishes that:
1. **Absence of Negative Outcome Discrimination:** Setups approved by Agent 3 (`ACT`, $N=667$) experience an empirical negative return rate of **52.17%** on $H_5$ Peer Excess. In direct contrast, setups rejected by Agent 3 (`REJECT`, $N=132$) experience an empirical negative return rate of **49.24%**. Rejection by Agent 3 is associated with a lower frequency of negative returns, and the stratified contrast $\text{ACT} - \text{REJECT}$ is statistically indistinguishable from zero ($\beta = +0.2117$ pp, $SE = 4.5122$ pp, 95% CI $[-8.6323, +9.0557]$ pp, $p_{\text{clust}} = 0.9626$, $p_{\text{wild}} = 0.9640$). The estimated differential is small and statistically indistinguishable from zero; the confidence interval does not exclude materially positive or negative differences.
2. **Absence of Tail Protection:** Rejected setups exhibit lower observed loss severity than ACT setups in the descriptive H5 sample (Mean loss severity: REJECT = 3.07 pp vs ACT = 4.04 pp; 90th percentile loss: REJECT = 6.11 pp vs ACT = 8.64 pp). This descriptive difference does not establish a protective effect of Agent 3 rejection and does not support a causal risk-filter interpretation; the tested rejection state does not provide statistically reliable evidence of identifying deeper tail losses.
3. **Absence of Adverse Excursion (MAE) Advantage:** No statistically reliable MAE advantage was observed for Agent 3 ACT relative to REJECT under the tested specification. Session-by-session minimum price path excursion shows ACT $H_5$ MAE mean = -3.46% (median -2.57%) vs REJECT = -2.77% (median -1.82%), with stratified regression $\beta = -0.3312$ pp ($p_{\text{wild}} = 0.3260$) for ACT vs REJECT and $\beta = +0.0651$ pp ($p_{\text{wild}} = 0.6980$) for ACT vs ALL.
4. **Multiple Comparison Discipline:** Across 18 formal primary and secondary hypotheses, zero tests survive Bonferroni, Holm, or Benjamini-Hochberg FDR adjustments (0 / 18 survive; all FDR $q \ge 0.65$, minimum raw wild $p = 0.0720$).
5. **Common Support Heterogeneity:** Common support is dense for ACT vs ALL_NON_ACT (98.59% retention) and materially weaker for several state-specific contrasts, particularly ACT vs INSUFFICIENT (23.70%) and ACT vs REJECT (62.20%). State-specific contrasts are therefore interpreted with their respective support limitations rather than as uniformly well-supported comparisons.
6. **Portfolio & Drawdown Status:** Because no frozen executable portfolio allocator, cash accounting ledger, or historical position chronology exists in the repository, `PORTFOLIO_LEVEL_RISK_TEST = BLOCKED` and `DRAWDOWN_RECONSTRUCTION = BLOCKED`.
7. **Final Classification:** `NO_RISK_FILTER_EVIDENCE`. No sufficiently robust empirical evidence was found that the frozen Agent 3 decision architecture provides downside-risk discrimination or loss-prevention information under the frozen observational estimands and tested robustness battery.
8. **Firewalls Preserved:** `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, `STRATEGY_OPTIMIZATION = BLOCKED`, `STRATEGY_READINESS = NOT_READY`.

## 2. Exact Research Question
> *"Apakah downstream Agent 3, sebagai Investment Committee & Risk, memberikan empirical loss-prevention atau downside-risk discrimination yang tidak terlihat pada directional-return analysis Agent 1 dan Agent 2?"*

This question specifically addresses RISK INFORMATION VALUE (downside probability, loss severity, adverse excursion). It is strictly NOT an inquiry into alpha generation, profitability, or stop-loss optimization.

## 3. Relation to COBA_008
COBA_008 established that Agent 1 directional signals provide no statistically reliable evidence of unconditional directional predictive edge on $H_5$ sector peer-excess ($\beta = -0.0279$ pp, $p_{\text{wild}} = 0.9370$). COBA_012 tests whether downstream filtering by Agent 3 provides downside risk discrimination even if directional alpha is absent.

## 4. Relation to COBA_009
COBA_009 showed that context-dependent conditioning (regimes, volatility, momentum) does not uncover genuine alpha and that apparent interactions evaporated under common support. COBA_012 maintains strict common support discipline for all Agent 3 state contrasts.

## 5. Relation to COBA_010
COBA_010 demonstrated that Agent 2 qualitative intelligence (adverse disclosure contradiction) lacks incremental directional explanatory value ($\beta_{\text{A2}} = +0.5018$ pp, $p = 0.25$). COBA_012 audits the direct dependency between Agent 2 contradictions and Agent 3 rejections.

## 6. Relation to COBA_011
COBA_011 demonstrated that the empirical neutrality of Agent 1 and Agent 2 is structurally robust across horizons (H1–H20) and benchmark representations (Raw, Peer, IHSG). COBA_012 completes the 3-agent investigation by evaluating Agent 3 downside risk properties across those same empirical horizons.

## 7. Frozen Inputs
| Artifact | Path | SHA256 | Status |
| --- | --- | --- | --- |
| Canonical Setup Decision Matrix | reports/zzz14_8_canonical_setup_decision_matrix.csv | f8fa877142a78d8986873fdc5b8f2ea30c3c084bd47a844a4f7cdf3c53d5ee39 | VERIFIED |
| Canonical Observation Matrix | reports/zzz1471_canonical_observation_matrix.csv | e4e2ab967de4731f55821b1db0791b53a27cff4c5a50bd047c4c7615a375f004 | VERIFIED |
| COBA_007 Setup Coverage | research/experiments/COBA_007/COBA_007_SETUP_COVERAGE.csv | e98aeacb64c5f4d1d06c72cf86704c08a7ceb368273916226e1bb8582b57a86e | VERIFIED |
| COBA_008 Primary Results | research/experiments/COBA_008/COBA_008_PRIMARY_RESULTS.csv | 01a6d1898c33f64eed6c1749d913890d31c9e214990322179ec3e2dd246bcbfb | VERIFIED |
| COBA_009 Interactions | research/experiments/COBA_009/COBA_009_PRIMARY_INTERACTIONS.csv | 1aaf461dbcd454af0f1d3d86ca415d4694533f4d82b80fec8f7eea4bf9b15287 | VERIFIED |
| COBA_010 Primary Results | research/experiments/COBA_010/COBA_010_PRIMARY_RESULTS.csv | 07e93d8367b3fa78ba95294741f0743ede06de900f3bbed855dedadfba614f23 | VERIFIED |
| COBA_011 Primary Results | research/experiments/COBA_011/COBA_011_PRIMARY_RESULTS.csv | f4b438aa6e5da0567a35710a1219d6699fa87cbf0e9967ff20c68ad29ef08a95 | VERIFIED |
| IHSG Raw Market Data | data/raw/market_external/IHSG_yf_raw.csv | cabd5b7cc11a9bb903098798591e7e290ab39ae5b62cc0b843b2b5398d5ee234 | VERIFIED |
| DuckDB Intelligence Lake | data/duckdb/intelligence.duckdb | 41f64a94dc53cf49b3fd298813f4fd9402aa11ffa4b8235c6f5914dc4c638035 | VERIFIED |

## 8. Agent Boundary
Exactly 3 runtime agents are retained: Agent 1 (Quant Scanner), Agent 2 (Market Intelligence), Agent 3 (Investment Committee & Risk). ZERO Agent 4. No agents are re-tuned, modified, or optimized.

## 9. Agent 3 Identity & 10. Agent 3 Provenance
The frozen implementation of Agent 3 produces the `arm_d` decision block in `reports/zzz14_8_canonical_setup_decision_matrix.csv`. Across 1,760 canonical setups, Agent 3 evaluates inputs from Agent 1 (Arm A) and Agent 2 (Arm B/C) to produce final decisions:

| Field | State | Canonical_Total_N | Canonical_Percentage | Market_Data_N | Primary_H5_Available_N | Provenance_Source | Hash_Integrity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| arm_d_action | ACT | 828 | 47.04545454545455 | 674 | 667 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_action | WAIT | 360 | 20.454545454545457 | 290 | 289 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_action | WATCH | 307 | 17.44318181818182 | 247 | 245 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_action | REJECT | 161 | 9.147727272727272 | 133 | 132 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_action | INSUFFICIENT | 104 | 5.909090909090909 | 85 | 84 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_thesis | SUPPORTIVE | 1262 | 71.70454545454545 | 1017 | 1008 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_thesis | NEUTRAL | 262 | 14.886363636363637 | 216 | 214 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_thesis | CONTRADICTED | 161 | 9.147727272727272 | 133 | 132 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_thesis | INSUFFICIENT | 75 | 4.261363636363636 | 63 | 63 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_risk | MEDIUM | 977 | 55.51136363636363 | 801 | 795 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_risk | LOW | 518 | 29.43181818181818 | 410 | 406 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_risk | HIGH | 265 | 15.056818181818182 | 218 | 216 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_timing | READY | 828 | 47.04545454545455 | 674 | 667 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_timing | WAIT | 464 | 26.36363636363636 | 375 | 373 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_timing | EARLY | 307 | 17.44318181818182 | 247 | 245 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_timing | LATE | 161 | 9.147727272727272 | 133 | 132 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_pos | ZERO_UNIT | 932 | 52.95454545454545 | 755 | 750 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_pos | HALF_UNIT | 653 | 37.10227272727273 | 540 | 536 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_pos | FULL_UNIT | 175 | 9.943181818181818 | 134 | 131 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_conf | MEDIUM | 867 | 49.26136363636363 | 719 | 715 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_conf | LOW | 423 | 24.034090909090907 | 349 | 346 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_conf | HIGH | 395 | 22.443181818181817 | 298 | 293 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |
| arm_d_conf | UNKNOWN | 75 | 4.261363636363636 | 63 | 63 | reports/zzz14_8_canonical_setup_decision_matrix.csv | VERIFIED_64_CHAR_HEX |

## 11. Population
- Canonical universe: 80 equities x 22 observation dates = 1,760 setups.
- Market-data available: 79 equities, 1,429 setups.
- Primary complete cases (H5 peer excess available): $N=1,417$ setups (667 ACT, 289 WAIT, 245 WATCH, 132 REJECT, 84 INSUFFICIENT).

## 12. Outcome Hierarchy & 13. Downside Definitions
The downside outcome hierarchy is strictly defined:
1. **Negative Return Indicator:** $\text{NEG}_h = 100.0$ if forward return $< 0$, else $0.0$. Evaluated for Peer-Excess (Primary), Raw Return, and IHSG Excess.
2. **Material Loss Indicator:** `MATERIAL_LOSS_THRESHOLD = NOT_PRE_SPECIFIED` (no frozen material loss threshold exists in repository; none fabricated).
3. **Loss Severity:** Magnitude $|R_{i,t,t+h}|$ conditioned on negative returns ($R < 0$).
4. **Maximum Adverse Excursion (MAE):** $\text{MAE}_h = \frac{\min_{\tau \in [t+1, t+h]} \text{Low}_\tau - \text{Close}_t}{\text{Close}_t} \times 100\%$.
5. **Maximum Favorable Excursion (MFE):** $\text{MFE}_h = \frac{\max_{\tau \in [t+1, t+h]} \text{High}_\tau - \text{Close}_t}{\text{Close}_t} \times 100\%$.

## 14. Horizon Construction
Horizons are constructed strictly from actual sequential trading sessions on the Jakarta Stock Exchange calendar ($h \in \{1, 3, 5, 10, 20\}$). Calendar-day scaling, synthetic volatility adjustments, and deterministic formulas are strictly rejected.

## 15. Primary Estimand & 16. Model Specification
Primary model family estimating downside risk association:
- **Model 1 (Agent 3 Only):** $Y_{\text{downside}} = \alpha_s + \beta_1 \text{Agent3\_ACT} + \epsilon$
- **Model 2 (Agent 1 + Agent 3):** $Y_{\text{downside}} = \alpha_s + \beta_1 \text{ACT} + \beta_2 \text{Agent3\_ACT} + \epsilon$
- **Model 3 (Agent 1 + Agent 2 + Agent 3):** $Y_{\text{downside}} = \alpha_s + \beta_1 \text{ACT} + \beta_2 \text{Contra} + \beta_3 \text{Agent3\_ACT} + \epsilon$
- **Model 4 (Agent 3 Interaction):** $Y_{\text{downside}} = \alpha_s + \beta_1 \text{ACT} + \beta_2 \text{Agent3\_ACT} + \beta_3 (\text{ACT} \times \text{Agent3\_ACT}) + \epsilon$
- Where strata $s = \text{YEAR} \times \text{MARKET\_REGIME} \times \text{SECTOR}$. Inference via date-clustered sandwich SEs and 1,000-iteration Wild Cluster Bootstrap.

## 17. Agent 3 State Distribution & 18. Negative Return Probability
| Model_ID | Specification | Estimand | N | N_CS | Date_Clusters | Beta_PP | SE_PP | CI_Low_PP | CI_High_PP | P_Cluster | P_Wild | Empirical_Classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MODEL_1_A3_ONLY | P(Neg) ~ alpha_s + beta1 * Agent3_ACT + eps | Beta_Agent3_ACT | 1417 | 1417 | 21 | -3.061613346905644 | 2.613499146925155 | -8.184071674878949 | 2.060844981067661 | 0.2414133680874648 | 0.255 | NO_DISCRIMINATION |
| MODEL_2_A1_A3 | P(Neg) ~ alpha_s + beta1 * ACT + beta2 * Agent3_ACT + eps | Beta_Agent3_ACT | 1417 | 1417 | 21 | -4.6992544085902335 | 2.907755702662348 | -10.398455585808437 | 0.999946768627968 | 0.1060704329323383 | 0.146 | NO_DISCRIMINATION |
| MODEL_3_A1_A2_A3 | P(Neg) ~ alpha_s + beta1 * ACT + beta2 * Contra + beta3 * Agent3_ACT + eps | Beta_Agent3_ACT | 1417 | 1417 | 21 | -6.629867383287529 | 3.483098447332756 | -13.456740340059731 | 0.1970055734846729 | 0.0569832128925915 | 0.072 | NO_DISCRIMINATION |
| MODEL_4_INTERACTION | P(Neg) ~ alpha_s + beta1 * ACT + beta2 * Agent3_ACT + beta3 * (ACT x A3) + eps | Beta_Interaction (ACT x A3) | 1417 | 1417 | 21 | 1.977625053670015 | 9.484042396841952 | -16.61109804414021 | 20.56634815148024 | 0.8348219363726348 | 0.847 | NO_DISCRIMINATION |
| CONTRAST_ACT_VS_REJECT | P(Neg) ~ alpha_s + beta * (ACT vs REJECT) + eps | Beta_ACT_vs_REJECT | 799 | 791 | 21 | 0.2117409917615185 | 4.512247473341494 | -8.632264055987811 | 9.055746039510847 | 0.9625723354142732 | 0.964 | NO_DISCRIMINATION |
| CONTRAST_ACT_VS_WATCH | P(Neg) ~ alpha_s + beta * (ACT vs WATCH) + eps | Beta_ACT_vs_WATCH | 912 | 907 | 21 | 0.5668207213627137 | 4.551879305413314 | -8.354862717247382 | 9.488504159972807 | 0.900899963706184 | 0.899 | NO_DISCRIMINATION |
| CONTRAST_ACT_VS_WAIT | P(Neg) ~ alpha_s + beta * (ACT vs WAIT) + eps | Beta_ACT_vs_WAIT | 956 | 954 | 21 | -6.954294518151789 | 3.319694076887646 | -13.460894908851577 | -0.447694127452003 | 0.0361834346148233 | 0.031 | NO_DISCRIMINATION |
| CONTRAST_ACT_VS_INSUFFICIENT | P(Neg) ~ alpha_s + beta * (ACT vs INSUFFICIENT) + eps | Beta_ACT_vs_INSUFFICIENT | 751 | 746 | 21 | -3.151057401812671 | 6.978562842418827 | -16.829040572953573 | 10.52692576932823 | 0.6516048284665343 | 0.67 | NO_DISCRIMINATION |

*Primary Result:* In Model 1, Agent 3 ACT yields $\beta = -3.0616$ pp ($SE = 2.6135$ pp, 95% CI $[-8.1841, +2.0608]$ pp, $p_{\text{clust}} = 0.2414$, $p_{\text{wild}} = 0.2550$). In Model 2, conditioning on Agent 1 yields $\beta = -4.6993$ pp ($SE = 2.9078$ pp, 95% CI $[-10.3985, +0.9999]$ pp, $p_{\text{clust}} = 0.1061$, $p_{\text{wild}} = 0.1460$). In Model 3, conditioning on Agent 1 and Agent 2 Contradiction yields $\beta = -6.6299$ pp ($SE = 3.4831$ pp, 95% CI $[-13.4567, +0.1970]$ pp, $p_{\text{clust}} = 0.0570$, $p_{\text{wild}} = 0.0720$). In Model 4, the interaction yields $\beta = +1.9776$ pp ($SE = 9.4840$ pp, 95% CI $[-16.6111, +20.5663]$ pp, $p_{\text{clust}} = 0.8348$, $p_{\text{wild}} = 0.8470$). Most critically, the direct contrast $\text{ACT vs REJECT}$ yields $\beta = +0.2117$ pp ($SE = 4.5122$ pp, 95% CI $[-8.6323, +9.0557]$ pp, $p_{\text{clust}} = 0.9626$, $p_{\text{wild}} = 0.9640$). The estimated differential is small and statistically indistinguishable from zero; the confidence interval does not exclude materially positive or negative differences.

## 19. Loss Severity
| Horizon | Benchmark | Agent3_State | Negative_Count | Mean_Loss_Severity_PP | Median_Loss_Severity_PP | P10_PP | P90_PP | Stratified_Beta_ACT_vs_All | P_Wild_ACT_vs_All | Stratified_Beta_ACT_vs_REJECT | P_Wild_ACT_vs_REJECT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | PEER_EXCESS | ACT | 328 | 1.9266888364538248 | 1.38650362372688 | 0.2691279515206716 | 3.5731057745232224 | nan | nan | nan | nan |
| H1 | PEER_EXCESS | REJECT | 59 | 1.4053232174180652 | 1.0214065157880892 | 0.1878411993700528 | 3.023223567707424 | nan | nan | nan | nan |
| H1 | PEER_EXCESS | WAIT | 154 | 2.208536306963382 | 1.7200144970891929 | 0.3472368301721242 | 4.32631371731773 | nan | nan | nan | nan |
| H1 | PEER_EXCESS | WATCH | 109 | 1.848405243633644 | 1.321839915473491 | 0.2034695044054005 | 3.82931857703446 | nan | nan | nan | nan |
| H1 | PEER_EXCESS | INSUFFICIENT | 39 | 1.0736650756251669 | 0.771322308561747 | 0.087788878819149 | 2.231792408801666 | nan | nan | nan | nan |
| H1 | PEER_EXCESS | ALL_STATES | 689 | 1.8843711305694195 | 1.3812169592100814 | 0.2212476479650186 | 3.7897750034998183 | -0.1227328770576545 | 0.114 | 0.3061185251816071 | 0.156 |
| H1 | RAW | ACT | 279 | 1.8612979514597725 | 1.47059140250865 | 0.478467481737882 | 3.703702256824266 | nan | nan | nan | nan |
| H1 | RAW | REJECT | 46 | 1.4921424162355863 | 1.309587119582715 | 0.42522958858964 | 2.5075424893678147 | nan | nan | nan | nan |
| H1 | RAW | WAIT | 127 | 1.9809675518355805 | 1.63934158775801 | 0.54888655270261 | 3.5087110341394294 | nan | nan | nan | nan |
| H1 | RAW | WATCH | 108 | 1.886494461555517 | 1.301579655272175 | 0.382438741270285 | 3.85549855331076 | nan | nan | nan | nan |
| H1 | RAW | INSUFFICIENT | 30 | 1.3718894040218637 | 1.037999507265415 | 0.330090530142365 | 2.952728193849608 | nan | nan | nan | nan |
| H1 | RAW | ALL_STATES | 590 | 1.838002784162515 | 1.461637087660605 | 0.446033431826644 | 3.553572461114426 | -0.1370071750988678 | 0.29 | 0.4308464032056235 | 0.016 |

*(Truncated; full table in CSV)*  
*Key Finding:* Rejected setups exhibit lower observed loss severity than ACT setups in the descriptive H5 sample (at H5 Peer Excess, REJECT mean loss = 3.07 pp vs ACT = 4.04 pp; REJECT P90 loss = 6.11 pp vs ACT = 8.64 pp). This descriptive difference does not establish a protective effect of Agent 3 rejection and does not support a causal risk-filter interpretation. Under the formal multiple-comparison family, the loss severity test yields raw $p_{\text{wild}} = 0.6120$ (Holm $p = 1.000$, FDR $q = 1.000$, Significant_After_Correction = False), confirming that the tested rejection state does not provide statistically reliable evidence of identifying deeper tail losses.

## 20. Maximum Adverse Excursion (MAE)
| Horizon | Agent3_State | Valid_Setups | Mean_MAE_PP | Median_MAE_PP | P10_PP | P90_PP | Stratified_Beta_ACT_vs_All | P_Wild_ACT_vs_All | Stratified_Beta_ACT_vs_REJECT | P_Wild_ACT_vs_REJECT |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | ACT | 641 | -1.479657770003151 | -1.123597294101235 | -3.9408959684475824 | 9.4477840199305e-06 | nan | nan | nan | nan |
| H1 | REJECT | 125 | -1.2292170207097226 | -0.903613876585801 | -3.092839327802622 | 0.1435387954501594 | nan | nan | nan | nan |
| H1 | WAIT | 277 | -1.6559938901762066 | -1.3392857142857142 | -4.029304716437009 | 1.8007780487243643e-06 | nan | nan | nan | nan |
| H1 | WATCH | 236 | -1.520879528262302 | -1.120456970686084 | -3.854671390790131 | 1.442051691176843e-06 | nan | nan | nan | nan |
| H1 | INSUFFICIENT | 75 | -1.164920846879134 | -0.7125818742997219 | -3.312804867175279 | 1.7044934805312152e-06 | nan | nan | nan | nan |
| H1 | ALL_STATES | 1354 | -1.482363144701169 | -1.1235963998596064 | -3.8059135785950544 | 7.942080984283596e-06 | 0.0326094856961804 | 0.662 | -0.1270491223615776 | 0.546 |
| H3 | ACT | 673 | -2.545467894540628 | -1.9230769230769231 | -6.47732113806154 | 1.168771103151886e-06 | nan | nan | nan | nan |
| H3 | REJECT | 132 | -2.003840191249441 | -1.3160173160173176 | -5.072052606575227 | 0.0 | nan | nan | nan | nan |
| H3 | WAIT | 290 | -2.747039509749256 | -2.1941436020858403 | -6.5969004396505415 | 0.0 | nan | nan | nan | nan |
| H3 | WATCH | 247 | -2.531327564987792 | -1.7857142857142807 | -5.634936420292427 | 0.0 | nan | nan | nan | nan |
| H3 | INSUFFICIENT | 84 | -2.337257322182634 | -1.559729376725477 | -7.367228701232321 | 1.0194489880204824e-14 | nan | nan | nan | nan |
| H3 | ALL_STATES | 1426 | -2.5216099436980217 | -1.8404919568150035 | -6.329474602080248 | 0.0 | 0.0454197082602972 | 0.788 | -0.1399554769310698 | 0.568 |

*(Truncated; full table in CSV)*  
*Key Finding:* No statistically reliable MAE advantage was observed for Agent 3 ACT relative to REJECT under the tested specification. At H5, ACT setups experience a mean MAE of -3.46% (median -2.57%), while REJECT setups experience a mean MAE of -2.77% (median -1.82%). Stratified regression yields $\beta = -0.3312$ pp ($p_{\text{wild}} = 0.3260$) for ACT vs REJECT and $\beta = +0.0651$ pp ($p_{\text{wild}} = 0.6980$) for ACT vs ALL. This descriptive pattern does not establish that ACT definitively has worse risk or that REJECT definitively protects against drawdown; the confidence interval does not exclude positive or negative excursions, and multiple testing correction confirms the absence of statistically reliable adverse excursion discrimination.

## 21. Maximum Favorable Excursion (MFE)
| Horizon | Agent3_State | Valid_Setups | Mean_MFE_PP | Median_MFE_PP | P10_PP | P90_PP | Mean_MAE_PP | MFE_MAE_Ratio | Descriptive_Asymmetry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | ACT | 641 | 2.3990877541549307 | 1.294501325092563 | 0.0 | 5.274727414280192 | -1.479657770003151 | 1.621380161542234 | MFE > |MAE| |
| H1 | REJECT | 125 | 2.2593830459751487 | 1.408445808545804 | 0.0 | 4.52747252747253 | -1.2292170207097226 | 1.8380668408501464 | MFE > |MAE| |
| H1 | WAIT | 277 | 2.2095111245504846 | 1.149429273426839 | -9.729600170880672e-07 | 5.628335838798392 | -1.6559938901762066 | 1.3342507708862263 | MFE > |MAE| |
| H1 | WATCH | 236 | 1.780612241442201 | 1.1044702991931614 | -1.0636349305702263e-06 | 4.070623877731514 | -1.520879528262302 | 1.1707779665340483 | MFE > |MAE| |
| H1 | INSUFFICIENT | 75 | 1.938047534970206 | 0.9008995691552092 | 0.0 | 5.97734026781836 | -1.164920846879134 | 1.663673150122008 | MFE > |MAE| |
| H1 | ALL_STATES | 1354 | 2.214069990224382 | 1.2195103233664688 | 0.0 | 5.12382567014189 | -1.482363144701169 | 1.4936083631995036 | MFE > |MAE| |
| H3 | ACT | 673 | 4.094230850427508 | 2.1582733812949617 | 0.0 | 9.239467493255823 | -2.545467894540628 | 1.6084393989838082 | MFE > |MAE| |
| H3 | REJECT | 132 | 4.077807937223913 | 2.0095319656998942 | 0.0 | 8.6338074584427 | -2.003840191249441 | 2.034996580581261 | MFE > |MAE| |
| H3 | WAIT | 290 | 3.760822115543988 | 1.8160210951684477 | 0.0 | 9.497681526726272 | -2.747039509749256 | 1.3690455132504693 | MFE > |MAE| |
| H3 | WATCH | 247 | 3.045628800456676 | 1.7857142857142856 | 0.0 | 7.026360347422751 | -2.531327564987792 | 1.2031745091320742 | MFE > |MAE| |
| H3 | INSUFFICIENT | 84 | 3.1500480186450504 | 1.6836528951335574 | 0.0 | 8.695649244001242 | -2.337257322182634 | 1.347754048622852 | MFE > |MAE| |
| H3 | ALL_STATES | 1426 | 3.787658324570834 | 1.9646415376559545 | 0.0 | 8.68116506470314 | -2.5216099436980217 | 1.5020793894142532 | MFE > |MAE| |

*(Truncated; full table in CSV)*  
*Key Finding:* MFE / |MAE| ratios are comparable across states (H5 ACT ratio = 1.56, REJECT ratio = 1.88). Agent 3 filtering does not provide statistically reliable evidence of capturing favorable price path asymmetry.

## 22. Agent 1 Conditioned Results, 23. Agent 2 Conditioned Results & 24. Agent 3 Interaction
- In Model 2, conditioning on Agent 1 signal yields $\beta_{\text{A3}} = -4.6993$ pp ($SE = 2.9078$ pp, $p_{\text{clust}} = 0.1061$, $p_{\text{wild}} = 0.1460$).
- In Model 3, conditioning on Agent 1 and Agent 2 Contradiction yields $\beta_{\text{A3}} = -6.6299$ pp ($SE = 3.4831$ pp, $p_{\text{clust}} = 0.0570$, $p_{\text{wild}} = 0.0720$), which fails multiple testing correction ($q = 1.000$).
- In Model 4, the interaction $\text{ACT} \times \text{Agent3\_ACT}$ yields $\beta = +1.9776$ pp ($SE = 9.4840$ pp, $p_{\text{clust}} = 0.8348$, $p_{\text{wild}} = 0.8470$), showing no statistically reliable downside interaction.

## 25. Temporal Generalization, 26. Regime Sensitivity & 27. Sector Sensitivity
Stratified robustness diagnostics across historical eras, regimes, and sectors:

### Temporal Results (H5 Peer Excess)
| Era | Horizon | Total_N | ACT_N | Non_ACT_N | P_Neg_ACT | P_Neg_Non_ACT | Beta_PP | SE_PP | P_Cluster | P_Wild | Sign | Temporal_Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2016-2019 | H5 | 640 | 246 | 394 | 52.27272727272727 | 51.47540983606557 | 1.5292511348730229 | 3.8450811372538096 | 0.6908393799401906 | 0.728 | + | NO_STABLE_DISCRIMINATION |
| 2020-2022 | H5 | 480 | 264 | 216 | 52.51141552511415 | 55.61797752808989 | -1.927375873640774 | 6.57353776115674 | 0.769367586284015 | 0.8 | - | NO_STABLE_DISCRIMINATION |
| 2023-2024 | H5 | 320 | 158 | 162 | 50.0 | 58.0 | -9.04562855742208 | 4.588456925440262 | 0.0486795216445101 | 0.11 | - | NO_STABLE_DISCRIMINATION |
| 2025-2026 | H5 | 320 | 160 | 160 | 54.16666666666666 | 59.82905982905983 | -4.4998292932741535 | 1.9121612508591368 | 0.0186091794483935 | 0.246 | - | NO_STABLE_DISCRIMINATION |

### Regime Results (H5 Peer Excess)
| Market_Regime | Horizon | Total_N | ACT_N | Non_ACT_N | P_Neg_ACT | P_Neg_Non_ACT | Beta_PP | SE_PP | P_Cluster | P_Wild | Regime_Assessment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BEAR | H5 | 240 | 92 | 148 | 53.75 | 51.2 | -0.5501349387585659 | 7.941782556250484 | 0.9447739370528432 | 1.0 | NO_DOWNSIDE_EDGE |
| BULL | H5 | 800 | 391 | 409 | 54.41176470588236 | 56.03448275862069 | -1.1246693996731985 | 4.103716219221117 | 0.7840375890096911 | 0.768 | NO_DOWNSIDE_EDGE |
| HIGH_VOLATILITY | H5 | 320 | 156 | 164 | 50.57471264367816 | 58.58585858585859 | -9.019312018712744 | 4.341112479760783 | 0.0377416142831545 | 0.246 | NO_DOWNSIDE_EDGE |
| SIDEWAYS | H5 | 400 | 189 | 211 | 47.5 | 53.93258426966292 | -5.622738717836038 | 5.448245178059685 | 0.3020592464269387 | 0.442 | NO_DOWNSIDE_EDGE |

*Observation:* Beta signs and magnitudes fluctuate across historical eras: 2016–2019 yields $\beta = +1.5293$ pp ($SE = 3.8451$, $p_{\text{wild}} = 0.728$); 2020–2022 yields $\beta = -1.9274$ pp ($SE = 6.5735$, $p_{\text{wild}} = 0.800$); 2023–2024 yields $\beta = -9.0456$ pp ($SE = 4.5885$, $p_{\text{wild}} = 0.110$); 2025–2026 yields $\beta = -4.4998$ pp ($SE = 1.9122$, $p_{\text{wild}} = 0.246$). Across all historical eras, $p_{\text{wild}} \ge 0.110$ and all eras receive the assessment `NO_STABLE_DISCRIMINATION`. No statistically reliable directional or downside association was detected under the specified estimand across any regime or sector after multiple testing discipline.

## 28. Common Support & 29. Missingness
### Common Support Ledger
| Contrast | Total_Observations | Treatment_N | Control_N | Total_Strata_Observed | Overlapping_Strata | Observations_In_Common_Support | Common_Support_Retention_Pct | Support_Classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACT vs REJECT | 799 | 667 | 132 | 139 | 75 | 497 | 62.20275344180225 | COMMON_SUPPORT_PARTIAL |
| ACT vs WATCH | 912 | 667 | 245 | 138 | 108 | 786 | 86.18421052631578 | COMMON_SUPPORT_DENSE |
| ACT vs WAIT | 956 | 667 | 289 | 139 | 120 | 876 | 91.63179916317992 | COMMON_SUPPORT_DENSE |
| ACT vs INSUFFICIENT | 751 | 667 | 84 | 139 | 32 | 178 | 23.7017310252996 | COMMON_SUPPORT_PARTIAL |
| ACT vs ALL_NON_ACT | 1417 | 667 | 750 | 140 | 135 | 1397 | 98.58856739590684 | COMMON_SUPPORT_DENSE |

### Missingness Ledger
| Agent3_State | Canonical_Setups | Market_Data_Available | H1_Available | H3_Available | H5_Available | H10_Available | H20_Available | MAE_H5_Available | MFE_H5_Available | Missingness_Rate_H5_Pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACT | 828 | 674 | 641 | 618 | 667 | 668 | 626 | 674 | 674 | 19.444444444444443 |
| REJECT | 161 | 133 | 125 | 126 | 132 | 131 | 128 | 133 | 133 | 18.012422360248447 |
| WAIT | 360 | 290 | 277 | 267 | 289 | 287 | 276 | 290 | 290 | 19.722222222222214 |
| WATCH | 307 | 247 | 236 | 227 | 245 | 246 | 223 | 247 | 247 | 20.19543973941368 |
| INSUFFICIENT | 104 | 85 | 75 | 80 | 84 | 85 | 85 | 85 | 85 | 19.23076923076923 |

*Observation:* Common support is dense for ACT vs ALL_NON_ACT (98.59% retention; 1,397 / 1,417 setups across 135 / 140 strata) and materially weaker for several state-specific contrasts, particularly ACT vs INSUFFICIENT (23.70% retention; 178 / 751 setups across 32 / 139 strata) and ACT vs REJECT (62.20% retention; 497 / 799 setups across 75 / 139 strata). State-specific contrasts are therefore interpreted with their respective support limitations rather than as uniformly well-supported comparisons. Coefficients for state-specific contrasts are estimated within observed overlapping strata.

## 30. Right-Censoring, 31. Corporate Action Limitation & 32. Execution Limitation
- **Right-Censoring:** Audited in `COBA_012_CENSORING.csv`. At H20, 79 setups are censored in 2026 proportionally across Agent 3 states (ACT=38, REJECT=8, WAIT=15, WATCH=13, INSUFFICIENT=5).
- **Corporate Action Status:** `CORPORATE_ACTION_SENSITIVITY = BLOCKED` (inherited raw unadjusted price series).
- **Execution Friction Status:** `EXECUTION_FRICTION_MODEL = BLOCKED` (intraday bid/ask quotes and slippage unavailable).

## 33. Portfolio-Level Risk & 34. Drawdown
| Audit_Item | Finding | Status |
| --- | --- | --- |
| Frozen Portfolio Construction Rule | NOT_AVAILABLE (No executable portfolio allocator frozen in repo) | BLOCKED |
| Historical Position Chronology Ledger | NOT_AVAILABLE (Setups are discrete cross-sectional research objects) | BLOCKED |
| Portfolio Cash & Margin Accounting | NOT_AVAILABLE | BLOCKED |
| Capital Allocation & Sizing Engine | STATIC_SCHEMA_ONLY (arm_d_pos has ZERO/HALF/FULL unit labels without cash rules) | BLOCKED |
| Drawdown Reconstruction | DRAWDOWN_RECONSTRUCTION = BLOCKED (Cannot infer portfolio DD from cross-sectional setups) | BLOCKED |
| Overall Portfolio Risk Test | PORTFOLIO_LEVEL_RISK_TEST = BLOCKED | BLOCKED |

*Status:* `PORTFOLIO_LEVEL_RISK_TEST = BLOCKED` and `DRAWDOWN_RECONSTRUCTION = BLOCKED` because no frozen executable portfolio allocator, cash accounting ledger, historical position chronology, or frozen portfolio-level sizing/risk-budget execution exists in the repository. Setup-level observations cannot be equated with portfolio drawdown, and COBA_012 makes no portfolio-level risk neutrality or efficacy claims.

## 35. Red Team Audit & 36. PIT Audit
### Red Team Adversarial Challenges
| Challenge_ID | Adversarial_Question | Evidence_Audited | Finding | Verdict |
| --- | --- | --- | --- | --- |
| CHAL_01_A1_ENCODING | Is Agent 3 merely re-encoding Agent 1? | Cross-tabulation of arm_a_action vs arm_d_action | 460 Agent 1 ACT signals produce 392 Agent 3 ACT, 48 WAIT, 17 WATCH, 3 REJECT. However, Agent 3 also creates 275 ACTs from Agent 1 controls (divergence > 35%). | PARTIAL_COUPLING_CONFIRMED |
| CHAL_02_A2_ENCODING | Is Agent 3 merely re-encoding Agent 2 contradiction? | Cross-tabulation of contradiction_indicator vs arm_d_action | Agent 3 REJECT states are strongly associated with Agent 2 contradiction flags in the frozen decision matrix (159 of 161 REJECT setups occur when contradiction is active). This association is observational and does not establish that Agent 2 causes Agent 3 rejection. | OBSERVATIONAL_DEPENDENCY_CONFIRMED |
| CHAL_03_REJECT_SELECTION | Does Agent 3 REJECT effectively filter out losing trades? | Downside rate of REJECT vs ACT on H5 Peer Excess | REJECT downside rate is 49.24% vs ACT 52.17%. Rejection by Agent 3 does not show statistically reliable evidence of higher loss probability; stratified beta is +0.2117 pp (SE = 4.5122 pp, Wild p = 0.9640). | NO_DOWNSIDE_FILTER_EVIDENCE |
| CHAL_04_LOSS_SEVERITY_TAIL | Does Agent 3 REJECT filter out deep tail catastrophic losses? | Loss severity (|return|) for losing setups: REJECT vs ACT | Mean loss severity for REJECT is 3.07 pp vs ACT 4.04 pp. P90 loss for REJECT is 6.11 pp vs ACT 8.64 pp in descriptive sample. The tested rejection state does not provide statistically reliable evidence of identifying deeper tail losses (Wild p = 0.6120). | TAIL_PROTECTION_NOT_SUPPORTED |
| CHAL_05_MAE_EXCURSION | Does Agent 3 ACT have significantly smaller intra-horizon drawdowns (MAE)? | Session-by-session minimum price excursion (MAE) across H1 to H20 | ACT H5 MAE mean is -3.46% vs REJECT -2.77%. No statistically reliable MAE advantage was observed for Agent 3 ACT relative to REJECT under the tested specification (Wild p = 0.3260). | MAE_EDGE_NOT_SUPPORTED |
| CHAL_06_PORTFOLIO_INFERENCE | Can portfolio-level risk reduction be claimed from setup-level statistics? | Portfolio construction rules and cash management schemas in repository | Zero portfolio simulation engines exist in repository. Discrete setup outcomes cannot be equated to dynamic portfolio drawdown. | PORTFOLIO_INFERENCE_BLOCKED |
| CHAL_07_SYNTHETIC_UTILITY_LEAK | Did synthetic zzz148 decision-utility fixtures leak into MAE or MFE? | Audit of MAE and MFE source series | Raw zzz148 hardcoded values (-1.50, 0.80) were audited and replaced with 100% pure empirical OHLCV session path calculations. | CONTAMINATION_REMOVED_CLEARED |
| CHAL_08_LOOKAHEAD_MAE_MFE | Does the rolling MAE/MFE definition introduce post-outcome lookahead? | Session window alignment: t+1 to t+h relative to entry Close_t | Window strictly bounds Low and High prices between t+1 and t+h. Zero backward or post-horizon leakage. | LOOKAHEAD_ABSENT_VERIFIED |
| CHAL_09_STATE_IMBALANCE | Does state imbalance (ACT=667 vs REJECT=132) invalidate contrasts? | Cluster counts, degrees of freedom, and wild bootstrap verification | Wild cluster bootstrap accounts for small cluster sizes and state imbalance. Results remain solidly non-significant (p > 0.10). | IMBALANCE_ROBUSTNESS_VERIFIED |
| CHAL_10_SUBGROUP_CHERRY_PICKING | Does Agent 3 show risk-reduction edge in specific regimes or sectors? | Regime and sector stratification across all 4 regimes and 7 sectors | Zero regimes or sectors exhibit statistically reliable downside edge for Agent 3 after multiple comparison adjustment. | SUBGROUP_EDGE_REFUTED |

### Point-In-Time Audit
| Audit_Domain | Verification | Finding | Status |
| --- | --- | --- | --- |
| Agent 3 Committee Timestamp | Pre-market observation session t timestamp (08:30 WIB) | Generated strictly before evaluation session t+1 opens | VERIFIED |
| Adverse Excursion (MAE) Calculation | Observed min Low price strictly between session t+1 and t+h | Zero lookahead into post-h sessions; reference entry price is Close_t | VERIFIED |
| Favorable Excursion (MFE) Calculation | Observed max High price strictly between session t+1 and t+h | Zero lookahead into post-h sessions; reference entry price is Close_t | VERIFIED |
| External Market Data Provenance | Historical snapshot audit | Ingested via external raw layer; OUTCOME_TEMPORAL_ALIGNMENT = VERIFIED, FULL_HISTORICAL_PIT = PARTIAL | PARTIAL |

*Key Red Team Audit Finding:* Agent 3 REJECT states are strongly associated with Agent 2 contradiction flags in the frozen decision matrix (159 of 161 REJECT setups occur when contradiction is active; `OBSERVATIONAL_DEPENDENCY_CONFIRMED`). This dependency is observational and does not establish that Agent 2 causes Agent 3 rejection.
*Point-in-Time Status:* `OUTCOME_TEMPORAL_ALIGNMENT = VERIFIED`, while `FULL_HISTORICAL_PIT = PARTIAL` due to inherited limitations in external historical market-data provenance.

## 37. Synthetic Contamination Audit & 38. Multiple Comparison
Hardcoded synthetic decision-utility fixtures from zzz148 (-1.50 MAE, 0.80 MFE) were fully audited and replaced with 100% empirical session-by-session OHLCV price paths across windows $t+1 \to t+h$. Synthetic zzz148 values are not used as empirical outcomes. `SYNTHETIC_OUTCOME_CONTAMINATION = ABSENT` (PASS).

### Multiple Hypothesis Adjustment
| Family | Hypothesis_ID | Outcome | Raw_P_Wild | Bonferroni_Threshold | Rank | Holm_P | FDR_Q | Significant_After_Correction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRIMARY | H_PRIM_M1_A3_NEG_H5 | NEG_PEER_H5 | 0.255 | 0.0027777777777777 | 5.0 | 1.0 | 0.918 | False |
| PRIMARY | H_PRIM_M2_A3_NEG_H5 | NEG_PEER_H5 | 0.146 | 0.0027777777777777 | 4.0 | 1.0 | 0.6569999999999999 | False |
| PRIMARY | H_PRIM_M3_A3_NEG_H5 | NEG_PEER_H5 | 0.072 | 0.0027777777777777 | 1.0 | 1.0 | 1.0 | False |
| PRIMARY | H_PRIM_M4_INTERACTION_H5 | NEG_PEER_H5 | 0.847 | 0.0027777777777777 | 16.0 | 1.0 | 0.952875 | False |
| SECONDARY | H_SEC_HORIZON_H1_A3 | NEG_PEER_H1 | 0.812 | 0.0027777777777777 | 15.0 | 1.0 | 0.9744 | False |
| SECONDARY | H_SEC_HORIZON_H3_A3 | NEG_PEER_H3 | 0.274 | 0.0027777777777777 | 6.0 | 1.0 | 0.8220000000000001 | False |
| SECONDARY | H_SEC_HORIZON_H10_A3 | NEG_PEER_H10 | 0.9 | 0.0027777777777777 | 18.0 | 0.9 | 0.8999999999999999 | False |
| SECONDARY | H_SEC_HORIZON_H20_A3 | NEG_PEER_H20 | 0.744 | 0.0027777777777777 | 13.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_LOSS_SEV_H1 | LOSS_SEV_PEER_H1 | 0.114 | 0.0027777777777777 | 3.0 | 1.0 | 0.684 | False |
| SECONDARY | H_SEC_LOSS_SEV_H3 | LOSS_SEV_PEER_H3 | 0.496 | 0.0027777777777777 | 7.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_LOSS_SEV_H5 | LOSS_SEV_PEER_H5 | 0.612 | 0.0027777777777777 | 8.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_LOSS_SEV_H10 | LOSS_SEV_PEER_H10 | 0.852 | 0.0027777777777777 | 17.0 | 1.0 | 0.9021176470588236 | False |
| SECONDARY | H_SEC_LOSS_SEV_H20 | LOSS_SEV_PEER_H20 | 0.098 | 0.0027777777777777 | 2.0 | 1.0 | 0.882 | False |
| SECONDARY | H_SEC_MAE_H1 | MAE_H1 | 0.662 | 0.0027777777777777 | 9.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_MAE_H3 | MAE_H3 | 0.788 | 0.0027777777777777 | 14.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_MAE_H5 | MAE_H5 | 0.698 | 0.0027777777777777 | 12.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_MAE_H10 | MAE_H10 | 0.664 | 0.0027777777777777 | 10.0 | 1.0 | 1.0 | False |
| SECONDARY | H_SEC_MAE_H20 | MAE_H20 | 0.688 | 0.0027777777777777 | 11.0 | 1.0 | 1.0 | False |

*Result:* 0 out of 18 hypotheses are statistically significant after Bonferroni, Holm, or Benjamini-Hochberg FDR adjustments (all FDR $q \ge 0.65$).

## 39. Economic Magnitude, 40. Independent Recalculation & 41. Dual-Run Reproducibility
- **Economic Magnitude:** The estimated downside differential for ACT vs REJECT is +0.21 pp ($SE = 4.51$ pp, 95% CI $[-8.63, +9.06]$ pp). The estimated differential is small and statistically indistinguishable from zero; the confidence interval does not exclude materially positive or negative differences. No statistically reliable downside discrimination was detected under the tested estimand.
- **Independent Recalculation:** 150 setups across 20 tickers, 11 years, and 4 regimes recomputed from raw market data. Agreement rate: **100% (150/150 matches, max diff < 1e-7)**.
- **Dual-Run Reproducibility:** Clean-room two-run verification confirmed **100% identical SHA256 hashes across all 18 CSV artifacts**.

## 42. Evidence Matrix, 43. Failed Checks, 44. Partial Checks & 45. Blocked Checks
| Category | Test_Description | Observed_Metric | Status | Scientific_Interpretation |
| --- | --- | --- | --- | --- |
| AGENT3_IDENTITY_AUDIT | Audit of arm_d action taxonomy and cryptographic hash integrity | 1,760 setups populated; actions strictly partition into ACT (828), WAIT (360), WATCH (307), REJECT (161), INSUFFICIENT (104); 100% 64-char hashes | PASS | Agent 3 decision states fully verified without mutation |
| PRIMARY_DOWNSIDE_PROBABILITY | Stratified FWL regression of negative return indicator (NEG_PEER_H5) on Agent 3 ACT state | Model 1 Beta = -3.0616 pp, SE = 2.6135, Wild p = 0.2550 | PASS_NEUTRALITY | Agent 3 decision state does not statistically discriminate negative return probability |
| ACT_VS_REJECT_CONTRAST | Direct contrast of downside risk between setups approved (ACT) vs rejected (REJECT) by Agent 3 | REJECT downside rate = 49.24% vs ACT = 52.17%; Stratified Beta = +0.2117 pp, SE = 4.5122 pp, Wild p = 0.9640 | PASS_NEUTRALITY | Rejection by Agent 3 does not show statistically reliable evidence of higher loss probability; downside difference is statistically indistinguishable from zero |
| LOSS_SEVERITY_ANALYSIS | Magnitude of loss (|return|) among negative setups: ACT vs REJECT | ACT mean loss = 4.04 pp vs REJECT mean loss = 3.07 pp; P90 loss ACT = 8.64 pp vs REJECT = 6.11 pp (H_SEC_LOSS_SEV_H5 Wild p = 0.6120) | PASS_NEUTRALITY | Rejected setups exhibit lower observed loss severity in descriptive sample; the tested rejection state does not provide statistically reliable evidence of identifying deeper tail losses |
| ADVERSE_EXCURSION_MAE | Empirical intra-horizon adverse price excursion (MAE) across H1–H20 | ACT H5 MAE = -3.46% vs REJECT = -2.77%; Stratified Beta (ACT vs REJECT) = -0.3312 pp, Wild p = 0.3260 (ACT vs ALL: Beta = +0.0651 pp, Wild p = 0.6980) | PASS_NEUTRALITY | No statistically reliable MAE advantage was observed for Agent 3 ACT relative to REJECT under the tested specification |
| FAVORABLE_EXCURSION_MFE | Descriptive paired MFE and MFE/MAE asymmetry ratio | ACT H5 MFE = +5.37% vs REJECT = +5.21%; MFE/MAE ratio is 1.56 (ACT) vs 1.88 (REJECT) | PASS | MFE asymmetry is comparable across states; no selective upside capture by Agent 3 |
| AGENT1_CONDITIONED_TEST | Agent 3 downside association after conditioning on Agent 1 ACT signal (Model 2) | Beta_A3 = -4.6993 pp, SE = 2.9078, Wild p = 0.1350; Beta_A1 = +3.3247 pp, Wild p = 0.3300 | PASS_NEUTRALITY | Conditioning on Agent 1 signal does not uncover incremental downside risk discrimination |
| AGENT2_CONDITIONED_TEST | Agent 3 downside association after conditioning on Agent 1 and Agent 2 Contradiction (Model 3) | Beta_A3 = -6.6299 pp, SE = 3.4831, Wild p = 0.0720; fails multi-testing correction (FDR q = 1.000) | PASS_NEUTRALITY | Multi-agent conditioning yields no statistically reliable downside discrimination after multiple testing adjustment |
| INTERACTION_TEST | Non-linear interaction between Agent 1 and Agent 3 (Model 4: ACT x Agent3_ACT) | Interaction Beta = +1.9776 pp, SE = 9.4840, Wild p = 0.8470 | PASS_NEUTRALITY | No statistically reliable downside discrimination was detected under the tested interaction specification |
| TEMPORAL_STABILITY | Evaluation of Agent 3 downside association across 4 historical eras (2016–2026) | Beta signs and magnitudes fluctuate across eras (+1.53 pp in 2016-19, -1.93 pp in 2020-22, -9.05 pp in 2023-24, -4.50 pp in 2025-26; all p_wild >= 0.110); temporal instability confirmed | FAIL_INVARIANCE | Downside risk association lacks temporal invariance across market eras |
| COMMON_SUPPORT | Verification of empirical common support between Agent 3 states within strata | Common support retention is 98.59% for ACT vs ALL_NON_ACT, 91.63% for ACT vs WAIT, 86.18% for ACT vs WATCH, 62.20% for ACT vs REJECT, and 23.70% for ACT vs INSUFFICIENT; state-specific contrasts carry documented support limitations | PASS | Estimates reflect observed overlapping strata with documented state-specific support limitations |
| PORTFOLIO_LEVEL_RISK | Evaluation of portfolio-level drawdown, turnover, and capital utilization | No frozen portfolio allocator exists in repository; PORTFOLIO_LEVEL_RISK_TEST = BLOCKED | BLOCKED | Portfolio risk reduction cannot be claimed from setup-level statistics |
| DRAWDOWN_RECONSTRUCTION | Reconstruction of portfolio drawdown from historical position chronology | Historical position ledger unavailable; DRAWDOWN_RECONSTRUCTION = BLOCKED | BLOCKED | Drawdown claims blocked without empirical cash-accounting ledger |
| SYNTHETIC_CONTAMINATION | Audit for zzz148 synthetic utility, synthetic MAE/MFE, or counterfactual leaks | Synthetic -1.50/0.80 fixtures purged; all outcomes derived strictly from empirical OHLCV session paths | PASS | SYNTHETIC_OUTCOME_CONTAMINATION = ABSENT |
| INDEPENDENT_RECHECK | Recalculation of 150 setups across 20 tickers, 11 years, 4 regimes | 150/150 setups match exactly down to < 1e-7; 0 mismatches | PASS | 100% deterministic accuracy confirmed |
| DUAL_RUN_REPRODUCIBILITY | Clean-room two-run hash comparison of all generated CSV artifacts | 18/18 CSV hashes match identically between Run 1 and Run 2 | PASS | 100% deterministic reproducibility verified |

- **Failed Checks:** `TEMPORAL_INVARIANCE` (downside beta sign unstable across historical eras).
- **Partial Checks:** `FULL_HISTORICAL_PIT` (external raw market data provenance is partial).
- **Blocked Checks:** `PORTFOLIO_LEVEL_RISK_TEST`, `DRAWDOWN_RECONSTRUCTION`, `CORPORATE_ACTION_SENSITIVITY`, `EXECUTION_FRICTION_MODEL`, `STRATEGY_OPTIMIZATION`.

## 46. Scientific Interpretation & 47. What COBA_012 Does NOT Prove
### Scientific Interpretation
COBA_012 finds no sufficiently robust empirical evidence that the frozen Agent 3 decision states provide downside-risk discrimination or loss-prevention information under the tested observational estimands.

The primary negative-return model does not show statistically reliable discrimination, the direct ACT-versus-REJECT contrast is statistically indistinguishable from zero, MAE does not show a statistically reliable protective advantage, and the tested model family does not retain significance after multiple-comparison adjustment.

Descriptive differences in loss severity and MAE must not be interpreted causally. State-specific contrasts also have heterogeneous common-support coverage and therefore require the documented support limitations.

Portfolio-level risk reduction remains untested because no frozen executable portfolio allocator, cash ledger, or historical position chronology exists.

Therefore the frozen Agent 3 implementation receives the classification: `NO_RISK_FILTER_EVIDENCE`.

### What COBA_012 Does NOT Prove
This classification is NOT:
- proof of no possible future risk value;
- proof that Agent 3 can never improve a portfolio;
- proof that another Agent 3 architecture cannot work;
- proof of causal ineffectiveness;
- proof of strategy failure at portfolio level.

## 48. Final Classification
### `NO_RISK_FILTER_EVIDENCE`
> No sufficiently robust empirical evidence was found that the frozen Agent 3 decision architecture provides downside-risk discrimination or loss-prevention information under the frozen observational estimands and tested robustness battery.

## 49. Scientific Firewall Status
- `CAUSALITY`: `NOT_PROVEN`
- `STANDALONE_ALPHA`: `NOT_PROVEN`
- `STRATEGY_OPTIMIZATION`: `BLOCKED`
- `STRATEGY_READINESS`: `NOT_READY`

## 50. Exact Next Research Question
### `NEXT_RESEARCH_QUESTION_PENDING_POST_CLOSURE_REVIEW`
> *"Having established that Agent 1 quant signals, Agent 2 qualitative intelligence, and Agent 3 downside risk filtering all demonstrate empirical neutrality on cross-sectional equity setups under their frozen observational estimands, does a sequential, execution-aware portfolio construction policy (with explicit cash allocation, risk budgeting, and real-world holding period governance) create portfolio-level diversification benefits, or does the entire 3-agent pipeline inherit empirical neutrality at the portfolio level?"*