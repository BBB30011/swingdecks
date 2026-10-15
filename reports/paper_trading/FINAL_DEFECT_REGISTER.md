# SWINGDECK FINAL DEFECT REGISTER

All six engineering and documentation defects identified during the autonomous expansion and truth gate audits were completely reproduced, traced, repaired, and regression-tested.

---

### DEFECT-001: Table 8.A Trade Listing Mismatch in Reconciliation Gate Report
* **Severity**: `P1` (Accounting Documentation Integrity)
* **Symptom**: Table 8.A in `FINAL_OPERATIONAL_RECONCILIATION_GATE.md` listed 7 trades summing to `-635,372.37`, conflicting with Table 8.B ledger sum of `-565,790.72` (apparent discrepancy of `Rp 69,581.65`).
* **Root Cause**: Table 8.A was copied from an unpinned preliminary exploratory script before deterministic symbol ordering (`_sym_code`) was locked. The canonical run actually generated BBNI, BMRI, ADRO, ADRO, ANTM, ADRO, and ADRO.
* **Repairs Implemented**: Updated Table 8.A with the true 7 trades from canonical run `CONT_DESK_20260928_103652`. Trade sum now equals **-565,790.72**, matching Table 8.B with **0.00 IDR variance**.
* **Files Changed**: `reports/paper_trading/FINAL_OPERATIONAL_RECONCILIATION_GATE.md`
* **Regression Result**: `PASS (0.00 Variance)`

---

### DEFECT-002: AuditLedger Disk I/O Bottleneck at Scale
* **Severity**: `P1` (Throughput & Scalability)
* **Symptom**: Running 1,000 historical sessions took ~150 seconds due to opening and closing `state/audit/ledger.jsonl` on every single logged event.
* **Root Cause**: `AuditLedger.log_event()` opened the file handle per-event inside a `with open(..., "a")` context.
* **Repairs Implemented**: Added persistent append file handle `_get_fh()` with immediate atomic `.flush()`.
* **Files Changed**: `core/audit_ledger.py`
* **Regression Result**: Benchmark showed 1,000 sessions executing in **2.5–3.7 seconds** (>40x speedup).

---

### DEFECT-003: Non-Deterministic `uuid.uuid4()` Identity Generation
* **Severity**: `P1` (Deterministic Replay)
* **Symptom**: Order, position, session, and event IDs varied between runs with identical market inputs.
* **Root Cause**: Usage of `uuid.uuid4()`.
* **Repairs Implemented**: Replaced with deterministic MD5 hashes based on `(job_id, timestamp, symbol, side, stage)`.
* **Files Changed**: `core/paper_execution.py`, `core/trading_desk_simulation.py`, `core/position_monitor.py`
* **Regression Result**: `RUN_A == RUN_B == RUN_C` bitwise match confirmed.

---

### DEFECT-004: Destructive Test Fixture in `test_batch_ac.py`
* **Severity**: `P0` (Production State Safety)
* **Symptom**: Executing `pytest` erased the `state/` directory, wiping production audit logs during testing.
* **Root Cause**: `test_health_dir_missing()` called `shutil.rmtree("state")` directly without mocking or isolating test paths.
* **Repairs Implemented**: Pointed test to safe temporary path `state_temp_test_missing`.
* **Files Changed**: `tests/test_batch_ac.py`
* **Regression Result**: Test passes without mutating production `state/`.

---

### DEFECT-005: Unhandled Missing Directory Exception in `HealthMonitor`
* **Severity**: `P1` (Reliability & Fail-Closed Safety)
* **Symptom**: `HealthMonitor.check_health()` crashed with unhandled `FileNotFoundError` if state directory was absent.
* **Root Cause**: Missing existence check before inspecting state subdirectories.
* **Repairs Implemented**: Added `self.state_file.parent.exists()` guard to fail-closed gracefully.
* **Files Changed**: `core/health.py`
* **Regression Result**: Passes cleanly under missing directory conditions.

---

### DEFECT-006: Hardcoded Open Position Label in Extended Master Report
* **Severity**: `P1` (Reporting Traceability)
* **Symptom**: Section 12 of `EXTENDED_PAPER_DESK_OPERATIONAL_HARDENING_REPORT.md` stated open position as `ASII, 2,200 shares`, while portfolio state held `ADRO, 2,600 shares`.
* **Root Cause**: Static string literal in markdown generator template instead of dynamic position query.
* **Repairs Implemented**: Updated generator to dynamically extract active position symbol, quantity, and cost basis from portfolio state.
* **Files Changed**: `scripts/audit/continuous_paper_desk_stress_run.py`
* **Regression Result**: Report now accurately states `ADRO, 2,600 shares` with exact cost basis and market value.
