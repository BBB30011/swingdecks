# THESIS MONITORING ARCHITECTURE

- **Data Anchor:** On encountering a `POSITION_OPENED` event, the system immediately snapshots the active intelligence context from `latest_state` and stores it as the "T0" Thesis.
- **Delta Engine:** The Dashboard dynamically calculates `Current Intel - T0 Intel`. It identifies "New Information" and numerical "Contradiction changes".
- **State Machine:** Thesis `STATUS` is derived from Red Team constraints: `0` contradictions = VALID, `>0` = WEAKENING, `>2` = INVALIDATED.
- **Implementation:** Fully integrated in `dashboard/app.py` via `thesis_snapshots` state object.
