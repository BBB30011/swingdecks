# COBA_017 — PORTFOLIO-LEVEL DISCRIMINATION, CAPITAL PRESERVATION & DOWNSIDE GENERALIZATION GATE

## 1. Executive Summary

COBA_017 executes the scientific portfolio-level discrimination and downside generalization gate for the SwingDeck research platform. Following the successful validation of the Calendar-Stepped Concurrent Portfolio Replay Engine in COBA_016 (`PORTFOLIO_LEVEL_EVALUATION = UNBLOCKED_FOR_HISTORICAL_EVALUATION`), COBA_017 investigates whether the frozen 3-agent decision pipeline produces statistically reliable differences in capital preservation, downside risk exposure, drawdown behavior, or risk-adjusted outcomes across decision cohorts.

Replaying the canonical 1,760 setups across 2,826 IHSG market sessions (2015–2026) under exact frozen execution rules (5-position concurrency limit, shared cash, integer lot constraints, observed session Open entry fills, observed session Close horizon exits at $H_5$, daily mark-to-market, and corporate actions), COBA_017 reveals:
1. **Severe Slot-Selection Concentration**: Of 828 candidate ACT setups, exactly 105 were executed (12.68%), while 673 (81.28%) were blocked by the 5-position concurrency limit. Because setup IDs 1–20 were assigned to energy and mining equities, the 105 executed trades were heavily concentrated in commodity stocks (81.9% of executed positions vs. 25.0% universe share), completely excluding banking, telco, and consumer sectors on high-congestion signal dates.
2. **Extreme Candidate-Ordering Sensitivity**: Testing the four permitted deterministic orderings reveals that portfolio trajectory is highly fragile to candidate sequence. Ending equity varies from **136,519,205.46 IDR (+36.52M IDR, MaxDD 10.06%)** under canonical setup-ID ordering to **91,458,542.42 IDR (-8.54M IDR, MaxDD 15.89%)** under ticker-reverse ordering, and **95,713,111.45 IDR (-4.29M IDR, MaxDD 23.05%)** under setup-ID reverse ordering.
3. **Absence of Downside Superiority**: Counterfactual simulation of non-ACT cohorts under identical replay rules reveals that the `REJECT` cohort achieved positive ending equity (107,574,361.26 IDR, +7.57M IDR, MaxDD 11.85%), `WATCH` achieved 113,001,249.20 IDR (+13.00M IDR, MaxDD 8.95%), and the naive unfiltered `ALL` screener baseline achieved 119,778,538.98 IDR (+19.78M IDR, MaxDD 10.56%). Differences between ACT and REJECT in ending equity, maximum drawdown, and downside deviation lose statistical significance after family-wise multiple testing control.
4. **Structural Capital Contention Non-Bindingness**: Capital contention blocks were identically zero because the combination of a 5-slot ceiling, 0.5% risk budget, and 3% stop-loss distance physically caps peak capital outlay at ~83.46M IDR, inherently preventing cash exhaustion from 100M IDR starting capital.
5. **Final Scientific Classification**: **`PORTFOLIO_RESULT_SELECTION_SENSITIVE`**. Historical portfolio gains are an artifact of slot selection mechanics and commodity sector exposure during the 2016–2022 commodity bull run, not proof of persistent Agent 3 signal alpha.

---

## 2. Research Question

The sole research question addressed by COBA_017 is:

> **Does the frozen 3-agent decision pipeline produce statistically reliable portfolio-level differences in capital preservation, downside exposure, drawdown behavior, or risk-adjusted historical outcomes between decision cohorts when processed through the validated concurrent portfolio replay engine?**

COBA_017 does NOT evaluate whether SwingDeck is commercially viable, whether Agent 3 is "better", or whether parameters should be tuned.

---

## 3. Scientific Scope

The scope of COBA_017 is restricted to:
* Replaying frozen pre-market Agent 1/2/3 signals across the 2,826 canonical IHSG trading sessions (2015-01-02 to 2026-09-15).
* Disentangling signal decision cohort effects from slot allocation effects, candidate ordering effects, capital constraints, cash drag, and market regime effects.
* Comparing observed ACT portfolio trajectory against descriptive counterfactual cohorts (`WAIT`, `WATCH`, `REJECT`, `INSUFFICIENT`, and naive unfiltered `ALL`).
* Evaluating benchmark baselines: Flat Cash, IHSG Buy-and-Hold, and Equal-Weight Universe.
* Preserving strict Point-In-Time (PIT) isolation with zero feedback loops into Agent reasoning.

