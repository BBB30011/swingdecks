# CONTROL PLANE FAILURE REPORT
- Ledger missing: `WAITING_FOR_DATA`
- Ledger corrupted (JSON error): Silent skip of invalid lines, parses valid ones.
- Daemon state missing: Defaults to empty dict.
- PIT/Replay failure: Escalates immediately to `BLOCKED`.
