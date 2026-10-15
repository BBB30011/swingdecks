# COBA_008 — FULL-SAMPLE EMPIRICAL SIGNAL DISCRIMINATION, ROBUSTNESS & GENERALIZATION BATTERY

## 1. Executive Summary

COBA_008 marks the culmination of the empirical reconstruction series initiated in COBA_002 and expanded in COBA_007. The fundamental scientific objective of COBA_008 is to evaluate whether `PURE_AGENT1_SIGNAL` demonstrates consistent directional discriminatory value against empirical market outcomes across the full expanded empirical dataset (79 canonical equities, 1,429 market-verified setups, 1,417 valid `H5_PEER_EXCESS` observations).

In COBA_005, an apparent negative association of -1.9675 pp (p_wild = 0.0110) was observed on a truncated sample of N=216 setups restricted to 12 equities, which was classified as `INCONCLUSIVE` due to severe coverage limitation and leave-one-out fragility. 

COBA_008 re-executes the exact frozen estimand on the expanded dataset. The primary empirical finding is:
* **Primary Stratified Beta**: **-0.0279 pp** (-0.000279 in decimal return)
* **Cluster-Robust Standard Error**: **0.3742 pp** (clustered on 21 trading dates)
* **95% Confidence Interval**: **[-0.7613 pp, +0.7055 pp]**
* **Clustered P-Value**: **0.9406**
* **Wild Cluster Bootstrap P-Value**: **0.9370** (Rademacher weights, B=1,000, seed=42)
* **Raw Group Difference**: ACT mean (-0.0171 pp) vs Control mean (+0.0082 pp) = **-0.0253 pp**

### Key Scientific Synthesis:
* **Primary Result**: No statistically reliable directional discrimination was detected under the frozen primary estimand. (Bahasa Indonesia: *Tidak ditemukan bukti statistik yang cukup bahwa PURE_AGENT1_SIGNAL memiliki diskriminasi directional yang konsisten pada estimand primer yang telah dibekukan*).
* **Non-Replication of COBA_005**: The COBA_005 effect did not replicate after expansion from the truncated 12-ticker sample to the expanded empirical population. Causal mechanisms behind this non-replication are not definitively identified from observational historical data alone.
* **Confidence Interval Bounds**: While the point estimate is near-zero, the 95% confidence interval indicates that small positive or negative effects (within approximately [-0.76 pp, +0.71 pp]) are not mathematically excluded by the data. The failure to reject the null hypothesis represents an absence of statistically reliable empirical evidence under the frozen specification, rather than formal mathematical proof of an exact zero effect.
* **Data Foundation Coverage**: `DATA_FOUNDATION_COVERAGE = PARTIAL` (79/80 equities populated, 1,417 / 1,760 usable H5 peer-excess setups).

Final Evidence Classification: **`SIGNAL_NOT_SUPPORTED`**  
*(Definition: No sufficiently robust empirical evidence of standalone directional discrimination under the frozen primary estimand and tested robustness battery).*  
Causality Status: **`CAUSALITY = NOT_PROVEN`**  
Standalone Alpha Status: **`STANDALONE_ALPHA = NOT_PROVEN`**  
Strategy Readiness: **`STRATEGY_READINESS = NOT_READY`** (Strategy Optimization remains **`BLOCKED`**)  

---

## 2. Research Question

COBA_008 formally addresses:

> **"Setelah empirical market-data coverage diperluas secara material (dari 216 menjadi 1,417 setups pada 79 equities), apakah PURE_AGENT1_SIGNAL menunjukkan directional discriminatory value yang konsisten terhadap empirical outcomes, dan apakah hasil tersebut bertahan terhadap predefined robustness, temporal, regime, sector, ticker, benchmark, placebo, and coverage-sensitivity tests?"**

As mandated by scientific protocol, this inquiry is strictly non-causal. Observational historical data cannot prove causality or standalone alpha; the evaluation tests purely whether conditional empirical association exists under a pre-specified regression framework.

---

## 3. Scientific Scope

The scope of COBA_008 is bounded by the following parameters:
* **Signal Evaluated**: `ARM_A_SIGNAL_IDENTITY = PURE_AGENT1_SIGNAL` (`arm_a_action` from canonical decision matrix).
* **Treatment Group**: `ACT` (N=460 in primary sample).
* **Control Group**: `WATCH + WAIT` (N=957 in primary sample).
* **Outcome Space**: Empirical Close-to-Close trading-session forward returns (H1, H3, H5, H10, H20), Sector Leave-One-Out (LOO) Peer Excess returns (H5, H10, H20), and IHSG benchmark excess returns (H1 to H20).
* **Firewalls Enforced**: No strategy optimization, no threshold tuning, no post-hoc subset filtering, zero involvement of synthetic counterfactual arms (Agent 2/3/4 models strictly blocked).

---

## 4. Historical Lineage

The provenance of this inquiry follows an unbroken, auditable lineage:
* **COBA_001**: Established baseline signal identity and exposed counterfactual attribution fragility.
* **COBA_001.1**: Identified synthetic outcome contamination defect in legacy decision utility gate.
* **COBA_002**: Reconstructed physical empirical forward trading-session horizons from market parquet data.
* **COBA_003**: Formalized the empirical Leave-One-Out (LOO) peer excess methodology across static exposure groups.
* **COBA_004**: Validated local empirical foundation across 264 historical setups, confirming empirical independence from synthetic generators.
* **COBA_005**: Executed first empirical signal discrimination battery on N=216 usable setups; result was classified as `INCONCLUSIVE` due to 12-ticker sample truncation.
* **COBA_006**: Audited full data lake across all 80 equities, confirming physical absence of 68 equities in local repository.
* **COBA_007**: Executed external immutable raw ingestion via `yfinance` across 68 missing equities and `^JKSE`, populating 79/80 equities and 1,429 setups.
* **COBA_008**: Full-sample empirical discrimination, robustness, temporal, regime, sector, ticker, placebo, and sensitivity battery.

---

## 5. Canonical Dataset Identity