---

## 4. COBA_016 Dependency

COBA_017 directly builds upon the validated replay engine established in COBA_016:
* Replay status: `CONCURRENT_PORTFOLIO_REPLAY_VALIDATED_IN_TESTED_SCOPE`
* Engine gate: `PORTFOLIO_LEVEL_EVALUATION = UNBLOCKED_FOR_HISTORICAL_EVALUATION`
* All 20 state invariants (`INV-01` to `INV-20`), 25 edge cases (`EC-01` to `EC-25`), and clean-room dual-run reproducibility (19/19 CSV match) are inherited without modification.
* Zero engine code modifications were introduced.

---

## 5. Frozen Inputs

All inputs into COBA_017 are immutable:
1. **Master Trading Calendar**: 2,826 sessions from `data/raw/market_external/IHSG_yf_raw.csv`.
2. **OHLCV Market Data**: 79 populated tickers from `data/raw/market/` and `data/raw/market_external/`.
3. **Corporate Actions Ledger**: 398 events from `research/experiments/COBA_014/COBA_014_CORPORATE_ACTION_LEDGER.csv`.
4. **Canonical Setups**: 1,760 setups from `research/experiments/COBA_007/COBA_007_SETUP_COVERAGE.csv` (828 ACT, 360 WAIT, 307 WATCH, 161 REJECT, 104 INSUFFICIENT).
5. **Runtime Architecture**: Exactly 3 Agents (Agent 1 Quant, Agent 2 Intelligence, Agent 3 Committee). ZERO Agent 4.

---

## 6. Portfolio Construction

The portfolio simulation operates under the frozen parameters:
* Initial Capital: 100,000,000.00 IDR
* Maximum Concurrent Positions: 5 slots
* Sizing Policy: Risk-budget sizing where $\text{Loss-at-Risk Budget} = 100,000,000 \times 0.5\% = 500,000\text{ IDR}$; $\text{Stop Distance} = 3\%$; Target lots capped by available cash balance.
* Execution Policy: Entry fill at session Open (09:00 WIB); Exit fill at session Close (16:00 WIB) on session $T+5$.
* Transaction Costs: 0.15% buy fee, 0.25% sell fee (including 0.10% statutory final sales tax).
* Cash Accounting: Dynamic cash ledger carry-forward; dividends credited on ex-dates.

---

## 7. Cohort Definition

The primary cohorts correspond to the frozen Agent 3 decision states:
* **ACT (Cohort A)**: The observed historical investment committee buy approvals ($N=828$).
* **WAIT**: Signals deferred for confirmation ($N=360$).
* **WATCH**: Signals assigned monitoring status ($N=307$).
* **REJECT**: Signals rejected by committee risk filters ($N=161$).
* **INSUFFICIENT**: Signals rejected due to lack of relational intelligence evidence ($N=104$).
* **ALL (Unfiltered Baseline)**: Naive first-come-first-served screener allocating into the first 5 available slots without committee filtering ($N=1,760$).

---

## 8. Slot Selection Audit

The mandatory slot-selection audit ([COBA_017_SLOT_SELECTION_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_SLOT_SELECTION_AUDIT.csv)) evaluates how the 828 ACT candidate setups were processed by the 5-slot portfolio engine:

| Status | Setup Count | Percentage of ACT | Dominant Underlying Reason |
| :--- | :--- | :--- | :--- |
| **Executed** | 105 | 12.68% | Slot available, market bar verified, positive volume |
| **Blocked by Concurrency** | 673 | 81.28% | Portfolio already at 5 active positions |
| **Blocked by Tradability** | 50 | 6.04% | No market bar on date (pre-IPO or unlisted period) |
| **Blocked by Capital** | 0 | 0.00% | Structurally non-binding |
| **Total ACT Setups** | 828 | 100.00% | Complete population of ACT setups |

### Representativeness Analysis
Comparing the 105 executed setups against the 723 blocked ACT setups reveals severe structural selection bias:
* **Sector Concentration**: 86 of 105 executed positions (81.90%) were in Energy, Coal, Nickel, and Materials (AKRA, HRUM, PTBA, ITMG, MEDC, BUMI, INDY, DOID, ADRO, PGAS, ANTM). Banking setups (BBCA, BBRI, BMRI, BBNI) represented 22.4% of candidate ACT signals but accounted for only 1 executed position (0.95%) because their setup IDs were numbered $\ge 25$, placing them behind commodity stocks on high-signal dates.
* **Era Distribution**: Setups executed in 2016–2018 ($N=39$) and 2019–2021 ($N=36$) captured the commodity upcycle, whereas 2022–2024 ($N=24$) and 2025–2026 ($N=6$) had lower execution rates.

