# CONTROL PLANE SOURCE MAP
The Control Plane derives its read-only snapshot strictly from:
- `state/audit/ledger.jsonl` (Canonical events, traces, decisions, blocks)
- `runtime/continuous_desk_daemon_state.json` (Daemon health and processed dates)
- `DriftObservatory` Engine (Drift matrices)
No parallel source of truth is created.