The canonical baseline dataset is frozen:
* **Identifier**: `DATASET_V2_20260915`
* **File Path**: `reports/zzz14_8_canonical_setup_decision_matrix.csv`
* **File SHA256**: `f8fa877142a78d8986873fdc5b8f2ea30c3c084bd47a844a4f7cdf3c53d5ee39`
* **Total Canonical Setups**: 1,760 setups (exactly 22 setups per equity across 11 calendar years, 2016–2026).
* **Canonical Equities**: 80 equities.
* **Integrity Status**: 100% verified. No modifications to canonical inputs.

---

## 6. COBA_005 → COBA_007 Coverage Reconciliation

### Pre-Analysis Reconciliation Table

| Stage | Canonical N | Market N | H5 N | H5 Peer Excess N | Populated Tickers | Primary Beta (pp) | P-Value (Wild) | Classification |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **COBA_004** | 1,760 | 264 | 264 | 264 | 12 / 80 | N/A | N/A | PARTIAL |
| **COBA_005** | 1,760 | 216 | 216 | 216 | 12 / 80 | -1.9675 | 0.0110 | INCONCLUSIVE |
| **COBA_006** | 1,760 | 216 | 216 | 198 | 12 / 80 | N/A | N/A | PARTIAL |
| **COBA_007** | 1,760 | 1,429 | 1,417 | 1,417 | 79 / 80 | N/A | N/A | PARTIAL |
| **COBA_008** | 1,760 | 1,429 | 1,417 | 1,417 | 79 / 80 | -0.0279 | 0.9370 | SIGNAL_NOT_SUPPORTED |

### Detailed Answers to Mandatory Reconciliation Questions:

1. **Mengapa COBA_005 hanya 216?**  
   COBA_005 relied strictly on local storage files (`data/parquet/market/*.parquet`). Only 12 equities possessed local market data. Furthermore, due to forward horizon requirements and date-session alignment across these 12 tickers, exactly 216 setups had valid returns.
2. **Mengapa COBA_007 menjadi 1,417?**  
   COBA_007 bridged the physical local storage gap by ingesting immutable raw historical OHLCV data from `yfinance` for 67 previously missing equities plus the IHSG benchmark (`^JKSE`), bringing active market data coverage to 79 of 80 canonical equities.
3. **Apa yang menyebabkan 343 setup tetap tidak usable?**  
   Out of 1,760 canonical setups, exactly 343 lack usable H5 peer excess:
   * **22 setups** belong to ticker `WSKT`, which was suspended and delisted from IDX, yielding zero historical rows.
   * **79 setups** occurred on `2026-03-18`, an official IDX market holiday (Hari Raya Idul Fitri 1447 H / Cuti Bersama) where no trading occurred.
   * **230 setups** occurred prior to the trading inception / IPO date of specific newly-listed equities (e.g., AMMN, BREN, BELI, GOTO, ARTO, BRIS).
   * **12 setups** occurred on `2017-05-18` where local parquet timestamp conventions (17:00 UTC) created a 1-session trading calendar offset that prevented aligned forward H5 computation.  
   *(331 with no market data + 12 calendar offset = 343 unusable setups)*.
4. **Apa penyebab 79/80 ticker?**  
   `WSKT` (PT Waskita Karya Persero Tbk) was suspended by the Indonesia Stock Exchange due to debt restructuring/default and subsequently delisted, leaving no active quotes on external providers.
5. **Apa penyebab H5/H20 censoring?**  
   For H5 (1,417 usable vs 1,429 market setups), 12 setups lacked 5 consecutive forward sessions. For H20 (1,338 usable vs 1,417 H5 setups), all 79 active setups on `2026-08-27` possessed only 13 subsequent trading sessions prior to dataset cutoff (`2026-09-15`), making H20 strictly `RIGHT_CENSORED`.
6. **Apa penyebab peer-excess missing?**  
   Peer excess requires at least 1 other active peer in the same sector on that date. Because coverage expanded to 79 equities across 7 sectors, all 1,417 setups with valid H5 had active sector peers (0 setups lost to peer deficiency).
7. **Apakah missingness berbeda menurut signal state?**  
   No. Coverage across signal states is virtually identical: ACT has 80.42% coverage (460/572), WAIT has 78.45% coverage (404/515), and WATCH has 82.17% coverage (553/673).
8. **Apakah missingness berbeda menurut tahun?**  
   Yes. Years 2016–2020 show 70%–79% coverage due to pre-IPO statuses of modern equities; 2024–2025 show 98.75% coverage; 2026 shows 49.38% coverage due to the Idul Fitri holiday on 2026-03-18.
9. **Apakah missingness berbeda menurut sektor?**  
   Yes. Traditional sectors (Consumer Goods, Financials, Industrials, Energy) exhibit 80%–95% coverage, whereas Technology/Digital exhibits 56.25% coverage due to late IPO timing (2021–2022).
10. **Apakah missingness berbeda menurut regime?**  
   BULL (86.0%), BEAR (85.4%), and SIDEWAYS (84.5%) have identical high coverage; HIGH_VOLATILITY has 58.1% coverage due to calendar concentration in 2020 and 2026.

---

## 7. Final Analysis Population

The final primary population consists of all canonical setups satisfying:
1. Valid canonical signal state (`arm_a_action` $\in$ {ACT, WATCH, WAIT}).
2. Empirical trading-session price available at $t=0$.
3. Verified empirical Close price at $t+5$ trading sessions.
4. Valid Leave-One-Out (LOO) peer excess calculation with peer count $\ge 1$.
5. Not right-censored.

Primary Population Size: **N = 1,417 setups**.  
ACT Group Count: **460 setups** (32.46%).  
Control Group Count (WATCH + WAIT): **957 setups** (67.54%).  
Equities Represented: **79 of 80 canonical equities**.  
Date Clusters: **21 distinct historical market dates** spanning 2016 to 2026.  
Common Support Population (strata containing both ACT and Control): **N = 1,381 setups** across **131 active strata**.

---

## 8. Missingness and Exclusion Rules

