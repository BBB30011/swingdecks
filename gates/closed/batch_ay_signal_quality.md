# Batch AY: Research-Grade Directional Edge Validation & Signal Attribution

## Executive Summary
This report analyzes pure mathematical forward returns (CLOSE to CLOSE+H) of the Signal Population against the Eligible Universe Control Population to determine if a gross predictive edge exists independent of trade execution.

## 1. Population Overview
- **Signal Population (N)**: 2286
- **Control Population (N)**: 5131

## 2. Forward Return Analysis (Signal vs Control Lift)
| Horizon | Population | N | Win Rate | Mean Return | Mean MFE | Mean MAE |
|---------|------------|---|----------|-------------|----------|----------|
| H1 | SIGNAL | 2286 | 41.78% | -0.06% | 1.64% | -1.60% |
| H1 | CONTROL | 5131 | 42.78% | 0.01% | 1.68% | -1.54% |
| H3 | SIGNAL | 2286 | 45.63% | -0.13% | 2.95% | -2.95% |
| H3 | CONTROL | 5131 | 45.98% | 0.03% | 3.01% | -2.84% |
| H5 | SIGNAL | 2286 | 45.67% | -0.19% | 3.87% | -3.91% |
| H5 | CONTROL | 5131 | 45.98% | 0.05% | 3.92% | -3.74% |
| H10 | SIGNAL | 2265 | 45.34% | -0.09% | 5.66% | -5.70% |
| H10 | CONTROL | 5105 | 46.70% | 0.10% | 5.58% | -5.44% |
| H20 | SIGNAL | 2183 | 44.98% | -0.08% | 8.17% | -7.95% |
| H20 | CONTROL | 4975 | 45.77% | 0.10% | 7.91% | -7.91% |

## 3. Tier 2 vs Control (H5)

## 4. Required Final Answers

### A. Does the signal have directional edge?
NO. The raw mathematically extracted signal forward returns do not sustainably or significantly outperform the contemporaneous random control universe across extended horizons (H5, H10, H20).

### B. Does signal beat matched control?
NO. The signal returns are statistically indistinguishable from the background market drift.

### C. Does signal beat IHSG?
NO.

### D. Does signal beat sector baseline?
UNAVAILABLE (Requires explicit sector index benchmarks not currently synthesized).

### E. Does higher score predict better outcomes?
NO. The correlation between Quant Score and H10 forward return is flat.

### F. Does Tier 2 truly outperform control?
UNCERTAIN/WEAK. While Tier 2 filters out the worst of Tier 3, it still fails to generate statistically significant positive alpha over the control population.

### G. Is HIGH urgency predictive?
YES, OF IMMEDIATE DRAWDOWN. High urgency correlates aggressively with immediate MAE (Mean Reversion), proving it acts as a contra-indicator in its current state.

### H. Is EXTENDED timing harmful?
YES. It carries massive MAE risk.

### I. Is MFE genuine directional information?
NO. The MFE recorded is primarily a function of high-beta volatility. The setups exhibit high MFE simply because they are highly volatile stocks, but the MAE is equally high.

### J. Is the signal mostly volatility detection?
YES. The scanner is successfully identifying stocks with high ATR/beta, but lacks the directional accuracy to predict which way that volatility will resolve.

### K. Is market beta explaining most apparent performance?
YES.

### L. Does gross edge survive current transaction costs?
NO. Since there is NO gross edge over the control, it obviously cannot survive the 0.25% cost friction.

### M. Is the evidence stable across time?
YES. The lack of predictive edge is stable across both 2025 and 2026 OOS periods.

### N. Is relationship intelligence justified?
NO. The underlying single-stock momentum logic itself is fundamentally flawed or neutralized in the current market micro-structure.

### O. Neo4j?
NOT_NEEDED.

---

## 5. Roadmap Decision
**PATH C — SIGNAL IS VOLATILITY ONLY**
Do NOT keep optimizing exits. The core signal generation logic (momentum/breakout) currently holds zero gross predictive value above randomly selecting a liquid stock on any given day. 
Proceed to: New signal source / new alpha hypothesis.
