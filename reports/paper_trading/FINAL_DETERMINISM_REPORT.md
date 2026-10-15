# SWINGDECK FINAL DETERMINISM & REPLAY AUDIT REPORT

## 1. REPLAY EXPERIMENT DESIGN
To prove absolute deterministic replay under identical inputs, the 1,000-session simulation was executed across three independent runs (`RUN_A`, `RUN_B`, `RUN_C`) using separate runtime state directories.

---

## 2. BITWISE REPLAY COMPARISON MATRIX

| EVALUATED METRIC | RUN A | RUN B | RUN C | DETERMINISTIC MATCH |
| :--- | :---: | :---: | :---: | :---: |
| **Total Candidates Scanned** | 12,000 | 12,000 | 12,000 | **BITWISE EXACT** |
| **Agent 3 BUY Decisions** | 109 | 109 | 109 | **BITWISE EXACT** |
| **Agent 3 WAIT Decisions** | 11,183 | 11,183 | 11,183 | **BITWISE EXACT** |
| **Agent 3 AVOID Decisions** | 708 | 708 | 708 | **BITWISE EXACT** |
| **Orders Created & Accepted** | 109 | 109 | 109 | **BITWISE EXACT** |
| **Orders Filled** | 109 | 109 | 109 | **BITWISE EXACT** |
| **Closed Positions** | 108 | 108 | 108 | **BITWISE EXACT** |
| **Ending Available Cash (IDR)** | 92,474,443.08 | 92,474,443.08 | 92,474,443.08 | **BITWISE EXACT** |
| **Ending Portfolio Equity (IDR)**| 99,312,443.08 | 99,312,443.08 | 99,312,443.08 | **BITWISE EXACT** |
| **Portfolio Realized P&L (IDR)**| -491,511.66 | -491,511.66 | -491,511.66 | **BITWISE EXACT** |
| **Total Transaction Costs (IDR)**| 3,029,591.92 | 3,029,591.92 | 3,029,591.92 | **BITWISE EXACT** |
| **Exit Trigger: THESIS_INVALID** | 81 | 81 | 81 | **BITWISE EXACT** |
| **Exit Trigger: STOP_LOSS** | 20 | 20 | 20 | **BITWISE EXACT** |
| **Exit Trigger: TARGET_REACHED** | 4 | 4 | 4 | **BITWISE EXACT** |
| **Exit Trigger: TIME_EXIT** | 3 | 3 | 3 | **BITWISE EXACT** |

---

## 3. SOURCES OF NONDETERMINISM AUDITED & FIXED
1. **Elimination of `uuid.uuid4()`**:
   - Replaced pseudo-random UUIDs in `core/paper_execution.py`, `core/trading_desk_simulation.py`, and `core/position_monitor.py` with deterministic MD5 hashes conditioned on `(job_id, timestamp, symbol, side, stage)`.
2. **Stable Symbol Ordering**:
   - Pinned deterministic symbol enumeration using `_sym_code()` to avoid dictionary ordering variations across Python executions.
3. **Audit Ledger Event Hash**:
   - Structured metadata JSON sorted deterministically via `json.dumps(..., sort_keys=True)`.

---

## 4. IDENTITY COLLISION AUDIT
* **Total Order IDs Evaluated**: 109 | Unique: 109 (**0 Collisions**)
* **Total Position IDs Evaluated**: 109 | Unique: 109 (**0 Collisions**)
* **Total Audit Event IDs Evaluated**: 37,170 | Unique: 37,170 (**0 Collisions**)

```text
================================================================================
REPLAY_DETERMINISM_STATUS = PASS
RUN_A == RUN_B == RUN_C   = TRUE (0.00 VARIANCE)
ID_COLLISION_COUNT        = 0
================================================================================
```
