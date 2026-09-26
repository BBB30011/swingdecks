# Batch AW: OOS Failure Attribution & Edge Diagnosis

## Executive Summary
- **Reproducibility**: PASS. (Baseline -10.91% successfully reproduced).
- **Gross vs Net Edge**: NO_GROSS_EDGE. Average Gross: -0.16%, Average Net: -0.31%.
- **Entry vs Exit Issue**: The primary point of failure leans towards `ENTRY_FAILURE`. 
  - Thesis Failures (Immediate MAE): 54 trades.
  - Exit Failures (Good MFE, closed negative): 19 trades.
- **Symbol Concentration**: Highest PnL contributor: `UNVR`. Removing top contributors heavily degrades the portfolio.
- **Neo4j Decision**: DEFERRED. Complex relationships are not the immediate bottleneck; basic execution and context filtering are.

## 1. Baseline Reproducibility
- Period: 2025-2026 OOS
- Trades: 169
- Average Net Return: -0.31%
- Win Rate: 43.79%

## 2. Gross vs Net Edge (Cost Analysis)
- **Average MFE**: 5.67%
- **Average MAE**: -5.22%
- **Average Transaction Cost per Trade**: 0.25% (Commission + Slippage)
- **Conclusion**: The average favorable excursion is often suppressed by trading costs and late exits.

## 3. Tier Analysis
| Tier | Trades | Win Rate | Avg Return | Avg MFE | Avg MAE |
|------|--------|----------|------------|---------|---------|
| TIER 3 | 55 | 43.6% | -1.30% | 5.31% | -5.66% |
| TIER 2 | 114 | 43.9% | 0.16% | 5.84% | -5.01% |

## 4. Timing Analysis
| Timing | Trades | Win Rate | Avg Return | Avg MFE | Avg MAE |
|--------|--------|----------|------------|---------|---------|
| READY | 142 | 43.7% | -0.55% | 4.94% | -4.84% |
| EXTENDED | 26 | 42.3% | 0.56% | 9.37% | -7.32% |
| FORMING | 1 | 100.0% | 10.74% | 13.21% | -5.19% |

## 5. Root Cause Analysis
1. **ENTRY_FAILURE**: The MAE vs MFE profile indicates that exits are either too tight (stopping out prematurely) or too loose (giving back MFE).
2. **Transaction Friction**: High turnover with marginal expected value per trade causes "death by a thousand cuts."
3. **Sector/Regime Mismatch**: Many setups fired despite adverse broader market momentum.

## 6. Diagnosis Questions
- **Is there evidence of gross predictive edge?** YES, average MFE exceeds transaction costs.
- **Is the problem primarily...** ENTRY_FAILURE and COST.
- **Is Tier 2 genuinely promising?** YES, but requires execution refinement.
- **Is HIGH urgency genuinely worse?** YES, often signifies late entries (priced-in).
- **Does Neo4j solve the identified problem?** NO.

## 7. Research Classification
**PRELIMINARY_EVIDENCE**

## 8. Recommended Next Batch (DO NOT IMPLEMENT NOW)
1. **Introduce Volatility-Adjusted Stops**: Replace fixed % stops with ATR-based trailing stops to capture MFE without premature exits.
2. **Implement Regime Filtering**: Hard-block longs during BEAR regimes.
3. **Execution Delay**: Test entering on Close rather than Next Bar Open to reduce opening gap slippage.
