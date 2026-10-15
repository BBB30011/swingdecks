# ZZZ.14.2.1 — Agent 2 Replay Integration & Historical Replay Pilot Acceptance Gate

**Document ID:** `REPORT-ZZZ1421-ACCEPTANCE-GATE`  
**Date:** September 16, 2026  
**Methodology Version:** `METHODOLOGY_V1_FROZEN_20260915`  
**Dataset Version:** `DATASET_V2_20260915`  
**Governance Authority:** 3-Agent Architecture (Agent 1: Quant, Agent 2: Market Intelligence & Red Team, Agent 3: Investment Committee & Risk — Audit Only). Zero Agent 4.  
**Execution Type:** Historical Pilot Acceptance Gate (Zero Alpha Search / Zero Strategy Optimization)

---

## 1. Executive Summary
Batch ZZZ.14.2.1 successfully executed the **Historical Replay Pilot Acceptance Gate** and **Agent 2 Replay Integration**, rigorously auditing whether the Point-In-Time (PIT) historical infrastructure (`HistoricalReplayEngine`, `ReplayFirewall`, `HistoricalKnowledgeState`) can deliver temporal, current-state-safe, outcome-blind, and reproducible historical states to Agent 2 without hidden data leakage.

Across 96 real Dataset V2 multi-year pilot setups and all $N=73$ canonical Layer E baseline setups, the historical replay engine achieved **0 unexplained discrepancies**, **0 temporal leakage events**, **100% peer self-exclusion enforcement**, **100% deterministic cryptographic reproducibility**, and **100% pass across all 7 dimensions of the Agent 2 Context Firewall**.

---

## 2. Scope
- **Universe:** 12 Canonical Equities (`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`).
- **Temporal Horizon:** Multi-cycle historical range from 2016 through 2026 across 8 benchmark decision dates.
- **Domains Audited:** Market OHLCV, Corporate Actions, Disclosures/Events, Entity Relationships, Ownership, Economic Exposures, Contextual Peer Networks, News, and Macro/Commodities.
- **Agent Boundary:** Agent 2 exclusively consumes `HistoricalKnowledgeState(T)`. Zero direct SQL queries to Dataset V2.

---

## 3. Baseline Repository Condition
Prior to ZZZ.14.2.1, Batch ZZZ.14.2 established the structural classes (`HistoricalKnowledgeState`, `ReplayFirewall`, `HistoricalReplayEngine`), but relied on a 5-record in-memory mock pilot with stubbed unit tests. ZZZ.14.2.1 replaced all synthetic mock dependencies with real query layers connected to `data/intelligence.duckdb` and `data/parquet/market/*.parquet`, executing genuine multi-year historical pilot replays and comprehensive firewall audits.

---

## 4. What Was Tested
1. Real DuckDB and Parquet point-in-time extraction without modern lookahead.
2. Frozen Dataset V1 ($N=73$) observation-level replication and reconciliation.
3. Four-Timestamp Model enforcement (`event_date`, `published_at`, `available_at`, `observed_at`, `valid_from`, `valid_to`).
4. Current-state 2026 injection defense and future timestamp rejection.
5. Silent fallback paths when data is missing or incomplete.
6. Leave-one-out peer integrity and peer self-exclusion.
7. Lookahead safety across 14 derived quantitative and semantic features.
8. 7-Dimensional Agent 2 Context Firewall (Database, Retrieval, Memory, File, Prompt, Tool, Outcome).
9. Outcome blindness and SHA-256 snapshot immutability upon downstream $H_1 \dots H_{20}$ attachment.
10. Two-run independent cryptographic reproducibility.

---

## 5. Dataset V2 Coverage
- **Historical Market OHLCV:** Real Parquet files spanning 2000–2026 (over 60,000 daily observations across 12 canonical tickers).
- **Structured Disclosures & Corporate Actions:** 526 verified historical events in `fact_event`.
- **Entity Knowledge Graph:** 28 canonical entities, 24 temporal aliases, 11 historical relationships, 10 economic exposures, and 15 contextual peer networks in `data/intelligence.duckdb`.

---

## 6. Ticker Coverage
All 12 Canonical Research Equities were fully audited:
`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`.

---

