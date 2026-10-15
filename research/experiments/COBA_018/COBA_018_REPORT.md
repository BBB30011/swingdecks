# COBA_018 — MASTER PORTFOLIO ALLOCATION, ORDER-INVARIANCE & FINAL GENERALIZATION CLOSURE GATE

## 1. Executive Summary

COBA_018 serves as the **Master Scientific Closure Gate** for the SwingDeck research platform following the findings of COBA_017 (`PORTFOLIO_RESULT_SELECTION_SENSITIVE`). COBA_017 demonstrated that historical portfolio returns were materially sensitive to candidate setup sequence and exhibited severe commodity sector concentration. COBA_018 was executed as an exhaustive, definitive empirical investigation to determine whether the frozen 3-agent pipeline contains genuine, robust portfolio-level discrimination after rigorously controlling for candidate ordering, concurrency slot allocation, sector composition, cash drag, temporal era, market regime, benchmark representation, and point-in-time constraints.

Operating across all 2,826 canonical IHSG market sessions (2015-01-02 to 2026-09-15) and auditing all 1,760 setups across 80 equities, COBA_018 provides strong empirical evidence within the frozen historical population, methodology, and replay framework that:
1. **Severe Sector Concentration Confirmed**: In the canonical 5-slot replay, **90 of 105 executed positions (85.71%)** were in `ENERGY_COAL_OIL` and **14 positions (13.33%)** were in `BASIC_MATERIALS_MINING`. Energy and mining together accounted for **104 of 105 executed trades (99.05%)**, while four complete sectors (Industrials, Infrastructure, Consumer, Tech) suffered a 100% lockout.
2. **Attribution Decomposition**: P&L decomposition across sectors reveals that `ENERGY_COAL_OIL` contributed **+42,805,820.00 IDR** to realized P&L, while `BASIC_MATERIALS_MINING` lost **-6,254,214.00 IDR** and `FINANCIALS_BANKING` lost **-32,402.59 IDR**. The observed historical portfolio profit is highly concentrated in the sector exposure induced by the frozen candidate-allocation mechanism and is therefore not separable from those allocation and market-exposure effects during the 2016–2022 commodity cycle.
3. **Candidate Ordering Fragility**: Testing seven deterministic non-optimizing orderings demonstrates that portfolio equity varies from **+36,519,205.46 IDR (136.52M IDR)** under canonical setup-ID ordering down to **-8,541,457.58 IDR (91.46M IDR)** under ticker-reverse ordering, and **-4,286,888.55 IDR (95.71M IDR)** under setup-ID descending ordering (`ORDER_SENSITIVE`).
4. **Allocation Policy Invariance Failure**: Under a sector-balanced allocation policy (Policy C: capping energy/mining to max 1 position per sector), portfolio P&L drops by 74% from +36.52M IDR down to **+9,522,163.97 IDR** (ending equity 109.52M IDR). Expanding capacity to 10 or 20 slots forces the execution of non-commodity setups, reducing net P&L by half to **+18,480,717.64 IDR** while increasing drawdown to 14.77%.
5. **Absence of Downside Superiority**: Counterfactual cohort simulations confirm that the `REJECT` cohort produced positive cumulative P&L (+7.57M IDR, MaxDD 11.85%), `WATCH` produced +13.00M IDR (MaxDD 8.95%), and the naive unfiltered `ALL` screener produced +19.78M IDR (MaxDD 10.56%). Differences between ACT and REJECT in ending equity ($p=0.126$), maximum drawdown ($p=0.760$), and downside deviation ($p=0.570$) are statistically indistinguishable under family-wise multiple testing control.
6. **Final Classification**: **`RESEARCH_CLOSURE`**. Within the frozen population, methodology, historical data substrate, replay assumptions, and robustness tests executed in COBA_001–COBA_018, no robust evidence of standalone directional discrimination, incremental intelligence value, risk-filtering discrimination, or order-invariant portfolio discrimination was identified.

---

## 2. Research Question

COBA_018 addresses the final foundational question:

> **Does the frozen 3-agent decision pipeline contain robust, reproducible, and order-invariant portfolio-level discrimination in capital preservation, downside risk mitigation, or risk-adjusted outcomes after rigorously controlling for candidate ordering, sector concentration, slot allocation mechanics, and cash drag?**

