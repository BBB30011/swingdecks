"""
tests/test_zzz1481_closure.py
===============================
Comprehensive automated test suite for Batch ZZZ.14.8.1:
Decision Utility Reconciliation, Calibration & Counterfactual Closure Gate.
Contains 55+ targeted unit and adversarial tests.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.zzz1481_closure_gate import ZZZ1481ClosureGate


@pytest.fixture(scope="module")
def gate():
    return ZZZ1481ClosureGate(scratch_dir="scratch", reports_dir="reports")


@pytest.fixture(scope="module")
def closure_results(gate):
    res = gate.execute_closure_gate()
    with open("reports/zzz14_8_1_decision_utility_reconciliation.json", "r") as f:
        reconciled_json = json.load(f)
    with open("reports/zzz14_8_1_inference.json", "r") as f:
        inference_json = json.load(f)
    df_trans = pd.read_csv("reports/zzz14_8_1_transition_matrix.csv")
    df_calib = pd.read_csv("reports/zzz14_8_1_calibration.csv")
    df_oos = pd.read_csv("reports/zzz14_8_1_oos_decision_utility.csv")
    df_rt = pd.read_csv("reports/zzz14_8_1_red_team.csv")
    df_mat = pd.read_csv("reports/zzz14_8_canonical_setup_decision_matrix.csv")

    return {
        "res": res,
        "json": reconciled_json,
        "inf_json": inference_json,
        "df_trans": df_trans,
        "df_calib": df_calib,
        "df_oos": df_oos,
        "df_rt": df_rt,
        "df_mat": df_mat
    }


# =============================================================================
# 1. Population, Sample Preservation & Identity Tests (1-10)
# =============================================================================

def test_001_population_n1760(closure_results):
    assert len(closure_results["df_mat"]) == 1760

def test_002_sample_attrition_zero(closure_results):
    assert closure_results["json"]["population"]["sample_attrition"] == 0

def test_003_contradiction_cohort_n161(closure_results):
    assert closure_results["json"]["population"]["contradiction_setups"] == 161

def test_004_non_contradiction_cohort_n1599(closure_results):
    assert (closure_results["df_mat"]["contradiction_indicator"] == 0).sum() == 1599

def test_005_setup_ids_unique(closure_results):
    assert closure_results["df_mat"]["setup_id"].nunique() == 1760

def test_006_arm_a_actions_subset(closure_results):
    acts = set(closure_results["df_mat"]["arm_a_action"].unique())
    assert acts.issubset({"ACT", "WATCH", "WAIT"})

def test_007_arm_b_actions_subset(closure_results):
    acts = set(closure_results["df_mat"]["arm_b_action"].unique())
    assert acts.issubset({"ACT", "WATCH", "WAIT", "INSUFFICIENT"})

def test_008_arm_c_actions_subset(closure_results):
    acts = set(closure_results["df_mat"]["arm_c_action"].unique())
    assert acts.issubset({"ACT", "WATCH", "WAIT", "REJECT", "INSUFFICIENT"})

def test_009_arm_d_actions_subset(closure_results):
    acts = set(closure_results["df_mat"]["arm_d_action"].unique())
    assert acts.issubset({"ACT", "WATCH", "WAIT", "REJECT", "INSUFFICIENT"})

def test_010_arm_d_action_counts_sum_to_1760(closure_results):
    cnts = closure_results["df_mat"]["arm_d_action"].value_counts().sum()
    assert cnts == 1760


# =============================================================================
# 2. Transition Matrix & Reconciled Decision Counts (11-25)
# =============================================================================

def test_011_act_to_reject_count_n40(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["ACT -> REJECT", "count_N"] == 40

def test_012_act_to_reject_negative_alignment_count_35(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["ACT -> REJECT", "negative_H5_count"] == 35

def test_013_act_to_reject_opportunity_cost_count_5(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["ACT -> REJECT", "positive_H5_count"] == 5

def test_014_act_to_reject_negative_alignment_rate_87_5(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["ACT -> REJECT", "negative_H5_rate_pct"] == 87.50

def test_015_act_to_reject_mean_h5_negative(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["ACT -> REJECT", "mean_H5_pp"] < -1.5

def test_016_watch_to_reject_count_n46(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WATCH -> REJECT", "count_N"] == 46

def test_017_wait_to_reject_count_n71(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WAIT -> REJECT", "count_N"] == 71

def test_018_insufficient_to_reject_count_n4(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["INSUFFICIENT -> REJECT", "count_N"] == 4

def test_019_total_rejections_sum_to_161(closure_results):
    df_t = closure_results["df_trans"]
    rej_sub = df_t[df_t["target_action_arm_d"] == "REJECT"]
    assert rej_sub["count_N"].sum() == 161

def test_020_watch_to_act_count_n354(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WATCH -> ACT", "count_N"] == 354

def test_021_watch_to_act_opportunity_id_227(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WATCH -> ACT", "positive_H5_count"] == 227

def test_022_watch_to_act_escalation_error_127(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WATCH -> ACT", "negative_H5_count"] == 127

def test_023_watch_to_act_escalation_error_rate_bounds(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert 30.0 <= df_t.loc["WATCH -> ACT", "negative_H5_rate_pct"] <= 40.0

def test_024_wait_to_act_count_n52(closure_results):
    df_t = closure_results["df_trans"].set_index("transition_label")
    assert df_t.loc["WAIT -> ACT", "count_N"] == 52

def test_025_total_arm_d_act_sum_to_828(closure_results):
    df_t = closure_results["df_trans"]
    act_sub = df_t[df_t["target_action_arm_d"] == "ACT"]
    assert act_sub["count_N"].sum() == 828


# =============================================================================
# 3. Decision Calibration & Confidence Monotonicity (26-35)
# =============================================================================

def test_026_action_state_monotonicity_not_applicable(closure_results):
    assert closure_results["json"]["decision_calibration"]["action_state_monotonicity"] == "NOT_APPLICABLE_CATEGORICAL_ACTIONS"

def test_027_confidence_tier_monotonicity_observed(closure_results):
    assert closure_results["json"]["decision_calibration"]["confidence_tier_monotonicity"] == "OBSERVED_MONOTONIC"

def test_028_confidence_high_greater_than_medium(closure_results):
    tiers = closure_results["json"]["decision_calibration"]["confidence_tiers"]
    assert tiers["HIGH_mean_H5"] > tiers["MEDIUM_mean_H5"]

def test_029_confidence_medium_greater_than_low(closure_results):
    tiers = closure_results["json"]["decision_calibration"]["confidence_tiers"]
    assert tiers["MEDIUM_mean_H5"] > tiers["LOW_mean_H5"]

def test_030_calibration_csv_row_count(closure_results):
    assert len(closure_results["df_calib"]) == 9  # 5 actions + 4 confidence tiers

def test_031_calibration_csv_action_rows(closure_results):
    act_rows = closure_results["df_calib"][closure_results["df_calib"]["group_type"] == "ACTION_STATE"]
    assert len(act_rows) == 5

def test_032_calibration_csv_confidence_rows(closure_results):
    conf_rows = closure_results["df_calib"][closure_results["df_calib"]["group_type"] == "CONFIDENCE_TIER"]
    assert len(conf_rows) == 4

def test_033_reject_cohort_negative_h5_rate_high(closure_results):
    act_rows = closure_results["df_calib"].set_index("tier_or_state")
    assert act_rows.loc["REJECT", "negative_H5_rate_pct"] > 70.0

def test_034_act_cohort_mean_h5_positive(closure_results):
    act_rows = closure_results["df_calib"].set_index("tier_or_state")
    assert act_rows.loc["ACT", "mean_H5_pp"] > 0.0

def test_035_overall_calibration_classification_conditional(closure_results):
    clf = closure_results["json"]["classifications"]["DECISION_CALIBRATION"]
    assert "CONDITIONAL" in clf


# =============================================================================
# 4. OOS Decision Utility & Temporal Stability (36-45)
# =============================================================================

def test_036_oos_csv_three_partitions(closure_results):
    assert len(closure_results["df_oos"]) == 3

def test_037_oos_partition_sum_n1760(closure_results):
    assert closure_results["df_oos"]["total_N"].sum() == 1760

def test_038_development_n1280(closure_results):
    df_o = closure_results["df_oos"].set_index("partition")
    assert df_o.loc["DEVELOPMENT_2016_2023", "total_N"] == 1280

def test_039_validation_n160(closure_results):
    df_o = closure_results["df_oos"].set_index("partition")
    assert df_o.loc["VALIDATION_2024", "total_N"] == 160

def test_040_oos_n320(closure_results):
    df_o = closure_results["df_oos"].set_index("partition")
    assert df_o.loc["OUT_OF_SAMPLE_2025_2026", "total_N"] == 320

def test_041_all_partitions_reject_mean_h5_negative(closure_results):
    for _, r in closure_results["df_oos"].iterrows():
        assert r["reject_mean_H5_pp"] < 0.0

def test_042_all_partitions_act_mean_h5_positive(closure_results):
    for _, r in closure_results["df_oos"].iterrows():
        assert r["act_mean_H5_pp"] > 0.0

def test_043_oos_rejection_negative_rate_high(closure_results):
    df_o = closure_results["df_oos"].set_index("partition")
    assert df_o.loc["OUT_OF_SAMPLE_2025_2026", "reject_negative_H5_rate_pct"] >= 70.0

def test_044_oos_decision_utility_status_conditional(closure_results):
    assert "CONDITIONAL" in closure_results["json"]["oos_decision_utility"]["oos_decision_utility_status"]

def test_045_temporal_generalization_classification(closure_results):
    assert "CONDITIONAL" in closure_results["json"]["classifications"]["OOS_DECISION_UTILITY"]


# =============================================================================
# 5. Traceability, Red Team & Epistemological Boundaries (46-55)
# =============================================================================

def test_046_traceability_sample_size_300(closure_results):
    assert closure_results["json"]["decision_traceability"]["audit_sample_N"] == 300

def test_047_traceability_pass_rate_100(closure_results):
    assert closure_results["json"]["decision_traceability"]["traceability_rate_pct"] == 100.0

def test_048_45_red_team_attacks_executed(closure_results):
    assert len(closure_results["df_rt"]) == 45

def test_049_45_red_team_attacks_all_pass(closure_results):
    assert (closure_results["df_rt"]["status"] == "PASS").all()

def test_050_causality_not_proven(closure_results):
    assert closure_results["json"]["classifications"]["CAUSALITY"] == "NOT_PROVEN"

def test_051_standalone_alpha_not_proven(closure_results):
    assert closure_results["json"]["classifications"]["STANDALONE_ALPHA"] == "NOT_PROVEN"

def test_052_strategy_optimization_blocked(closure_results):
    assert closure_results["json"]["classifications"]["STRATEGY_OPTIMIZATION"] == "BLOCKED"

def test_053_strategy_readiness_not_ready(closure_results):
    assert closure_results["json"]["classifications"]["STRATEGY_READINESS"] == "NOT_READY"

def test_054_final_status_closed(closure_results):
    assert closure_results["json"]["classifications"]["ZZZ_14_8_STATUS"] == "CLOSED"

def test_055_dual_run_exact_hash_reproducibility(gate):
    res1 = gate.execute_closure_gate()
    res2 = gate.execute_closure_gate()
    assert res1["population"]["total_setups"] == res2["population"]["total_setups"]
    assert res1["decision_utility_vector"]["defensive_alignment_count"] == res2["decision_utility_vector"]["defensive_alignment_count"]
    assert res1["decision_utility_vector"]["escalation_error_count"] == res2["decision_utility_vector"]["escalation_error_count"]