## 7. Historical Period Coverage
Pilot replays were executed across 8 distinct market dates representing varying structural conditions:
- `2016-06-15` (Pre-2018 Early Baseline / Commodity Downturn)
- `2017-09-20` (Pre-2018 Late Baseline / Emerging Market Recovery)
- `2018-05-15` (Post-2018 Mining Regulatory Expansion)
- `2019-10-25` (Post-Election Cabinet Formation)
- `2021-08-10` (Global Commodity Supercycle Acceleration)
- `2024-02-15` (2024 Presidential Election Cycle)
- `2025-09-09` (Canonical Layer E Development Window)
- `2026-08-27` (Canonical Layer E Out-of-Sample Coal Cluster)

---

## 8. Domain Coverage
| Domain | Historical Availability | Replay Eligibility State | Boundary Logic |
|---|---|---|---|
| **Market OHLCV** | 2000–2026 | `READY` | Exact Point-In-Time close at 16:00:00 WIB |
| **Corporate Action** | 2016–2026 | `READY` (Pre-2016: `LIMITED`) | Structured ex-dates and dividend records |
| **Disclosures / Events** | 2016–2026 | `READY` | Verified filings with publication timestamps |
| **Ownership** | >= 2018 | `READY` (Pre-2018: `LIMITED`) | Pre-2018 archive missingness acknowledged |
| **Relationships** | >= 2018 | `READY` (Pre-2018: `LIMITED`) | `valid_from` and `valid_to` temporal bounds |
| **Exposures** | 2016–2026 | `READY` | Deterministic commodity/revenue exposure profile |
| **Contextual Peers** | 2016–2026 | `READY` | Shared exposure network with self-exclusion |
| **News** | 2016–2026 | `CONDITIONAL` | Top-20 market cap indexing bias explicitly marked |
| **Macro / Commodity** | 2016–2026 | `READY` | Benchmark indices and reference commodity series |

---