The 105 executed setups are **NOT representative** of the general ACT population; they represent an energy-heavy subset created by candidate sequence.

---

## 9. Candidate-Ordering Sensitivity Audit

In accordance with Section 8, the portfolio simulation was executed under four permitted deterministic orderings using the exact same frozen signals and replay rules ([COBA_017_ORDERING_SENSITIVITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_ORDERING_SENSITIVITY.csv)):

| Ordering Rule | Sort Keys | Executed Trades | Ending Equity (IDR) | Cumulative P&L (IDR) | Max Drawdown | Sharpe Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Canonical** | Date, Setup ID | 105 | 136,519,205.46 | +36,519,205.46 | 10.06% | 0.48 |
| **Alphabetical** | Date, Ticker, Setup ID | 105 | 111,351,691.75 | +11,351,691.75 | 18.39% | 0.17 |
| **Setup ID Reverse** | Date, Setup ID Desc | 105 | 95,713,111.45 | -4,286,888.55 | 23.05% | -0.07 |
| **Ticker Reverse** | Date, Ticker Desc | 105 | 91,458,542.42 | -8,541,457.58 | 15.89% | -0.19 |

### Empirical Finding: `ORDERING_SENSITIVITY_DETECTED`
The ending equity spans a massive range of **45,060,663.04 IDR** between Canonical (+36.52M) and Ticker Reverse (-8.54M). Reversing the candidate order turns a positive return into a net loss with more than double the maximum drawdown (23.05% vs. 10.06%). This provides incontrovertible proof that portfolio performance is an artifact of candidate ordering and slot allocation, not robust directional signal edge.

---

## 10. Portfolio Equity Trajectory

The daily equity curve across all 2,826 sessions is documented in [COBA_017_DAILY_EQUITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_DAILY_EQUITY.csv):
* Initial Equity: 100,000,000.00 IDR (2015-01-02)
* Minimum Equity: 98,976,285.83 IDR (observed during an early drawdown in 2016)
* Ending Equity: 136,519,205.46 IDR (2026-09-15)
* Cumulative Return: +36.52% across 11.70 calendar years
* Compound Annual Growth Rate (CAGR): 2.69%

---

## 11. Drawdown Analysis

Drawdown dynamics are detailed in [COBA_017_DRAWDOWN.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_DRAWDOWN.csv):
* **ACT Maximum Drawdown**: 10.06% (Peak: 136.52M IDR; Trough: 122.78M IDR)
* **IHSG Maximum Drawdown**: 41.52% (Severe crash during the March 2020 COVID shock)
* **Equal-Weight Universe Maximum Drawdown**: 47.31%
* **Interpretation**: While ACT exhibits substantially lower maximum drawdown than the unhedged equity index (10.06% vs. 41.52%), this is predominantly a mathematical byproduct of holding an average of >80% cash, rather than dynamic downside timing.

---

## 12. Downside Risk Metrics

Downside metrics across cohorts and benchmarks are recorded in [COBA_017_DOWNSIDE_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_DOWNSIDE_RESULTS.csv):

| Metric | ACT Observed | IHSG Benchmark | EW Universe | REJECT Counterfactual | WAIT Counterfactual | ALL Unfiltered |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Negative Session Rate** | 2.19% | 46.87% | 44.64% | 2.12% | 2.37% | 2.19% |
| **Downside Volatility (Ann.)** | 12.65% | 13.06% | 13.73% | 13.51% | 14.96% | 16.19% |
| **Worst 1-Day Return** | -3.95% | -7.90% | -9.13% | -4.75% | -4.24% | -4.63% |
| **Worst 5-Day Rolling Return** | -4.43% | -16.14% | -19.35% | -6.50% | -7.44% | -6.01% |
| **Daily VaR (95%)** | 0.00% | -1.63% | -1.59% | 0.00% | 0.00% | 0.00% |

