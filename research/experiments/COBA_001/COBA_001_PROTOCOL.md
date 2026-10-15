# COBA_001 PROTOCOL

## 1. PRE-EXECUTION AUDIT
Before running `coba_001_engine.py`, the following conditions must hold:
1. `DATASET_V2_20260915` remains identical and untampered (Verify against canonical hash).
2. The `ide_research_BBCA_live.json` payload remains completely detached from the historical matrices.
3. The exact `COBA_001_MANIFEST.json` and `COBA_001_DESIGN.md` are frozen.

## 2. EXPERIMENT EXECUTION PIPELINE
1. **Data Load**: Load `reports/zzz14_8_canonical_setup_decision_matrix.csv`.
2. **Treatment Assignment**: Mark setups with `arm_a_action == 'ACT'` as `Treatment = 1`. Mark others (`WATCH`, `WAIT`) as `Treatment = 0`.
3. **Stratification Algorithm**: Construct an **EXACT-STRATIFIED COMMON-SUPPORT SAMPLE** using exclusively pre-outcome variables: `[year, market_regime, sector]`. Group by these variables and retain only strata containing both Treatment and Control.
4. **Common Support Documentation**: The execution output MUST document structural support ONLY:
    - Total treatment count
    - Total control count
    - Number of strata
    - Strata with treatment only
    - Strata with control only
    - Strata with both
    - Retained treatment count
    - Retained control count
    - Retained total count
5. **Regression & Inference**: 
    - **Primary Outcome:** `H5_PEER_EXCESS`
    - **Secondary Outcomes:** `H1_return`, `H3_return`, `H10_PEER_EXCESS`, `H20_PEER_EXCESS`.
    - **Primary Inference:** Fit OLS with standard errors clustered on `date`.
    - **Secondary Inference:** Execute Wild Cluster Bootstrap on the treatment coefficient.
    - Record Treatment Beta ($\beta_1$), 95% Confidence Interval, Clustered SE, Clustered p-value, Bootstrap p-value, and Economically Interpretable Effect Magnitude. (MINIMUM_EFFECT_SIZE = NOT_PRE_SPECIFIED).
6. **Report Generation**: Output results to `reports/COBA_001_RESULTS.md` and `reports/coba_001_inference.json`.

## 3. RED TEAM & LEAKAGE CHECKS
- At no point during the script execution should `arm_b`, `arm_c`, or `arm_d` paths be queried or utilized.
- MFE and MAE are allowed **only** as secondary descriptive columns.
- Multiple Testing: Secondary horizon p-values must be reported individually and explicitly labeled as exploratory/secondary comparisons. 
- If primary (OLS) and secondary (Bootstrap) inference disagree, report the disagreement as evidence of inference sensitivity. Do not select the method to force significance.

## 4. STATUS
**FROZEN_READY**. Awaiting execution authorization.
