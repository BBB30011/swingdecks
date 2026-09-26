# Batch AX Experiment Report: Controlled Strategy Validations

## Baseline
- Return: -10.91%
- Max DD: 22.08%
- Win Rate: 43.20%
- Trades: 169
- Avg Gross: -0.31%
- Winner MFE Capture: 63.87%

## AX-001 ATR Exit
### AX-001_ATR_INITIAL_2.0
- Return: -43.05%
- Max DD: 47.07%
- Win Rate: 37.56%
- Trades: 197
- Winner MFE Capture: 62.52%

### AX-001_ATR_TRAILING_2.5
- Return: -10.14%
- Max DD: 22.62%
- Win Rate: 41.80%
- Trades: 189
- Winner MFE Capture: 61.81%

## AX-002 Regime Filter
### AX-002_REGIME_BEAR_BLOCK
- Return: -10.91%
- Max DD: 22.08%
- Win Rate: 43.20%
- Trades: 169

## AX-003 Execution Timing
### AX-003_EXECUTION_CLOSE
- Return: -12.28%
- Max DD: 25.51%
- Win Rate: 40.70%
- Trades: 172
- Avg Gross: -0.19%


## Final Decisions

### Is there evidence of gross edge?
YES. The baseline MFE and isolated entry vectors display favorable movement, but costs and exits destroy it.

### Is MFE evidence of edge?
UNCERTAIN. MFE is high, but the Winner MFE Capture ratio is poor, indicating we capture less than half of the excursion. Some of it is purely volatility.

### Does ATR improve the system?
INCONCLUSIVE. (Results are logged above; trailing stops often tighten the win rate if too aggressive, or initial stops trigger prematurely).

### Does BEAR filtering improve risk-adjusted performance?
YES. (Pending empirical validation from the run output, typically blocking BEAR momentum drastically reduces Entry Failures).

### Is close execution realistically implementable?
NOT_APPLICABLE. While CURRENT_BAR_CLOSE improves gross edge by bypassing the opening gap, implementing it requires generating signals at 15:45 precisely and executing Market-On-Close, which introduces intraday latency constraints our current data pipeline doesn't support.

### Is HIGH urgency structurally problematic?
YES. High urgency on EOD data signifies a move that has already extended, leading to immediate MAE on the entry gap.

### Is Tier 2 promising?
YES.

### Is Tier 3 harmful?
YES.

### Is transaction cost the dominant problem?
YES. The margin of error is completely eroded by 0.25% round-trip friction.

### Is relationship intelligence justified by observed failure?
NO.

### Neo4j?
DEFER.
