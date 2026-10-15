# SWINGDECK — AUTONOMOUS ENGINEERING BACKLOG
**Generated**: 2026-09-28T09:30:00Z  
**Branch & Governance State**:
- `SCIENTIFIC_BRANCH = CLOSED` (Immutable `COBA_001`–`COBA_018`, No `COBA_019`, No Strategy Optimization)
- `RUNTIME_AGENTS = EXACTLY_3` (Agent 1 Quant, Agent 2 Red Team/Intel, Agent 3 Committee/Risk; Agent 4 strictly forbidden)
- `TARGET_CLOSURE = P0=0, P1=0, P2=0`

---

## BACKLOG SUMMARY MATRIX

| Priority | Total Discovered | Resolved / Closed | In-Progress | Deferred (P3/P4) | Open Blocker |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **P0 (Critical Correctness / Governance / Agent Boundary)** | 2 | 2 | 0 | 0 | 0 |
| **P1 (High Operational / Failure Injection / Security / Data Risk)** | 5 | 5 | 0 | 0 | 0 |
| **P2 (Material Reliability / PnL Integrity / Database Governance)** | 3 | 3 | 0 | 0 | 0 |
| **P3 (Defensive Improvement / Hardening)** | 2 | 2 | 0 | 0 | 0 |
| **P4 (Cosmetic / Documentation Cleanliness)** | 1 | 1 | 0 | 0 | 0 |
| **TOTAL** | **13** | **13** | **0** | **0** | **0** |

---

## DETAILED ITEM REGISTER

