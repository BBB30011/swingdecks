# SHADOW LIVE ARCHITECTURE

- **Data Ingestion**: The daemon polls for new `.parquet` data.
- **State Tracking**: `DAEMON_STATE_FILE` tracks `processed_dates`. If a date is not in this list, it is processed.
- **Pipeline**: New data -> Agent 1 -> Agent 2 -> Red Team -> Agent 3 -> Risk -> Paper Execution -> Thesis -> Ledger -> Dashboard.
- **Idempotency**: Duplicate dates are skipped.