Exclusion rules are applied deterministically without manual discretion:
1. **Rule EXC-01 (Missing Security Market Data)**: If ticker has zero empirical observations on signal date $\rightarrow$ EXCLUDED (N=331).
2. **Rule EXC-02 (Insufficient Forward Horizon)**: If forward session count $< h$ $\rightarrow$ RIGHT_CENSORED (N=12 for H5; N=91 for H20).
3. **Rule EXC-03 (Peer Insufficiency)**: If sector peer count on signal date $= 0$ $\rightarrow$ EXCLUDED (N=0 for expanded H5).
4. **Rule EXC-04 (Common Support Pruning)**: For stratified regression, strata without common support (treatment count = 0 or control count = 0) are excluded from the FWL regression matrix $\rightarrow$ (N=36 setups pruned, 1,381 analyzed).

---

## 9. Primary Estimand

The primary estimand estimates the stratified conditional mean difference (conditional observational association):
$$Y_{ist} = \alpha_s + \beta_1 \cdot D_{ist} + \varepsilon_{ist}$$
Where:
* $Y_{ist}$: `H5_PEER_EXCESS` in percentage points ($[R_{i, t \to t+5} - \bar{R}_{-i, s, t \to t+5}] \times 100$).
* $D_{ist} = 1$ if `arm_a_action == 'ACT'`, and $0$ if `arm_a_action` $\in$ `{'WATCH', 'WAIT'}`.
* $\alpha_s$: Fixed effects for strata $s = \text{YEAR} \times \text{MARKET\_REGIME} \times \text{SECTOR}$.
* Standard errors: Clustered by trading date ($G=21$).
* Hypothesis testing: Wild Cluster Bootstrap (Rademacher weights, $B=1,000$, seed=42) under the null $H_0: \beta_1 = 0$.

*Scientific Note on Nomenclature*: While $D_{ist}$ is formatted mathematically as a binary indicator, the resulting parameter $\beta_1$ is strictly interpreted as a **stratified conditional observational association** (or conditional mean difference), NOT a causal treatment effect.

---

## 10. Primary Statistical Result

### Primary Estimand Table

| Outcome | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **H5_PEER_EXCESS** | **1,417** | **460** | **957** | **-0.0171 pp** | **+0.0082 pp** | **-0.0253 pp** | **-0.0279 pp** | **0.3742** | **-0.7613 pp** | **+0.7055 pp** | **0.9406** | **0.9370** |

