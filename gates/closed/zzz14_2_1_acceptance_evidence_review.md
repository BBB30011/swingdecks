# ZZZ.14.2.1 — Acceptance Evidence Review

**Document ID:** `REPORT-ZZZ1421-EVIDENCE-REVIEW`  
**Date:** September 16, 2026  
**Review Type:** Independent Acceptance Evidence Review & Epistemic Audit  
**Target Gate:** Batch ZZZ.14.2.1 Historical Replay Pilot Acceptance  
**Governance Authority:** 3-Agent Architecture (Agent 1: Quant, Agent 2: Market Intelligence & Red Team, Agent 3: Investment Committee & Risk — Audit Only). Zero Agent 4.  
**Execution Environment:** Local Windows / Python 3.12.10 / `.venv` / DuckDB / Parquet

---

## 1. Executive Summary
An exhaustive, independent verification was conducted on all code, tests, dataset layers, and artifacts produced in Batch **ZZZ.14.2.1 (Agent 2 Replay Integration & Historical Replay Pilot Acceptance Gate)**.

This review did **not** accept summary claims or previous AI affirmations as ground truth. Every claim was audited directly against the physical files, AST/source implementations, DuckDB tables, Parquet partitions, test assertions, and generated JSON/Parquet outputs in ``.

### Primary Audit Findings:
1. **Real Dataset V2 Substrate:** Replays query real DuckDB tables (526 events, 10 exposures, 11 relationships, 15 peer networks) and real Parquet daily market data (4,458–6,470 bars per ticker). No mock data or hardcoded returns were substituted in the pilot.
2. **Observation-Level V1 Reconciliation ($N=73$):** All 73 canonical Layer E baseline setups from `scratch/zzz115_observation_level.parquet` were replayed through the real DuckDB/Parquet engine and matched with **0 unexplained discrepancies**.
3. **Agent 2 Hard Context Firewall:** The database bypass was completely dismantled in `agents/agent2_intelligence/llm_reasoner.py` (`self.engine` removed). Agent 2 consumes exclusively `HistoricalKnowledgeState(T)` with zero forward return keys ($H_1 \dots H_{20}$) in generated prompts.
4. **Temporal Rigor & Outcome Blindness:** Four-Timestamp filtering rejected 100% of adversarial future/current-state injections. Snapshot hashes computed before downstream outcome attachment matched post-outcome hashes 100% (`hash_before == hash_after`).
5. **Reproducibility:** 2 independent runs of the 96-observation multi-year pilot yielded 0 hash mismatches (100% deterministic reproducibility).
6. **Verdict:** All 20 reviewed claims are verified by tangible, reproducible evidence. **ZZZ.14.3 eligibility is ALLOWED.**

---

## 2. Scope
- **Universe:** 12 Canonical Equities (`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`).
- **Audit Subjects:** `HistoricalReplayEngine`, `ReplayFirewall`, `HistoricalKnowledgeState`, `Agent2LLMReasoner`, `Agent2IntelligencePipeline`, test suites, scratch artifacts, DuckDB data tables, and Parquet partitions.
- **Constraints Checked:** Zero Agent 4, zero strategy changes, zero parameter tuning, zero lookahead leakage, zero silent fallbacks.

---

## 3. Baseline
- **Methodology Baseline:** `METHODOLOGY_V1_FROZEN_20260915` (`docs/RESEARCH_METHODOLOGY_LOCK_ZZZ12.md`).
- **Dataset Baselines:** `DATASET_V1_CANONICAL_FROZEN` ($N=73$) and `DATASET_V2_20260915` (10-year multi-domain substrate).
- **Snapshot Baselines:** `SNAPSHOT_ZZZ117_687970d0e904`.

---

## 4. Claims Reviewed
A total of 20 core claims (CLAIM-001 through CLAIM-020) spanning data provenance, reconciliation, firewalls, temporal integrity, peer mechanics, derived features, and outcome blindness were audited.

---

## 5. Claim-to-Evidence Matrix

