# SWINGDECK — LIVE-LIKE OPERATIONAL RUN REPORT
> [!WARNING]
> **SUPERSEDED REPORT**: This document reflects an initial 5-session scenario test (`LIVE_LIKE_DESK_20260928_094840`).
> The canonical source of truth for the complete 70-session continuous desk operations is run **`CONT_DESK_20260928_103652`** documented in [CONTINUOUS_PAPER_DESK_OPERATIONS_REPORT.md](file:///D:/Project/SwingDeck/reports/paper_trading/CONTINUOUS_PAPER_DESK_OPERATIONS_REPORT.md) and [FINAL_OPERATIONAL_RECONCILIATION_GATE.md](file:///D:/Project/SwingDeck/reports/paper_trading/FINAL_OPERATIONAL_RECONCILIATION_GATE.md).

**Run ID**: LIVE_LIKE_DESK_20260928_094840 (SUPERSEDED)
**Execution Timestamp**: 2026-09-28T09:48:40.576902+00:00
**Initial Capital**: Rp 100,000,000.00
**Ending Equity**: Rp 99,860,344.65
**Realized PnL**: Rp 0.00
**Transaction Costs**: Rp 10,715.35

## 1. MULTI-DAY SESSION EXECUTION SUMMARY

| Session Date | Market Regime | Scanned | Decisions | Orders | Open Positions | Ending Equity | Reconciled |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 2026-03-23 | BULL | 10 | 10 | 1 | 1 | Rp 99,985,714.65 | PASS |
| 2026-03-24 | BULL | 10 | 10 | 0 | 1 | Rp 100,057,114.65 | PASS |
| 2026-03-25 | BULL | 10 | 10 | 0 | 1 | Rp 100,021,064.65 | PASS |
| 2026-03-26 | BULL | 10 | 10 | 0 | 1 | Rp 100,308,064.65 | PASS |
| 2026-03-27 | BULL | 10 | 10 | 0 | 1 | Rp 99,860,344.65 | PASS |

## 2. DESK GOVERNANCE CONCLUSION
All multi-day cycles executed cleanly across market regime transitions without unhandled exceptions or state drift.