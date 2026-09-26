# Batch AU: Real IDX Backtest & Walk-Forward Validation Report

> [!WARNING]
> **SURVIVORSHIP BIAS WARNING**  
> This backtest uses a snapshot of 13 currently liquid IDX symbols. Symbols that were delisted, suspended, or fell out of the liquidity criteria prior to September 2026 are excluded. The performance metrics presented below represent **Predictive Classification Validity** of the signal factors (Opportunity Score, Timing, Tiers) rather than unbiased trade profitability.

## 1. Backtest Configuration
- **Dataset**: `IDX_DAILY_20260911_069ee2ed.json` (13 Symbols)
- **Initial Capital**: Rp 100,000,000
- **Transaction Costs**: 0.15% Commission, 0.1% Slippage
- **Risk Management**: 1.0% max risk per trade, Lot size = 100
- **Execution Model**: Next Bar Open Entry, Fixed/Stop/Target Exit (Stop-First logic)
- **Split Configuration**:
  - Train: 2021-01-01 to 2023-12-31
  - Validation: 2024-01-01 to 2024-12-31
  - Test (OOS): 2025-01-01 to 2026-09-01

## 2. Walk-Forward Out-Of-Sample (OOS) Performance
**Period:** 2025-01-01 to 2026-09-01

- **Total Return:** -10.91%
- **Max Drawdown:** 22.08%
- **Win Rate:** 43.20%
- **Profit Factor:** 0.84
- **Trades Executed:** 169 closed (174 opened, 5 skipped)

## 3. Signal Feature Attribution (OOS)

The following tables evaluate whether our qualitative metadata layers provide actual empirical separation in the market.

### By Opportunity Score
| Score Range | Trades | Win Rate | Profit Factor | Avg Return |
|-------------|--------|----------|---------------|------------|
| 60-69 | 0 | - | - | - |
| 70-79 | 0 | - | - | - |
| 80-89 | 0 | - | - | - |
| 90-100 | 0 | - | - | - |

### By Alert Urgency
| Urgency | Trades | Win Rate | Profit Factor | Avg Return |
|---------|--------|----------|---------------|------------|
| HIGH | 142 | 43.0% | 0.80 | -0.55% |
| MEDIUM | 1 | 100.0% | - | 10.74% |
| LOW | 26 | 42.3% | 1.11 | 0.56% |

### By Signal Tier
| Tier | Trades | Win Rate | Profit Factor | Avg Return |
|------|--------|----------|---------------|------------|
| TIER 1 | 0 | - | - | - |
| TIER 2 | 114 | 43.0% | 0.94 | 0.16% |
| TIER 3 | 55 | 43.6% | 0.67 | -1.30% |

## 4. Robustness Sensitivities

### Sensitivity 1: High Transaction Costs
Simulating +100% impact from slippage and commissions (0.3% Comm, 0.2% Slippage).
- **Original Net Return:** -10.91%
- **Stressed Net Return:** -25.34%
- **Degradation:** 14.44%

### Sensitivity 2: Exclude Top Performer
Testing reliance on single-stock survivorship bias (Removed `UNVR`).
- **Original Net Return:** -10.91%
- **Stressed Net Return:** -24.76%
- **Degradation:** 13.86%

## 5. Conclusion & Integrity Warnings
- `[WARNING]` POSSIBLE_SURVIVORSHIP_BIAS
- `[WARNING]` POSSIBLE_SELECTION_BIAS
- `[WARNING]` NO_OOS_SPLIT
- `[WARNING]` NO_REAL_BROKER_FLOW
- `[WARNING]` NO_MARKET_IMPACT_MODEL

**Next Steps:** Proceed to cross-source validation and execution model refinement in subsequent batches.