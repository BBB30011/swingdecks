# DECISION REPLAY SOURCE MAP

| SOURCE | FIELD | MEANING | TIMESTAMP | PIT RULE | READ METHOD | VALIDATION |
|---|---|---|---|---|---|---|
| `ledger.jsonl` | `MARKET_REGIME` | Overall market state | `timestamp` | `< T` | Direct scan | Monotonicity Check |
| `ledger.jsonl` | `AGENT_1_QUANT` | Quant Candidate | `timestamp` | `< T` | Direct scan | Monotonicity Check |
| `ledger.jsonl` | `AGENT_2_INTEL` | Intelligence Info | `timestamp` | `< T` | Direct scan | Monotonicity Check |
| `ledger.jsonl` | `AGENT_3_COMMITTEE`| Action | `timestamp` | `== T` | Direct scan | Event matching |
| `ledger.jsonl` | `PORTFOLIO` | Position Update | `timestamp` | `> T` | Direct scan | Post-decision only |
