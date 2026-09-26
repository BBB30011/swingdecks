# Paper Position Monitoring & Learning

This document describes the design of the Paper Position Lifecycle and Knowledge Learning module.

## Core Concepts

**Paper Positions**: Virtual representations of market exposure. There is NO connection to a real broker. Positions act as simulation units designed to test the system's ongoing thesis management logic.
- States: `PENDING` -> `OPEN` -> `CLOSED` -> `CANCELLED`
- Constraints: Only one `OPEN` or `PENDING` position per symbol at a time (Duplicate Protection).

**Position Monitor**: Monitors active open positions on every tick. Computes material trigger levels (LOW, MEDIUM, HIGH, CRITICAL). Generates `PositionMonitorEvent`s but does NOT directly sell.

**Exit Engine**: Consumes position state and market context to deterministically recommend an exit action based on priority:
1. `DATA_INVALID`: E.g., incoming stream has severe gaps or NaNs.
2. `THESIS_INVALIDATED`: E.g., fundamental news contradict the initial thesis.
3. `STOP_LOSS`: Reached downside limit.
4. `RISK_RED`: Macro or portfolio risk flag flips to red.
5. `TARGET_REACHED`: Reached profit objective.
6. `TIME_EXIT`: Holding period expiration.

## Portfolio Accounting & Reconciliation

The `PaperPortfolio` handles equity, cash, unrealized/realized PnL, and max drawdown. The `PortfolioReconciliationReport` guarantees that equity = cash + position values at any given point, flagging impossibilities like negative cash.

## Learning Ledger & Knowledge

After a position is closed, it is compiled into a `TradeLesson`.
- Separates *pre-trade features* from *post-trade outcome* (No Hindsight Leakage).
- Extracted into deterministic sets (`successful_setups`, `failures`, `patterns`).
- Pattern extraction allows historical context gathering without utilizing Machine Learning or altering arbitrary thresholds.

## Safety & Security

- **Kill Switch**: The system can PAUSE. In this mode, no new paper positions will open, but active ones will continue to monitor exits.
- **Fail Closed**: In case of invalid market data or process crashes, positions are atomically persisted to disk and recover without fabricating hallucinated fill prices.
- **No Broker API**: The entire flow operates on memory structures and file artifacts.
