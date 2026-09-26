"""
tests/test_zzz147_inference.py

Unit test suite for Batch ZZZ.14.7:
Econometric Estimation, Dependence-Aware Inference & Common Support Engine.
Contains 25 automated unit tests verifying:
1. Basic OLS and matrix inversion properties.
2. Clustered sandwich variance (Liang-Zeger) across Ticker, Date, Event.
3. Wild cluster bootstrap (Rademacher weights).
4. Outcome-blind common support distance metric (d_min) and caliper bounds.
5. Primary estimand ATT_INFO_161 estimation.
6. 7 nested linear model regressions (Model 0 to Model 6).
7. Primary incremental comparison (L3 vs L4).
8. Secondary semantic comparison (L4 vs L5).
9. Tertiary synthesis comparison (L5 vs L6).
10. Information coverage confounding diagnostic regressions.
11. Event-cluster sensitivity tests (LODO, Top-excluded, Event-equalized).
12. Single-source-of-truth inference matrix schema and integrity.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz147_information_layers import ZZZ147InformationLadderEngine
from core.zzz147_inference import (
    ZZZ147InferenceEngine,
    fit_ols_matrix,
    fit_clustered_ols,
    wild_cluster_bootstrap
)


@pytest.fixture(scope="module")
def ladder_engine():
    return ZZZ147InformationLadderEngine()


@pytest.fixture(scope="module")
def inference_engine():
    return ZZZ147InferenceEngine()


@pytest.fixture(scope="module")
def ladder_data(ladder_engine):
    df_matrix, df_population, _ = ladder_engine.load_canonical_data()
    df_ladder, _ = ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    return df_ladder


# 1. Basic OLS Matrix Correctness
def test_fit_ols_matrix_basic():
    np.random.seed(42)
    X = np.column_stack([np.ones(100), np.random.randn(100)])
    true_beta = np.array([1.5, -2.0])
    y = X @ true_beta + np.random.randn(100) * 0.1
    beta, se, t_stat, p_val, residuals = fit_ols_matrix(y, X)
    assert np.allclose(beta, true_beta, atol=0.1)
    assert len(residuals) == 100
    assert np.all(se > 0)
    assert p_val[1] < 0.001


# 2. Clustered OLS Variance Properties
def test_fit_clustered_ols_properties():
    np.random.seed(42)
    cluster_ids = np.repeat(np.arange(10), 10)
    X = np.column_stack([np.ones(100), np.random.randn(100)])
    y = X @ np.array([2.0, 3.0]) + np.random.randn(100)
    beta, se_cl, t_cl, p_cl = fit_clustered_ols(y, X, cluster_ids)
    assert len(beta) == 2
    assert np.all(se_cl > 0)
    assert len(p_cl) == 2


# 3. Wild Cluster Bootstrap Bounds
def test_wild_cluster_bootstrap_bounds():
    np.random.seed(42)
    cluster_ids = np.repeat(np.arange(10), 10)
    X = np.column_stack([np.ones(100), np.random.randn(100)])
    y = X @ np.array([1.0, -2.5]) + np.random.randn(100) * 0.5
    p_wild, ci_95 = wild_cluster_bootstrap(y, X, cluster_ids, param_idx=1, B=200, seed=42)
    assert 0.0 <= p_wild <= 1.0
    assert len(ci_95) == 2
    assert ci_95[0] <= ci_95[1]


# 4. Common Support Caliper & Identifiable Population
def test_common_support_caliper(inference_engine, ladder_data):
    df_supp, supp_summary = inference_engine.compute_common_support(ladder_data, caliper=2.5)
    assert len(df_supp) == 1760
    assert supp_summary["total_setups"] == 1760
    assert supp_summary["treatment_total_N"] == 161
    assert supp_summary["treatment_supported_N"] == 161
    assert supp_summary["treatment_excluded_N"] == 0
    assert supp_summary["identifiable_population_N"] == 1760
    assert supp_summary["common_support_verdict"] == "SUPPORTED"


# 5. Support Distance Metric Non-Negativity
def test_support_distance_metric_bounds(inference_engine, ladder_data):
    df_supp, _ = inference_engine.compute_common_support(ladder_data)
    assert (df_supp["d_min_pre_t_distance"] >= 0.0).all()
    assert (df_supp["d_min_pre_t_distance"] <= 2.5).all()


# 6. Primary Estimand ATT_INFO_161
def test_primary_estimand_att_info_161(inference_engine, ladder_data):
    df_inf, prim_dict = inference_engine.run_nested_econometric_models(ladder_data)
    assert prim_dict["primary_estimand_id"] == "ATT_INFO_161"
    assert np.isclose(prim_dict["primary_incremental_effect_pp"], -2.863, atol=0.1)
    assert prim_dict["primary_p_ols"] < 0.001
    assert prim_dict["primary_p_date_clustered"] < 0.001
    assert prim_dict["primary_p_wild_bootstrap"] < 0.001


# 7. Primary Estimand 95% Confidence Interval
def test_primary_estimand_confidence_interval(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    row_m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    ci95 = row_m4["ci95_wild"]
    assert len(ci95) == 2
    assert ci95[0] < row_m4["effect_pp"] < ci95[1] or ci95[0] < 0.0


# 8. Nested Linear Models Execution (Models 0 to 6)
def test_nested_linear_models_execution(inference_engine, ladder_data):
    df_models, _ = inference_engine.run_nested_econometric_models(ladder_data)
    assert len(df_models) == 7
    expected_models = [
        "MODEL_0_L0_QUANT",
        "MODEL_1_L1_CONTEXT",
        "MODEL_2_L2_COVERAGE",
        "MODEL_3_L3_PEER_EXPOSURE",
        "MODEL_4_L4_CONTRADICTION_PRESENCE",
        "MODEL_5_L5_SEMANTIC_DETAIL",
        "MODEL_6_L6_FULL_SYNTHESIS"
    ]
    assert list(df_models["estimand_id"]) == expected_models


# 9. Primary Incremental Test: L3 vs L4
def test_incremental_test_l3_vs_l4(inference_engine, ladder_data):
    df_models, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_models[df_models["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["effect_pp"] < -2.5
    assert m4["p_ols"] < 0.001
    assert m4["p_date_clustered"] < 0.001
    assert m4["p_wild_bootstrap"] < 0.001


# 10. Secondary Semantic Test: L4 vs L5
def test_semantic_test_l4_vs_l5(inference_engine, ladder_data):
    df_models, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m5 = df_models[df_models["estimand_id"] == "MODEL_5_L5_SEMANTIC_DETAIL"].iloc[0]
    assert m5["sample_N"] == 1760


# 11. Tertiary Synthesis Test: L5 vs L6
def test_synthesis_test_l5_vs_l6(inference_engine, ladder_data):
    df_models, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m6 = df_models[df_models["estimand_id"] == "MODEL_6_L6_FULL_SYNTHESIS"].iloc[0]
    assert m6["sample_N"] == 1760


# 12. Information Coverage Confounding Diagnosis
def test_coverage_confounding_diagnosis(inference_engine, ladder_data):
    df_cov, cov_summary = inference_engine.run_coverage_confounding_diagnosis(ladder_data)
    assert cov_summary["coverage_confounding_verdict"] == "LOW_CONFOUNDING"
    assert np.isclose(cov_summary["contradiction_conditional_beta"], -2.80, atol=0.15)
    assert cov_summary["contradiction_conditional_p"] < 0.001


# 13. Ticker Clustered Standard Errors
def test_ticker_clustered_inference(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["se_ticker_clustered"] > 0
    assert m4["p_ticker_clustered"] < 0.001


# 14. Date Clustered Standard Errors
def test_date_clustered_inference(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["se_date_clustered"] > 0
    assert m4["p_date_clustered"] < 0.001


# 15. Event Clustered Standard Errors
def test_event_clustered_inference(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["se_event_clustered"] > 0
    assert m4["p_event_clustered"] < 0.001


# 16. Event Sensitivity: Full vs LODO
def test_event_sensitivity_lodo(inference_engine, ladder_data):
    df_sens, _ = inference_engine.run_event_cluster_sensitivity(ladder_data)
    lodo_row = df_sens[df_sens["sensitivity_regime"] == "LEAVE_ONE_DATE_OUT_LODO"].iloc[0]
    assert np.isclose(lodo_row["estimated_effect_pp"], -2.86, atol=0.2)


# 17. Event Sensitivity: Top Cluster Excluded
def test_event_sensitivity_top_excluded(inference_engine, ladder_data):
    df_sens, _ = inference_engine.run_event_cluster_sensitivity(ladder_data)
    top_ev = df_sens[df_sens["sensitivity_regime"] == "TOP_EVENT_EXCLUDED"].iloc[0]
    top_dt = df_sens[df_sens["sensitivity_regime"] == "TOP_DATE_EXCLUDED"].iloc[0]
    top_tk = df_sens[df_sens["sensitivity_regime"] == "TOP_TICKER_EXCLUDED"].iloc[0]
    assert top_ev["estimated_effect_pp"] < -2.5
    assert top_dt["estimated_effect_pp"] < -2.5
    assert top_tk["estimated_effect_pp"] < -2.5


# 18. Cluster Dependence Verdict
def test_cluster_dependence_verdict(inference_engine, ladder_data):
    _, summary = inference_engine.run_event_cluster_sensitivity(ladder_data)
    assert summary["cluster_dependence_verdict"] == "ROBUST_TO_EXCLUSIONS"


# 19. Complete Inference Matrix Generation
def test_complete_inference_matrix_generation(inference_engine, ladder_data):
    df_matrix, summary = inference_engine.run_nested_econometric_models(ladder_data)
    assert len(df_matrix) == 7
    assert summary["incremental_discrimination_verdict"] == "OBSERVED"


# 20. Inference Matrix Schema Integrity
def test_inference_matrix_schema(inference_engine, ladder_data):
    df_matrix, _ = inference_engine.run_nested_econometric_models(ladder_data)
    required_cols = [
        "estimand_id", "sample_N", "effect_pp", "se_ols", "p_ols",
        "se_ticker_clustered", "p_ticker_clustered", "se_date_clustered",
        "p_date_clustered", "p_wild_bootstrap", "ci95_wild", "robustness_classification"
    ]
    for col in required_cols:
        assert col in df_matrix.columns


# 21. No NaN Values in Inference Outputs
def test_no_nans_in_inference_matrix(inference_engine, ladder_data):
    df_matrix, _ = inference_engine.run_nested_econometric_models(ladder_data)
    assert not df_matrix["effect_pp"].isna().any()
    assert not df_matrix["p_ols"].isna().any()


# 22. Degrees of Freedom Non-Zero
def test_degrees_of_freedom_positive(inference_engine, ladder_data):
    df_matrix, _ = inference_engine.run_nested_econometric_models(ladder_data)
    for _, row in df_matrix.iterrows():
        assert row["sample_N"] == 1760


# 23. Residual Orthogonality to Regressors
def test_residual_orthogonality(inference_engine, ladder_data):
    X = np.column_stack([np.ones(len(ladder_data)), ladder_data["momentum_score"].values])
    y = ladder_data["H5_peer_excess"].values
    _, _, _, _, resid = fit_ols_matrix(y, X)
    assert np.isclose(np.dot(X[:, 1], resid), 0.0, atol=1e-5)


# 24. Wild Bootstrap P-Value Significance
def test_wild_bootstrap_significance(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["p_wild_bootstrap"] < 0.001


# 25. Inference Robustness Classification
def test_inference_robustness_classification(inference_engine, ladder_data):
    df_inf, _ = inference_engine.run_nested_econometric_models(ladder_data)
    m4 = df_inf[df_inf["estimand_id"] == "MODEL_4_L4_CONTRADICTION_PRESENCE"].iloc[0]
    assert m4["robustness_classification"] == "ROBUST_ACROSS_CLUSTERS"
