# SWINGDECK — AUTONOMOUS EXPANSION SOURCE OF TRUTH & RUN PROVENANCE AUDIT

**Date**: 2026-09-28  
**Operating Mode**: Autonomous Quantitative Infrastructure & Audit Hardening  
**Scientific Branch**: `CLOSED` (`COBA_019 = NOT_CREATED` | `IMMUTABLE`)  
**Runtime Decision Agents**: Exactly 3 (`Agent 1`, `Agent 2`, `Agent 3`)  
**Execution Mode**: `PAPER_ONLY` (`LiveExecutionBlockedError` strictly fail-closed)  

---

## 1. CANONICAL RUN IDENTIFICATION & VERIFICATION

An exhaustive audit of all state stores, ledger trails, and report artifacts was conducted to verify run lineage without blind trust in string identifiers.

### A. Evaluated Run IDs
1. **`LIVE_LIKE_DESK_20260928_094840`**:
   - *Horizon*: 5 historical market sessions (`2026-03-23` to `2026-03-27`).
   - *Scope*: Initial scenario & component validation test.
   - *Trades*: 1 trade (`BBCA`, Qty 7,000, Realized P&L: Rp 0.00).
   - *Status*: **SUPERSEDED** by continuous multi-month stress run.
2. **`CONT_DESK_20260928_103652`**:
   - *Horizon*: 70 contiguous historical market sessions (`2026-06-03` to `2026-09-13`).
   - *Scope*: Comprehensive continuous trading desk simulation across 12 liquid IDX equities.
   - *Total Symbol-Sessions*: $70 \times 12 = \mathbf{840}$.
   - *Decisions*: BUY: 8, WAIT: 781, AVOID: 51, HOLD: 0, SELL: 0.
   - *Positions*: 8 entries, 7 exits, 1 active open position (`ADRO`).
   - *Accounting*: Ending Cash Rp 92,481,339.60 + Open MV Rp 7,101,000.00 = Ending Equity Rp 99,582,339.60 (Variance: Rp 0.00).
   - *Status*: **CANONICAL_70_SESSION_RUN**.
3. **`EXT_DESK_750`** (Under Expansion):
   - *Horizon*: 750 contiguous historical market sessions (~3 calendar years).
   - *Scope*: Extended sample operational breadth and multi-regime hardening.
   - *Status*: **ACTIVE_AUTONOMOUS_EXPANSION_TARGET**.

---

## 2. PRIMARY SOURCE-OF-TRUTH ARTIFACTS

| SOURCE OF TRUTH PATH | ROLE | FORMAT | INTEGRITY GUARANTEE |
| :--- | :--- | :--- | :--- |
| [`state/audit/ledger.jsonl`](file:///D:/Project/SwingDeck/state/audit/ledger.jsonl) | Primary Event Audit Ledger | JSON Lines (Append-Only) | Cryptographic MD5 event IDs, timestamped, deduplicated |
| [`state/trading_desk_simulation/trading_desk_state.json`](file:///D:/Project/SwingDeck/state/trading_desk_simulation/trading_desk_state.json) | Runtime Desk Snapshot | JSON | Atomic tmp-rename write, state snapshot |
| [`data/parquet/market/*.parquet`](file:///D:/Project/SwingDeck/data/parquet/market) | Approved Market Data | Parquet (12 symbols) | Point-in-time historical daily bars (4,458 common sessions) |
| [`scripts/audit/continuous_paper_desk_stress_run.py`](file:///D:/Project/SwingDeck/scripts/audit/continuous_paper_desk_stress_run.py) | Canonical Replay Harness | Python | Deterministic replay, fixed seed, identical input invariant |

---

## 3. REPORT LINEAGE & STATUS MATRIX

| REPORT PATH | RUN ID BASIS | HORIZON | STATUS | RECONCILIATION STATUS |
| :--- | :---: | :---: | :---: | :---: |
| [`reports/paper_trading/DAILY_DESK_SIMULATION_REPORT.md`](file:///D:/Project/SwingDeck/reports/paper_trading/DAILY_DESK_SIMULATION_REPORT.md) | `LIVE_LIKE_DESK_20260928_094840` | 5 sessions | **SUPERSEDED** | Quarantined with warning banner |
| [`reports/paper_trading/LIVE_LIKE_OPERATIONAL_RUN_REPORT.md`](file:///D:/Project/SwingDeck/reports/paper_trading/LIVE_LIKE_OPERATIONAL_RUN_REPORT.md) | `LIVE_LIKE_DESK_20260928_094840` | 5 sessions | **SUPERSEDED** | Quarantined with warning banner |
| [`reports/paper_trading/CONTINUOUS_DESK_COVERAGE_MATRIX.md`](file:///D:/Project/SwingDeck/reports/paper_trading/CONTINUOUS_DESK_COVERAGE_MATRIX.md) | `CONT_DESK_20260928_103652` | 70 sessions | **ACTIVE_CANONICAL** | Fully reconciled with ledger |
| [`reports/paper_trading/CONTINUOUS_PAPER_DESK_OPERATIONS_REPORT.md`](file:///D:/Project/SwingDeck/reports/paper_trading/CONTINUOUS_PAPER_DESK_OPERATIONS_REPORT.md) | `CONT_DESK_20260928_103652` | 70 sessions | **ACTIVE_CANONICAL** | Fully reconciled with ledger |
| [`reports/paper_trading/FINAL_OPERATIONAL_RECONCILIATION_GATE.md`](file:///D:/Project/SwingDeck/reports/paper_trading/FINAL_OPERATIONAL_RECONCILIATION_GATE.md) | `CONT_DESK_20260928_103652` | 70 sessions | **ACTIVE_CANONICAL** | Fully reconciled with ledger |

---

## 4. ZERO CROSS-RUN CONTAMINATION GUARANTEE

To prevent metric pollution:
1. Each run's audit trail is isolated by `job_id` within the append-only ledger.
2. Metrics from the 5-session scenario (`LIVE_LIKE_DESK_20260928_094840`) are never added, averaged, or mixed into 70-session or 750-session metrics.
3. Every report clearly specifies its underlying run identifier, date range, and sample size.
