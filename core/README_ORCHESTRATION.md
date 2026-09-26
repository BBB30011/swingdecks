# Core Orchestration and Reliability Layer (Batch AC)

This layer acts as the backbone of the Swing Trading AI, ensuring that jobs moving through the pipelines are resilient, auditable, and idempotent.

## Architecture & Lifecycle
Jobs transition through a strictly defined `JobState` machine:
`CREATED -> PROCESSING -> QUANT_READY -> RESEARCH_READY -> RED_TEAM_READY -> COMMITTEE_REVIEW -> RISK_CHECK -> DECISION_READY -> COMPLETED`

If an error occurs, it goes to `RETRY`, and if exhausted, it goes to `FAILED` or `DEAD_LETTER`.

## Key Features
- **Idempotency**: Prevents duplicate processing based on `job_id` and payload `input_hash`. Protects against duplicate trades.
- **Crash Recovery**: Saves intermediate states (Agent 1 -> Agent 2 -> Agent 3) atomically using `.tmp` writes followed by an `os.replace`. Restarting the pipeline resumes from the last successful stage.
- **Retry Policy & Failure Classification**: Distinguishes between `TRANSIENT` (e.g., IO Timeout, retried up to 3 times) and `VALIDATION` or `SECURITY` errors (immediate block/dead letter).
- **Dead Letter Queue**: Logs permanently failed jobs with full context and the original payload for analysis.
- **Audit Ledger**: Append-only `JSONL` file that tracks all stage transitions deterministically. Automatically ignores duplicate logs upon restart.
- **Health Monitor & Kill Switch**: Uses `system_state.json`. If set to `PAUSED` or if corruption is detected, the Orchestrator safely rejects new jobs.
- **Reconciliation**: Inspects queues for orphan `.tmp` files or corrupt `.json` files, emitting a report for manual or automated recovery.
- **Queue Watcher**: Provides a filesystem interface to reliably poll directories, ignoring `.tmp` files.

## Determinism and Safety
- **No Path Traversal**: Rejects job IDs with `../` or other unsafe characters.
- **Synthetic Limitation**: Operates strictly under `SYNTHETIC_VALIDATION_ONLY`.
- **No Secrets in Audit**: Sanitizes payloads before writing to the audit ledger.
