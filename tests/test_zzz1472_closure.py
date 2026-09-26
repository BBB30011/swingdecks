"""
tests/test_zzz1472_closure.py
==============================
Targeted unit test suite for Batch ZZZ.14.7.2: Final Inference Contract, Cluster Taxonomy & Terminology Closure Gate.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.zzz1472_closure_engine import ZZZ1472ClosureEngine


@pytest.fixture(scope="module")
def closure_engine():
    return ZZZ1472ClosureEngine(scratch_dir="scratch", reports_dir="reports")


@pytest.fixture(scope="module")
def canonical_data(closure_engine):
    df_obs, summary = closure_engine.load_canonical_observation_matrix()
    wb_res = closure_engine.run_wild_cluster_bootstrap_reconstruction(df_obs, B=1000, seed=42)
    ev_tax = closure_engine.audit_event_cluster_taxonomy()
    canonical_obj = closure_engine.generate_canonical_inference_artifact(df_obs, wb_res, ev_tax)
    df_rt = closure_engine.generate_red_team_battery(canonical_obj)
    return {
        "df_obs": df_obs,
        "summary": summary,
        "wb_res": wb_res,
        "ev_tax": ev_tax,
        "canonical_obj": canonical_obj,
        "df_rt": df_rt
    }


def test_primary_sample_size_n1760(canonical_data):
    df_obs = canonical_data["df_obs"]
    assert len(df_obs) == 1760, f"Expected N=1760, got {len(df_obs)}"


def test_contradiction_count_n161(canonical_data):
    df_obs = canonical_data["df_obs"]
    contra_count = int(df_obs["contradiction_indicator"].sum())
    assert contra_count == 161, f"Expected 161 contradictions, got {contra_count}"


def test_control_population_count_n1599(canonical_data):
    df_obs = canonical_data["df_obs"]
    ctrl_count = int((1 - df_obs["contradiction_indicator"]).sum())
    assert ctrl_count == 1599, f"Expected 1599 controls, got {ctrl_count}"


def test_primary_coefficient_reproducibility(canonical_data):
    wb_res = canonical_data["wb_res"]
    assert np.isclose(wb_res["effect"], -2.8622, atol=1e-4), f"Primary beta expected -2.8622, got {wb_res['effect']}"


def test_canonical_estimand_id(canonical_data):
    canonical_obj = canonical_data["canonical_obj"]
    assert canonical_obj["primary_estimand"]["canonical_id"] == "BETA_CONTRADICTION_L3_CONDITIONAL_N1760"


def test_legacy_id_mapping(canonical_data):
    canonical_obj = canonical_data["canonical_obj"]
    assert canonical_obj["primary_estimand"]["legacy_id"] == "ATT_INFO_161_REGRESSION_BETA"
    assert canonical_obj["primary_estimand"]["legacy_status"] == "NON_CANONICAL_TERMINOLOGY_ALIASED"


def test_date_cluster_count_g22(canonical_data):
    wb_res = canonical_data["wb_res"]
    assert wb_res["cluster_count"] == 22, f"Expected 22 date clusters, got {wb_res['cluster_count']}"


def test_event_taxonomy_identity(canonical_data):
    ev_tax = canonical_data["ev_tax"]
    assert ev_tax["canonical_event_cluster_count"] == 3
    assert ev_tax["level_1_taxonomy"]["cluster_count"] == 3
    assert ev_tax["level_2_taxonomy"]["cluster_count"] == 5
    assert ev_tax["small_cluster_limitation"] is True


def test_event_cluster_count_verification(canonical_data):
    canonical_obj = canonical_data["canonical_obj"]
    event_hier = canonical_obj["inference_hierarchy"]["4_event_clustered_sensitivity"]
    assert event_hier["cluster_count"] == 3
    assert event_hier["small_cluster_warning"] is True


def test_wild_bootstrap_seed_and_b(canonical_data):
    wb_res = canonical_data["wb_res"]
    assert wb_res["seed"] == 42
    assert wb_res["B"] == 1000
    assert wb_res["bootstrap_algorithm"] == "WILD_RADEMACHER"


def test_ci_source_identity_bifurcation(canonical_data):
    wb_res = canonical_data["wb_res"]
    normal_ci = wb_res["date_clustered_normal_ci95"]
    perc_ci = wb_res["wild_bootstrap_percentile_ci95"]
    assert np.isclose(normal_ci[0], -3.1605, atol=1e-3)
    assert np.isclose(normal_ci[1], -2.5639, atol=1e-3)
    assert np.isclose(perc_ci[0], -3.1595, atol=1e-3)
    assert np.isclose(perc_ci[1], -2.5800, atol=1e-3)


def test_p_value_source_identity(canonical_data):
    wb_res = canonical_data["wb_res"]
    assert wb_res["wild_bootstrap_p"] < 0.0001
    assert wb_res["date_clustered_normal_p"] < 0.0001


def test_estimator_ci_consistency(canonical_data):
    wb_res = canonical_data["wb_res"]
    beta = wb_res["effect"]
    normal_ci = wb_res["date_clustered_normal_ci95"]
    midpoint = (normal_ci[0] + normal_ci[1]) / 2.0
    assert np.isclose(midpoint, beta, atol=1e-3)


def test_no_outcome_leakage(canonical_data):
    df_obs = canonical_data["df_obs"]
    assert "H5_PEER_EXCESS" in df_obs.columns
    # Check that pre-T features are strictly pre-T
    pre_cols = [c for c in df_obs.columns if c != "H5_PEER_EXCESS"]
    assert len(pre_cols) == 19
    for col in pre_cols:
        assert not col.startswith("post_")
        assert not col.startswith("future_")


def test_small_cluster_warning_flag(canonical_data):
    canonical_obj = canonical_data["canonical_obj"]
    assert canonical_obj["event_taxonomy"]["small_cluster_limitation"] is True
    assert canonical_obj["event_taxonomy"]["inference_designation"] == "SECONDARY_SENSITIVITY_ONLY_NOT_PRIMARY"


def test_ten_red_team_attacks_pass(canonical_data):
    df_rt = canonical_data["df_rt"]
    assert len(df_rt) == 10
    assert (df_rt["status"] == "PASS").all()


def test_dual_run_reproducibility(closure_engine):
    res1 = closure_engine.execute_closure_gate()
    res2 = closure_engine.execute_closure_gate()
    assert res1["wild_bootstrap"]["effect"] == res2["wild_bootstrap"]["effect"]
    assert res1["wild_bootstrap"]["date_clustered_se"] == res2["wild_bootstrap"]["date_clustered_se"]
    assert res1["wild_bootstrap"]["wild_bootstrap_p"] == res2["wild_bootstrap"]["wild_bootstrap_p"]


def test_canonical_json_exists_and_valid(canonical_data):
    json_path = "reports/zzz14_7_2_canonical_inference.json"
    assert os.path.exists(json_path)
    with open(json_path, "r") as f:
        data = json.load(f)
    assert data["classifications"]["ZZZ_14_7_STATUS"] == "CLOSED"
    assert data["classifications"]["ZZZ_14_8_STATUS"] == "ELIGIBLE"
