# SWINGDECK — LIVE-LIKE DESK ARCHITECTURE & OPERATING MODEL
**Architecture State**: STRICT 3-AGENT RUNTIME | PAPER-ONLY ISOLATION

## 1. THREE RUNTIME AGENTS
1. **Agent 1 (Quant & Market Scanner)**: Scans universe, computes momentum, trend, liquidity, candidate ranking. Strictly no fundamental/news reasoning.
2. **Agent 2 (Market Intelligence + Red Team)**: Analyzes why assets are moving, evaluates catalysts, detects contradictions, issues Red Team verdict (`PASS`, `REWORK`, `BLOCK`). Strictly no order execution or position sizing.
3. **Agent 3 (Investment Committee + Risk)**: Sole final decision maker. Evaluates risk, portfolio limits, sizing, and issues decisions (`BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID`, `INSUFFICIENT`).

## 2. DESK OPERATING LOOP
```text
MARKET DATA -> DATA QUALITY GATE -> REGIME DETECTOR -> AGENT 1 -> CANDIDATE QUEUE ->
AGENT 2 (RED TEAM) -> AGENT 3 (COMMITTEE) -> RISK GATE -> PAPER ORDER ->
SIMULATED EXECUTION -> POSITION STATE MACHINE -> THESIS MONITORING -> EXIT ENGINE ->
P&L RECONCILIATION -> LEARNING LEDGER -> AUDIT TRAIL
```

## 3. STRICT PAPER ISOLATION
- `LIVE_EXECUTION = DISABLED`
- `PAPER_EXECUTION = ENABLED`
- Automated fail-closed lock upon any discovery of broker API keys or live endpoints.