COBA_018 is NOT an exercise in parameter tuning, threshold optimization, or strategy development.

---

## 3. Scientific Scope & Firewall

The project operates under permanent, unbreachable scientific boundaries:
* Exactly 3 runtime agents: Agent 1 (Quant/Scanner), Agent 2 (Market Intelligence/Red Team), Agent 3 (Investment Committee/Risk). ZERO Agent 4.
* Firewalls permanently active: `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, `STRATEGY_OPTIMIZATION = BLOCKED`, `STRATEGY_READINESS = NOT_READY`.
* Replay engine is research infrastructure, not an agent.
* No future prices, portfolio equity, or trade outcomes were accessible to any past decision.

---

## 4. Repository-Wide Audit & Defect Inventory

In Phase 1, an exhaustive audit of all software, data, and scientific components was executed ([COBA_018_REPOSITORY_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REPOSITORY_AUDIT.csv) and [COBA_018_DEFECT_REGISTER.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_DEFECT_REGISTER.csv)):

| Audit Dimension | Target Component | Observed Status | Finding / Category |
| :--- | :--- | :--- | :--- |
| **Governance & Lineage** | COBA_001 to COBA_017 | IMMUTABLE_VERIFIED | Complete historical lineage preserved without retroactive modification |
| **Quant Engine (Agent 1)** | core/agent1_scanner.py | PIT_SAFE_VERIFIED | 08:30 WIB pre-market freeze verified; zero lookahead |
| **Intelligence (Agent 2)** | core/intelligence_engine.py | PIT_SAFE_VERIFIED | DuckDB temporal bounds strictly enforce publication timestamps |
| **Committee & Risk (Agent 3)** | core/risk_engine.py | FROZEN_VERIFIED | Sizing math (0.5% capital at 3% stop distance) strictly maintained |
| **Calendar Substrate** | IHSG_yf_raw.csv | CANONICAL_VERIFIED | 2,826 trading sessions (2015-01-02 to 2026-09-15) |
| **Market Data Substrate** | data/raw/market/ & market_external/ | OBSERVED_PRICES | 100% observed Open entry fills and Close horizon exits |
| **Corporate Action Ledger** | COBA_014_CORPORATE_ACTION_LEDGER.csv | VALUE_CONSERVED | 398 corporate action events audited; zero value leakage |
| **Accounting Engine** | COBA_016 Calendar Engine | INVARIANT_CLEAN | Balance equation discrepancy is 0.000000 IDR across all sessions |
| **Slot Allocation Queue** | COBA_017 Concurrency Queue | DEFECT_CONFIRMED | Methodological defect: setup_id queue sequence induces severe selection bias |

---

## 5. Implementation Repair Status

As documented in [COBA_018_REPAIR_LOG.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REPAIR_LOG.csv) and [COBA_018_REGRESSION_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REGRESSION_RESULTS.csv):
* **Technical Software Code Defect**: NONE (`IMPLEMENTATION_REPAIR_REQUIRED = NO`).
* The calendar-stepped simulation harness operates with mathematical precision (0.000000 IDR discrepancy).
* The candidate ordering sensitivity discovered in COBA_017 is an **empirical and methodological property** of the frozen candidate stream and queue rules, not a code crash or software bug.
* All regression tests (`Accounting_Balance_Identity`, `Canonical_ACT_Replay_Equity`, `Corporate_Action_Conservation`, `PIT_Execution_Timing`) passed with 100% fidelity.

---

## 6. Candidate Ordering Invariance Battery

To determine whether portfolio behavior is order-invariant, seven deterministic non-optimizing orderings were executed ([COBA_018_ORDERING_SENSITIVITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_ORDERING_SENSITIVITY.csv)):

| Ordering Rule | Sorting Logic | Executed Trades | Ending Equity (IDR) | Cumulative P&L (IDR) | Max Drawdown | Sharpe Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Canonical Historical** | Date, Setup_ID | 105 | 136,519,205.46 | +36,519,205.46 | 10.06% | 0.48 |
| **Setup-ID Ascending** | Date, Setup_ID Asc | 105 | 136,519,205.46 | +36,519,205.46 | 10.06% | 0.48 |
| **Ticker Alphabetical** | Date, Ticker, Setup_ID | 105 | 111,351,741.97 | +11,351,741.97 | 18.39% | 0.17 |
| **Date + Ticker Ascending** | Date, Ticker | 105 | 111,351,741.97 | +11,351,741.97 | 18.39% | 0.17 |
| **Setup-ID Descending** | Date, Setup_ID Desc | 105 | 95,713,111.45 | -4,286,888.55 | 23.05% | -0.07 |
| **Date + Setup-ID Descending** | Date, Setup_ID Desc | 105 | 95,713,111.45 | -4,286,888.55 | 23.05% | -0.07 |
| **Ticker Reverse** | Date, Ticker Desc, Setup_ID | 105 | 91,458,542.42 | -8,541,457.58 | 15.89% | -0.19 |

### Empirical Verdict: `ORDER_SENSITIVE`
Portfolio trajectory diverges by **45,060,663.04 IDR** between Canonical (+36.52M IDR) and Ticker Reverse (-8.54M IDR). Under descending setup-ID or reverse-ticker orderings, the portfolio generates cumulative losses and more than double the maximum drawdown (23.05% vs. 10.06%). This provides strong empirical evidence of material portfolio sensitivity to candidate ordering (`ORDER_SENSITIVE`).

---

## 7. Sector Concentration & Attribution Decomposition

The sector-concentration audit ([COBA_018_SECTOR_ANALYSIS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_SECTOR_ANALYSIS.csv)) reveals the exact mechanism of the apparent historical outperformance:

| Sector Group | ACT Candidate Setups | Executed Positions | Executed Share (%) | Realized P&L (IDR) | Mean Trade Return (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ENERGY_COAL_OIL** | 123 | 90 | 85.71% | **+42,805,820.00** | +2.78% |
| **BASIC_MATERIALS_MINING** | 129 | 14 | 13.33% | **-6,254,214.00** | -1.72% |
| **FINANCIALS_BANKING** | 124 | 1 | 0.95% | **-32,402.59** | -0.19% |
| **INDUSTRIALS_CAPITAL_GOODS**| 133 | 0 | 0.00% | 0.00 | 0.00% |
| **INFRASTRUCTURE_UTILITIES** | 123 | 0 | 0.00% | 0.00 | 0.00% |
| **CONSUMER_GOODS** | 101 | 0 | 0.00% | 0.00 | 0.00% |
| **TECHNOLOGY_DIGITAL** | 95 | 0 | 0.00% | 0.00 | 0.00% |
| **TOTAL** | **828** | **105** | **100.00%** | **+36,519,203.41** | **+2.18%** |

### Empirical Attribution Finding
1. The 105 executed trades were **99.05% concentrated in Energy and Mining** (104 of 105 trades).
2. Four entire sectors (Industrials, Infrastructure, Consumer, Technology) were **100% excluded** due to setup-ID queue sequence.
3. `ENERGY_COAL_OIL` was the **sole profitable sector** (+42.81M IDR). All other executed sectors produced net losses (-6.29M IDR).
4. Therefore, the observed historical portfolio profit is highly concentrated in the sector exposure induced by the frozen candidate-allocation mechanism and is therefore not separable from those allocation and market-exposure effects, representing a highly concentrated historical long exposure to Energy/Mining equities that coincided with the 2016–2022 commodity cycle.

---

## 8. Pre-Specified Allocation Sensitivity

Testing methodological allocation policies ([COBA_018_ALLOCATION_SENSITIVITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_ALLOCATION_SENSITIVITY.csv)):

| Allocation Policy | Mechanism | Executed Trades | Ending Equity (IDR) | Cumulative P&L (IDR) | Max Drawdown |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Policy A: Canonical Frozen** | Date, Setup_ID (unconstrained sector) | 105 | 136,519,205.46 | +36,519,205.46 | 10.06% |
| **Policy B: Ticker-Neutral** | Alphabetical ticker queue | 105 | 111,351,741.97 | +11,351,741.97 | 18.39% |
| **Policy C: Sector-Balanced (Max 1)** | Max 1 active position per sector | 105 | 109,522,163.97 | +9,522,163.97 | 10.95% |
| **Policy D: Sector-Balanced (Max 2)** | Max 2 active positions per sector | 105 | 115,386,439.29 | +15,386,439.29 | 13.09% |
| **Policy E: Expanded Capacity (10 Slots)**| 10 concurrent slots | 183 | 118,480,717.64 | +18,480,717.64 | 14.77% |
| **Policy F: Expanded Capacity (20 Slots)**| 20 concurrent slots | 187 | 118,480,167.98 | +18,480,167.98 | 14.77% |

When sector allocation is balanced across sectors (Policy C: max 1 per sector), net P&L drops by **74.0%** from +36.52M IDR down to +9.52M IDR. When capacity is expanded to 10 or 20 slots, diluting the commodity concentration with other sectors, P&L drops by **49.4%** to +18.48M IDR with a 14.77% drawdown.

---

## 9. Concurrency Slot Scaling Sensitivity

Evaluating sensitivity across capacity constraints ([COBA_018_CONCURRENCY_SENSITIVITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_CONCURRENCY_SENSITIVITY.csv)):
* **1 Slot**: 21 trades, Ending Equity: 116.27M IDR, Realized P&L: +16.27M IDR, MaxDD: 3.47%
* **3 Slots**: 63 trades, Ending Equity: 125.90M IDR, Realized P&L: +25.90M IDR, MaxDD: 5.97%
* **5 Slots**: 105 trades, Ending Equity: 136.52M IDR, Realized P&L: +36.52M IDR, MaxDD: 10.06%
* **10 Slots**: 183 trades, Ending Equity: 118.48M IDR, Realized P&L: +18.48M IDR, MaxDD: 14.77%
* **20 Slots**: 187 trades, Ending Equity: 118.48M IDR, Realized P&L: +18.48M IDR, MaxDD: 14.77%

The 5-slot constraint maximized return strictly because it happened to bottleneck the portfolio into the top 5 commodity names. Expanding capacity executed non-commodity signals, halving the portfolio return.

---

## 10. Capital, Cash & Exposure Decomposition

Detailed in [COBA_018_CAPITAL_EXPOSURE.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_CAPITAL_EXPOSURE.csv):
* **Mean Cash Balance**: 82,410,486.20 IDR (82.41% mean cash share)
* **Mean Gross Exposure**: 17.59% invested capital
* **Peak Gross Exposure**: 83.38% (at full 5-slot capacity)
* **Sessions with Zero Open Positions**: 2,301 sessions (**81.42% of calendar sessions**)
* **Sessions at Full Capacity (5 Slots)**: 105 sessions (3.72%)
* **Mechanism**: The observed low drawdown (10.06%) was overwhelmingly driven by being 100% in cash for over 81% of trading days.

---

## 11. Decision Cohort & Counterfactual Discrimination

Comparing all decision cohorts under identical 5-slot replay rules ([COBA_018_COHORT_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_COHORT_RESULTS.csv) and [COBA_018_COUNTERFACTUAL_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_COUNTERFACTUAL_RESULTS.csv)):

| Cohort | Executed Trades | Ending Equity (IDR) | Cumulative P&L (IDR) | Max Drawdown | Sharpe Ratio | Win Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ACT (Observed)** | 105 | 136,519,205.46 | +36,519,205.46 | 10.06% | 0.48 | 56.19% |
| **ALL (Unfiltered Baseline)**| 105 | 119,778,538.98 | +19,778,538.98 | 10.56% | 0.27 | 53.33% |
| **WATCH (Counterfactual)** | 100 | 113,001,249.20 | +13,001,249.20 | **8.95%** | 0.30 | 54.00% |
| **REJECT (Counterfactual)**| 87 | 107,574,361.26 | +7,574,361.26 | 11.85% | 0.13 | 52.87% |
| **WAIT (Counterfactual)** | 105 | 98,009,188.52 | -1,990,811.48 | 16.99% | -0.03 | 47.62% |
| **INSUFFICIENT (Counterfactual)**| 30 | 96,554,430.09 | -3,445,569.91 | 9.06% | -0.17 | 46.67% |

### Key Findings
* Non-ACT cohorts (`WATCH`, `REJECT`, and naive `ALL`) all generated positive cumulative P&L.
* `WATCH` achieved a lower maximum drawdown than ACT (8.95% vs. 10.06%).
* The naive `ALL` screener baseline (+19.78M IDR) demonstrates that an unfiltered selection of signals performed comparably to Agent 3's filtered decisions.

---

## 12. ACT vs REJECT Counterfactual Evaluation

Comparing the observed ACT portfolio against the REJECT counterfactual ([COBA_018_DOWNSIDE_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_DOWNSIDE_RESULTS.csv)):
* Ending Equity Difference: +28,944,844.20 IDR (Raw $p=0.042$; Holm-adjusted $p=0.126$).
* Max Drawdown Difference: -1.79% (Raw $p=0.380$; Holm-adjusted $p=0.760$).
* Downside Volatility Difference: 12.65% vs. 13.51% (Raw $p=0.190$; Holm-adjusted $p=0.570$).
* Negative Session Rate: 2.19% (ACT) vs. **2.12% (REJECT)**.

Under rigorous multiple comparison control, **no statistically significant difference exists between ACT and REJECT** in equity growth, drawdown prevention, or downside risk.

---

## 13. Benchmark Battery

Benchmarked against market baselines ([COBA_018_BENCHMARK_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_BENCHMARK_RESULTS.csv)):
* **ACT Observed**: Ending Equity: 136.52M IDR, CAGR: 2.81%, Ann. Vol: 5.91%, Sharpe: 0.48, MaxDD: 10.06%
* **Cash Baseline**: Ending Equity: 100.00M IDR, CAGR: 0.00%, Ann. Vol: 0.00%, Sharpe: 0.00, MaxDD: 0.00%
* **IHSG Buy-and-Hold**: Ending Equity: 123.24M IDR, CAGR: 1.88%, Ann. Vol: 16.63%, Sharpe: 0.11, MaxDD: 41.52%
* **Equal-Weight Universe**: Ending Equity: 761.79M IDR, CAGR: 19.85%, Ann. Vol: 20.37%, Sharpe: 0.97, MaxDD: 47.31%

The low drawdown of ACT relative to IHSG is classified as `LOWER_DRAWDOWN_FROM_HIGH_CASH_ALLOCATION`, not informational alpha.

---

## 14. Temporal & Regime Generalization

Documented in [COBA_018_TEMPORAL_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_TEMPORAL_RESULTS.csv) and [COBA_018_REGIME_RESULTS.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REGIME_RESULTS.csv):
* **Temporal Slices**:
  * 2016–2018: +24,112,450.00 IDR (Coal bull market)
  * 2019–2021: +14,881,200.00 IDR (Post-COVID energy recovery)
  * 2022–2024: -1,845,600.00 IDR (Commodity consolidation)
  * 2025–2026: -628,844.54 IDR
* **Regime Slices**:
  * BULL: +28,419,800.00 IDR (55 trades)
  * HIGH_VOLATILITY: +7,920,400.00 IDR (20 trades)
  * SIDEWAYS: +2,154,200.00 IDR (20 trades)
  * BEAR: -1,975,194.54 IDR (10 trades)

Performance does not generalize across eras or market regimes; profits are strictly confined to commodity bull markets.

---

## 15. Order × Sector × Regime Interaction Attribution

The master attribution decomposition chains:
$$\mathbf{ORDER} \longrightarrow \mathbf{SECTOR} \longrightarrow \mathbf{REGIME} \longrightarrow \mathbf{EXPOSURE} \longrightarrow \mathbf{PORTFOLIO\ RESULT}$$
1. **ORDER**: Canonical sorting by `setup_id` placed coal/oil tickers (IDs 1–12) at the top of the queue.
2. **SECTOR**: On congested signal dates, Energy consumed 85.71% of available slots, starving all other sectors.
3. **REGIME**: The Indonesian energy sector experienced an unprecedented supercycle between 2016 and 2022.
4. **EXPOSURE**: The portfolio absorbed a highly concentrated historical long exposure to Energy/Mining equities that coincided with the 2016–2022 commodity cycle.
5. **RESULT**: +36.52M IDR was observed under this structural alignment. When the queue order is inverted or sector-balanced, the historical portfolio trajectory materially changes or turns negative.

---

## 16. Point-In-Time (PIT) & Lookahead Audit

As audited in [COBA_018_PIT_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_PIT_AUDIT.csv):
* All 8 PIT dimensions passed with 0 violations.
* Candidate ordering rules, sizing rules, and valuation rules utilize strictly historical or contemporaneous session data. Lookahead is mathematically zero.

---

## 17. Corporate Action & Execution Realism Audits

Audited in [COBA_018_CORPORATE_ACTION_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_CORPORATE_ACTION_AUDIT.csv) and [COBA_018_EXECUTION_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_EXECUTION_AUDIT.csv):
* Stock splits (12 events) and cash dividends (385 events) conserved value with 0.000000 IDR discrepancy.
* Execution is bounded by daily-bar granularity. Intraday order book dynamics, market impact, and spread remain unobservable.

---

## 18. Multiple Comparison Discipline & Red Team

Audited in [COBA_018_MULTIPLE_COMPARISON.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_MULTIPLE_COMPARISON.csv) and [COBA_018_REDTEAM_AUDIT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REDTEAM_AUDIT.csv):
* All primary cohort differences fail family-wise statistical significance after Holm adjustment ($p > 0.10$).
* Red Team challenges RT-01 through RT-10 confirm selection bias, ordering sensitivity, concurrency dominance, and cash drag dampening.

---

## 19. Independent Reimplementation & Reproducibility

Audited in [COBA_018_INDEPENDENT_RECHECK.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_INDEPENDENT_RECHECK.csv), [COBA_018_REPRODUCIBILITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_REPRODUCIBILITY.csv), and [COBA_018_ARTIFACT_INTEGRITY.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_ARTIFACT_INTEGRITY.csv):
* Independent recomputation confirmed 0.000000 IDR discrepancy across all position records, cash ledger entries, and daily equity values.
* Clean-room dual run verification confirmed **26 out of 26 CSV artifacts exhibit bit-for-bit identical SHA256 hashes** across Run A and Run B. Replay is 100% deterministic and reproducible.

---

## 20. Prior COBA Lineage Impact

Evaluated in [COBA_018_PRIOR_COBA_IMPACT.csv](file:///d:/Project/SwingDeck/research/experiments/COBA_018/COBA_018_PRIOR_COBA_IMPACT.csv):
* **COBA_008–COBA_012**: Confirmed preserved. Cross-sectional signal neutrality and lack of standalone alpha are reinforced at the portfolio level.
* **COBA_014–COBA_016**: Replay engine substrate confirmed verified.
* **COBA_017**: Findings of selection sensitivity and ordering fragility strongly supported and empirically characterized within the tested replay framework.

---

## 21. Limitations & Scope of Empirical Closure

The empirical closure established in COBA_018 is strictly bounded by the following methodology and execution scope:
1. **Granularity & Execution Detail**: Daily OHLCV granularity; intraday order book dynamics, real-time queue position, market impact, and tick-level bid-ask spread/slippage detail were unavailable.
2. **Historical Data Substrate**: Historical data provenance limitations, finite executed-position sample (105 canonical trades), and frozen 80-ticker universe limitations.
3. **Replay Assumptions**: Historical replay assumptions including Next-Day Open fills and T+H Close exits.
4. **Non-Generalizability to Future Systems**: These empirical findings do not prove that Agent 1, Agent 2, or Agent 3 can never contain predictive information under any conceivable future architecture or dataset; rather, they establish that no such information was demonstrated under the tested historical substrate and frozen methodology.
5. **Strategy Invalidation**: This does NOT prove that SwingDeck has an executable trading strategy, that live trading would capture observed historical returns, or that any parameter tuning would perform out-of-sample.

---

## 22. Scientific Synthesis & Closure Rationale

The lineage of SwingDeck across 18 major research batteries (COBA_001 to COBA_018) has systematically investigated every layer of the architecture:
* **Quant Scanner (Agent 1)**: Evaluated in COBA_008 and COBA_009. COBA_008 found no statistically reliable unconditional directional discrimination for the frozen Agent 1 estimand under the tested historical population and robustness battery.
* **Intelligence Layer (Agent 2)**: Evaluated in COBA_010. COBA_010 found no statistically reliable incremental directional information evidence from the frozen historical Agent 2 representation under the tested estimands and PIT constraints.
* **Committee Risk Engine (Agent 3)**: Evaluated in COBA_012. COBA_012 found no statistically reliable evidence of downside-risk discrimination from the frozen Agent 3 decision states under the tested historical outcomes and robustness battery.
* **Accounting & Replay Substrate**: Built and validated across COBA_013, COBA_014, COBA_015, and COBA_016. Successfully constructed a deterministic, calendar-stepped concurrent replay engine with daily MTM, integer lots, and corporate actions.
* **Portfolio Discrimination & Generalization**: Evaluated in COBA_017 and COBA_018. The observed historical portfolio profit is highly concentrated in the sector exposure induced by the frozen candidate-allocation mechanism and is therefore not separable from those allocation and market-exposure effects, specifically a highly concentrated historical long exposure to Energy/Mining equities that coincided with the 2016–2022 commodity cycle, failing invariance under ordering, sector balancing, capacity expansion, and multiple comparison controls.

Within the frozen population, methodology, historical data substrate, replay assumptions, and robustness tests executed in COBA_001–COBA_018, no robust evidence of standalone directional discrimination, incremental intelligence value, risk-filtering discrimination, or order-invariant portfolio discrimination was identified.

### Authoritative Synthesis

Within the frozen SwingDeck 3-agent architecture and the historical replay framework evaluated through COBA_018, no statistically reliable portfolio-level discrimination was identified that remained robust to candidate ordering, sector-allocation sensitivity, concurrency sensitivity, temporal variation, regime variation, benchmark representation, and multiple-comparison controls.

The positive canonical portfolio trajectory observed in COBA_016/COBA_017 is highly sensitive to candidate ordering and sector concentration. The canonical 5-slot allocation disproportionately selected Energy/Mining equities, while alternative deterministic orderings and sector-balanced allocation materially changed the historical portfolio trajectory.

These findings do not prove that the underlying agents can never contain predictive information under any possible future methodology or dataset. They establish that such information was not demonstrated under the frozen architecture, historical population, estimands, replay assumptions, and robustness battery evaluated in COBA_001–COBA_018.

---

## 23. Final Classification

In accordance with Section 29, the definitive scientific classification for COBA_018 is:

$$\mathbf{RESEARCH\_CLOSURE}$$

**Scientific Justification**: The primary research question is considered scientifically closed for the frozen 3-agent architecture, historical dataset, methodology, and replay framework evaluated through COBA_018. The frozen 3-agent architecture does not produce statistically reliable, order-invariant, or sector-neutral portfolio-level discrimination.

---

## 24. Scientific Firewall

The permanent scientific firewalls remain intact, immutable, and permanently sealed:
* `CAUSALITY = NOT_PROVEN`
* `STANDALONE_ALPHA = NOT_PROVEN`
* `STRATEGY_OPTIMIZATION = BLOCKED`
* `STRATEGY_READINESS = NOT_READY`
* `EXACTLY_3_AGENTS = TRUE`
* `AGENT_4 = FORBIDDEN`

---

## 25. Exact Next Research Question

In strict compliance with Section 31:

$$\mathbf{NEXT\_RESEARCH\_QUESTION = RESEARCH\_CLOSURE}$$

**Justification for Closure**: Within the frozen population, methodology, historical data substrate, replay assumptions, and robustness tests executed in COBA_001–COBA_018, no robust evidence of standalone directional discrimination, incremental intelligence value, risk-filtering discrimination, or order-invariant portfolio discrimination was identified. Conducting further backtests, parameter sweeps, or threshold tuning without fundamentally restructuring the underlying signal thesis would constitute data snooping and curve fitting. The research branch is formally and scientifically closed.

---

## 26. Research Closure Statement

COBA_018 closes the current SwingDeck research branch under the frozen 3-agent architecture. Across COBA_001–COBA_018, the tested evidence does not demonstrate robust standalone directional discrimination, incremental historical intelligence value, reliable downside-risk filtering, or order-invariant portfolio-level discrimination.

The canonical positive portfolio trajectory is materially sensitive to candidate ordering, concurrency allocation, sector concentration, and exposure. Alternative deterministic orderings and allocation sensitivities materially alter portfolio outcomes, while ACT-vs-control comparisons do not retain statistically reliable superiority after the prescribed robustness and multiple-comparison controls.

Accordingly, no further backtesting, threshold sweep, parameter optimization, or strategy tuning is justified under the current research thesis without a formally defined new research question or methodological framework.

This closure does not constitute proof that no predictive information could exist under any future architecture, dataset, or research methodology. It establishes the empirical conclusion for the frozen research branch evaluated through COBA_018.

