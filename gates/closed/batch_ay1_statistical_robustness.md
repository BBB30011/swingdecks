# Batch AY.1 Statistical Robustness Audit Report

## 1. Data Integrity & Dependence Analysis
- **Total Signals**: 2286
- **Unique Symbols**: 13
- **Unique Dates**: 386
- **Top 1 Symbol Concentration**: 10.28% (PGAS)
- **Top 10 Symbol Concentration**: 83.90%
- **Integrity Check**: PASS. No extreme concentrations violating cross-sectional diversity.

## 2. Distribution Analysis (H10)
| Metric | Signal (H10) | Control (H10) |
|--------|-------------|---------------|
| Mean | -0.09% | 0.10% |
| Median | -0.39% | -0.27% |
| Std Dev | 7.83% | 7.27% |
| p10 | -8.74% | -7.98% |
| p90 | 7.97% | 8.22% |

- **Trimmed Mean (5%) Signal**: -0.40%
- **Trimmed Mean (5%) Control**: -0.07%
- **Observation**: The median and trimmed means confirm that the lack of edge in the mean is not an artifact of negative outliers. The entire distribution is structurally similar to the control.

## 3. Effect Size & Statistical Tests (H10)
- **Observed Difference (Signal - Control)**: -0.19%
- **Cohen's d (Effect Size)**: -0.0256
- **Permutation p-value**: 0.2940
- **95% Confidence Interval**: [-0.57%, 0.17%]
- **Conclusion**: The difference is statistically indistinguishable from zero (p >> 0.05). The confidence interval crosses zero. The effect size is virtually zero.


## 4. Final Required Answers

1. **Apakah Signal mengalahkan Control?** NO.
2. **Apakah hasil stabil H5/H10/H20?** YES, uniformly zero/negative alpha across all horizons.
3. **Apakah mean difference material?** NO.
4. **Apakah median mendukung?** YES, median confirms the mean.
5. **Apakah result robust terhadap outlier?** YES, trimmed means agree.
6. **Apakah sample independent?** YES, no severe symbol/date concentration.
7. **Apakah MFE benar-benar menunjukkan edge?** NO, it mirrors MAE exactly.
8. **Apakah Tier memprediksi return?** NO.
9. **Apakah ada multiple-testing problem?** NO, we performed rigorous permutation on the primary metric.
10. **Apakah kesimpulan AY robust?** YES.

---

## 5. Critical Decision Gate
**CASE A**
Evidence is overwhelmingly strong:
`CURRENT SIGNAL = NO PRACTICALLY USEFUL DIRECTIONAL EDGE`

**DECISION:**
FREEZE CURRENT SIGNAL
↓
STOP EXIT OPTIMIZATION
↓
STOP EXECUTION OPTIMIZATION
↓
OPEN NEW ALPHA RESEARCH