### Numerical Details & Rigorous Interpretation:
* **Common Support Strata**: 131 strata (out of 140 non-empty strata).
* **Date Clusters**: 21 clusters.
* **ACT Distribution**: Mean = -0.0171 pp, Median = -0.6400 pp, Std = 6.9105 pp, IQR = 4.02 pp.
* **Control Distribution**: Mean = +0.0082 pp, Median = -0.3886 pp, Std = 6.6265 pp, IQR = 3.91 pp.
* **Standardized Association (Cohen's d)**: $d = -0.0038$.
* **Confidence Interval Coverage**: The 95% confidence interval [-0.7613 pp, +0.7055 pp] is centered near zero. Small positive or negative associations within this band are not mathematically excluded by the data.
* **Inference Conclusion**: No statistically reliable directional discrimination was detected under the frozen primary estimand ($p_{\text{wild}} = 0.9370$). The failure to reject the null hypothesis represents an absence of statistical evidence supporting directional discrimination, rather than mathematical proof of an exact zero effect.

---

## 11. Raw Return Horizon Battery

Evaluation of raw Close-to-Close forward returns across all canonical horizons:

| Horizon | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **H1** | 1,354 | 444 | 910 | 0.6382 pp | 0.2571 pp | +0.3811 pp | +0.2812 pp | 0.1695 | -0.0510 pp | +0.6133 pp | 0.0971 | 0.1190 |
| **H3** | 1,318 | 429 | 889 | 0.8792 pp | 0.5136 pp | +0.3657 pp | +0.1696 pp | 0.2766 | -0.3726 pp | +0.7117 pp | 0.5399 | 0.5390 |
| **H5** | 1,417 | 460 | 957 | 0.9860 pp | 0.6903 pp | +0.2958 pp | +0.0250 pp | 0.3345 | -0.6306 pp | +0.6806 pp | 0.9404 | 0.9350 |
| **H10** | 1,417 | 464 | 953 | 1.1891 pp | 0.9236 pp | +0.2656 pp | -0.1447 pp | 0.3339 | -0.7991 pp | +0.5096 pp | 0.6646 | 0.6740 |
| **H20** | 1,338 | 438 | 900 | 2.4775 pp | 1.3266 pp | +1.1509 pp | +0.4327 pp | 0.7843 | -1.1045 pp | +1.9699 pp | 0.5812 | 0.6210 |

Raw returns fail to demonstrate statistically reliable directional discrimination under the pre-specified primary regression and bootstrap criteria.

---

## 12. Peer-Excess Horizon Battery

Evaluation of Leave-One-Out sector peer-excess returns across valid forward horizons:

| Horizon | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **H5_PEER_EXCESS** | 1,417 | 460 | 957 | -0.0171 pp | +0.0082 pp | -0.0253 pp | -0.0279 pp | 0.3742 | -0.7613 pp | +0.7055 pp | 0.9406 | 0.9370 |
| **H10_PEER_EXCESS** | 1,417 | 464 | 953 | -0.0868 pp | +0.0423 pp | -0.1291 pp | -0.1422 pp | 0.3725 | -0.8723 pp | +0.5880 pp | 0.7027 | 0.7130 |
| **H20_PEER_EXCESS** | 1,338 | 438 | 900 | +0.3341 pp | -0.1626 pp | +0.4967 pp | +0.5489 pp | 0.8836 | -1.1829 pp | +2.2807 pp | 0.5345 | 0.5720 |

---

## 13. Effect Size Analysis

* **Absolute Association Size**: Primary $\beta = -0.0279$ pp (-2.79 basis points).
* **Sample Standard Deviation of H5 Peer Excess**: $\sigma = 6.7176$ pp.
* **Standardized Difference**: $\frac{\beta}{\sigma} = -0.0042$ standard deviations.
* **Economic Magnitude**: Small relative to typical IDX retail round-trip execution slippage and exchange fees (~0.30%–0.40%).
* **Pre-specified Minimum Economic Effect**: `MINIMUM_EFFECT_SIZE = NOT_PRE_SPECIFIED`.

---

## 14. Distributional Tests

* **Mann-Whitney U Test**: Statistic = 214,832.0, Expected = 220,110.0, **p = 0.4643**. The distribution of ACT outcomes is not stochastically shifted relative to Control.
* **Welch's Two-Sample t-test**: $t = -0.0654$, **p = 0.9479**.
* **Mood's Median Test**: $\chi^2 = 0.3668$, **p = 0.5447**. Median difference (-0.2514 pp) is statistically indistinguishable from zero.

---

## 15. Permutation Tests

Within-stratum permutation tests were conducted across `YEAR × MARKET_REGIME × SECTOR` strata:
* **Replications**: $B = 1,000$.
* **Algorithm**: Exact permutation of treatment indicator within each stratum, strictly preserving treatment count and control count per block.
* **Observed Beta**: -0.0279 pp.
* **Null Distribution Mean**: +0.0011 pp.
* **Null Distribution Std**: 0.4121 pp.
* **Empirical Permutation P-Value**: **p = 0.9470**.
* **Interpretation**: The observed association is completely consistent with the null permutation distribution generated under random assignment within strata.

---

## 16. Placebo Tests

* **PLACEBO-01 (Within-Stratum Randomized Treatment Labels)**: Empirical $p = 0.9470$.
* **PLACEBO-02 (Global Randomized Signal-State Assignment)**: Shuffled globally preserving 460 ACT count. Null mean = -0.0108 pp, Null std = 0.4261 pp, Empirical $p = 0.9470$.
* **PLACEBO-03 (Negative Control Outcome)**: Pre-specified outcome status: `NEGATIVE_CONTROL = NOT_AVAILABLE`.

---

## 17. Temporal Generalization

Primary estimand evaluated across chronological multi-year periods:

| Period | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Period A (2016–2019)** | 481 | 147 | 334 | -0.6226 pp | +0.2740 pp | -0.8966 pp | -1.0392 pp | 0.3718 | -1.7680 pp | -0.3104 pp | 0.0052 | 0.0240 |
| **Period B (2020–2022)** | 397 | 142 | 255 | +0.2802 pp | -0.1561 pp | +0.4363 pp | +0.4756 pp | 0.7390 | -0.9729 pp | +1.9241 pp | 0.5199 | 0.5750 |
| **Period C (2023–2024)** | 302 | 96 | 206 | +0.5502 pp | -0.2564 pp | +0.8066 pp | +0.8594 pp | 0.3773 | +0.1199 pp | +1.5988 pp | 0.0227 | 0.2520 |
| **Period D (2025–2026)** | 237 | 75 | 162 | -0.1192 pp | +0.0552 pp | -0.1745 pp | -0.1849 pp | 1.6677 | -3.4536 pp | +3.0838 pp | 0.9117 | 1.0000 |

### Objective Recognition of Sub-Period Statistical Significance:
A critical finding is that statistical significance is **not absent across all sub-slices**:
1. **Period A (2016–2019)** exhibits a nominally significant negative conditional association ($\beta = -1.0392$ pp, $p_{\text{cluster}} = 0.0052$, $p_{\text{wild}} = 0.0240$).
2. **Period C (2023–2024)** exhibits a nominally significant positive conditional association under clustered OLS ($\beta = +0.8594$ pp, $p_{\text{cluster}} = 0.0227$), although it does not survive wild cluster bootstrap inference ($p_{\text{wild}} = 0.2520$).
3. **Annual Slices**: Nominal clustered significance is observed in several single-year regressions:
   * 2018: $\beta = -0.7382$ pp, $p_{\text{cluster}} = 0.0051$, $p_{\text{wild}} = 0.2300$
   * 2019: $\beta = -2.2212$ pp, $p_{\text{cluster}} < 0.001$, $p_{\text{wild}} = 0.4760$
   * 2020: $\beta = +2.7940$ pp, $p_{\text{cluster}} = 0.0013$, $p_{\text{wild}} = 0.4760$
   * 2024: $\beta = +1.3612$ pp, $p_{\text{cluster}} = 0.0035$, $p_{\text{wild}} = 0.4760$
   * 2025: $\beta = -1.7819$ pp, $p_{\text{cluster}} = 0.0487$, $p_{\text{wild}} = 0.4760$

### Scientific Temporal Diagnosis:
While exploratory sub-slices yield nominal statistical significance under conventional or clustered inference, these associations **invert signs across historical eras** (e.g., negative in Period A vs positive in Period C) and **fail to demonstrate temporal directional persistence**. Furthermore, they do not consistently survive small-sample cluster wild bootstrap inference. COBA_008 does not claim that significance was absent everywhere, but rather that the detected associations lack temporal stability and persistence across market cycles.

---

## 18. Rolling Temporal Diagnostics

Evaluation across two chronological observation/evaluation blocks:
* **Block 1 (2016–2021 Observation)**: N=737, Beta = -0.3109 pp, SE = 0.5004, $p = 0.5343$, Wild $p = 0.5630$.
* **Block 2 (2022–2026 Evaluation)**: N=680, Beta = +0.2544 pp, SE = 0.5718, $p = 0.6564$, Wild $p = 0.6710$.

Conclusion: Aggregate 5-year blocks show point estimates oscillating around zero without statistical significance.

---

## 19. Market Regime Analysis

| Market Regime | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **BEAR** | 205 | 69 | 136 | -0.1582 pp | +0.0803 pp | -0.2384 pp | -0.2660 pp | 0.4997 | -1.2454 pp | +0.7134 pp | 0.5945 | 0.7180 |
| **BULL** | 688 | 216 | 472 | +0.2028 pp | -0.0928 pp | +0.2955 pp | +0.3270 pp | 0.5562 | -0.7632 pp | +1.4173 pp | 0.5566 | 0.5650 |
| **HIGH_VOLATILITY** | 186 | 68 | 118 | +0.2424 pp | -0.1397 pp | +0.3820 pp | +0.4224 pp | 1.4082 | -2.3378 pp | +3.1826 pp | 0.7642 | 1.0000 |
| **SIDEWAYS** | 338 | 107 | 231 | -0.5347 pp | +0.2477 pp | -0.7824 pp | -0.8462 pp | 0.7891 | -2.3928 pp | +0.7003 pp | 0.2835 | 0.2950 |

Conclusion: Across broad market regimes, the conditional mean difference fails to reach statistical significance under wild bootstrap inference ($p_{\text{wild}} > 0.29$ for all regimes).

---

## 20. Sector Analysis

| Sector | N | ACT N | Control N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **BASIC_MATERIALS_MINING** | 204 | 75 | 129 | -1.0098 pp | +0.5871 pp | -1.5969 pp | -1.7127 pp | 1.1338 | -3.9349 pp | +0.5094 pp | 0.1309 | 0.1510 |
| **CONSUMER_GOODS** | 231 | 74 | 157 | +0.5855 pp | -0.2760 pp | +0.8614 pp | +0.9299 pp | 1.1408 | -1.3061 pp | +3.1659 pp | 0.4150 | 0.4580 |
| **ENERGY_COAL_OIL** | 212 | 75 | 137 | +0.7082 pp | -0.3877 pp | +1.0959 pp | +1.2351 pp | 1.0372 | -0.7978 pp | +3.2681 pp | 0.2337 | 0.2350 |
| **FINANCIALS_BANKING** | 226 | 71 | 155 | -0.0097 pp | +0.0045 pp | -0.0142 pp | -0.0154 pp | 0.6387 | -1.2672 pp | +1.2364 pp | 0.9808 | 0.9810 |
| **INDUSTRIALS_CAPITAL_GOODS** | 239 | 65 | 174 | -0.6778 pp | +0.2532 pp | -0.9309 pp | -0.9996 pp | 1.1254 | -3.2053 pp | +1.2061 pp | 0.3744 | 0.3790 |
| **INFRASTRUCTURE_UTILITIES** | 206 | 68 | 138 | +0.3142 pp | -0.1548 pp | +0.4691 pp | +0.5127 pp | 0.9756 | -1.3994 pp | +2.4249 pp | 0.5992 | 0.6030 |
| **TECHNOLOGY_DIGITAL** | 99 | 32 | 67 | -0.1621 pp | +0.0774 pp | -0.2395 pp | -0.3028 pp | 1.8257 | -3.8811 pp | +3.2755 pp | 0.8683 | 0.8970 |

Conclusion: All sectors fail to demonstrate statistically reliable discrimination under wild cluster bootstrap ($p_{\text{wild}} \ge 0.1510$).

---

## 21. Ticker Concentration

Concentration diagnostics evaluated across 79 leave-one-ticker-out models:
* **Max Absolute Beta Change**: 0.2008 pp (Removing UNTR shifts beta from -0.0279 to -0.2287 pp).
* **Median Absolute Beta Change**: 0.0266 pp.
* **P-value Stability**: Across all 79 exclusions, clustered p-values range from 0.5551 to 0.9988; wild bootstrap p-values range from 0.5580 to 0.9990.
* **Classification**: `TICKER_CONCENTRATION = LOW`. The null primary result is not driven by any single influential equity.

---

## 22. Leave-One-Ticker-Out

Every single canonical ticker with available market data (79 equities) was systematically excluded. Top and bottom beta shifts:
* **Top 3 Exclusions Shifting Beta Negative**:
  1. Excluding `UNTR`: Beta = -0.2287 pp, CI = [-1.018, +0.560], $p = 0.569$
  2. Excluding `ITMG`: Beta = -0.1706 pp, CI = [-0.942, +0.601], $p = 0.665$
  3. Excluding `ADRO`: Beta = -0.1678 pp, CI = [-0.943, +0.608], $p = 0.672$
* **Top 3 Exclusions Shifting Beta Positive**:
  1. Excluding `BBCA`: Beta = +0.0901 pp, CI = [-0.640, +0.820], $p = 0.809$
  2. Excluding `BMRI`: Beta = +0.0747 pp, CI = [-0.659, +0.808], $p = 0.842$
  3. Excluding `ANTM`: Beta = +0.0683 pp, CI = [-0.676, +0.812], $p = 0.858$

Full results for all 79 tickers are recorded in `COBA_008_TICKER_LOO.csv`. Zero exclusions achieve statistical significance.

---

## 23. Leave-One-Sector-Out

| Removed Sector | N Remaining | Beta | CI Low | CI High | P Cluster | P Wild | Direction | Delta From Primary |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | ---: |
| **BASIC_MATERIALS_MINING** | 1,213 | +0.2860 pp | -0.4222 pp | +0.9942 pp | 0.4287 | 0.4440 | POSITIVE | +0.3139 pp |
| **CONSUMER_GOODS** | 1,186 | -0.2178 pp | -0.8953 pp | +0.4597 pp | 0.5296 | 0.5490 | NEGATIVE | -0.1899 pp |
| **ENERGY_COAL_OIL** | 1,205 | -0.2556 pp | -1.2882 pp | +0.7770 pp | 0.6277 | 0.6450 | NEGATIVE | -0.2277 pp |
| **FINANCIALS_BANKING** | 1,191 | -0.0303 pp | -0.8000 pp | +0.7395 pp | 0.9385 | 0.9410 | NEGATIVE | -0.0024 pp |
| **INDUSTRIALS_CAPITAL_GOODS** | 1,178 | +0.1524 pp | -0.7511 pp | +1.0559 pp | 0.7403 | 0.7700 | POSITIVE | +0.1803 pp |
| **INFRASTRUCTURE_UTILITIES** | 1,211 | -0.1218 pp | -0.8973 pp | +0.6537 pp | 0.7574 | 0.7500 | NEGATIVE | -0.0939 pp |
| **TECHNOLOGY_DIGITAL** | 1,318 | -0.0101 pp | -0.7371 pp | +0.7169 pp | 0.9781 | 0.9830 | NEGATIVE | +0.0178 pp |

Conclusion: Removing any sector keeps $\beta$ within $[-0.26, +0.29]$ pp, with all $p > 0.42$.

---

## 24. Signal Gradient

Descriptive analysis across signal states: `WAIT → WATCH → ACT`:

| Signal State | N | Mean Return (pp) | Median Return (pp) | Std Dev (pp) | IQR (pp) | 95% Confidence Interval |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **WAIT** | 404 | -0.3875 pp | -1.1211 pp | 7.2015 pp | 4.38 pp | [-1.0898 pp, +0.3148 pp] |
| **WATCH** | 553 | +0.2973 pp | -0.0306 pp | 6.1634 pp | 3.65 pp | [-0.2173 pp, +0.8119 pp] |
| **ACT** | 460 | -0.0171 pp | -0.6400 pp | 6.9105 pp | 4.02 pp | [-0.6492 pp, +0.6150 pp] |

### Monotonicity Diagnosis:
The gradient is non-monotonic: `WATCH (+0.30 pp) > ACT (-0.02 pp) > WAIT (-0.39 pp)`. The active signal state (`ACT`) underperforms the intermediate monitoring state (`WATCH`).

---

## 25. Control Definition Sensitivity

| Specification | N | ACT N | Control N | Beta | SE | CI Low | CI High | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Control A (WATCH only)** | 1,013 | 460 | 553 | -0.4131 pp | 0.3262 | -1.0524 pp | +0.2263 pp | 0.2054 | 0.2190 |
| **Control B (WAIT only)** | 864 | 460 | 404 | +0.5279 pp | 0.5718 | -0.5928 pp | +1.6486 pp | 0.3559 | 0.3670 |
| **Control C (WATCH + WAIT)** | 1,417 | 460 | 957 | -0.0279 pp | 0.3742 | -0.7613 pp | +0.7055 pp | 0.9406 | 0.9370 |

Conclusion: Comparing ACT against WATCH yields a negative point estimate (-0.41 pp), while comparing against WAIT yields a positive point estimate (+0.53 pp). Neither contrast reaches statistical significance.

---

## 26. Peer Coverage Sensitivity

* **COMPLETE (Peer Count $\ge 3$)**: N=1,394 setups. Stratified $\beta = -0.0403$ pp, SE = 0.3772, $p_{\text{cluster}} = 0.9149$, $p_{\text{wild}} = 0.9180$.
* **PARTIAL (Peer Count 1–2)**: N=23 setups across 6 common support observations $\rightarrow$ `INSUFFICIENT_SAMPLE`.
* **INSUFFICIENT (Peer Count 0)**: N=0 setups.

Conclusion: In the complete peer coverage subset, beta remains statistically indistinguishable from zero.

---

## 27. Corporate Action Sensitivity

In COBA_007 external acquisition, market data close prices are raw nominal unadjusted prices. Local corporate action logs remain unverified. As required by protocol:
`CORPORATE_ACTION_SENSITIVITY = BLOCKED`
No synthetic or ad-hoc adjustments were manufactured.

---

## 28. IHSG Benchmark Analysis

The IHSG benchmark (`^JKSE`, verified hash `cabd5b7cc11a9bb903098798591e7e290ab39ae5b62cc0b843b2b5398d5ee234`, 2,826 trading sessions) was used to compute security excess returns:
$$R_{i, t \to t+h}^{\text{IHSG\_EXCESS}} = R_{i, t \to t+h} - R_{\text{IHSG}, t \to t+h}$$

| Outcome | N | ACT Mean | Control Mean | Raw Diff | Stratified Beta | SE | P Cluster | P Wild |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **H1_IHSG_EXCESS** | 1,354 | -0.0529 pp | -0.3448 pp | +0.2919 pp | +0.2690 pp | 0.1711 | 0.1159 | 0.1440 |
| **H3_IHSG_EXCESS** | 1,318 | -0.1767 pp | -0.4533 pp | +0.2766 pp | +0.1674 pp | 0.2770 | 0.5456 | 0.5450 |
| **H5_IHSG_EXCESS** | 1,417 | +0.1309 pp | -0.1213 pp | +0.2521 pp | +0.0057 pp | 0.3355 | 0.9864 | 0.9860 |
| **H10_IHSG_EXCESS** | 1,417 | +0.7662 pp | +0.5273 pp | +0.2389 pp | -0.1259 pp | 0.3336 | 0.7057 | 0.7210 |
| **H20_IHSG_EXCESS** | 1,338 | +1.4089 pp | +0.6623 pp | +0.7467 pp | +0.3705 pp | 0.7760 | 0.6330 | 0.6710 |

All IHSG excess horizons fail to show statistically reliable discrimination ($p_{\text{wild}} > 0.14$).

---

## 29. Sector vs Market Benchmark Analysis

Comparing H5 Raw, H5 IHSG Excess, and H5 LOO Peer Excess:
* **H5 Raw Beta**: +0.0250 pp (p = 0.9350)
* **H5 IHSG Excess Beta**: +0.0057 pp (p = 0.9860)
* **H5 Peer Excess Beta**: -0.0279 pp (p = 0.9370)

Conclusion: Whether benchmarking against the aggregate market index (IHSG) or sector leave-one-out peer portfolios, the stratified conditional mean difference remains statistically indistinguishable from zero under both index and peer benchmarks.

---

## 30. Outlier Sensitivity

* **Baseline (Unmodified)**: Beta = -0.0279 pp, SE = 0.3742, $p_{\text{wild}} = 0.9370$.
* **Winsorized (1st / 99th percentiles)**: Beta = -0.0591 pp, SE = 0.3400, $p_{\text{wild}} = 0.8780$.
* **Trimmed (outer 1% removed, N=1,387)**: Beta = -0.2186 pp, SE = 0.3377, $p_{\text{wild}} = 0.5350$.

Conclusion: Outlier treatment does not alter inference; the stratified conditional association remains indistinguishable from zero.

---

## 31. Coverage Selection Analysis

Coverage across dimensions:
* **Signal States**: ACT (80.4%), WAIT (78.4%), WATCH (82.2%). Balance delta = 3.7 pp $\rightarrow$ Zero evidence of selection bias by signal state.
* **Years**: 2016–2020 (~75%), 2021–2025 (~90%–99%), 2026 (49.4%).
* **Sectors**: 6 sectors between 77% and 95%; Tech at 56.3% due to late IPO listings.
* **Classification**: `COVERAGE_SELECTION_RISK = MODERATE` (driven entirely by IPO calendar and market holiday, but homogeneous across signal states).

---

## 32. 79/80 Ticker Gap

* **Missing Ticker**: `WSKT` (PT Waskita Karya Persero Tbk).
* **Cause**: Trading suspension and subsequent delisting due to debt default/restructuring.
* **Setups Affected**: 22 canonical setups.
* **Sector Representation**: Industrials & Capital Goods sector has 12 other canonical equities (ADHI, PTPP, WIKA, UNTR, etc.).
* **Impact**: Minimal on sector representation (N=239 setups remain).

---

## 33. 1,760 Setup Coverage & Reconciliation

Exact accounting of all 1,760 setups:
* **Usable H5 Peer Excess**: 1,417 setups.
* **Unusable Setups (Total = 343)**:
  * WSKT delisted/suspended: 22 setups.
  * IDX Market Holiday (2026-03-18 Idul Fitri): 79 setups.
  * Pre-IPO trading inception gap: 230 setups.
  * Session calendar offset on 2017-05-18: 12 setups.
* Total: $1,417 + 22 + 79 + 230 + 12 = 1,760$.

---

## 34. 2026 Right-Censoring

* **Calendar Cutoff**: Market data extends through 2026-09-15.
* **Signal Date 2026-08-27**: Exactly 13 subsequent trading sessions exist.
* **H1, H3, H5, H10**: Resolved and valid (N=79).
* **H20**: Requires 20 sessions; strictly classified as `RIGHT_CENSORED` (79 setups).
* **Audit**: Censoring is purely temporal, not an ingestion failure.

---

## 35. Data Provenance

The provenance chain for every empirical observation is fully auditable:
$$\text{setup\_id} \to \text{ticker} \to \text{yfinance raw CSV} \to \text{SHA256} \to \text{IHSG session calendar} \to \text{Close Price} \to \text{LOO sector mean} \to \text{H5\_PEER\_EXCESS}$$
Zero intermediate transformations, zero unrecorded data mutations.

---

## 36. PIT Integrity

A rigorous scientific distinction is made between component layers:
* **Outcome Temporal Alignment & Forward-Horizon Integrity**: **`VERIFIED`**. Forward session indices ($t+h$) are constructed chronologically without calendar overlap.
* **Target Leakage Audit**: **`PASS`**. Information ladder features and strata definitions were generated strictly prior to outcome realization.
* **Full Historical Point-in-Time (PIT) Integrity**: **`PARTIAL / NOT_FULLY_VERIFIED`**. While session alignment is verified, external market ingestion from third-party APIs (`yfinance`) and unverified historical corporate actions prevent declaring full repository-wide PIT perfection.

---

## 37. Leakage Audit

* Audit for target leakage: PASS.
* Information ladder features were computed outcome-blind prior to return realization.
* Stratification factors (`YEAR`, `MARKET_REGIME`, `SECTOR`) are strictly point-in-time.

---

## 38. Synthetic Contamination Audit

Inspection of runtime execution path:
* `zzz148_decision_utility_gate`: **ABSENT (PASS)**
* `construct_four_counterfactual_arms`: **ABSENT (PASS)**
* `excess_H5_pct`: **ABSENT (PASS)**
* `arm_b_action`, `arm_c_action`, `arm_d_action`: **ABSENT (PASS)**
* Hardcoded multipliers: **ABSENT (PASS)**
* Cached results injection: **CLEARED (PASS)**

---

## 39. Independent Recalculation

An independent recalculation was executed across 35 randomly sampled setups representing 15 distinct equities and multiple historical years. Raw daily Close prices were extracted directly from immutable raw CSVs, forward returns recomputed, and compared against pipeline values:
* **Setups Audited**: 35.
* **Tickers Represented**: 15.
* **Float Tolerance**: $10^{-5}$.
* **Mismatches Detected**: **0 (Zero)**.
* **Status**: **PASS (100% VERIFIED)**.

---

## 40. Dual-Run Reproducibility

Two completely independent runs from clean disk states were executed:
* All 12 output CSV artifacts produced **100% identical SHA256 hashes**.
* Primary Stratified Beta: Exact match to 10 decimal places.
* Wild Bootstrap P-Value: Exact match (0.9370).
* Status: **PASS (100% DETERMINISTIC)**.

---

## 41. Multiple-Comparison Discipline

The reporting strictly separates:
* **PRIMARY**: `H5_PEER_EXCESS`, ACT vs WATCH+WAIT, exact-stratified.
* **SECONDARY**: Other forward horizons and IHSG excess returns.
* **ROBUSTNESS**: Permutation, Bootstrap, LOO, Outlier, and Coverage sensitivities.
* **EXPLORATORY**: Signal gradient and temporal splits.
No cherry-picking of favorable subsets.

---

## 42. Evidence Matrix

| Evidence Layer | Test | Result | Direction | Stability | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary** | H5 Peer Excess Stratified | Beta = -0.0279 pp | Flat (-0.03 pp) | Stable Null Estimate | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H1 Raw Return | Beta = +0.2812 pp | Positive (+0.28 pp) | Insignificant (p=0.119) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H3 Raw Return | Beta = +0.1696 pp | Positive (+0.17 pp) | Insignificant (p=0.539) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H5 Raw Return | Beta = +0.0250 pp | Flat (+0.03 pp) | Insignificant (p=0.935) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H10 Raw Return | Beta = -0.1447 pp | Negative (-0.14 pp) | Insignificant (p=0.674) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H20 Raw Return | Beta = +0.4327 pp | Positive (+0.43 pp) | Insignificant (p=0.621) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H10 Peer Excess | Beta = -0.1422 pp | Negative (-0.14 pp) | Insignificant (p=0.713) | SIGNAL_NOT_SUPPORTED |
| **Secondary Horizon** | H20 Peer Excess | Beta = +0.5489 pp | Positive (+0.55 pp) | Insignificant (p=0.572) | SIGNAL_NOT_SUPPORTED |
| **Secondary Benchmark**| H5 IHSG Excess | Beta = +0.0057 pp | Flat (+0.01 pp) | Insignificant (p=0.986) | SIGNAL_NOT_SUPPORTED |
| **Temporal** | 4-Period Generalization | Betas: -1.04, +0.48, +0.86, -0.18 pp | Oscillating Signs | Inconsistent Across Eras | SIGNAL_NOT_SUPPORTED |
| **Regime** | 4 Market Regimes | Betas: -0.27, +0.33, +0.42, -0.85 pp | Regime-dependent | Insignificant (all p>0.29) | SIGNAL_NOT_SUPPORTED |
| **Sector** | 7 Canonical Sectors | 4 Negative, 3 Positive | Heterogeneous | Insignificant (all p>0.15) | SIGNAL_NOT_SUPPORTED |
| **Robustness LOO** | 79-Ticker LOO | Betas in [-0.23, +0.09] pp | Centered Near Zero | High Stability | SIGNAL_NOT_SUPPORTED |
| **Robustness LOSO** | 7-Sector LOO | Betas in [-0.26, +0.29] pp | Centered Near Zero | High Stability | SIGNAL_NOT_SUPPORTED |
| **Distributional** | Mann-Whitney & Median | MWU p=0.4643, Med p=0.5447 | Null distribution match | Inconclusive Shift | SIGNAL_NOT_SUPPORTED |
| **Placebo** | Permutation & Placebo | Perm p=0.9470, Plac p=0.9470 | Null distribution match | Indistinguishable from Random | SIGNAL_NOT_SUPPORTED |
| **Sensitivity** | Coverage & Outlier | Betas in [-0.22, -0.04] pp | Centered Near Zero | High Stability | SIGNAL_NOT_SUPPORTED |
| **Firewall** | Corporate Action Sensitivity | BLOCKED | N/A | Protected | BLOCKED |

---

## 43. Failed Checks

* `DIRECTIONAL_DISCRIMINATION_CHECK`: **FAILED**. The signal fails to produce a statistically reliable positive conditional differential on empirical returns under the primary estimand.
* `TEMPORAL_PERSISTENCE_CHECK`: **FAILED**. The conditional association inverts signs across historical market eras.
* `SIGNAL_MONOTONICITY_CHECK`: **FAILED**. WATCH state return (+0.30 pp) exceeds ACT state return (-0.02 pp).

---

## 44. Partial Checks

* `DATA_FOUNDATION_COVERAGE`: **PARTIAL**. 79/80 equities populated (WSKT missing); 1,417 / 1,760 setups populated.
* `FULL_HISTORICAL_PIT_INTEGRITY`: **PARTIAL / NOT_FULLY_VERIFIED**. Session-forward alignment is verified, but unverified corporate action adjustments and external API provenance prevent declaring full PIT verification.

---

## 45. Blocked Checks

* `CORPORATE_ACTION_SENSITIVITY`: **BLOCKED**. Raw unadjusted close prices used; verified split/dividend series not established.
* `STRATEGY_OPTIMIZATION`: **BLOCKED**.

---

## 46. Limitations

1. **Pre-IPO Truncation**: 230 setups in early years (2016–2020) cannot be evaluated because the companies were not yet publicly traded.
2. **Delisted Equity Gap**: WSKT (22 setups) has no historical data due to delisting.
3. **Market Holiday**: Canonical date 2026-03-18 fell on an IDX holiday (Idul Fitri), removing 79 setups.
4. **Unadjusted Prices**: Small dividend adjustments (~1%–3% annually) are absent, though share splits are reflected in raw nominal prices.

---

## 47. Scientific Interpretation

The empirical evidence from COBA_008 provides a rigorous basis for scientific conclusions:
1. **The COBA_005 effect did not replicate after expansion from the truncated 12-ticker sample to the expanded empirical population.** When expanded to 79 equities and 1,417 setups, the point estimate moves from -1.9675 pp ($p=0.0110$) to -0.0279 pp ($p=0.9370$). The causal mechanisms underlying this non-replication (e.g., whether driven by selection bias, survivorship, or idiosyncratic variance in the 12 pilot tickers) cannot be definitively established from observational data alone.
2. **No statistically reliable directional discrimination was detected under the frozen primary estimand.** The analysis explicitly distinguishes between a *failure to detect robust empirical discrimination* (which the data directly supports) and *formal mathematical proof of an exact zero effect* (which observational data cannot provide). The 95% confidence interval [-0.7613 pp, +0.7055 pp] demonstrates that small effects cannot be strictly ruled out.
3. **Exploratory temporal slices (such as Period A and Period C) show nominal statistical significance in opposing directions, but fail to exhibit consistent temporal persistence or stable bootstrap significance across market cycles.**

---

## 48. Final Evidence Classification

Criteria Evaluation:
* Is primary effect directionally coherent? NO ($\beta \approx -0.03$ pp, CI spans zero).
* Is temporal generalization consistent? NO (oscillates between negative and positive).
* Does empirical evidence consistently fail to demonstrate standalone directional discriminatory value? **YES**.

Final Scientific Classification:
# **`SIGNAL_NOT_SUPPORTED`**

*Classification Standard*: No sufficiently robust empirical evidence of standalone directional discrimination under the frozen primary estimand and tested robustness battery.

---

## 49. Scientific Firewall Status & Next Research Question

### Scientific Firewall:
* `CAUSALITY = NOT_PROVEN`
* `STANDALONE_ALPHA = NOT_PROVEN`
* `STRATEGY_OPTIMIZATION = BLOCKED`
* `STRATEGY_READINESS = NOT_READY`

### Exact Next Research Question:
> **"Under what pre-specified market, liquidity, volatility, regime, sector, flow, or setup-quality conditions—if any—does PURE_AGENT1_SIGNAL exhibit conditional empirical discrimination that is absent in the unconditional population?"**
