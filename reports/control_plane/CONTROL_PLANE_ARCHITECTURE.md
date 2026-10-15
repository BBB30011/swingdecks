# CONTROL PLANE ARCHITECTURE
- **`core/control_plane.py`**: Aggregator module that constructs a point-in-time `ControlPlaneSnapshot`.
- **`dashboard/app.py`**: Re-uses the snapshot to populate the "OPERATIONAL CONTROL PLANE" view.
- **Fail-Closed Principle**: If data is missing or corrupted, the snapshot degrades status gracefully rather than failing completely or fabricating data.
