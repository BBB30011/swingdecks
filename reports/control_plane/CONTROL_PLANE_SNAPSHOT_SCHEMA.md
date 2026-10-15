# CONTROL PLANE SNAPSHOT SCHEMA
- `snapshot_id`: Unique identifier (e.g., `SNAP_<timestamp>`).
- `generated_at`: UTC ISO timestamp.
- `system_status`: Evaluated system health.
- `daemon`, `market`, `agents`, `positions`, `thesis`, `drift`, `accounting`, `alerts`, `recent_events`, `what_changed`.
All fields are immutable upon generation.
