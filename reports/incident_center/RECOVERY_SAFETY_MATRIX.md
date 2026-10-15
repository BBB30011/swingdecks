# RECOVERY SAFETY MATRIX
| Component | Failure Type | Safe Auto-Recovery |
|-----------|--------------|--------------------|
| Agent | Execution Error | SAFE_RETRY |
| PIT | Future Data Access | BLOCK & ESCALATE |
| Live Boundary | Order Attempt | BLOCK & ESCALATE |
| Accounting | Variance > 0 | BLOCK & ESCALATE |
| Data | Missing Parquet | WAIT_FOR_DATA |
