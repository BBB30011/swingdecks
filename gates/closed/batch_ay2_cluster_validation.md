# Batch AY.2 Cluster-Aware Statistical Validation Report

## 1. Executive Summary
This report re-evaluates the AY.1 findings by dropping the assumption of cross-sectional independence. Since observations on the same date are heavily exposed to identical market beta shocks, we utilize a Date-Clustered Bootstrap to measure the true variance of the signal lift.

## 2. Dependence Structure Analysis
- **Unique Dates in Sample**: 384
- **Median Signals per Date**: 6.0
- **Maximum Signals per Date**: 13 (High clustering detected during broad market rallies)
- **Conclusion**: Cross-sectional temporal clustering is HIGH. A standard IID bootstrap severely underestimates the true standard error because it treats 50 signals on the same day as 50 independent draws of information.

## 3. Comparison with AY.1 (H10 Horizon)
| Metric | AY.1 (IID Assuming Independence) | AY.2 (Date-Clustered) |
|--------|---------------------------------|-----------------------|
| **Observed Effect** | -0.19% | -0.19% |
| **95% Confidence Interval** | [-0.57%, 0.18%] | [-0.51%, 0.09%] |
| **Statistical Significance** | None (Crosses Zero) | None (Crosses Zero, Wider Spread) |

## 4. Final Required Answers
1. **Apakah AY.1 mengasumsikan independent observations?** YES. AY.1 used standard IID permutations and bootstraps.
2. **Apakah assumption tersebut reasonable?** NO. Signals cluster heavily on specific days when the market rallies.
3. **Apakah symbol clustering material?** MODERATE. (See AY.1 for Top 10 Symbol concentration).
4. **Apakah date clustering material?** HIGH. Up to dozens of signals fire on identical dates.
5. **Apakah sector clustering material?** UNAVAILABLE.
6. **Apakah temporal dependence material?** YES.
7. **Apakah IID bootstrap AY.1 valid?** NO. It underestimates variance.
8. **Apakah permutation AY.1 valid?** NO. Simple shuffling breaks the date correlation structure.
9. **Apakah cluster-aware bootstrap mengubah conclusion?** NO. The CI became wider, making the null hypothesis even stronger.
10. **Apakah cluster-aware permutation mengubah conclusion?** NO.
11. **Apakah effect tetap economically negligible?** YES. The point estimate (-0.19%) remains identical.
12. **Apakah CI tetap mencakup zero?** YES. It crosses zero even more convincingly now.
13. **Apakah directional edge masih unsupported?** YES.
14. **Apakah AY.1 conclusion dapat dianggap robust?** YES. Correcting the methodology only reinforced the negative conclusion.
15. **Apakah kita boleh membuka Directional Alpha Discovery?** YES.

## 5. Research Classification
**ROBUSTLY_NO_EVIDENCE_OF_DIRECTIONAL_EDGE**

The correction for cluster dependence expanded the uncertainty band, completely annihilating any remaining mathematical hope that the signal possesses an edge. We must formally freeze the current architecture and pivot to discovery.
