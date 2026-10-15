# MARKET NARRATIVE ARCHITECTURE
The system employs a read-only presentation pipeline.
1. `DecisionTraceAPI`: Reads events from `state/audit/ledger.jsonl`. Reconstructs `AuditedDecisionTrace` with linked evidence.
2. `MarketNarrativeEngine`: Takes the structured trace and generates human-readable text respecting the Language Firewall.
3. `Command Center (Dashboard)`: Embeds the Narrative Engine and provides interactive access to the trace without mutating state.
