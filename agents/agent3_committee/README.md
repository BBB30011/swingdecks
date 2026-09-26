# Agent 3: Investment Committee & Risk Engine

> **NOTE:** This agent operates strictly under the core constraints defined in the master constitution: [AGENTS.md](../../AGENTS.md).
Agent 3 acts as the final decision maker before an order would be executed. It acts as an integration point for:
1. Agent 1 (Quant Context)
2. Agent 2 (Market Intelligence, Research Evidence)
3. Red Team Analyzer
4. Current Portfolio Risk State

## Key Capabilities

### 1. Risk Engine Gates
The risk engine imposes strict, deterministic constraints. Even if the thesis is incredibly bullish, it will **BLOCK** the trade if any of the following gates fail:
- **Risk per Share / Reward Structure**: Entry, stop, and target must form a valid trade (stop < entry < target).
- **Minimum Risk/Reward (R/R)**: Defaults to 2.0. Trades failing this are blocked.
- **Data Quality**: Rejects STALE_DATA, INSUFFICIENT_DATA, or INVALID.
- **Evidence Quality**: Blocks if research is incomplete (`INSUFFICIENT`) or Red Team triggers `BLOCK`.
- **Contradiction**: Blocks if there are unresolved `HIGH` severity contradictions.
- **Speculation**: Blocks if the thesis depends heavily on speculative claims instead of facts.
- **Confidence**: Rejects if confidence drops below the required threshold (default: 70).

### 2. Position Limits & Portfolio Risk
The engine dynamically sizes positions using a fixed fractional risk approach:
- Allowed Risk = Portfolio Capital * Max Single Position Risk (e.g., 0.5%).
- Position Shares = Allowed Risk / Risk Per Share.
- Converts to standard **IDX Lots (1 lot = 100 shares)**.
- If total portfolio risk exceeds `max_portfolio_risk` (e.g., 2.0%), the trade is blocked.
- Caps maximum open positions (e.g., 5).

### 3. Action Decision Matrix
Outputs an `ACTION` and a `RISK_STATE`:
- **ACTION**: `BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID`
- **RISK_STATE**: `GREEN`, `YELLOW`, `RED`

### 4. Decision Trace
Every decision generates a `DecisionTrace` that precisely details which gates passed and which failed, providing auditability for "Why BUY?" or "Why blocked?".

## Synthetic-Only Limitation
Because there is no real-world integrated historical IDX dataset (`REAL_HISTORICAL_DATASET_NOT_PROVISIONED`), Agent 3 is strictly restricted to **SYNTHETIC_VALIDATION_ONLY**. It does not place live trades, issue real market recommendations, or use real broker APIs.
