# SWINGDECK — POINT-IN-TIME (PIT) & DATA ISOLATION REPORT
**Firewall Policy**: `DATA_TIMESTAMP <= SIMULATION_TIMESTAMP`

## 1. CONTAMINATION PREVENTION CONTROLS
1. **Future Bar Rejection**: Any market bar with a timestamp ahead of current simulation time is rejected with `DataValidationError`.
2. **Lookahead News Prohibition**: Agent 2 intelligence retrieval is strictly scoped to historical knowledge prior to the decision timestamp.
3. **Zero Outcome Leakage**: Post-trade lessons and labels cannot be queried during historical candidate selection.