# DECISION TRACE SCHEMA
The `AuditedDecisionTrace` object consists of:
- `trace_id`: Deterministic hash of symbol and timestamp.
- `symbol`, `decision_timestamp`
- `agent1_observation`, `agent2_intelligence`, `red_team_assessment`, `agent3_decision`
- `market_delta`
- `decision_change`: (NO_CHANGE, UPGRADE, DOWNGRADE, NEW_ACTION, ACTION_CHANGED)
- `pit_status`: Enforced via timestamp validation.
- `source_completeness`: (COMPLETE, PARTIAL, NOT_AVAILABLE)
- `evidence_refs`: Array of canonical event IDs.
