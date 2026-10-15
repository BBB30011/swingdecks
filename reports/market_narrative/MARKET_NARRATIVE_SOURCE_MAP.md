# SWINGDECK MARKET NARRATIVE SOURCE MAP

This document maps all canonical sources of truth that power the Market Narrative & Decision Trace Engine.
No duplicate sources of truth are created. The narrative relies entirely on these pre-validated, immutable, point-in-time stores.

| SOURCE | PURPOSE | EVENT TYPES | TIMESTAMP | PIT RULE | IDENTITY | READ/WRITE | CANONICAL STATUS |
|--------|---------|-------------|-----------|----------|----------|------------|------------------|
| `data/parquet/market/*.parquet` | Raw market data and calculated quant features | `MARKET` | `timestamp` column | `timestamp <= T` | Symbol + Date | READ-ONLY | PRIMARY SOURCE |
| `state/audit/ledger.jsonl` | Auditable operational events (Agent 1/2/3 actions, Delta detection, Order processing, Errors) | `SYSTEM`, `DECISION`, `INFORMATION`, `RED_TEAM`, `ORDER`, `EXECUTION` | `timestamp` inside JSON | Appended at `T` | `event_id`, `job_id` | READ-ONLY | PRIMARY SOURCE |
| `runtime/test_loop_state/knowledge/*.json` or `state/knowledge/` | Learning Ledger holding closed trade post-mortem and `exit_delta` | `ACCOUNTING`, `THESIS` | `exit_timestamp` | At Trade Exit | `trade_id` | READ-ONLY | PRIMARY SOURCE |
| `runtime/continuous_desk_daemon_state.json` | System operational status and last processed dates | `SYSTEM` | `last_poll_time` | N/A | Daemon state | READ-ONLY | RUNTIME STATE |
| `runtime/trading_desk_state/delta/market_delta_state.json` | T-1 Market State caching to compute real-time deltas | `MARKET`, `INFORMATION` | Last processed `T` | Bounded by T | Symbol | READ-ONLY | RUNTIME STATE |
| `runtime/trading_desk_state/portfolio.json` (If persistent) | Canonical paper positions, cash, execution history | `POSITION`, `ACCOUNTING` | Current `T` | Snapshot at T | Account ID | READ-ONLY | PRIMARY SOURCE |

## RATIONALE
The narrative engine is strictly a **PRESENTATION MODULE**. It does not generate new events or hypothesize unrecorded rationales. All data is fetched dynamically from the `state/audit/ledger.jsonl` (for timeline and agent deltas) and `data/parquet/market` (for baseline market conditions).
