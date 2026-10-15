# DECISION REPLAY ARCHITECTURE

**System Component:** Embedded into `dashboard/app.py` as a separate mode ("DECISION REPLAY").
**Data Pipeline:**
1. Parse `ledger.jsonl`.
2. Extract all `AGENT_3_COMMITTEE` / `DECISION_FINALIZED` events.
3. Group by Symbol and Timestamp.
4. On selection, generate a deterministic `REPLAY_ID`.
5. Slice `events` array strictly by `< T` for PRE-DECISION context and `> T` for POST-DECISION outcomes.
6. Display visual UI.
