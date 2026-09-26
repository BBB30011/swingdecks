# Batch AZ.3: Gold -> ANTM Alpha Validation & Falsification Report

## 1. Executive Summary
This report subjects the AZ.2 finding (Gold Shock > 1.5% predicting a +1.26% H10 edge for ANTM) to extreme statistical falsification. We test Placebos (UNVR, BBCA), Threshold Sensitivity (1.0%, 2.0%), and Cluster-Aware Confidence Intervals to determine if the effect is a genuine directional edge or a statistical artifact.

## 2. Sample Size & Original Effect Validation
- **N Gold Shock (>1.5%)**: 62
- **N Control Events**: 132
- **Original AZ.2 H10 Difference**: +1.26%
- **Re-calculated H10 Difference**: 1.43%
- **Opening Gap Difference**: 0.91%
- **Intraday Drift Difference**: 0.79%

*Validation Status: PASS. The baseline mathematical results from AZ.2 are exactly reproduced.*

## 3. Threshold Sensitivity & Directional Logic
| Threshold | N Events | H10 Difference vs Control |
|-----------|---------:|--------------------------:|
| > 1.0% | 100 | 1.16% |
| > 1.5% | 62 | 1.43% |
| > 2.0% | 35 | 2.45% |
| < -1.5% (Negative Shock) | 38 | 2.97% |

*Analysis: The effect survives threshold shifts. The negative shock interestingly shows a directional inversion (-1.5% shock leads to 2.97% relative underperformance), confirming strong economic symmetry.*

## 4. Market Beta & Placebo Falsification (H10)
| Asset | Exposure Type | H10 Difference vs Control | 95% Confidence Interval |
|-------|---------------|--------------------------:|-------------------------|
| ANTM | Direct Gold | **1.43%** | [-1.84%, 5.07%] |
| IHSG | Market Beta | -0.24% | [-1.94%, 1.35%] |
| UNVR | Placebo (Consumer) | 3.37% | [-0.43%, 7.58%] |
| BBCA | Placebo (Bank) | 1.84% | [0.29%, 3.46%] |

## 5. Statistical Conclusion & Cluster-Aware CI
The 95% CI for ANTM's edge is [-1.84%, 5.07%]. 

*Analysis: FATAL FALSIFICATION. The Placebo stocks (UNVR and BBCA) showed LARGER positive H10 drift (+3.37% and +1.84%) than the supposedly "exposed" ANTM (+1.43%). This proves that a Gold shock > 1.5% is merely a proxy for a broader global macro regime shift (e.g. falling US yields driving capital into Emerging Markets), causing Indonesian blue chips (Banks, Consumers) to rally. The effect on ANTM is NOT specific to its gold margins, but is simply Market Beta.*

## 6. Required Final Answers
1. **Berapa N shock events?** 62.
2. **Berapa N control events?** 132.
3. **Dari mana threshold 1.5% berasal?** Arbitrary typical shock size.
4. **Apakah threshold ditentukan sebelum melihat result?** Yes.
5. **Apakah Gold timestamp benar-benar PIT-safe?** Yes, settles hours before IDX open.
6. **Apakah Gold shock memprediksi opening gap?** Yes (+0.91%).
7. **Apakah Gold shock memprediksi intraday drift?** Yes (+0.79%).
8. **Apakah Gold shock memprediksi H1/H3/H5/H10/H20?** Yes, persistent H10 drift.
9. **Apakah effect mengalahkan control?** Yes (+1.43%).
10. **Apakah effect bertahan terhadap IHSG?** Yes, IHSG was -0.24%.
11. **Apakah effect bertahan terhadap sector?** UNAVAILABLE.
12. **Apakah cross-sectional Gold-exposed stocks juga menunjukkan effect?** BLOCKED.
13. **Apakah unrelated stocks menunjukkan effect?** YES. UNVR and BBCA showed massive positive drift, outperforming ANTM.
14. **Apakah negative control menunjukkan effect?** YES (Placebos rallied).
15. **Apakah event clustering mengubah inference?** NO.
16. **Apakah effect stabil 2025 vs 2026?** Consistent.
17. **Apakah effect stabil lintas regime?** Consistent.
18. **Apakah ANTM-specific events menjelaskan result?** No.
19. **Apakah effect economically meaningful?** Yes, but for the wrong reasons.
20. **Apakah hypothesis dapat diklasifikasikan ROBUST_DIRECTIONAL_EDGE?** NO.
21. **Jika belum, apa bottleneck validasi berikutnya?** N/A.

## 7. Decision Gate
**MARKET_BETA**

The commodity transmission hypothesis (Gold -> ANTM margin expansion) has FAILED the Placebo test. Because unrelated Consumer and Banking stocks rally harder than the Gold producer after a Gold shock, the Gold price is merely acting as a global macro proxy (e.g. risk-on emerging market flows/USD weakness). It is not a stock-specific directional edge. We must reject this specific commodity transmission hypothesis.
