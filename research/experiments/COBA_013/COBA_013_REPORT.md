# COBA_013 — MASTER FOUNDATION CLOSURE, DATA INTEGRITY, SELECTION, EXECUTION & PORTFOLIO READINESS BATTERY

**Scientific Battery Status:** `COMPLETED`  
**Master Foundation Classification:** `FOUNDATION_BLOCKED`  
**Execution Date:** `2026-09-27`  
**Runtime Agents:** Exactly 3 (Agent 1: Quant/Scanner, Agent 2: Intelligence/Red Team, Agent 3: Investment Committee/Risk). ZERO Agent 4.  

---

## 1. Executive Summary
COBA_013 executes a comprehensive, single-battery master foundation closure audit across the entire SwingDeck quantitative research pipeline. Following the completion and scientific freezing of COBA_008 through COBA_012—which systematically demonstrated empirical neutrality across Agent 1 quantitative signals, Agent 2 qualitative intelligence, and Agent 3 downside risk filtering—COBA_013 consolidates the empirical and operational infrastructure required to evaluate whether SwingDeck's scientific foundation is sufficiently complete, point-in-time safe, representative, execution-aware, and portfolio-accounting-ready to support a future controlled portfolio-level evaluation.

Auditing 80 canonical equities, 1,760 setups, 2,826 master market trading sessions, 15 red-team adversarial dimensions, and all repository schemas, COBA_013 establishes that:
1. **Market Data Foundation is Partial:** 79 out of 80 canonical equities (98.75%) are populated with valid daily OHLCV files across 1,429 setups. Exactly 1 equity (`WSKT`, 22 setups) is completely unpopulated due to trading suspension/delisting on the Indonesia Stock Exchange. In 76,000+ audited daily price bars across 2016–2026, zero fatal OHLC errors, zero duplicate dates, and zero negative prices exist. Exactly 3 historical High < Low inversions were discovered in pre-sample data (2007-02-01 in ASII, TLKM, UNTR) and are formally flagged in the quality ledger without silent deletion.
2. **Point-in-Time Alignment is Structurally Sound but Provenance is Partial:** Pre-market signal observation at 08:30 T strictly precedes 09:00 T market open. Forward outcome evaluation strictly starts at Close of session t+1 and bounds path excursions across [t+1, t+h], establishing `OUTCOME_TEMPORAL_ALIGNMENT = VERIFIED`. However, because external market data and historical news disclosures lack certified immutable exchange snapshot feeds, `FULL_HISTORICAL_PIT = PARTIAL`.
3. **Corporate Action Adjustments are Unperformed:** The repository operates on raw unadjusted price series (`PRICE_SERIES = RAW_UNADJUSTED`). Pilot equities exhibit 1 to 2 stock splits and 18 to 47 cash dividend distributions. Because no external corporate action adjustments ledger is frozen, `CORPORATE_ACTION_SENSITIVITY = BLOCKED`.
4. **Benchmark & Peer Calculations are Methodologically Sound:** The broad-market IHSG benchmark (^JKSE, 2,826 sessions) is 100% calendar-aligned with equity trading days (`BENCHMARK_STATUS = VERIFIED`). The canonical leave-one-out sector peer-excess calculation strictly excludes the target equity from its own benchmark (`SELF_INCLUSION_NONE = VERIFIED`).
5. **Sample Attrition & Missingness is Non-Random:** Canonical universe of 1,760 setups attrites to 1,429 market setups and 1,417 complete cases on H5 peer excess (80.51% coverage). The 343 missing setups decompose into: 309 pre-IPO history (companies not yet listed on IDX), 22 WSKT suspension/delisting, and 12 historical holiday calendar gaps. Missingness mechanism is classified as `SECTOR_ASSOCIATED_MISSINGNESS` / `UNKNOWN_NON_MCAR`; missing completely at random (MCAR) is definitively refuted.
6. **Right-Censoring is Confined and Proportional:** Across H1, H3, H5, and H10, censoring is 0.0%. At H20, exactly 79 setups (5.58%) are censored strictly on terminal date 2026-08-27. Censoring is distributed proportionally across Agent 3 states (48.1% ACT, 19.0% WAIT, 16.5% WATCH, 10.1% REJECT, 6.3% INSUFFICIENT), introducing no relative state bias.
7. **Liquidity is Highly Dispersed with an Illiquidity Tail:** Across 1,417 setups, median daily volume is 14.2M shares and median turnover is 20.9B IDR. However, 35 setups experienced zero volume on the observation bar, and 225 setups (15.88%) had daily turnover < 1B IDR, indicating meaningful execution constraints for institutional sizing.
8. **Execution Friction Modeling is Blocked:** Intraday bid/ask quotes, order book depth, market impact, slippage, and auction prints do not exist in the repository (`EXECUTION_FRICTION_MODEL = BLOCKED`). All raw returns assume friction-free execution at continuous closing prices.
9. **Portfolio Foundation is Structurally Blocked:** No cash balance ledger, historical position chronology, dynamic exposure constraint, concurrent risk budget, or equity curve engine exists in the repository (`PORTFOLIO_LEDGER = BLOCKED`, `CASH_ALLOCATION = NOT_PRE_SPECIFIED`). Equating setup-level statistics to portfolio CAGR, Sharpe ratio, or dynamic drawdown is strictly prohibited (`PORTFOLIO_LEVEL_INFERENCE = BLOCKED`).
10. **Scientific Reproducibility is 100% Verified:** Independent recalculation of 150 setups across 20 tickers, 11 years, and 4 regimes yielded 100% match (< 1e-7 diff). Clean-room dual-run comparison of all 17 generated CSV artifacts produced 100% identical SHA-256 hashes.
11. **Prior COBA Conclusions are Fully Preserved:** Findings of COBA_008 (unconditional directional null), COBA_009 (common support limitation), COBA_010 (Agent 2 neutrality), COBA_011 (structural robustness across horizons), and COBA_012 (absence of downside risk filtering) remain frozen with `LIMITED_IMPACT` (no implementation defects found).
12. **Master Readiness Decision:** `FOUNDATION_BLOCKED`. While setup-level observational foundations and benchmark mechanics are verified, the absence of an executable portfolio cash ledger, historical position chronology, corporate action adjusted series, and intraday execution friction data critically prevents scientifically valid portfolio-level evaluation at this stage.
13. **Scientific Firewalls Preserved:** `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, `STRATEGY_OPTIMIZATION = BLOCKED`, `STRATEGY_READINESS = NOT_READY`.

## 2. Exact Research Question
> *"Is the current SwingDeck scientific foundation sufficiently complete, Point-in-Time safe, representative, execution-aware, reproducible, and portfolio-accounting-ready to support a future controlled portfolio-level empirical evaluation without introducing hidden assumptions, selection bias, lookahead, corporate-action distortion, execution fantasy, or post-hoc optimization?"*

## 3. Scope & Consolidation Mandate
COBA_013 consolidates the complete empirical and operational audit into one unified master battery. It explicitly avoids splitting foundation questions into smaller sequential experiments. It does not perform trading strategy optimization, alpha hunting, threshold tuning, or profitability searches. It rigorously evaluates the ten subquestions across Historical Market Data, Point-in-Time Integrity, Corporate Actions, Benchmark Alignment, Peer Groups, Coverage, Selection Bias, Right-Censoring, Tradability/Liquidity, Execution Friction, Portfolio Accounting, Adversarial Red-Teaming, Synthetic Contamination, Reproducibility, and Prior COBA Impact.

## 4. Historical Lineage
The complete scientific lineage is strictly preserved:

`AU → AW → AX → AY → ... → ZZZ.14.x → COBA_001 → COBA_001.1 → COBA_002 → COBA_003 → COBA_004 → COBA_005 → COBA_006 → COBA_007 → COBA_008 → COBA_009 → COBA_010 → COBA_011 → COBA_012 → COBA_013`

No historical research artifacts are renamed, deleted, or altered. Prior negative or neutral empirical findings are treated as immutable frozen evidence.

## 5. Frozen Prior Findings
- **COBA_008 (`SIGNAL_NOT_SUPPORTED`):** Pure Agent 1 quantitative signals show no statistically reliable unconditional directional discrimination on H5 sector peer-excess ($\beta = -0.0279$ pp, $p_{\text{wild}} = 0.9370$).
- **COBA_009 (`NO_CONDITIONAL_EVIDENCE`):** Context-dependent conditioning (momentum, volatility, regimes) does not yield genuine alpha; apparent interactions evaporated under common support discipline.
- **COBA_010 (`NO_INCREMENTAL_INFORMATION_EVIDENCE`):** Agent 2 qualitative intelligence (adverse disclosure contradiction) provides no robust incremental directional information lift ($\beta_{\text{A2}} = +0.5018$ pp, $p_{\text{wild}} = 0.2690$).
- **COBA_011 (`STRUCTURAL_ROBUSTNESS_SUPPORTED`):** Empirical neutrality is structurally invariant across sequential horizons ($H_1$ to $H_{20}$) and benchmark representations (Raw, Sector Peer, Broad IHSG).
- **COBA_012 (`NO_RISK_FILTER_EVIDENCE`):** Downstream Agent 3 decision states demonstrate no statistically reliable downside loss prevention or adverse excursion (MAE) filtering (ACT vs REJECT $\beta = +0.2117$ pp, $p_{\text{wild}} = 0.9640$).

## 6. Frozen Inputs
| Artifact | Path | SHA256 | Status |
| --- | --- | --- | --- |
| Canonical Setup Decision Matrix | reports/zzz14_8_canonical_setup_decision_matrix.csv | f8fa877142a78d8986873fdc5b8f2ea30c3c084bd47a844a4f7cdf3c53d5ee39 | VERIFIED |
| Canonical Observation Matrix | reports/zzz1471_canonical_observation_matrix.csv | e4e2ab967de4731f55821b1db0791b53a27cff4c5a50bd047c4c7615a375f004 | VERIFIED |
| COBA_007 Setup Coverage | research/experiments/COBA_007/COBA_007_SETUP_COVERAGE.csv | e98aeacb64c5f4d1d06c72cf86704c08a7ceb368273916226e1bb8582b57a86e | VERIFIED |
| COBA_008 Primary Results | research/experiments/COBA_008/COBA_008_PRIMARY_RESULTS.csv | 01a6d1898c33f64eed6c1749d913890d31c9e214990322179ec3e2dd246bcbfb | VERIFIED |
| COBA_009 Primary Results | research/experiments/COBA_009/COBA_009_PRIMARY_INTERACTIONS.csv | 1aaf461dbcd454af0f1d3d86ca415d4694533f4d82b80fec8f7eea4bf9b15287 | VERIFIED |
| COBA_010 Primary Results | research/experiments/COBA_010/COBA_010_PRIMARY_RESULTS.csv | 07e93d8367b3fa78ba95294741f0743ede06de900f3bbed855dedadfba614f23 | VERIFIED |
| COBA_011 Primary Results | research/experiments/COBA_011/COBA_011_PRIMARY_RESULTS.csv | f4b438aa6e5da0567a35710a1219d6699fa87cbf0e9967ff20c68ad29ef08a95 | VERIFIED |
| COBA_012 Primary Results | research/experiments/COBA_012/COBA_012_PRIMARY_DOWNSIDE_RESULTS.csv | caee3dd548074d6fe69527ec56c7017fc294119f071ce5757d5490bc1f8c6d48 | VERIFIED |
| IHSG Raw Market Data | data/raw/market_external/IHSG_yf_raw.csv | cabd5b7cc11a9bb903098798591e7e290ab39ae5b62cc0b843b2b5398d5ee234 | VERIFIED |
| DuckDB Intelligence Lake | data/duckdb/intelligence.duckdb | 41f64a94dc53cf49b3fd298813f4fd9402aa11ffa4b8235c6f5914dc4c638035 | VERIFIED |

## 7. Agent Boundary
Exactly 3 runtime agents are retained: Agent 1 (Quant Scanner), Agent 2 (Market Intelligence), Agent 3 (Investment Committee & Risk). ZERO Agent 4. No agents are re-tuned, modified, split, or optimized.

## 8. Canonical Population
The canonical experimental design consists of exactly 80 equities observed across 22 historical dates spanning 2016 through 2026, defining $80 \times 22 = 1,760$ theoretical canonical setups.

## 9. Historical Market Data Foundation & 10. Data Quality Ledger
Historical market data comprises 12 local pilot equities (`data/raw/market/*_raw.csv`) and 67 external equities plus IHSG (`data/raw/market_external/*_raw.csv`). Exactly 79 of 80 canonical equities have populated market data files. WSKT is unpopulated due to trading suspension/delisting.

### Market Data Quality Audit (Sample of 15 Equities)
| Ticker | Source | File_Path | Total_Rows | Date_Min | Date_Max | Null_OHLC_Rows | Zero_Volume_Rows | Negative_Price_Rows | High_Low_Inversion_Rows | Duplicate_Dates | Continuity_Gaps_Gt5d | Raw_SHA256 | Data_Quality_Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACES | external_yfinance | data/raw/market_external/ACES_yf_raw.csv | 2879 | 2015-01-02 | 2026-09-15 | 0 | 72 | 0 | 0 | 0 | 12 | fdac80dcb30ed3616483e48470bb57f40000f69ab82c635754e088048bd25a4b | VERIFIED_VALID |
| ADHI | external_yfinance | data/raw/market_external/ADHI_yf_raw.csv | 2882 | 2015-01-02 | 2026-09-15 | 0 | 95 | 0 | 0 | 0 | 12 | 62c686091311a9df971cb67829dff32be7fee0f4c5f3422ae3fa31de1ef5f1f3 | VERIFIED_VALID |
| ADRO | local_pilot | data/raw/market/ADRO_raw.csv | 4458 | 2008-07-15 | 2026-09-13 | 0 | 91 | 0 | 0 | 0 | 20 | 8f91590d0b9fcfb98cb708029c6e4e7b7dc5b230f83eeee58436331fcbbea414 | VERIFIED_VALID |
| AKRA | external_yfinance | data/raw/market_external/AKRA_yf_raw.csv | 2880 | 2015-01-02 | 2026-09-15 | 0 | 73 | 0 | 0 | 0 | 12 | 078243e2e69e54120fc7333ad79bc64073215ab424526790bb830ad409006fd7 | VERIFIED_VALID |
| AMMN | external_yfinance | data/raw/market_external/AMMN_yf_raw.csv | 763 | 2023-07-07 | 2026-09-15 | 0 | 7 | 0 | 0 | 0 | 4 | fc6bcad5449c0c3cca38d9e3ae994aad02fb34ae69b769729b1cc5c2fbfc0284 | VERIFIED_VALID |
| ANTM | local_pilot | data/raw/market/ANTM_raw.csv | 5159 | 2005-09-28 | 2026-09-13 | 0 | 769 | 0 | 0 | 0 | 23 | cdfab8b0c8e39f80b9507d8af298ad708f6fe13caa87b825c6138abad3090b37 | VERIFIED_VALID |
| ARTO | external_yfinance | data/raw/market_external/ARTO_yf_raw.csv | 2621 | 2016-01-12 | 2026-09-15 | 0 | 300 | 0 | 0 | 0 | 12 | 5d05e37c3036248cc232a205a9f3f5dea2bdec7852e3c32b7acaae4ac9441de5 | VERIFIED_VALID |
| ASII | local_pilot | data/raw/market/ASII_raw.csv | 6440 | 2000-10-16 | 2026-09-13 | 0 | 196 | 0 | 1 | 0 | 23 | d651e78fa8db13e0749eac68f60dd51da425df696da8d9cd85975a7d61f669a9 | HISTORICAL_ANOMALY_FLAGGED |
| ASSA | external_yfinance | data/raw/market_external/ASSA_yf_raw.csv | 2879 | 2015-01-02 | 2026-09-15 | 0 | 71 | 0 | 0 | 0 | 12 | 18a51660f169d832345984da24d5555506e8ea82d2efc19e1ea5d9bcc8b5550b | VERIFIED_VALID |
| BBCA | local_pilot | data/raw/market/BBCA_raw.csv | 5490 | 2004-06-07 | 2026-09-13 | 0 | 123 | 0 | 0 | 0 | 23 | df07a39de50c0132c57b04778c7b443ef2b320cf6197503096dcefeb3398aa24 | VERIFIED_VALID |
| BBNI | local_pilot | data/raw/market/BBNI_raw.csv | 5611 | 2003-12-22 | 2026-09-13 | 0 | 160 | 0 | 0 | 0 | 23 | bd7f032efeda3515695e932b5cea22b536c39a8692d32b1ee492b6ce483f6adb | VERIFIED_VALID |
| BBRI | local_pilot | data/raw/market/BBRI_raw.csv | 5642 | 2003-11-09 | 2026-09-13 | 0 | 140 | 0 | 0 | 0 | 23 | 1082ab04b913b664e75a7741c444454103ccd64fe469cec8b6ae81670031ee75 | VERIFIED_VALID |
| BBTN | external_yfinance | data/raw/market_external/BBTN_yf_raw.csv | 2880 | 2015-01-02 | 2026-09-15 | 0 | 71 | 0 | 0 | 0 | 12 | ed4025c6ac737d25f9248cfb498b9517d811e7e2f8687ff8cdfc6df63d785324 | VERIFIED_VALID |
| BDMN | external_yfinance | data/raw/market_external/BDMN_yf_raw.csv | 2881 | 2015-01-02 | 2026-09-15 | 0 | 76 | 0 | 0 | 0 | 12 | a40c2b836bea3242054206ce142e9c1452d1386644073323d3c81b63c90a4a2b | VERIFIED_VALID |
| BELI | external_yfinance | data/raw/market_external/BELI_yf_raw.csv | 920 | 2022-11-08 | 2026-09-15 | 0 | 7 | 0 | 0 | 0 | 6 | 9372b6789e301304fd3605bb034723ef24512859de3d78ce3909dc6f31fe5902 | VERIFIED_VALID |

*(Full audit of all 80 equities available in `COBA_013_MARKET_DATA_QUALITY.csv`)*

*Quality Audit Findings:*
- Total price bars audited: 76,000+ daily OHLCV rows across 79 equities.
- Null OHLC rows: 0 in the 2016–2026 observation era.
- Negative price rows: 0.
- Duplicate dates: 0.
- Historical Inversions: Exactly 1 row on `2007-02-01` exhibits High < Low in ASII, TLKM, and UNTR. These occur nearly a decade prior to our experimental observation window (2016–2026). They are formally retained and flagged in the quality ledger rather than silently deleted.

## 11. Point-in-Time (PIT) Audit
Point-in-time integrity was audited across signal generation, execution, forward outcome horizons, and external data provider provenance:

| Dimension | Audit_Target | Observed_Specification | Temporal_Bound | Leakage_Risk | Status |
| --- | --- | --- | --- | --- | --- |
| SIGNAL_TIMESTAMP | Agent 1 Scanner Observation Timestamp | Fixed pre-market 08:30:00+07:00 on observation date T | Pre-market T (strictly prior to 09:00:00 market open) | ABSENT | VERIFIED |
| MARKET_OPEN_EXECUTION | Market Session Opening Price Alignment | IDX trading session begins at 09:00:00+07:00 | Open T occurs 30 minutes after signal freeze | ABSENT | VERIFIED |
| OUTCOME_WINDOW_START | Forward Outcome Accounting Start Horizon | Horizon evaluation begins at Close of session t+1 relative to setup date t | Window strictly [t+1, t+h]; zero contemporaneous same-day bar outcome evaluation | ABSENT | VERIFIED |
| OUTCOME_WINDOW_END | Forward Horizon Terminal Session Offset | Terminal trading sessions h in {1, 3, 5, 10, 20} sequential trading days | Window strictly terminates at Close_{t+h} | ABSENT | VERIFIED |
| INTRADAY_EXTREMA_MAE_MFE | Session-by-Session Path Excursions | Minimum Low and Maximum High calculated across sessions tau in [t+1, t+h] | Strictly post-entry path; Close_t used solely as denominator basis | ABSENT | VERIFIED |
| AGENT2_INTELLIGENCE_PIT | Qualitative Intelligence Publication Timestamps | Pre-market event archiving in DuckDB; external historical news provenance partially archived | Events timestamped prior to 08:30 T where available | LOW_TO_MODERATE | PARTIAL |
| EXTERNAL_PROVENANCE_SNAPSHOTS | Historical Point-in-Time Data Lake Provenance | Market data acquired via yfinance external raw download; point-in-time exchange snapshot audit trails absent | Historical corporate adjustments may reflect retrospective provider restatements | MODERATE | PARTIAL |
| OUTCOME_TEMPORAL_ALIGNMENT | Mathematical Offset Alignment Across Datasets | 1,417 setups verified with exact sequential calendar session indices | 100% verified alignment across H1 to H20 | ABSENT | VERIFIED |
| FULL_HISTORICAL_PIT | Universal Point-in-Time Audit Across Entire Pipeline | External market data and historical news provenance lack certified immutable exchange snapshot feeds | Certified pre-outcome availability cannot be proven for all historical external records | MODERATE | PARTIAL |

*Audit Classification:* `OUTCOME_TEMPORAL_ALIGNMENT = VERIFIED`, while `FULL_HISTORICAL_PIT = PARTIAL` due to inherited limitations in external market-data and historical news archival provenance.

## 12. Corporate Actions Audit
The repository operates on raw unadjusted price series (`PRICE_SERIES = RAW_UNADJUSTED`). Pilot equities exhibit 1 to 2 stock splits and 18 to 47 cash dividend distributions:

| Ticker | Source | Known_Splits | Known_Dividends | Known_Rights_Issues | Price_Series_Type | Adjustment_Status | Outcome_Impact_Known | Corporate_Action_Sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACES | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| ADHI | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| ADRO | local_pilot | 0 | 35 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |
| AKRA | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| AMMN | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| ANTM | local_pilot | 1 | 18 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |
| ARTO | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| ASII | local_pilot | 1 | 46 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |
| ASSA | external_yfinance | 0 | 0 | 0 | RAW_UNADJUSTED | UNADJUSTED | UNKNOWN_UNPERFORMED | BLOCKED |
| BBCA | local_pilot | 2 | 47 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |
| BBNI | local_pilot | 1 | 24 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |
| BBRI | local_pilot | 2 | 29 | 0 | RAW_UNADJUSTED | ADJUSTED_COLUMN_PRESENT_BUT_NOT_USED | UNKNOWN_UNPERFORMED | BLOCKED |

*(Truncated; full table in `COBA_013_CORPORATE_ACTION_AUDIT.csv`)*  
*Finding:* Because external market data files lack split and dividend adjustment history, `CORPORATE_ACTION_SENSITIVITY = BLOCKED`. Long-horizon returns (H20) remain potentially sensitive to unadjusted distributions.

## 13. Benchmark Integrity & 14. Peer Group Integrity
### Benchmark Alignment Ledger
| Benchmark_Name | Source | Trading_Sessions | Start_Date | End_Date | Calendar_Alignment_With_Equities | Missing_Dates | Hash_SHA256 | Benchmark_Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IHSG (^JKSE) | data/raw/market_external/IHSG_yf_raw.csv | 2826 | 2015-01-02 | 2026-09-15 | 100% (Acts as master trading session calendar) | 0 | cabd5b7cc11a9bb903098798591e7e290ab39ae5b62cc0b843b2b5398d5ee234 | VERIFIED |
| Canonical Sector Peer (12-Ticker Universe) | core/research_methodology_lock.py (EXPOSURE_GROUPS) | 2826 | 2015-01-02 | 2026-09-11 | Leave-one-out calculation within sector groups | 0 | e4e2ab967de4731f55821b1db0791b53a27cff4c5a50bd047c4c7615a375f004 | VERIFIED |

### Peer Support Sufficiency Ledger
| Sector_Or_Group | Total_Setups | Valid_Peer_Setups | Mean_Peer_Count | Min_Peer_Count | Max_Peer_Count | Insufficient_Peer_Setups | Self_Inclusion_Status | Peer_Support_Classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BASIC_MATERIALS_MINING | 204 | 204 | 9.0 | 6 | 11 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| CONSUMER_GOODS | 231 | 231 | 10.0 | 10 | 10 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| ENERGY_COAL_OIL | 212 | 212 | 9.34 | 6 | 11 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| FINANCIALS_BANKING | 226 | 226 | 10.06 | 5 | 11 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| INDUSTRIALS_CAPITAL_GOODS | 239 | 239 | 10.45 | 8 | 11 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| INFRASTRUCTURE_UTILITIES | 206 | 206 | 9.04 | 7 | 11 | 0 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_SUFFICIENT |
| TECHNOLOGY_DIGITAL | 99 | 85 | 5.11 | 1 | 7 | 14 | SELF_INCLUSION_NONE (VERIFIED) | PEER_SUPPORT_PARTIAL |

*Finding:* Broad-market IHSG benchmark acts as master trading calendar (2,826 sessions) with 100% calendar alignment (`VERIFIED`). Sector peer mean strictly excludes the target symbol (`SELF_INCLUSION_NONE = VERIFIED`), ensuring algebraically unbiased peer excess returns.

## 15. Coverage Ledger & 16. Missingness Decomposition
### Coverage Ledger
| Metric | Canonical_N | Populated_N | Coverage_Pct | Missing_N | Audit_Status |
| --- | --- | --- | --- | --- | --- |
| Canonical Population Universe | 1760 | 1760 | 100.0 | 0 | VERIFIED |
| Equities Populated | 80 | 79 | 98.75 | 1 | PARTIAL (WSKT missing) |
| Market Data Available Setups | 1760 | 1429 | 81.19 | 331 | PARTIAL |
| Primary Complete Cases (H5 Peer Excess) | 1760 | 1417 | 80.51 | 343 | PARTIAL |
| H1 Return Complete Cases | 1760 | 1417 | 80.51 | 343 | PARTIAL |
| H3 Return Complete Cases | 1760 | 1417 | 80.51 | 343 | PARTIAL |
| H10 Return Complete Cases | 1760 | 1417 | 80.51 | 343 | PARTIAL |
| H20 Return Complete Cases | 1760 | 1338 | 76.02 | 422 | PARTIAL (Right-censoring at H20) |
| MAE / MFE Excursion Setups | 1760 | 1429 | 81.19 | 331 | PARTIAL |
| Agent 1 Signal States | 1760 | 1760 | 100.0 | 0 | VERIFIED |
| Agent 2 Intelligence States | 1760 | 1760 | 100.0 | 0 | VERIFIED |
| Agent 3 Decision States | 1760 | 1760 | 100.0 | 0 | VERIFIED |

### Missingness Decomposition (343 Missing Setups)
| Missingness_Reason | Category | Setup_Count | Pct_Of_Missing | Mechanism_Classification | Impact_Assessment |
| --- | --- | --- | --- | --- | --- |
| Pre-IPO Historical Horizon (Company Not Yet Listed on IDX) | LISTING_CHRONOLOGY | 309 | 90.09 | SECTOR_ASSOCIATED_MISSINGNESS | Cannot observe market returns before company listing date |
| Trading Suspension / Delisting (WSKT) | REGULATORY_SUSPENSION | 22 | 6.41 | MNAR_REGULATORY | Ticker halted/delisted on IDX; external provider returned zero rows |
| Public Holiday / Forward Session Gap (2017-05-18) | SESSION_ALIGNMENT | 12 | 3.5 | MAR_CALENDAR | Market data file present but forward 5 sessions cross historical holiday gap |
| Total Missingness (1760 Canonical - 1417 Usable H5) | TOTAL_POPULATION_ATTRITION | 343 | 100.0 | UNKNOWN_NON_MCAR | Overall sample attrition is 19.49%; cannot assume missing completely at random (MCAR) |

*Finding:* Out of 1,760 canonical setups, 1,417 (80.51%) are complete cases on primary H5 peer excess. Missingness is driven by pre-IPO listing chronology (309 setups), regulatory trading suspension (22 setups for WSKT), and a historical holiday gap (12 setups on 2017-05-18). Missingness is non-random (`SECTOR_ASSOCIATED_MISSINGNESS` / `UNKNOWN_NON_MCAR`); MCAR is refuted.

## 17. Selection Bias Sensitivity & 18. Representativeness Assessment
Comparing covered ($N=1,417$) versus uncovered ($N=343$) setups:

| Dimension | Covered_Sample_N | Covered_Pct | Uncovered_Sample_N | Uncovered_Pct | SMD | Selection_Sensitivity |
| --- | --- | --- | --- | --- | --- | --- |
| Sector: BASIC_MATERIALS_MINING | 204 | 14.4 | 60 | 17.49 | -0.0846 | BALANCED |
| Sector: CONSUMER_GOODS | 231 | 16.3 | 11 | 3.21 | 0.4525 | MODERATE_SECTOR_IMBALANCE |
| Sector: ENERGY_COAL_OIL | 212 | 14.96 | 52 | 15.16 | -0.0056 | BALANCED |
| Sector: FINANCIALS_BANKING | 226 | 15.95 | 38 | 11.08 | 0.1428 | BALANCED |
| Sector: INDUSTRIALS_CAPITAL_GOODS | 239 | 16.87 | 47 | 13.7 | 0.088 | BALANCED |
| Sector: INFRASTRUCTURE_UTILITIES | 206 | 14.54 | 58 | 16.91 | -0.0652 | BALANCED |
| Sector: TECHNOLOGY_DIGITAL | 99 | 6.99 | 77 | 22.45 | -0.4472 | MODERATE_SECTOR_IMBALANCE |
| Era: 2016-2019 | 481 | 33.94 | 159 | 46.36 | -0.2552 | BALANCED |
| Era: 2020-2022 | 397 | 28.02 | 83 | 24.2 | 0.087 | BALANCED |
| Era: 2023-2024 | 302 | 21.31 | 18 | 5.25 | 0.4872 | SUBSTANTIAL_ERA_IMBALANCE |
| Era: 2025-2026 | 237 | 16.73 | 83 | 24.2 | -0.186 | BALANCED |

*Finding:* The covered sample exhibits moderate sector imbalance and substantial era imbalance (newer technology and renewable energy IPOs are absent in 2016–2021). Consequently, prior empirical findings generalize strictly to mature, established equities rather than early-stage newly listed IPOs.

## 19. Right-Censoring Audit
| Horizon | Total_Setups | Complete_Setups | Censored_Setups | Censoring_Pct | Censored_Date | Proportionality_Status |
| --- | --- | --- | --- | --- | --- | --- |
| H1 | 1417 | 1417 | 0 | 0.0 | NONE | ZERO_CENSORING |
| H3 | 1417 | 1417 | 0 | 0.0 | NONE | ZERO_CENSORING |
| H5 | 1417 | 1417 | 0 | 0.0 | NONE | ZERO_CENSORING |
| H10 | 1417 | 1417 | 0 | 0.0 | NONE | ZERO_CENSORING |
| H20 | 1417 | 1338 | 79 | 5.58 | 2026-08-27 | PROPORTIONAL_ACROSS_STATES_CONFIRMED |

*Finding:* Right-censoring is strictly zero for H1, H3, H5, and H10. At H20, exactly 79 setups are censored on the terminal observation date (2026-08-27). Censoring is proportional across Agent 3 states (48.1% ACT, matching the population proportion), introducing zero differential selection bias.

## 20. Execution Data Foundation, 21. Liquidity Distribution & 22. Tradability
### Liquidity & Turnover Distribution
| Metric | Observation_Sample | Mean_Value | Median_Value | P10_Value | P90_Value | Illiquid_Count | Tradability_Flag |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Daily Trading Volume (Shares) | 1417 | 61,796,273 | 14,214,600 | 360,180 | 107,513,900 | 103 | HIGH_LIQUIDITY_DISPERSION |
| Daily Trading Turnover (IDR) | 1417 | 70,509,270,690 | 20,944,694,900 | 165,158,940 | 166,102,781,800 | 225 | SUBSTANTIAL_TURNOVER_TAIL |
| Zero Volume Days on Observation Bar | 1417 | 0.0247 | 0.0 | 0.0 | 0.0 | 35 | UNTRADABLE_ON_DATE_BAR |
| Severe Illiquidity (<100K shares / <1B IDR) | 1417 | 0.1588 | 0.0 | 0.0 | 1.0 | 225 | EXECUTION_LIMITED |

### Execution Friction Audit
| Execution_Component | Data_Availability | Empirical_Source | Default_Assumption | Status |
| --- | --- | --- | --- | --- |
| Bid / Ask Quotes & Spread | UNAVAILABLE | None in repository | Zero friction assumed in raw returns | EXECUTION_FRICTION_BLOCKED |
| IDX Auto-Rejection Price Limits (ARA/ARB) | RULE_BASED_ONLY | IDX regulatory asymmetric bands (20%-35%) | Unbounded fill assumed | STATIC_RULES_ONLY |
| Mandatory Lot Sizing | RULE_BASED_ONLY | IDX 100 shares per lot standard | Continuous sizing assumed in theoretical models | STATIC_RULES_ONLY |
| Brokerage Commissions & Taxes | RULE_BASED_ONLY | 0.1% sales tax, 0.043% IDX levy, 0.15%-0.25% broker fee | Zero friction assumed in raw returns | STATIC_RULES_ONLY |
| Market Impact & Order Book Depth | UNAVAILABLE | Intraday L2/L3 order book unavailable | Infinite depth assumed | BLOCKED |
| Pre-Close & Pre-Open Auction Matching | UNAVAILABLE | Auction prints not separated from continuous session | Continuous close fill assumed | BLOCKED |

*Finding:* Median daily turnover is 20.9B IDR, but 35 setups had zero trading volume on the observation date, and 225 setups (15.88%) had turnover < 1B IDR. Furthermore, intraday bid/ask quotes, order book depth, market impact, and auction prints are completely unavailable (`EXECUTION_FRICTION_MODEL = BLOCKED`). All raw returns assume frictionless execution at closing prices.

## 23. Portfolio Accounting Foundation & 24. Portfolio Inference Boundary
| Portfolio_Component | Repository_Availability | Frozen_Specification | Implementation_Status | Readiness_Classification |
| --- | --- | --- | --- | --- |
| Dynamic Cash Balance Accounting | UNAVAILABLE | No cash ledger frozen in repository | ABSENT | BLOCKED |
| Historical Position Chronology Ledger | UNAVAILABLE | Setups evaluated as isolated cross-sectional rows | ABSENT | BLOCKED |
| Capital Allocation & Sizing Policy | STATIC_TIERS_ONLY | Arm D specifies size tier 1-3 without cash basis | STATIC_SCHEMA_ONLY | PARTIAL |
| Overlapping Position Governance | UNAVAILABLE | No concurrent risk-budget rules | ABSENT | NOT_PRE_SPECIFIED |
| Rebalancing, Margining & Cash Drag | UNAVAILABLE | No portfolio simulation engine | ABSENT | BLOCKED |
| Portfolio-Level Drawdown Reconstruction | UNAVAILABLE | No equity curve reconstruction engine | ABSENT | BLOCKED |
| Portfolio-Level Risk Inference | UNAVAILABLE | Equating setup returns to portfolio CAGR/Sharpe is blocked | PROHIBITED_BY_FIREWALL | BLOCKED |

*Boundary Enforcement:* `PORTFOLIO_LEDGER = BLOCKED`, `CASH_ALLOCATION = NOT_PRE_SPECIFIED`, and `PORTFOLIO_LEVEL_INFERENCE = BLOCKED`. No dynamic portfolio simulation engine exists in the repository. Cross-sectional setup returns cannot be equated to dynamic portfolio performance, Sharpe ratio, or drawdown.

## 25. Red Team Adversarial Audit
| Challenge_ID | Adversarial_Question | Evidence_Audited | Finding | Verdict |
| --- | --- | --- | --- | --- |
| RT-01_LOOKAHEAD | Does any setup outcome evaluation leak future bar information into signal generation? | Signal timestamp 08:30 T vs Market Open 09:00 T; outcome window strictly t+1 to t+h | Forward returns and excursions start at session t+1. Zero contemporaneous bar leakage. | LOOKAHEAD_ABSENT_VERIFIED |
| RT-02_SURVIVORSHIP | Does the 80-equity population suffer from survivorship bias? | Canonical population includes historical listing and delisting/suspended equities (e.g. WSKT) | Canonical list reflects historical constituent snapshots. Missingness for WSKT is documented, not omitted. | SURVIVORSHIP_CONTROLLED_AND_FLAGGED |
| RT-03_CORP_ACTION_DISTORTION | Do stock splits or extraordinary dividends distort empirical return calculations? | Audit of raw vs adjusted series in data/raw/market and market_external | External market data is unadjusted; splits and dividends introduce unperformed sensitivity at long horizons. | CORPORATE_ACTION_SENSITIVITY_BLOCKED |
| RT-04_SELECTION_BIAS | Does the covered sample (N=1,417) differ systematically from the canonical universe (N=1,760)? | Cross-tabulation of missingness across sectors, listing eras, and regimes | Newer tech and energy IPOs are absent in earlier historical eras (2016-2021). Selection is non-random. | SELECTION_BIAS_CONFIRMED_NON_RANDOM |
| RT-05_MISSINGNESS_MECHANISM | Can missing setups be classified as Missing Completely at Random (MCAR)? | Missingness decomposition: 309 IPO timing, 22 suspension, 12 calendar gap | Missingness is strongly associated with listing date and regulatory status. MCAR is refuted. | MCAR_REFUTED_UNKNOWN_NON_MCAR |
| RT-06_RIGHT_CENSORING | Does right censoring at H20 introduce asymmetric treatment/control bias? | Analysis of 79 censored setups on 2026-08-27 across Agent 1, 2, 3 states | Censoring occurs strictly on terminal date and is proportional across Agent 3 states (ACT=48.1%, matches population). | PROPORTIONAL_CENSORING_VERIFIED |
| RT-07_BENCHMARK_CONTAMINATION | Is the broad-market IHSG benchmark contaminated by lookahead or holiday misalignment? | Session-by-session calendar join between equity Close and IHSG Close | IHSG acts as the master trading calendar across 2,826 sessions with 100% calendar concordance. | BENCHMARK_ALIGNMENT_VERIFIED |
| RT-08_PEER_SELF_INCLUSION | Does the sector peer excess calculation accidentally include the target ticker? | Formula inspection of LOO peer calculation in canonical scripts | Target symbol is strictly excluded from its own exposure group mean. Algebraic LOO equivalence confirmed. | SELF_INCLUSION_NONE_VERIFIED |
| RT-09_SYNTHETIC_OUTCOME_LEAKAGE | Do synthetic fixtures from zzz148 (-1.50 MAE, 0.80 MFE) contaminate outcomes? | Inspection of all MAE/MFE series across COBA_011, COBA_012, and COBA_013 | All excursion metrics derived 100% from empirical daily High/Low price paths. Contamination absent. | SYNTHETIC_CONTAMINATION_ABSENT |
| RT-10_A2_HINDSIGHT | Does Agent 2 qualitative intelligence use post-event information to tag contradiction? | DuckDB event ingestion timestamps and pre-market 08:30 T freeze audit | Agent 2 state is frozen pre-market; however external historical news provider provenance lacks certified snapshots. | PARTIAL_PIT_PROVENANCE_CONFIRMED |
| RT-11_A3_POST_OUTCOME | Does Agent 3 decision logic evaluate forward returns or stop-loss events? | Logic audit of Arm D decision generation in zzz148 decision matrix | Arm D decisions are generated solely from Arm A (quant) and Arm B/C (intelligence). Zero outcome leakage. | DECISION_BLINDNESS_VERIFIED |
| RT-12_EXECUTION_FANTASY | Does the research assume instantaneous, friction-free execution at mid-market prices? | Audit of bid/ask spread, market impact, and fee modeling in repository | No intraday bid/ask spreads or execution engines exist. Raw Close prices assume zero friction. | EXECUTION_FANTASY_ACKNOWLEDGED_BLOCKED |
| RT-13_PORTFOLIO_LEAKAGE | Can setup-level regression statistics be cited as portfolio Sharpe or CAGR? | Firewall enforcement against portfolio performance extrapolations | Cross-sectional setup statistics cannot be equated to dynamic portfolio drawdown without cash ledger. | PORTFOLIO_INFERENCE_STRICTLY_BLOCKED |
| RT-14_POST_HOC_TUNING | Were any agent parameters, thresholds, or estimands tuned in COBA_013? | Comparison of Agent 1, 2, 3 logic against frozen definitions | Zero parameters tuned. Zero thresholds modified. Exactly 3 frozen agents evaluated. | ZERO_TUNING_VERIFIED |
| RT-15_HIDDEN_AGENT4 | Has a 4th runtime agent or external meta-agent been introduced into the architecture? | Codebase inspection of agents/ directory and runtime imports | Exactly 3 agents exist (Agent 1, Agent 2, Agent 3). ZERO Agent 4. | AGENT_BOUNDARY_PRESERVED |

*Red Team Verdict:* 100% of 15 adversarial challenges audited with rigorous empirical findings and explicit firewall classifications.

## 26. Synthetic Contamination Audit
Hardcoded synthetic decision-utility fixtures from zzz148 (-1.50 MAE, 0.80 MFE) were fully audited. All forward returns, MAE, and MFE derive 100% from empirical daily OHLCV price paths across windows $t+1 \to t+h$. `SYNTHETIC_OUTCOME_CONTAMINATION = ABSENT` (PASS).

## 27. Scientific Reproducibility & 28. Independent Recalculation
| Verification_Type | Target_Dataset | Items_Checked | Matches | Mismatches | Match_Rate_Pct | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Independent Recheck | 150 setups across 20 tickers, 11 years, 4 regimes recomputed from raw market data | 150 | 150 | 0 | 100.0 | PASS |
| Clean-Room Dual Run | 17 generated CSV artifacts in COBA_013 battery | 17 | 17 | 0 | 100.0 | PASS |
| Cryptographic Hash Manifest | All input raw market files, observation matrices, and report outputs | 89 | 89 | 0 | 100.0 | PASS |

*Finding:* Clean-room dual-run reproducibility verified 100% identical SHA-256 hashes across all 17 generated CSV artifacts. Independent recheck of 150 setups across 20 tickers, 11 years, and 4 regimes yielded 100% match (< 1e-7 diff).

## 29. Prior COBA Impact Matrix
| Prior_COBA | Frozen_Finding | Foundation_Dependency | Impact_Classification | Detailed_Assessment |
| --- | --- | --- | --- | --- |
| COBA_008 | SIGNAL_NOT_SUPPORTED (Pure Agent 1 directional beta = -0.0279 pp, p_wild = 0.9370) | Market data coverage (1,417 setups), LOO peer excess benchmark | LIMITED_IMPACT | Directional neutrality is an empirical finding robust to sample size. Data gaps do not reverse null. |
| COBA_009 | NO_CONDITIONAL_EVIDENCE (Context interactions evaporated under common support) | Common support distribution across momentum and volatility strata | LIMITED_IMPACT | Structural dependence on momentum score >= 80 remains mechanically true. Common support limitation confirmed. |
| COBA_010 | NO_INCREMENTAL_INFORMATION_EVIDENCE (Agent 2 contradiction beta = +0.5018 pp, p_wild = 0.2690) | Historical news disclosure archiving in DuckDB, event timestamps | LIMITED_IMPACT | Partial PIT provenance of external news does not invalidate empirical neutrality of recorded contradiction flags. |
| COBA_011 | STRUCTURAL_ROBUSTNESS_SUPPORTED (Empirical neutrality robust across H1-H20 and Raw/Peer/IHSG) | Multi-horizon sequential sessions and benchmark definitions | LIMITED_IMPACT | Invariance of neutrality across estimands is robust. Corporate action sensitivity remains unperformed. |
| COBA_012 | NO_RISK_FILTER_EVIDENCE (Agent 3 ACT vs REJECT downside beta = +0.2117 pp, p_wild = 0.9640) | Intra-horizon MAE/MFE, loss severity, discrete state contrasts | LIMITED_IMPACT | Downside neutrality and absence of loss filtering confirmed. Portfolio-level risk remains blocked. |

*Finding:* Prior COBA findings (COBA_008 to COBA_012) remain frozen with `LIMITED_IMPACT`. Data foundation limitations do not constitute implementation defects that reverse prior empirical neutrality conclusions.

## 30. Master Readiness Matrix & 31–33. Check Statuses
| Domain | Status | Evidence | Limitation | Consequence |
| --- | --- | --- | --- | --- |
| Historical Market Data | PARTIAL | 79/80 equities populated, 1,429 setups covered, zero fatal errors in 2016-2026 | WSKT missing; 3 historical 2007 High<Low inversions flagged | Usable setup coverage is 81.19% of canonical universe |
| Point-in-Time (PIT) Alignment | PARTIAL | 08:30 T pre-market freeze verified; outcome window t+1 to t+h verified | External raw news and price providers lack certified immutable historical snapshot audit trails | OUTCOME_TEMPORAL_ALIGNMENT = VERIFIED, but FULL_HISTORICAL_PIT = PARTIAL |
| Corporate Actions | BLOCKED | Split and dividend counts identified for pilot tickers; raw series documented | External market data is unadjusted; corporate action adjustments unperformed | CORPORATE_ACTION_SENSITIVITY = BLOCKED; long-horizon returns potentially sensitive |
| Benchmark Integrity | VERIFIED | IHSG master calendar (2,826 sessions) 100% aligned with equity trading sessions | None detected | Broad-market benchmark is sound and reproducible |
| Peer Group Integrity | VERIFIED | Canonical LOO sector peer mean strictly excludes target symbol (SELF_INCLUSION_NONE) | Small peer counts (<2) in 12 setups | Peer excess is algebraically sound and unbiased |
| Sample Selection & Missingness | PARTIAL | Decomposition of 343 missing setups into IPO timing, suspension, and calendar gaps | Missingness is non-random (SECTOR_ASSOCIATED_MISSINGNESS; newer IPOs absent in early eras) | Prior findings apply strictly to populated equity-date sample, not universal 80 universe |
| Right Censoring | VERIFIED | 79 setups censored strictly at H20 on terminal date 2026-08-27 | H20 sample reduced to 1,338 setups | Censoring is proportional across states; selection bias absent |
| Agent 1 Implementation | VERIFIED | Frozen quant scanner rules and signal taxonomy strictly preserved without tuning | Directional alpha absent across all horizons | Pure Agent 1 signal provides no standalone directional alpha |
| Agent 2 Implementation | VERIFIED | Historical intelligence, contradiction tags, and archival depth preserved without tuning | Incremental information value absent | Agent 2 provides no statistically reliable incremental directional lift |
| Agent 3 Implementation | VERIFIED | Investment committee decision block (Arm D) preserved without tuning | Downside risk filter evidence absent | Agent 3 provides no statistically reliable downside loss prevention |
| Execution & Friction Modeling | BLOCKED | IDX statutory tax (0.1%), levy (0.043%), lot sizing (100 shares) documented | Intraday bid/ask quotes, order book depth, spread, slippage, and auction prints absent | EXECUTION_FRICTION_MODEL = BLOCKED; execution feasibility unverified |
| Tradability & Liquidity | PARTIAL | Volume and turnover distribution audited across 1,417 setups | 35 zero-volume setups; 225 setups (15.88%) have daily turnover < 1B IDR | Material execution drag would occur for institutional portfolio sizing |
| Portfolio Accounting Foundation | BLOCKED | Static position sizing schema exists in Arm D | No cash accounting ledger, dynamic capital allocation, or historical position chronology | PORTFOLIO_LEDGER = BLOCKED; dynamic drawdown reconstruction is blocked |
| Scientific Reproducibility | VERIFIED | 100% independent recalculation (150/150 setups) and 100% dual-run CSV hash match | None detected | All empirical calculations are deterministic and reproducible |
| Governance & Firewalls | VERIFIED | Zero Agent 4, exact 3-agent boundary, lineage AU->COBA_013 strictly preserved | None detected | Research integrity and firewall boundaries strictly intact |

- **Failed Checks:** None (all empirical foundation audits executed cleanly).
- **Partial Checks:** Historical Market Data, Point-in-Time Provenance, Sample Coverage, Missingness, Selection Bias, Liquidity.
- **Blocked Checks:** Corporate Action Sensitivity, Execution Friction Modeling, Portfolio Accounting Foundation, Dynamic Drawdown Reconstruction, Portfolio-Level Inference, Strategy Optimization.

## 34. Scientific Interpretation & 35. What This Does NOT Prove
### Scientific Interpretation
COBA_013 demonstrates that SwingDeck's setup-level observational and statistical foundation is internally consistent, deterministic, and free of fatal bugs for the populated sample of 79 mature equities. However, the scientific foundation is NOT ready for portfolio-level evaluation.

Critical unresolved blockers prevent valid portfolio-level testing: (1) corporate action adjustments are unperformed on raw price series; (2) intraday bid/ask spreads and market impact data are absent; and (3) no executable cash accounting ledger, historical position chronology, or capital allocation engine exists in the repository.

### What This Does NOT Prove
This classification does NOT prove:
- that trading is impossible;
- that a future portfolio edge cannot exist;
- that Agent 1, 2, or 3 signals are random;
- that the entire research pipeline failed.

It strictly proves that portfolio-level empirical claims cannot be made scientifically without the missing foundation layers.

## 36. Final Foundation Classification
### `FOUNDATION_BLOCKED`
> The scientific foundation is partially complete at the setup level but BLOCKED for portfolio-level empirical evaluation due to unresolved critical dependencies in dynamic cash accounting, position chronology, corporate action adjustments, and execution friction modeling.

## 37. Scientific Firewall Status
- `CAUSALITY`: `NOT_PROVEN`
- `STANDALONE_ALPHA`: `NOT_PROVEN`
- `STRATEGY_OPTIMIZATION`: `BLOCKED`
- `STRATEGY_READINESS`: `NOT_READY`

## 38. Exact Next Research Question
> *"How can a deterministic, execution-aware historical portfolio accounting ledger (incorporating explicit cash allocation, real-world lot constraints, brokerage transaction fees, and corporate action adjustments) be constructed and validated for the canonical equity universe, so that portfolio-level holding period dynamics can be evaluated without relying on frictionless setup-level return assumptions?"*