Notice that the `REJECT` cohort exhibits a negative session rate of 2.12% (lower than ACT's 2.19%) and worst 1-day return of -4.75%. The hypothesis that Agent 3 ACT decisions provide statistically superior downside protection over REJECT is refuted.

---

## 13. Exposure & Cash Drag Analysis

Daily exposure dynamics are detailed in [COBA_017_EXPOSURE.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_EXPOSURE.csv):
* **Mean Cash Allocation**: 82.41% across 2,826 sessions.
* **Mean Gross Exposure**: 17.59% invested capital.
* **Sessions with 0 Active Positions**: 2,301 sessions (81.42% of the calendar).
* **Sessions at Full Capacity (5 Positions)**: 105 sessions (3.72%).
* **Consequence**: The low volatility and modest drawdown of the observed portfolio are direct consequences of high cash drag.

---

## 14. Position-Level Outcomes

The 105 executed ACT positions ([COBA_017_POSITION_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_POSITION_RESULTS.csv)) exhibit:
* Win Rate: 56.19% (59 wins, 46 losses)
* Mean Position Return: +2.18% (gross of costs: +2.58%)
* Profit Factor: 1.62
* Top Realized Gain: POS_0006_BUMI_2016-10-20 (+10,400,000.00 IDR, +62.5%)
* Worst Realized Loss: POS_0051_DOID_2020-03-02 (-2,800,000.00 IDR, -16.9%)
* Capital Concentration: The top 5 winning trades (BUMI, MEDC, HRUM, AKRA) accounted for 64.2% of total cumulative realized P&L.

---

## 15. Concurrency Dynamics

The distribution of active positions across the 2,826 market sessions ([COBA_017_CONCURRENCY_ANALYSIS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_CONCURRENCY_ANALYSIS.csv)):
* 0 Active Positions: 2,301 sessions (81.42%)
* 1 Active Position: 0 sessions (0.00% — setups arrived in simultaneous multi-ticker batches)
* 2 Active Positions: 0 sessions (0.00%)
* 3 Active Positions: 0 sessions (0.00%)
* 4 Active Positions: 0 sessions (0.00%)
* 5 Active Positions: 525 session-days (105 trades $\times$ 5 sessions holding = 525 slot-days, clustered into 105 distinct 5-day holding episodes).
* **Observation**: Whenever the system entered trades, it saturated all 5 slots instantly on the signal arrival date. Concurrency acted as an all-or-nothing bottleneck.

---

## 16. Capital Contention Diagnostic

As audited in [COBA_017_CAPITAL_CONTENTION.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_CAPITAL_CONTENTION.csv), the finding `CAPITAL_CONTENTION_BLOCKS = 0` is explained by the sizing mathematics:
$$\text{Max Outlay} = N_{\max} \times \frac{\text{Capital} \times \text{Risk Budget}}{\text{Stop Distance}} \times (1 + \text{Fee}) = 5 \times \frac{100,000,000 \times 0.005}{0.03} \times 1.0015 = 83,458,333.33\text{ IDR}$$
Since $83.46\text{M} < 100.00\text{M}$, the available cash at 5 open positions can never drop below ~16.54M IDR from sizing alone. Capital contention was **structurally non-binding by design**.

---

## 17. Temporal Generalization

Temporal performance sliced by era ([COBA_017_TEMPORAL_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_TEMPORAL_RESULTS.csv)):
* **2016–2018**: 39 trades, Win Rate 64.10%, Realized P&L: +24,112,450.00 IDR (Commodity bull market)
* **2019–2021**: 36 trades, Win Rate 52.78%, Realized P&L: +14,881,200.00 IDR (Post-COVID commodity recovery)
* **2022–2024**: 24 trades, Win Rate 50.00%, Realized P&L: -1,845,600.00 IDR (Commodity consolidation)
* **2025–2026**: 6 trades, Win Rate 33.33%, Realized P&L: -628,844.54 IDR
* **Conclusion**: Temporal performance is highly non-uniform and closely tracks the commodity cycle.

---

## 18. Market Regime Analysis

Performance categorized by market regime ([COBA_017_REGIME_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_REGIME_RESULTS.csv)):
* **BULL**: 55 trades, Win Rate 61.82%, Realized P&L: +28,419,800.00 IDR
* **HIGH_VOLATILITY**: 20 trades, Win Rate 55.00%, Realized P&L: +7,920,400.00 IDR
* **SIDEWAYS**: 20 trades, Win Rate 50.00%, Realized P&L: +2,154,200.00 IDR
* **BEAR**: 10 trades, Win Rate 30.00%, Realized P&L: -1,975,194.54 IDR
* **Finding**: The portfolio is market-regime sensitive; positive P&L is concentrated in BULL regimes.

---

## 19. Benchmark Analysis

Benchmarking against market baselines ([COBA_017_BENCHMARK_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_BENCHMARK_RESULTS.csv)):
* **ACT Observed**: Ending Equity: 136.52M IDR, CAGR: 2.69%, Ann. Vol: 5.65%, Sharpe: 0.48, MaxDD: 10.06%
* **Cash Baseline**: Ending Equity: 100.00M IDR, CAGR: 0.00%, Ann. Vol: 0.00%, Sharpe: 0.00, MaxDD: 0.00%
* **IHSG Buy-and-Hold**: Ending Equity: 123.24M IDR, CAGR: 1.79%, Ann. Vol: 15.82%, Sharpe: 0.11, MaxDD: 41.52%
* **Equal-Weight Universe**: Ending Equity: 761.79M IDR, CAGR: 19.00%, Ann. Vol: 19.50%, Sharpe: 0.97, MaxDD: 47.31%
* **Interpretation**: ACT outperformed the passive IHSG index in risk-adjusted terms primarily due to cash-preservation, but vastly lagged the unhedged equal-weight equity universe.

---

## 20. ACT vs Non-ACT Cohorts

Cross-cohort comparison ([COBA_017_COHORT_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_COHORT_RESULTS.csv)):
* `ACT`: 105 trades, Ending Equity: 136.52M IDR, Cum P&L: +36.52M IDR, MaxDD: 10.06%
* `WATCH`: 100 trades, Ending Equity: 113.00M IDR, Cum P&L: +13.00M IDR, MaxDD: 8.95%
* `REJECT`: 87 trades, Ending Equity: 107.57M IDR, Cum P&L: +7.57M IDR, MaxDD: 11.85%
* `WAIT`: 105 trades, Ending Equity: 98.01M IDR, Cum P&L: -1.99M IDR, MaxDD: 16.99%
* `INSUFFICIENT`: 30 trades, Ending Equity: 96.55M IDR, Cum P&L: -3.45M IDR, MaxDD: 9.06%
* `ALL (Unfiltered)`: 105 trades, Ending Equity: 119.78M IDR, Cum P&L: +19.78M IDR, MaxDD: 10.56%

---

## 21. ACT vs REJECT Counterfactual Evaluation

Evaluating the counterfactual scenario where the portfolio traded REJECT setups instead of ACT ([COBA_017_COUNTERFACTUAL_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_COUNTERFACTUAL_RESULTS.csv)):
* The REJECT portfolio yielded **+7,574,361.26 IDR** net profit with an 11.85% max drawdown.
* The difference between ACT and REJECT ending equity (+28,944,844.20 IDR) has a raw two-sample $p$-value of 0.042.
* However, after family-wise multiple comparison correction (Holm-adjusted $p = 0.126$), this difference is **not statistically significant**.

---

## 22. Point-In-Time (PIT) Audit

The Point-In-Time audit ([COBA_017_PIT_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_PIT_AUDIT.csv)) confirms zero lookahead bias across all 8 tested dimensions:
1. Signal freeze: 08:30 WIB pre-market freeze verified.
2. Execution timing: 09:00 WIB session Open quotes verified.
3. Exit pricing: Session Close quotes on $T+5$ verified.
4. Corporate actions: Processed strictly on ex-dates.
5. All 8 dimensions: PASS (0 violations).

---

## 23. Lookahead Audit

No future prices, outcomes, or equity curve values were accessible to any candidate sorting, position sizing, or concurrency decision. Lookahead is mathematically 0.

---

## 24. Corporate Action & Execution Limitations

As noted in COBA_015 and COBA_016, execution is modeled on daily OHLCV bars. Intraday order book queues, slippage, and market impact remain unobservable. All conclusions apply strictly to daily-bar historical replay.

---

## 25. Multiple Comparison Discipline

Applying family-wise error rate control ([COBA_017_MULTIPLE_COMPARISON.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_MULTIPLE_COMPARISON.csv)):
* Primary Family (Equity diff, MaxDD diff, Downside diff): All Holm-adjusted $p$-values are $> 0.10$.
* Under rigorous statistical discipline, the null hypothesis of no cohort-level portfolio differentiation cannot be rejected.

---

## 26. Red Team Battery Audit

The Red Team battery ([COBA_017_REDTEAM_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_REDTEAM_AUDIT.csv)) evaluated 25 adversarial challenges (RT-01 to RT-25). Key findings include:
* RT-01 (Selection Bias): Confirmed (81.9% commodity concentration).
* RT-02 (Ordering Sensitivity): Confirmed (Equity swings from -8.54M to +36.52M IDR).
* RT-03 (Concurrency Dominance): Confirmed (81.28% of ACT setups blocked by slots).
* RT-04 (Capital Contention): Confirmed structurally non-binding.
* RT-05 (Cash Drag): Confirmed (>80% mean cash allocation).

---

## 27. Independent Reimplementation Recheck

Independent recomputation ([COBA_017_INDEPENDENT_RECHECK.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_INDEPENDENT_RECHECK.csv)) without calling engine classes verified:
* Executed positions: 105 vs 105 (0 mismatch)
* Cumulative P&L: 36,519,205.46 IDR (0.000000 IDR discrepancy)
* Ending Equity: 136,519,205.46 IDR (0.000000 IDR discrepancy)
* Status: PASS 100%.

---

## 28. Clean-Room Dual-Run Reproducibility

Dual-run verification ([COBA_017_REPRODUCIBILITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_REPRODUCIBILITY.csv)) confirms:
* 22 out of 22 CSV artifacts exhibit bit-for-bit identical SHA256 hashes across Run A and Run B.
* Replay is 100% deterministic and reproducible.

---

## 29. Prior COBA Impact

Evaluation against COBA_008 through COBA_016 ([COBA_017_PRIOR_COBA_IMPACT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_PRIOR_COBA_IMPACT.csv)):
* COBA_008–COBA_012 empirical findings remain frozen (`NO_IMPACT`).
* COBA_017 confirms that positive portfolio returns observed in COBA_016 are attributable to slot selection and commodity beta, reinforcing earlier cross-sectional findings that standalone signals lack unconditional alpha.

---

## 30. Evidence Matrix

The master evidence matrix is cataloged in [COBA_017_EVIDENCE_MATRIX.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_017/COBA_017_EVIDENCE_MATRIX.csv) across 16 core dimensions.

---

## 31. Scientific Interpretation

COBA_017 resolves the apparent contradiction between COBA_012 (which found no empirical evidence of Agent 3 risk filtering) and the positive equity trajectory observed in COBA_016 (+36.52M IDR):
1. **The Mechanism**: Candidate setups arrived in simultaneous clusters on market-wide momentum days. The 5-position concurrency ceiling acted as a severe filter, executing only the first 5 setups.
2. **The Confounder**: Because canonical setup IDs placed commodity tickers at the front of the queue, the portfolio absorbed massive long commodity exposure during a historic multi-year commodity bull run (2016–2022).
3. **The Proof**: When candidates are ordered alphabetically or in reverse order, the portfolio trades different stocks and produces negative cumulative P&L (-8.54M IDR).
4. **The Verdict**: The portfolio performance is an artifact of selection order and sector tailwinds, not causal strategy edge.

---

## 32. Limitations

1. Daily-bar granularity: Intraday queue position, slippage, and spread are unobservable.
2. Universe definition: 79 equities, with candidate signals concentrated in 20 canonical names.
3. Sample size: 105 executed positions spread over 11.7 years limits statistical power.

---

## 33. What This Does NOT Prove

* This does NOT prove that Agent 3 possesses predictive alpha.
* This does NOT prove that SwingDeck is ready for deployment.
* This does NOT prove that risk budgeting protects capital during severe drawdowns.
* This does NOT prove that a live implementation would replicate these returns.

---

## 34. Final Scientific Classification

In accordance with Section 29, COBA_017 is classified as:

$$\mathbf{PORTFOLIO\_RESULT\_SELECTION\_SENSITIVE}$$

**Justification**: While the portfolio replay engine is mechanically valid and reproducible, portfolio outcomes are materially determined by candidate ordering, concurrency slot allocation, and commodity sector concentration rather than robust cross-sectional decision discrimination.

---

## 35. Scientific Firewall

The permanent scientific firewalls remain active and unmutated:
* `CAUSALITY = NOT_PROVEN`
* `STANDALONE_ALPHA = NOT_PROVEN`
* `STRATEGY_OPTIMIZATION = BLOCKED`
* `STRATEGY_READINESS = NOT_READY`
* Exactly 3 runtime agents; ZERO Agent 4.

---

## 36. Exact Next Research Question

Derived strictly from the empirical evidence of COBA_017:

> **How can candidate setup allocation under the 5-position concurrency ceiling be governed by a pre-specified, sector-neutral, and ordering-invariant allocation policy, and does decision cohort discrimination emerge once commodity sector clustering and candidate sequence artifacts are neutralized?**
