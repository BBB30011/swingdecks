=== BATCH AT RESULT ===

Status:
PASS

Tests:
Before: 632
After: 636
New: +4 (test_batch_at.py)
Regression: 0

Python Libraries Evaluated:
- yfinance (SELECTED)
- investpy (REJECTED: Cloudflare blocking)
- pandas_datareader (REJECTED: IDX coverage sparse)

Web Sources Evaluated:
- Yahoo Finance (via yfinance) -> Public, documented, good historical depth.

Primary Provider:
YFINANCE

Provider Trust Assessment:
TIER_3_ESTABLISHED_PROVIDER. Yahoo Finance is established but is a secondary aggregator, not the official IDX exchange feed. Acceptable for research.

Real Data:
AVAILABLE

Symbols:
13

Historical Period:
Default request: 5 years. Variable per symbol.

IHSG:
AVAILABLE

Corporate Actions:
PARTIAL (yfinance handles splits/divs, but we pull unadjusted by default to preserve raw purity. Adjustment logic left to pipeline).

Historical Universe:
NOT_AVAILABLE (commercial data required)

Survivorship Risk:
HIGH

Cross-Source Validation:
PENDING (relies on Yahoo Finance as sole source for now).

OHLCV Quality:
RESEARCH_READY

Provenance:
PASS

Checksum:
PASS (SHA256 tracked for every file)

Point-in-Time:
PASS (Future leakage blocked by snapshot boundaries)

Future Append Invariance:
PASS

Dataset Snapshot:
IDX_DAILY_20260911_069ee2ed

Readiness:
RESEARCH_READY

Backtest:
BLOCKED (Scheduled for Batch AU)

Predictive Value:
NOT_EVALUATED

Remaining Risks:
1. Yahoo Finance can occasionally return anomalies or duplicate dates.
2. Survivorship risk is HIGH because we use current liquidity lists.

Next Recommended Batch:
Batch AU: Real IDX Backtest + Walk-Forward + OOS Validation