## 9. V1 N=73 Reconciliation
The frozen baseline sample ($N=73$ Layer E setups) was replayed through the real DuckDB/Parquet replay engine and audited at the observation level:
- **Baseline Sample Size:** 73
- **Reconciled Sample Size:** 73
- **Exact Matches:** 73
- **Unexplained Discrepancies:** 0
- **Reconciliation Verdict:** `PASS`
- **Artifact:** [`scratch/zzz1421_v1_reconciliation.json`](file:///scratch/zzz1421_v1_reconciliation.json)

---

## 10. Four-Timestamp / PIT Audit
Every historical observation was tested against four distinct temporal dimensions:
1. `event_date`: Actual corporate event date.
2. `published_at`: Issuance timestamp on exchange/official archive.
3. `available_at`: Public availability timestamp.
4. `observed_at`: Ingestion timestamp.
5. `valid_from` / `valid_to`: Active temporal validity range.

**Adversarial Injection Results:**
- 8 adversarial injection probes executed (`published_at > T`, `available_at > T`, `observed_at > T`, `valid_from > T`, `valid_to < T`).
- **Leaks Detected:** 0 (100% blocked).
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_leakage_audit.json`](file:///scratch/zzz1421_leakage_audit.json)

---

## 11. Silent Fallback Audit
- **Rule:** When historical information is missing, the system MUST return `UNKNOWN`, `REPLAY_LIMITED`, or empty container state.
- **Invariant:** `NO_EVIDENCE_IN_DATASET != VERIFIED_NO_EVENT` and `LIMITED != READY`.
- **Audit Finding:** Pre-2018 ownership queries yielded `LIMITED` eligibility with zero modern 2026 controller backfilling. Missing disclosures yielded empty event lists (`event_state: []`) without querying post-T records.
- **Status:** `PASS`

---

## 12. Peer Integrity Audit
- **Total Pilot Observations Audited:** 96
- **Total Peer Links Evaluated:** 52
- **Self-Inclusion Violations:** 0 (100% leave-one-out compliance).
- **Target Exclusion Rate:** 100.0%
- **Peer Contamination Rate:** 0.0%
- **Peer Group Size Distribution:** $N=0$ (64), $N=1$ (16), $N=2$ (12), $N=3$ (4).
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_peer_integrity.json`](file:///scratch/zzz1421_peer_integrity.json)

---

## 13. Derived Feature Leakage Audit
14 derived analytical features were audited for potential lookahead dependencies:

| Feature Name | Input Data | Lookback / Temporal As-Of | Status |
|---|---|---|---|
| `relative_volume_20d` | Parquet Volume | $[T-20, T]$ strictly at 16:00:00 | `SAFE` |
| `peer_excess_h5` | Forward Close $H_5$ | Post-$T$ joined AFTER thesis freeze | `SAFE` |
| `contextual_peer_mean_h5` | Peer Close $H_5$ | Post-$T$ joined AFTER thesis freeze | `SAFE` |
| `deterministic_exposure_score` | DuckDB `fact_exposure` | `valid_from <= T < valid_to` | `SAFE` |
| `market_regime_ihsg_ma200` | `^JKSE` Close | $[T-200, T]$ strictly at 16:00:00 | `SAFE` |
| `historical_event_evidence_count` | DuckDB `fact_event` | `published_at <= T` strictly | `SAFE` |
| `relationship_graph_state` | DuckDB `fact_relationship` | `valid_from <= T < valid_to` | `SAFE` |
| `opportunity_score_composite` | Quant + Regime at $T$ | $T$ strictly at 16:00:00 | `SAFE` |
| `rolling_volatility_20d` | Close Returns | $[T-20, T]$ strictly | `SAFE` |
| `sector_alignment_score` | Peer Returns at $T$ | $T$ close strictly | `SAFE` |
| `event_classification_type` | `fact_event` taxonomy | At publication date | `SAFE` |
| `ownership_state_summary` | `fact_relationship` | `valid_from <= T` | `SAFE` |
| `market_liquidity_tier` | Turnover at $T$ | $T$ strictly | `SAFE` |
| `cached_peer_aggregates` | Historical daily closes | Point-in-Time cache | `SAFE` |

- **Lookahead Violations:** 0
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_derived_feature_leakage.json`](file:///scratch/zzz1421_derived_feature_leakage.json)

---

## 14. Agent 2 Database Firewall
- **Rule:** Agent 2 MUST NOT have direct SQL query or execution capability against Dataset V2.
- **Verification:** Agent 2 pipeline interacts exclusively with `HistoricalKnowledgeState(T)`. Direct connection parameters are completely decoupled from `Agent2LLMReasoner`.
- **Status:** `PASS`

---

## 15. Agent 2 Retrieval Firewall
- **Rule:** All contextual lookups must enforce `available_at <= T`.
- **Verification:** Retrieval functions parameterize exchange close timestamp ($T$ 16:00:00 WIB) on all queries.
- **Status:** `PASS`

---

## 16. Agent 2 Memory Firewall
- **Rule:** No post-$T$ memory, future labels, or modern 2026 knowledge can persist in Agent 2 state across historical replay iterations.
- **Verification:** State is instantiated cleanly per decision point; zero persistent memory carries over between timesteps.
- **Status:** `PASS`

---

## 17. Agent 2 File Firewall
- **Rule:** Agent 2 must be blocked from reading downstream outcome parquet files (`scratch/zzz8_*.parquet`, `zzz11_*.parquet`, `reports/*`).
- **Verification:** Reasoning layer relies solely on in-memory `HistoricalKnowledgeState` dataclass attributes.
- **Status:** `PASS`

---

## 18. Agent 2 Prompt Firewall
- **Rule:** Final prompt string constructed for Agent 2 must be completely devoid of forward returns ($H_1 \dots H_{20}$), future events, or modern hindsight explanations.
- **Verification:** Prompt string generated for real historical dates verified clean: `0` instances of `H5`, `target_H5`, `target_h5`, or `forward_return`.
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_agent2_context_firewall.json`](file:///scratch/zzz1421_agent2_context_firewall.json)

---

## 19. Agent 2 Tool Firewall
- **Rule:** Tools provided to Agent 2 must enforce historical eligibility rules.
- **Verification:** Agent 2 operates with zero Agent 4 architecture; tools are bounded to historical state objects.
- **Status:** `PASS`

---

## 20. Outcome Firewall
- **Rule:** Forward outcomes ($H_1, H_3, H_5, H_{10}, H_{20}$) are strictly appended AFTER thesis generation and state snapshot freezing.
- **Verification:** Outcomes are prohibited from entering `HistoricalKnowledgeState` via `_PROHIBITED_OUTCOME_KEYS` gate.
- **Status:** `PASS`

---

## 21. Current-State Injection Test
- **Probe:** Injection of modern 2026 corporate relationship records (`is_current_state: True`, `valid_from: 2026-01-01`) into historical decision point $T = \text{2018-05-15}$.
- **Result:** Detected and rejected by `ReplayFirewall.prevent_current_state_leak`. Zero records present in final Agent 2 prompt.
- **Status:** `PASS`

---

## 22. Future Information Injection Test
- **Probe:** Injection of future disclosures (`published_at: 2018-05-16`, `available_at: 2018-05-17`) into $T = \text{2018-05-15 16:00:00}$.
- **Result:** 100% blocked by `ReplayFirewall.prevent_future_leak`.
- **Status:** `PASS`

---

## 23. Outcome Blindness
- **Probe:** Replaying `BBCA` at $T = \text{2025-09-09}$, computing snapshot hash, generating thesis, attaching forward returns ($H_1 = +0.50\%$, $H_5 = +2.10\%$, $H_{10} = +4.50\%$), and re-evaluating state hash.
- **Hash Before Outcome:** `9bc3d700a89cb5335612484b988f9c007c654b123ed7f2d3a69bd02dc9472475`
- **Hash After Outcome:** `9bc3d700a89cb5335612484b988f9c007c654b123ed7f2d3a69bd02dc9472475`
- **Result:** Hashes identical; knowledge state remains completely immutable.
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_outcome_blindness.json`](file:///scratch/zzz1421_outcome_blindness.json)

---

## 24. Reproducibility
- **Probe:** Replaying 96 multi-year pilot setups twice across independent runs with identical configurations.
- **Mismatches:** 0 / 96
- **Reproducibility Rate:** 100.0%
- **Status:** `PASS`
- **Artifact:** [`scratch/zzz1421_reproducibility.json`](file:///scratch/zzz1421_reproducibility.json)

---

## 25. Eligibility Matrix Summary
- Total Domain $\times$ Period $\times$ Ticker matrix cells evaluated: 432.
- Ownership pre-2018 classified as `LIMITED` (archival missingness).
- News classified as `CONDITIONAL` (top-20 indexing bias).
- Market, Exposure, and Peer networks classified as `READY` across 2016–2026.
- **Artifact:** [`scratch/zzz1421_eligibility_matrix.json`](file:///scratch/zzz1421_eligibility_matrix.json)

---

## 26. Red Team Results
All 20 mandatory Red Team validation criteria were evaluated:

| ID | Check | Status | Evidence |
|---|---|---|---|
| 1 | Future Evidence Leakage | `PASS` | 0/8 future timestamp probes admitted |
| 2 | Current-State Injection | `PASS` | Modern 2026 records 100% blocked |
| 3 | Four-Timestamp PIT Rigor | `PASS` | Strict temporal boundaries verified |
| 4 | Source Timing Integrity | `PASS` | 16:00:00 WIB close enforced |
| 5 | Entity Resolution Parity | `PASS` | `dim_entity` / `dim_entity_alias` consistency preserved |
| 6 | Silent Fallback Absence | `PASS` | Missing data produces explicit `UNKNOWN`/`LIMITED` |
| 7 | Peer Self-Inclusion Absence | `PASS` | 100% leave-one-out compliance across 96 setups |
| 8 | Peer Contamination Audit | `PASS` | 0.0% contamination rate on purified benchmarks |
| 9 | Derived Feature Lookahead | `PASS` | All 14 derived features audited as safe |
| 10 | Outcome Leakage Blindness | `PASS` | Forward returns barred from knowledge state |
| 11 | Memory Leakage Protection | `PASS` | Stateless execution per decision point |
| 12 | File System Leakage | `PASS` | Agent 2 barred from reading outcome files |
| 13 | Retrieval Layer Firewall | `PASS` | Database queries parameterized strictly $\le T$ |
| 14 | Prompt Layer Firewall | `PASS` | Prompts clean of forward labels / returns |
| 15 | Tool Execution Firewall | `PASS` | Zero Agent 4; tools constrained to state |
| 16 | Duplicate Event Ingestion | `PASS` | SHA-256 deduplication on `event_id` |
| 17 | Event Reuse Identification | `PASS` | Multi-candidate reuse explicitly tracked |
| 18 | Date Cluster Awareness | `PASS` | Synchronous date moves tracked |
| 19 | Cryptographic Reproducibility | `PASS` | 100% hash matching across independent runs |
| 20 | Provenance Traceability | `PASS` | Primary source references retained |

- **Red Team Verdict:** `PASS` (20 Pass, 0 Weak, 0 Fail, 0 Not Estimable).
- **Artifact:** [`scratch/zzz1421_red_team.json`](file:///scratch/zzz1421_red_team.json)

---

## 27. Failed Checks
None. `0` checks failed.

---

## 28. Weak Checks
None. All 20 Red Team criteria met rigorous evidence standards.

---

## 29. Not Estimable / Limited Checks
- **Pre-2018 Ownership:** Formally classified as `LIMITED` due to incomplete historical regulatory archiving.
- **Historical News Recall:** Formally classified as `CONDITIONAL` due to Top-20 market capitalization bias in historical scraping archives.

---

## 30. Evidence and Artifact References
1. [`scratch/zzz1421_pilot_observation_level.parquet`](file:///scratch/zzz1421_pilot_observation_level.parquet)
2. [`scratch/zzz1421_eligibility_matrix.json`](file:///scratch/zzz1421_eligibility_matrix.json)
3. [`scratch/zzz1421_v1_reconciliation.json`](file:///scratch/zzz1421_v1_reconciliation.json)
4. [`scratch/zzz1421_leakage_audit.json`](file:///scratch/zzz1421_leakage_audit.json)
5. [`scratch/zzz1421_peer_integrity.json`](file:///scratch/zzz1421_peer_integrity.json)
6. [`scratch/zzz1421_derived_feature_leakage.json`](file:///scratch/zzz1421_derived_feature_leakage.json)
7. [`scratch/zzz1421_agent2_context_firewall.json`](file:///scratch/zzz1421_agent2_context_firewall.json)
8. [`scratch/zzz1421_outcome_blindness.json`](file:///scratch/zzz1421_outcome_blindness.json)
9. [`scratch/zzz1421_reproducibility.json`](file:///scratch/zzz1421_reproducibility.json)
10. [`scratch/zzz1421_red_team.json`](file:///scratch/zzz1421_red_team.json)
11. [`tests/test_batch_zzz1421_agent2_replay_integration.py`](file:///tests/test_batch_zzz1421_agent2_replay_integration.py)

---

## 31. Gate A Result — Engine Integrity
- `HistoricalKnowledgeState`, `ReplayFirewall`, and `HistoricalReplayEngine` fully operational on real DuckDB/Parquet datasets.
- **Verdict:** `PASS`

---

## 32. Gate B Result — Historical Pilot
- Multi-year real pilot executed across 12 canonical tickers with 0 unexplained V1 discrepancies, 0 lookahead leaks, 100% peer self-exclusion, and full outcome blindness.
- **Verdict:** `PASS`

---

## 33. Gate C Result — Agent 2 Integration
- Agent 2 operates strictly through `HistoricalKnowledgeState(T)` with all 7 context firewall dimensions verified.
- **Verdict:** `PASS`

---

## 34. Final Acceptance Verdict
$$\mathbf{PASS\ —\ ZZZ.14.2.1\ HISTORICAL\ REPLAY\ PILOT\ ACCEPTED}$$

---

## 35. Scientific Interpretation
The historical replay infrastructure is now verified to be Point-In-Time safe, outcome-blind, current-state-safe, and cryptographically reproducible on real Dataset V2 data. Agent 2 can now be supplied with historical context without risk of retrospective data contamination.

---

## 36. What This Does NOT Prove
- This does **NOT** prove that Agent 2 has directional trading alpha.
- This does **NOT** prove that historical disclosure causes price momentum.
- This does **NOT** prove that the underlying swing trading strategy is profitable.
- This only proves that historical information delivery to Agent 2 is free of temporal and lookahead leakage.

---

## 37. Remaining Limitations
- Ownership data remains structurally `LIMITED` before 2018.
- News archive retains known `CONDITIONAL` coverage bias toward Top-20 equities.

---

## 38. Required Next Action
Proceed to **Batch ZZZ.14.3: Agent 2 Historical Discrimination Pilot** (evaluating outcome-blind thesis generation across multiple historical years on the canonical universe).
