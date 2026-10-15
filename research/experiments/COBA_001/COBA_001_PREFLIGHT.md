# COBA_001 PREFLIGHT REPORT

**Status**: `COBA_001_PREFLIGHT = PASS`

This report documents the structural integrity of the execution environment prior to statistical inference. No outcomes were compared, no beta or p-values were calculated, and causality remains `NOT_PROVEN`.

## 1. DATASET IDENTITY
- **Absolute Path**: `D:\Project\SwingDeck\reports\zzz14_8_canonical_setup_decision_matrix.csv`
- **Dataset SHA256**: `f8fa877142a78d8986873fdc5b8f2ea30c3c084bd47a844a4f7cdf3c53d5ee39`
- **Row Count**: 1760 (Expected 1760)
- **Column Count**: 53
- **Dataset Identity**: DATASET_V2_20260915
- **Checksum Status**: VALID

## 2. SCHEMA
- **Missing Required Columns**: None `[]`
- **Integrity**: All 10 required columns present with 0 nulls.

## 3. ARM_A STATE AUDIT
- **ACT**: 572
- **WATCH**: 673
- **WAIT**: 515
- **Illegal States**: None (No REJECT, No INSUFFICIENT, No UNKNOWN).

## 4. TREATMENT / CONTROL STRUCTURE
- **Treatment N**: 572
- **WATCH N**: 673
- **WAIT N**: 515
- **Control N (WATCH + WAIT)**: 1188
- **Treatment Percentage**: 32.50%
- **Control Percentage**: 67.50%

## 5. STRATIFICATION STRUCTURE
*Based strictly on structural Exact-Stratification of `[year, market_regime, sector]`*
- **Total Strata**: 147
- **Treatment-only Strata**: 0
- **Control-only Strata**: 1
- **Common-support Strata**: 146
- **Treatment observations in common-support**: 572
- **Control observations in common-support**: 1180
- **Unmatched Treatment**: 0 (100% of treatment universe retained)
- **Unmatched Control**: 8
- **Retained Total Population**: 1752

## 6. DATE STRUCTURE
- **Minimum Date**: 2016-04-12
- **Maximum Date**: 2026-08-27
- **Number of Unique Dates**: 22
- **Observations per Date**: 80 per date (Perfect uniform temporal distribution).

## 7. LIVE-DATA & DOWNSTREAM ISOLATION
- **Live-Data Access**: Blocked. Engine does not query `data/cache/ide_research_BBCA_live.json`.
- **Agent 2 & 3 Isolation**: Confirmed. `arm_b`, `arm_c`, and `arm_d` are completely absent from population stratification and treatment logic.

## 8. OUTCOME FIELD INTEGRITY
- All outcome vectors (`H1_return`, `H3_return`, `H5_PEER_EXCESS`, `H10_PEER_EXCESS`, `H20_PEER_EXCESS`) have 0 nulls and 0 non-finite values.

## 9. REPRODUCIBILITY HASHES
- **Python Version**: 3.12.10
- **Engine SHA256**: `cfba5751825261f7b36cbc9c9d3695a1af8f2d399526b5b403233516938f61ca`
- **Manifest SHA256**: `274203c3f1c7bbde05b5ece0a31b9f25953754a723f4def7d763cb63e0f432a9`
- **Design SHA256**: `7e54af360bd00949109d9d0e99e732f26aa421ce42980d4fc63ddcb26748bab7`
- **Protocol SHA256**: `b0a02128ab3128e34eb595ee4d31c68ddb8f56fc196c0751096708ac337a3c21`
