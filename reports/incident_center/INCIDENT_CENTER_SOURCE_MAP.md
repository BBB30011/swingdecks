# INCIDENT CENTER SOURCE MAP
The Incident Center directly consumes read-only event patterns from:
- `ControlPlaneSnapshot`
- `state/audit/ledger.jsonl`
No parallel internal state is created. State is derived deterministically at runtime.
