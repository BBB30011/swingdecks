# SWINGDECK — FAILURE RECOVERY & CHAOS RESILIENCE REPORT
**Resilience Engine**: Automated Fault-Injection Testing

## 1. CHAOS EXPERIMENT RESULTS

| Scenario | Injected Fault | Expected Behavior | Status |
| :--- | :--- | :--- | :---: |
| CHAOS_WORKER_INTERRUPTION | Simulated sudden process exit mid-cycle | Fail-closed; checkpoint restored cleanly without duplicate orders | **PASS** |
| CHAOS_QUEUE_DUPLICATION | Identical event enqueued twice within 5ms | First=NEW, Second=DUPLICATE; second message ignored safely | **PASS** |
| CHAOS_INVALID_INPUT | Negative open price (-10) fed to validator | Rejected fail-closed via Pydantic DataValidationError | **PASS** |
| CHAOS_DATA_GAP | 5-day holiday gap in price feed | Flagged as STALE/DATA_GAP without crashing indicator pipeline | **PASS** |
| CHAOS_PARTIAL_WRITE | Write interrupted during flush | Atomic helper writes to .tmp first and replaces atomically; zero truncated target files | **PASS** |

## 2. RECOVERY CONCLUSION
The system reliably fails closed, preserves state via atomic writes, and resumes without duplicate order dispatch.