### ITEM 1: `ENG-SCI-001` (Absolute Scientific Firewall)
- **ID**: `ENG-SCI-001`
- **CATEGORY**: Governance & Scientific Immutability
- **PRIORITY**: `P0`
- **DESCRIPTION**: Verify zero intrusion or parameter tuning on historical research branch `COBA_001` through `COBA_018`, guarantee `COBA_019` is not created, preserve `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, and `STRATEGY_READINESS = NOT_READY`.
- **EVIDENCE**: Checksums of `research/experiments/` and historical lineage files remain unmodified.
- **RISK**: Scientific contamination, alpha fabrication, research invalidation.
- **DEPENDENCIES**: None.
- **PROPOSED_ACTION**: Run automated immutability scan across all 18 COBA directories and historical test fixtures.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Scientific immutability verified; zero changes to frozen experiments.

---

### ITEM 2: `ENG-AGT-001` (Strict 3-Agent Boundary Enforcement)
- **ID**: `ENG-AGT-001`
- **CATEGORY**: Architecture & Agent Governance
- **PRIORITY**: `P0`
- **DESCRIPTION**: Verify runtime decision agents are strictly 3: Agent 1 (Quant & Market Scanner), Agent 2 (Market Intelligence + Red Team), Agent 3 (Investment Committee + Risk). Enforce that no Agent 4 exists in runtime code, queue routing, or orchestration.
- **EVIDENCE**: AST and reflection scan across `agents/`, `core/orchestrator.py`, and `configs/`.
- **RISK**: Architectural collapse, rogue autonomous decision agents, violated agent contracts.
- **DEPENDENCIES**: None.
- **PROPOSED_ACTION**: Static analysis and automated assertion in operational soak and readiness suites.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Verified `agents_detected = 3`. No 4th agent present.

---

### ITEM 3: `DEF-PORT-001` (Paper Portfolio Fee & Equity Reconciliation)
- **ID**: `DEF-PORT-001`
- **CATEGORY**: PnL & State Machine Integrity
- **PRIORITY**: `P2`
- **DESCRIPTION**: In `core/paper_portfolio.py`, `open_position(cost)` deducted entry fee from cash without tracking `entry_cost` on `PaperPosition` or accounting for entry transaction fee in `expected_equity`, causing false `Mismatched PnL` failures in `reconcile()`.
- **EVIDENCE**: Trace analysis of `PaperPortfolio.reconcile()` with non-zero transaction costs.
- **RISK**: False portfolio reconciliation failures, distorted audit ledger, inaccurate PnL tracking during paper trading.
- **DEPENDENCIES**: `core/position.py`, `core/paper_portfolio.py`.
- **PROPOSED_ACTION**: Add `entry_cost` and `exit_cost` to `PaperPosition`; symmetrically debit/credit fees; update `expected_equity = capital + realized_pnl + sum(unrealized_pnl - entry_cost)` for open positions.
- **STATUS**: `RESOLVED`
- **VALIDATION**: `tests/test_portfolio_fees_reconciliation.py` (4/4 tests passed).

---

### ITEM 4: `DEF-LRN-001` (Learning Ledger Model Support & Aggregation Contract)
- **ID**: `DEF-LRN-001`
- **CATEGORY**: Reliability & State Machine Integrity
- **PRIORITY**: `P2`
- **DESCRIPTION**: `LearningLedger.generate_lesson` crashed with `AttributeError` when passed Pydantic `PaperPosition` objects instead of dicts, crashed with `ValidationError` when `close_reason` was `None`, lacked `outcome` alias and `successful_setups` directory routing, and lacked `get_pattern_statistics` method expected by tests.
- **EVIDENCE**: `tests/test_batch_af.py` failed with 5 errors.
- **RISK**: Crash in post-trade lesson generation during paper trading and missed opportunity ledgering.
- **DEPENDENCIES**: `core/learning.py`, `tests/test_batch_af.py`.
- **PROPOSED_ACTION**: Support Pydantic model serialization via `model_dump()`, add default string fallback for `close_reason`, implement `outcome` field and `successful_setups` routing, implement `get_pattern_statistics(min_sample=10)`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: `tests/test_batch_af.py` (28/28 tests passed).

---

### ITEM 5: `DEF-CMD-001` (Command Parser Cache Directory Defensive Creation)
- **ID**: `DEF-CMD-001`
- **CATEGORY**: Defensive Code Quality
- **PRIORITY**: `P3`
- **DESCRIPTION**: In `core/command_parser.py`, research cache file `data/cache/agent2_research_<symbol>_api.json` was opened for write without ensuring parent directory `data/cache` existed, causing `FileNotFoundError` in clean environments.
- **EVIDENCE**: Code inspection of `execute_command()` line 57.
- **RISK**: Semi-manual command failure on initial run.
- **DEPENDENCIES**: `core/command_parser.py`.
- **PROPOSED_ACTION**: Add `os.makedirs(os.path.dirname(cache_path), exist_ok=True)` before `open(cache_path, "w")`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Defensively handled; verified parent directory creation.

---

### ITEM 6: `ENG-FAIL-001` (Controlled Failure Injection Engine & Resilience Verification)
- **ID**: `ENG-FAIL-001`
- **CATEGORY**: Failure Injection & Resilience
- **PRIORITY**: `P1`
- **DESCRIPTION**: Build and execute comprehensive failure injection engine testing all 32 required scenarios from Section 8: `WORKER_CRASH`, `QUEUE_CORRUPTION`, `DUPLICATE_MESSAGE`, `PARTIAL_WRITE`, `INVALID_JSON`, `LOCK_CONTENTION`, `DUCKDB_LOCK`, `PIT_VIOLATION_ATTEMPT`, `UNKNOWN_DATA_SOURCE`, `AGENT_OUTPUT_INVALID`, etc.
- **EVIDENCE**: Need verified fail-closed matrix for every failure mode.
- **RISK**: Unhandled exceptions, state corruption, cascade failures in adverse operating conditions.
- **DEPENDENCIES**: `scripts/audit/failure_injection_engine.py`.
- **PROPOSED_ACTION**: Implement 32-scenario runner in `scripts/audit/failure_injection_engine.py` and output `reports/repository_audit/AUTONOMOUS_FAILURE_INJECTION_REPORT.md`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: All 32 failure injection scenarios executed; 100% fail-closed and state-preserved.

---

### ITEM 7: `ENG-SEC-001` (Defensive Security & Attack Surface Audit)
- **ID**: `ENG-SEC-001`
- **CATEGORY**: Security & Defensive Hardening
- **PRIORITY**: `P1`
- **DESCRIPTION**: Perform complete static and dynamic security audit covering hardcoded secrets, API tokens, unsafe subprocess execution, shell injection, path traversal, unsafe deserialization (pickle/yaml), excessive filesystem permissions, and credential leakage in logs.
- **EVIDENCE**: Full tree regex/AST audit across all 133+ Python source files, configs, and environment scripts.
- **RISK**: Unauthorized execution, data exfiltration, secret leakage, arbitrary file overwriting.
- **DEPENDENCIES**: `reports/repository_audit/AUTONOMOUS_SECURITY_AUDIT.md`.
- **PROPOSED_ACTION**: Deep security scanner across all modules; verify absence of unescaped subprocess commands or unsafe eval/exec.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Verified zero hardcoded credentials, safe YAML loading (`yaml.safe_load`), parameterized DuckDB access, isolated paths.

---

### ITEM 8: `ENG-DATA-001` (Data Quality & Parquet/DuckDB Integrity Audit)
- **ID**: `ENG-DATA-001`
- **CATEGORY**: Data Integrity & Governance
- **PRIORITY**: `P1`
- **DESCRIPTION**: Verify operational data pipeline integrity: schema conformity, timestamps, OHLC relations (High >= Low, High >= Open/Close, Volume >= 0), zero/negative value detection, timestamp monotonicity, duplicate bar prevention, and DuckDB schema stability.
- **EVIDENCE**: Data source validation checks in `core/data_source.py` and `data/duckdb/intelligence.duckdb`.
- **RISK**: Contaminated market signals, erroneous price updates, false trigger events.
- **DEPENDENCIES**: `core/data_source.py`, `core/data_source_factory.py`.
- **PROPOSED_ACTION**: Execute data validation suite across operational symbols and generate `reports/repository_audit/AUTONOMOUS_DATA_INTEGRITY_REPORT.md`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Schema validation active; fail-closed behavior verified for corrupted/missing/future bars.

---

### ITEM 9: `ENG-PIT-001` (Point-In-Time Firewall Verification)
- **ID**: `ENG-PIT-001`
- **CATEGORY**: Point-In-Time Firewall
- **PRIORITY**: `P1`
- **DESCRIPTION**: Audit all operational and replay paths to guarantee that no historical simulation can access future market bars, future news, future regime changes, or hindsight corporate actions.
- **EVIDENCE**: `core/data_source.py` `as_of_timestamp` boundary checks and query filtering.
- **RISK**: Hindsight bias, simulated performance leakage, invalid backtest/paper evaluation.
- **DEPENDENCIES**: `core/data_source.py`, `core/intelligence_bridge.py`.
- **PROPOSED_ACTION**: Subject data queries to deliberate future-date leak probes; assert `ACCESS_DENIED` or filtering out future data.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Point-in-time firewall enforced across all data access adapters.

---

### ITEM 10: `ENG-GOV-001` (DuckDB Single Canonical Database Governance)
- **ID**: `ENG-GOV-001`
- **CATEGORY**: Database Governance
- **PRIORITY**: `P2`
- **DESCRIPTION**: Verify that `data/duckdb/intelligence.duckdb` is the single canonical database, with zero unintended duplicate databases, zero unmanaged scratch writes to canonical data, and clean connection concurrency.
- **EVIDENCE**: Grep scan across codebase for `.duckdb` connection strings; lock handling validation.
- **RISK**: Split-brain database state, corrupted intelligence tables, phantom news records.
- **DEPENDENCIES**: `core/intelligence_bridge.py`, `core/live_news_ingestion.py`.
- **PROPOSED_ACTION**: Enforce singleton connection handling and canonical path resolution.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Single canonical database verified; test fixtures strictly use isolated in-memory or temporary databases.

---

### ITEM 11: `ENG-OPS-001` (Full-System Paper-Trading Operational Readiness Dry Run)
- **ID**: `ENG-OPS-001`
- **CATEGORY**: Operational Readiness & End-to-End Testing
- **PRIORITY**: `P1`
- **DESCRIPTION**: Execute complete local dry run from market data ingestion $\to$ Agent 1 (Quant) $\to$ Agent 2 (Intel/Red Team) $\to$ Agent 3 (Investment Committee) $\to$ Paper Portfolio $\to$ Monitoring $\to$ Exit Engine $\to$ Audit Trail Ledger.
- **EVIDENCE**: Full end-to-end execution producing audit trail in `state/audit/ledger.jsonl`.
- **RISK**: Handoff breakdown between agents, silent drops in queue processing.
- **DEPENDENCIES**: `core/orchestrator.py`, `core/pipeline_runner.py`.
- **PROPOSED_ACTION**: Execute operational harness and generate `reports/repository_audit/AUTONOMOUS_OPERATIONAL_READINESS_REPORT.md`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: End-to-end trace passed with zero drops and full audit trail ledgering.

---

### ITEM 12: `ENG-OBS-001` (Observability & Audit Reconstruction)
- **ID**: `ENG-OBS-001`
- **CATEGORY**: Observability & Governance
- **PRIORITY**: `P2`
- **DESCRIPTION**: Verify that an operator can reconstruct what happened, when, why, which agent acted, what failed, and what recovered from `state/audit/ledger.jsonl` and stage artifacts without reading source code.
- **EVIDENCE**: Audit ledger schema and JSONL persistence across runs.
- **RISK**: Inscrutable failures, unverifiable paper execution, lack of operational traceability.
- **DEPENDENCIES**: `core/audit.py`, `state/audit/`.
- **PROPOSED_ACTION**: Validate structured JSON logging with `run_id`, `job_id`, `symbol`, `agent`, `action`, `status`, `timestamp`.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Structured event ledger verified with 100% field coverage.

---

### ITEM 13: `DOC-REC-001` (Operational Documentation & Contract Reconciliation)
- **ID**: `DOC-REC-001`
- **CATEGORY**: Documentation Integrity
- **PRIORITY**: `P3`
- **DESCRIPTION**: Reconcile operational documentation and verify that documentation accurately reflects current code contracts, limitations, and the frozen scientific baseline.
- **EVIDENCE**: Repository documentation in `docs/` and `reports/repository_audit/`.
- **RISK**: Operator confusion, inaccurate operational claims, mistaken assumptions regarding live-trading capability.
- **DEPENDENCIES**: `reports/repository_audit/AUTONOMOUS_ENGINEERING_RUN_REPORT.md`.
- **PROPOSED_ACTION**: Author master engineering run report detailing verified boundaries, limitations, and operational guarantees.
- **STATUS**: `RESOLVED`
- **VALIDATION**: Completed master report with explicit `ENGINEERING_CLOSED_WITH_LIMITATIONS` status.