| Claim ID | Description | Expected Evidence | Actual Evidence | Code Verified | Test Verified | Artifact Verified | Status | Reason |
|---|---|---|---|---|---|---|---|---|
| **CLAIM-001** | 96 real multi-year pilot observations | 96 rows in parquet with 12 tickers x 8 dates | Parquet file contains exactly 96 rows, 12 tickers, 8 dates | `HistoricalReplayEngine.replay_state_from_db` | `test_evidence_review_pilot_96_observations_integrity` | `zzz1421_pilot_observation_level.parquet` | `VERIFIED` | Exact schema, real close prices & event counts present. |
| **CLAIM-002** | Real Dataset V2 used, no synthetic mock | Real DuckDB/Parquet tables queried | `intelligence.duckdb` (526 events) & Parquet (4k-6k bars) queried | `core/historical_replay_engine.py` (lines 108–212) | `test_evidence_review_real_dataset_v2_storage` | Parquet market files & DuckDB tables | `VERIFIED` | Queries execute against local DuckDB and Parquet files. |
| **CLAIM-003** | 73/73 V1 reconciliation exact match | 73 baseline setups replayed & matched | 73 setups from `zzz115_observation_level.parquet` replayed | `scratch/run_zzz1421_pilot_acceptance.py` (lines 109–165) | `test_evidence_review_v1_reconciliation_zero_discrepancy` | `zzz1421_v1_reconciliation.json` | `VERIFIED` | 73/73 exact matches. |
| **CLAIM-004** | Unexplained discrepancy = 0 | Count = 0 in reconciliation | `unexplained_discrepancies: 0` in json | Reconciliation loop checks discrepancy trigger | `test_v1_observation_reconciliation_zero_discrepancy` | `zzz1421_v1_reconciliation.json` | `VERIFIED` | Zero unexplained discrepancies found. |
| **CLAIM-005** | Agent 2 receives only `HistoricalKnowledgeState(T)` | Reasoner & Pipeline consume state only | `process_historical_state(state)` & `generate_prompt(state)` | `agents/agent2_intelligence/llm_reasoner.py` (line 15) | `test_agent2_context_firewall_prompt_isolation` | `zzz1421_agent2_context_firewall.json` | `VERIFIED` | Strict typed dataclass input boundary. |
| **CLAIM-006** | Agent 2 cannot access raw DuckDB directly | Reasoner has no DB connection | `self.engine` completely removed from Reasoner | `agents/agent2_intelligence/llm_reasoner.py` (lines 8–13) | `test_evidence_review_agent2_isolation_from_database` | Code inspection | `VERIFIED` | Zero SQL or DB client imports in Agent 2. |
| **CLAIM-007** | Retrieval uses historical availability semantics | Queries filter $\le T$ close timestamp | `published_at <= decision_datetime` & `valid_from <= decision_date` | `core/historical_replay_engine.py` (lines 117, 138, 158) | `test_real_dataset_replay_loading` | DuckDB queries parameterized | `VERIFIED` | 2020 exposure properly excluded in 2018 replay. |
| **CLAIM-008** | Future publication/availability blocked | Future timestamps rejected | 8 adversarial probes evaluated; 0 leaks | `ReplayFirewall.prevent_future_leak` & `enforce_pit` | `test_evidence_review_four_timestamp_pit_rigor` | `zzz1421_leakage_audit.json` | `VERIFIED` | 100% blocked at firewall layer. |
| **CLAIM-009** | Current 2026 state blocked from past T | `is_current_state` & modern `valid_from` rejected | Modern 2026 records rejected from 2018 replay | `ReplayFirewall.prevent_current_state_leak` | `test_current_state_injection_blocked` | `zzz1421_leakage_audit.json` | `VERIFIED` | Current state flag and future `valid_from` blocked. |
| **CLAIM-010** | Future disclosure/news blocked | News/filings post-T blocked | Probes with future dates rejected | `ReplayFirewall.prevent_future_leak` | `test_future_information_injection_blocked` | `zzz1421_leakage_audit.json` | `VERIFIED` | Future event filtering verified. |
| **CLAIM-011** | Silent fallback = 0 | Missing data yields UNKNOWN/LIMITED, not modern data | Empty lists returned when records missing; no modern fallback | `core/historical_replay_engine.py` & `replay_firewall.py` | `test_silent_fallback_absence` | `zzz1421_derived_feature_leakage.json` | `VERIFIED` | Missing data does not query modern state. |
| **CLAIM-012** | UNKNOWN truly preserved | Empty events yield UNKNOWN/LOW confidence | Reasoner returns `research_status: "UNKNOWN"` on empty events | `agents/agent2_intelligence/llm_reasoner.py` (lines 70–87) | `test_agent2_context_firewall_prompt_isolation` | `zzz1421_pilot_observation_level.parquet` | `VERIFIED` | `NO_EVIDENCE` mapped to UNKNOWN. |
| **CLAIM-013** | Peer self-inclusion = 0 | Target excluded from own peer set | 0 self-inclusion violations across 96 setups | `ReplayFirewall.enforce_peer_self_exclusion` | `test_evidence_review_peer_integrity_leave_one_out` | `zzz1421_peer_integrity.json` | `VERIFIED` | 100% leave-one-out compliance. |
| **CLAIM-014** | Derived features free of future leakage | 14 derived features audited as SAFE | All 14 features audited; zero lookahead | Feature audit table in `scratch/run_zzz1421_pilot_acceptance.py` | `test_evidence_review_derived_feature_safety` | `zzz1421_derived_feature_leakage.json` | `VERIFIED` | Lookahead window strictly $\le T$. |
| **CLAIM-015** | Outcome blindness enforced | Prohibited outcome keys blocked | `_PROHIBITED_OUTCOME_KEYS` gate rejects forward returns | `core/historical_knowledge_state.py` (lines 33–37) | `test_outcome_blindness_snapshot_immutability` | `zzz1421_outcome_blindness.json` | `VERIFIED` | $H_1 \dots H_{20}$ barred from knowledge state. |
| **CLAIM-016** | Attaching outcomes leaves state unmutated | `hash_before == hash_after` | Hashes match byte-for-byte | `core/historical_knowledge_state.py` | `test_evidence_review_outcome_blindness` | `zzz1421_outcome_blindness.json` | `VERIFIED` | Downstream outcome attachment leaves snapshot intact. |
| **CLAIM-017** | Reproducibility tested with same config | 2 runs produce identical hashes | 96/96 hashes identical across independent runs | Multi-run verification in `run_zzz1421_pilot_acceptance.py` | `test_evidence_review_reproducibility` | `zzz1421_reproducibility.json` | `VERIFIED` | Deterministic SHA-256 state serialization. |
| **CLAIM-018** | 20 Red Team checks substantive | 20 checks map to code & data tests | All 20 checks verified against concrete boundaries | Red Team generator & test assertions | `test_evidence_review_red_team_20_checks` | `zzz1421_red_team.json` | `VERIFIED` | 20 PASS, 0 WEAK, 0 FAIL. |
| **CLAIM-019** | Eligibility matrix represents availability | 432 domain/period/ticker cells mapped | Matrix generated across 9 domains, 4 periods, 12 tickers | `ReplayFirewall.evaluate_eligibility` | `test_evidence_review_eligibility_matrix` | `zzz1421_eligibility_matrix.json` | `VERIFIED` | Pre-2018 ownership LIMITED, news CONDITIONAL. |
| **CLAIM-020** | Gate A/B/C PASS meets criteria | All 3 sub-gates satisfy frozen criteria | Engine, Pilot, and Agent 2 Integration verified | All test suites & artifacts | 25/25 combined pytest tests passed | Full repository inspection | `VERIFIED` | Fully verified across all dimensions. |

---

## 6. Repository Implementation Review
1. [`core/historical_knowledge_state.py`](file:///core/historical_knowledge_state.py): Implements immutable dataclass with four-timestamp enforcement (`enforce_pit`), custom JSON serializer for `date`/`datetime` types, strict rejection of prohibited outcome keys (`_PROHIBITED_OUTCOME_KEYS`), and deterministic SHA-256 snapshot hashing.
2. [`core/replay_firewall.py`](file:///core/replay_firewall.py): Implements domain eligibility mapping, future timestamp rejection (`prevent_future_leak`), current-state rejection (`prevent_current_state_leak`), outcome leak prevention (`prevent_outcome_leak`), and leave-one-out peer filtering (`enforce_peer_self_exclusion`).
3. [`core/historical_replay_engine.py`](file:///core/historical_replay_engine.py): Direct read-only query layer for DuckDB and Parquet. Enforces temporal parameterization ($T$ close at 16:00:00 WIB), loads OHLCV, corporate actions, disclosures, exposures, relationships, and peer networks.
4. [`agents/agent2_intelligence/llm_reasoner.py`](file:///agents/agent2_intelligence/llm_reasoner.py): Consumes exclusively `HistoricalKnowledgeState(T)`. Zero database clients, zero SQL dependencies, zero forward return keys in prompt generation.
5. [`agents/agent2_intelligence/pipeline.py`](file:///agents/agent2_intelligence/pipeline.py): Pipeline wrapper operating exclusively on historical knowledge state.

---

## 7. Test Quality Review
The repository contains 2 active test suites for Batch ZZZ.14.2.1:
1. [`tests/test_batch_zzz1421_agent2_replay_integration.py`](file:///tests/test_batch_zzz1421_agent2_replay_integration.py) (13 tests):
   - Tests real database replay loading, V1 reconciliation zero discrepancy, future injection blocking, current-state injection blocking, peer self-exclusion, silent fallback absence, prompt isolation, outcome blindness, reproducibility, and Red Team results.
2. [`tests/test_zzz1421_acceptance_evidence_review.py`](file:///tests/test_zzz1421_acceptance_evidence_review.py) (12 tests):
   - Independent deep tests verifying database row counts, pilot parquet schema/distributions, prompt content string checks, artifact integrity, and temporal boundaries.
- **Combined Test Status:** 25 passed in 3.28s. Zero dummy tests (`test_dummy` removed/superseded). All assertions are substantive.

---

## 8. Real Dataset V2 Verification
- **DuckDB Intelligence Database:** [`data/intelligence.duckdb`](file:///data/intelligence.duckdb)
  - `fact_event`: 526 verified historical events.
  - `fact_exposure`: 10 deterministic economic exposures.
  - `fact_relationship`: 11 temporal corporate relationships.
  - `fact_peer_network`: 15 peer group mappings.
  - `dim_entity`: 28 canonical entities.
  - `dim_entity_alias`: 24 aliases.
- **Parquet Market Data:** [`data/parquet/market/`](file:///data/parquet/market/)
  - Real daily OHLCV bars across all 12 canonical tickers spanning 2000–2026 (4,458 to 6,470 bars per ticker).

---

## 9. 96 Pilot Verification
- **Total Pilot Observations:** 96
- **Unique Tickers:** 12 (`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`)
- **Observations Per Ticker:** Exactly 8 per ticker (Balanced).
- **Unique Decision Dates:** 8 (`2016-06-15`, `2017-09-20`, `2018-05-15`, `2019-10-25`, `2021-08-10`, `2024-02-15`, `2025-09-09`, `2026-08-27`)
- **Observations Per Date:** Exactly 12 per date (Balanced).
- **Market Availability:** 96 / 96 (100%).
- **Peer Self-Exclusion Passed:** 96 / 96 (100%).
- **Total Events Ingested Across Replays:** 2,435.
- **Total Exposures Replayed:** 28.
- **Total Peer Links Replayed:** 52.

---

## 10. V1 N=73 Reconciliation Verification
- **Baseline File:** [`scratch/zzz115_observation_level.parquet`](file:///scratch/zzz115_observation_level.parquet)
- **Baseline Sample Size:** 73
- **Replayed Sample Size:** 73
- **Observation-Level Exact Matches:** 73
- **Unexplained Discrepancies:** 0
- **Artifact Verified:** [`scratch/zzz1421_v1_reconciliation.json`](file:///scratch/zzz1421_v1_reconciliation.json)

---

## 11. Four-Timestamp / PIT Audit
- `event_date`, `published_at`, `available_at`, `observed_at`, `valid_from`, and `valid_to` were audited across queries and filtering gates.
- 8 adversarial injection probes executed (`published_at > T`, `available_at > T`, `observed_at > T`, `valid_from > T`, `valid_to < T`, modern 2026 records).
- **Leaks Detected:** 0 (100% blocked).
- **Artifact Verified:** [`scratch/zzz1421_leakage_audit.json`](file:///scratch/zzz1421_leakage_audit.json)

---

## 12. Silent Fallback Audit
- **Pre-2018 Ownership:** Evaluated as `LIMITED`. Engine does not query modern 2026 ownership records when pre-2018 records are absent.
- **News Coverage:** Evaluated as `CONDITIONAL`. Missing news yields empty event state rather than asserting `VERIFIED_NO_EVENT`.
- **Silent Fallbacks Found:** 0.

---

## 13. UNKNOWN Preservation
- `NO_EVIDENCE_IN_DATASET` is preserved as `UNKNOWN` / `OBSERVATION` in Agent 2 thesis output.
- Confidence is set to `LOW` and differential status to `UNKNOWN` when evidence is missing.
- Zero conversion of `NO_EVIDENCE` into `VERIFIED_NO_EVENT`.

---

## 14. Peer Integrity
- **Total Observations Audited:** 96
- **Total Peer Links Evaluated:** 52
- **Self-Inclusion Violations:** 0 (100% leave-one-out compliance).
- **Peer Contamination Rate:** 0.0% on clean purified benchmarks.
- **Artifact Verified:** [`scratch/zzz1421_peer_integrity.json`](file:///scratch/zzz1421_peer_integrity.json)

---

## 15. Derived Feature Leakage
14 derived features audited across input data, lookback windows, and as-of time rules. Zero lookahead dependencies identified.
- **Artifact Verified:** [`scratch/zzz1421_derived_feature_leakage.json`](file:///scratch/zzz1421_derived_feature_leakage.json)

---

## 16. Agent 2 Hard Context Firewall
All 7 firewall dimensions verified:
1. *Database Firewall:* Direct SQL access removed (`self.engine` eliminated).
2. *Retrieval Firewall:* Enforces $\le T$ 16:00:00 WIB close parameterization.
3. *Memory Firewall:* Stateless per-decision-point execution.
4. *File Firewall:* Barred from reading outcome parquet/report files.
5. *Prompt Firewall:* Prompts verified clean: zero occurrences of `H1`, `H3`, `H5`, `H10`, `H20`, `forward_return`.
6. *Tool Firewall:* Constrained to historical state objects. Zero Agent 4.
7. *Outcome Firewall:* Forward returns attached strictly after thesis freeze.
- **Artifact Verified:** [`scratch/zzz1421_agent2_context_firewall.json`](file:///scratch/zzz1421_agent2_context_firewall.json)

---

## 17. Current-State Injection
- Probed with modern 2026 corporate relationship and ownership records.
- Blocked by `prevent_current_state_leak` and excluded from final Agent 2 prompt.

---

## 18. Future Injection
- Probed with future publication and availability dates.
- 100% blocked by `prevent_future_leak`.

---

## 19. Outcome Blindness
- `BBCA` replayed at $T = \text{2025-09-09}$.
- Pre-outcome hash: `9bc3d700a89cb5335612484b988f9c007c654b123ed7f2d3a69bd02dc9472475`.
- Post-outcome hash: `9bc3d700a89cb5335612484b988f9c007c654b123ed7f2d3a69bd02dc9472475`.
- Hashes identical; snapshot immutable.
- **Artifact Verified:** [`scratch/zzz1421_outcome_blindness.json`](file:///scratch/zzz1421_outcome_blindness.json)

---

## 20. Reproducibility
- 96 setups executed across 2 independent runs.
- **Hash Mismatches:** 0 / 96 (100.0% reproducibility).
- **Artifact Verified:** [`scratch/zzz1421_reproducibility.json`](file:///scratch/zzz1421_reproducibility.json)

---

## 21. Eligibility Distribution
Distribution of 432 Domain $\times$ Period $\times$ Ticker matrix cells:

### By Period
| Period | READY | LIMITED | BLOCKED | Total |
|---|---|---|---|---|
| `PRE_2016` | 36 | 72 | 0 | 108 |
| `2016_2017` | 84 | 24 | 0 | 108 |
| `2018_2024` | 108 | 0 | 0 | 108 |
| `2025_2026` | 108 | 0 | 0 | 108 |

### By Domain
| Domain | READY | LIMITED | BLOCKED | Total |
|---|---|---|---|---|
| `MARKET` | 48 | 0 | 0 | 48 |
| `EXPOSURE` | 48 | 0 | 0 | 48 |
| `PEER` | 48 | 0 | 0 | 48 |
| `CORPORATE_ACTION` | 36 | 12 | 0 | 48 |
| `COMMODITY` | 36 | 12 | 0 | 48 |
| `MACRO` | 36 | 12 | 0 | 48 |
| `NEWS` | 36 | 12 | 0 | 48 |
| `OWNERSHIP` | 24 | 24 | 0 | 48 |
| `RELATIONSHIP` | 24 | 24 | 0 | 48 |

---

## 22. Ticker / Date / Domain Concentration
- **Concentration by Ticker:** Perfectly uniform (8 observations for each of the 12 tickers).
- **Concentration by Date:** Perfectly uniform (12 observations for each of the 8 decision dates).
- **Concentration by Sector:** Financials (32), Coal (24), Metals (8), Automotive (8), Nickel (8), Telecom (8), Mining Services (8).
- **Commodity vs Non-Commodity:** Exactly 48 (50.0%) Commodity vs 48 (50.0%) Non-Commodity.

---

## 23. Red Team 20 Checks
All 20 Red Team checks verified against substantive code and data bounds:
- **Pass Count:** 20 / 20
- **Weak Count:** 0
- **Fail Count:** 0
- **Not Estimable Count:** 0
- **Artifact Verified:** [`scratch/zzz1421_red_team.json`](file:///scratch/zzz1421_red_team.json)

---

## 24. Evidence Gaps
None. All required datasets, code paths, test suites, and 10 required artifacts exist and match expected values.

---

## 25. Contradictions
None. No contradictions found between code implementation, database tables, test assertions, and report metrics.

---

## 26. Failed Checks
`0` failed checks.

---

## 27. Weak Checks
`0` weak checks.

---

## 28. Not Estimable Checks
- Pre-2018 ownership coverage is structurally documented as `LIMITED`.
- Historical news recall retains known `CONDITIONAL` bias for Top-20 equities.

---

## 29. Gate A Assessment — Engine Integrity
- `HistoricalKnowledgeState`, `ReplayFirewall`, and `HistoricalReplayEngine` fully operational on real DuckDB/Parquet datasets.
- **Status:** `PASS`

---

## 30. Gate B Assessment — Historical Pilot
- 96 multi-year real pilot setups replayed with 0 lookahead leaks, 100% peer self-exclusion, and 0 unexplained V1 discrepancies.
- **Status:** `PASS`

---

## 31. Gate C Assessment — Agent 2 Integration
- Agent 2 operates exclusively via `HistoricalKnowledgeState(T)` with all 7 context firewall dimensions verified.
- **Status:** `PASS`

---

## 32. Final Acceptance Status
$$\mathbf{PASS\ —\ ZZZ.14.2.1\ EVIDENCE\ VERIFIED}$$

---

## 33. ZZZ.14.3 Eligibility
$$\mathbf{ZZZ.14.3\ ELIGIBILITY:\ ALLOWED}$$

---

## 34. Scientific Interpretation
The evidence confirms that the historical replay infrastructure is Point-In-Time safe, outcome-blind, current-state-safe, and cryptographically reproducible on real Dataset V2 data. Agent 2 can safely receive historical context without data leakage.

---

## 35. What This Review Does NOT Prove
- This does **NOT** prove that Agent 2 has predictive alpha.
- This does **NOT** prove that disclosure causes price movement.
- This does **NOT** prove that the swing trading strategy is profitable.
- This only proves that historical information delivery to Agent 2 is free of temporal and lookahead leakage.

---

## 36. Limitations
- Ownership data is structurally `LIMITED` before 2018.
- News archive retains `CONDITIONAL` coverage bias toward Top-20 market capitalization equities.

---

## 37. Next Action
Proceed to **Batch ZZZ.14.3: Agent 2 Historical Discrimination Pilot** (evaluating outcome-blind thesis generation across multiple historical years on the canonical universe).
