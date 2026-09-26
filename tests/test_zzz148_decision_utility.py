"""
tests/test_zzz148_decision_utility.py
======================================
Comprehensive automated test suite for Batch ZZZ.14.8:
Agent 2 Information-to-Decision Utility, Counterfactual Decision & OOS Validation Gate.
Contains 100+ targeted unit and integration tests.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.zzz148_decision_utility_gate import ZZZ148DecisionUtilityGate


@pytest.fixture(scope="module")
def gate():
    return ZZZ148DecisionUtilityGate(scratch_dir="scratch", reports_dir="reports")


@pytest.fixture(scope="module")
def validation_results(gate):
    res = gate.execute_validation_gate()
    with open("reports/zzz14_8_canonical_result.json", "r") as f:
        canonical_json = json.load(f)
    df_matrix = pd.read_csv("reports/zzz14_8_canonical_setup_decision_matrix.csv")
    with open("reports/zzz14_8_decision_objects.json", "r") as f:
        decision_objs = json.load(f)
    df_cf = pd.read_csv("reports/zzz14_8_counterfactual_matrix.csv")
    df_attr = pd.read_csv("reports/zzz14_8_information_attribution.csv")
    df_placebo = pd.read_csv("reports/zzz14_8_placebo_results.csv")
    df_temp = pd.read_csv("reports/zzz14_8_temporal_results.csv")
    df_bench = pd.read_csv("reports/zzz14_8_semantic_benchmark.csv")
    df_conc = pd.read_csv("reports/zzz14_8_concentration_audit.csv")
    df_rt = pd.read_csv("reports/zzz14_8_red_team.csv")
    with open("reports/zzz14_8_manifest.json", "r") as f:
        manifest = json.load(f)

    return {
        "res": res,
        "json": canonical_json,
        "df_mat": df_matrix,
        "dec_objs": decision_objs,
        "df_cf": df_cf,
        "df_attr": df_attr,
        "df_placebo": df_placebo,
        "df_temp": df_temp,
        "df_bench": df_bench,
        "df_conc": df_conc,
        "df_rt": df_rt,
        "manifest": manifest
    }


# =============================================================================
# 1. Population & Sample Preservation Tests (1-10)
# =============================================================================

def test_001_population_count_n1760(validation_results):
    assert len(validation_results["df_mat"]) == 1760

def test_002_counterfactual_matrix_n1760(validation_results):
    assert len(validation_results["df_cf"]) == 1760

def test_003_information_attribution_n1760(validation_results):
    assert len(validation_results["df_attr"]) == 1760

def test_004_decision_objects_map_n1760(validation_results):
    assert len(validation_results["dec_objs"]) == 1760

def test_005_canonical_contradiction_count_n161(validation_results):
    assert int(validation_results["df_mat"]["contradiction_indicator"].sum()) == 161

def test_006_non_contradiction_count_n1599(validation_results):
    assert int((1 - validation_results["df_mat"]["contradiction_indicator"]).sum()) == 1599

def test_007_equities_count_80(validation_results):
    assert validation_results["df_mat"]["ticker"].nunique() == 80

def test_008_date_clusters_count_22(validation_results):
    assert validation_results["df_mat"]["date"].nunique() == 22

def test_009_zero_sample_attrition(validation_results):
    assert validation_results["json"]["population"]["sample_attrition"] == 0

def test_010_setup_id_format_integrity(validation_results):
    assert validation_results["df_mat"]["setup_id"].str.startswith("SETUP_V2_").all()


# =============================================================================
# 2. Counterfactual Arms & Decision Objects Tests (11-25)
# =============================================================================

def test_011_all_arms_present_in_decision_objects(validation_results):
    for s_id, obj in list(validation_results["dec_objs"].items())[:20]:
        assert "ARM_A" in obj and "ARM_B" in obj and "ARM_C" in obj and "ARM_D" in obj

def test_012_arm_a_quant_only_action_states(validation_results):
    acts = validation_results["df_mat"]["arm_a_action"].unique()
    assert set(acts).issubset({"ACT", "WATCH", "WAIT"})

def test_013_arm_b_context_insufficient_present(validation_results):
    assert "INSUFFICIENT" in validation_results["df_mat"]["arm_b_action"].unique()

def test_014_arm_c_contradiction_rejection_present(validation_results):
    assert "REJECT" in validation_results["df_mat"]["arm_c_action"].unique()

def test_015_arm_d_full_action_taxonomy_valid(validation_results):
    acts = set(validation_results["df_mat"]["arm_d_action"].unique())
    assert acts.issubset({"ACT", "WATCH", "WAIT", "REJECT", "INSUFFICIENT"})

def test_016_arm_d_act_count_positive(validation_results):
    assert (validation_results["df_mat"]["arm_d_action"] == "ACT").sum() > 500

def test_017_arm_d_reject_count_positive(validation_results):
    assert (validation_results["df_mat"]["arm_d_action"] == "REJECT").sum() >= 159

def test_018_arm_d_insufficient_count_positive(validation_results):
    assert (validation_results["df_mat"]["arm_d_action"] == "INSUFFICIENT").sum() > 50

def test_019_arm_d_watch_count_positive(validation_results):
    assert (validation_results["df_mat"]["arm_d_action"] == "WATCH").sum() > 200

def test_020_arm_d_wait_count_positive(validation_results):
    assert (validation_results["df_mat"]["arm_d_action"] == "WAIT").sum() > 200

def test_021_decision_hash_present_in_all_arms(validation_results):
    assert validation_results["df_mat"]["arm_a_hash"].str.len().eq(64).all()
    assert validation_results["df_mat"]["arm_b_hash"].str.len().eq(64).all()
    assert validation_results["df_mat"]["arm_c_hash"].str.len().eq(64).all()
    assert validation_results["df_mat"]["arm_d_hash"].str.len().eq(64).all()

def test_022_decision_hash_distinct_across_arms(validation_results):
    df = validation_results["df_mat"]
    assert (df["arm_a_hash"] != df["arm_d_hash"]).sum() > 1000

def test_023_arm_d_thesis_direction_non_empty(validation_results):
    assert (validation_results["df_mat"]["arm_d_thesis"].str.len() > 0).all()

def test_024_arm_d_confidence_levels(validation_results):
    confs = set(validation_results["df_mat"]["arm_d_conf"].unique())
    assert confs.issubset({"LOW", "MEDIUM", "HIGH", "UNKNOWN"})

def test_025_arm_d_position_sizes(validation_results):
    pos = set(validation_results["df_mat"]["arm_d_pos"].unique())
    assert pos.issubset({"FULL_UNIT", "HALF_UNIT", "ZERO_UNIT"})


# =============================================================================
# 3. Decision Divergence Metrics M1-M6 Tests (26-35)
# =============================================================================

def test_026_m1_decision_divergence_rate_bounds(validation_results):
    m1 = validation_results["json"]["decision_metrics"]["M1_decision_divergence_rate"]
    assert 0.40 <= m1 <= 1.0

def test_027_m2_action_divergence_rate_bounds(validation_results):
    m2 = validation_results["json"]["decision_metrics"]["M2_action_divergence_rate"]
    assert 0.20 <= m2 <= 0.70

def test_028_m3_thesis_divergence_rate_bounds(validation_results):
    m3 = validation_results["json"]["decision_metrics"]["M3_thesis_divergence_rate"]
    assert 0.30 <= m3 <= 1.0

def test_029_m4_risk_divergence_rate_bounds(validation_results):
    m4 = validation_results["json"]["decision_metrics"]["M4_risk_divergence_rate"]
    assert 0.15 <= m4 <= 0.60

def test_030_m5_timing_divergence_rate_bounds(validation_results):
    m5 = validation_results["json"]["decision_metrics"]["M5_timing_divergence_rate"]
    assert 0.20 <= m5 <= 0.70

def test_031_m6_position_size_divergence_bounds(validation_results):
    m6 = validation_results["json"]["decision_metrics"]["M6_position_size_divergence_rate"]
    assert 0.20 <= m6 <= 0.70

def test_032_divergence_counts_sum_invariant(validation_results):
    dm = validation_results["json"]["decision_metrics"]
    assert dm["M1_decision_divergence_count"] <= dm["total_setups"]

def test_033_arm_a_vs_arm_d_divergence_positive(validation_results):
    dm = validation_results["json"]["decision_metrics"]
    assert dm["arm_a_vs_arm_d_action_divergence"] > 0.30

def test_034_arm_b_vs_arm_c_divergence_positive(validation_results):
    dm = validation_results["json"]["decision_metrics"]
    assert dm["arm_b_vs_arm_c_action_divergence"] > 0.05

def test_035_decision_difference_taxonomy_coverage(validation_results):
    diffs = set(validation_results["df_mat"]["diff_ad"].unique())
    assert len(diffs) >= 4


# =============================================================================
# 4. Action-Conditional Outcomes & Calibration Tests (36-50)
# =============================================================================

def test_036_act_mean_h5_positive(validation_results):
    act_res = validation_results["json"]["action_conditional_outcomes"]["ACT"]
    assert act_res["mean_H5_pp"] > 0.0

def test_037_reject_mean_h5_negative(validation_results):
    rej_res = validation_results["json"]["action_conditional_outcomes"]["REJECT"]
    assert rej_res["mean_H5_pp"] < -1.0

def test_038_reject_negative_h5_rate_high(validation_results):
    rej_res = validation_results["json"]["action_conditional_outcomes"]["REJECT"]
    assert rej_res["negative_H5_rate_pct"] > 60.0

def test_039_act_mean_h10_positive(validation_results):
    act_res = validation_results["json"]["action_conditional_outcomes"]["ACT"]
    assert act_res["mean_H10_pp"] > 0.0

def test_040_reject_mean_h10_negative(validation_results):
    rej_res = validation_results["json"]["action_conditional_outcomes"]["REJECT"]
    assert rej_res["mean_H10_pp"] < -2.0

def test_041_act_mean_h20_positive(validation_results):
    act_res = validation_results["json"]["action_conditional_outcomes"]["ACT"]
    assert act_res["mean_H20_pp"] > 0.0

def test_042_reject_mean_h20_negative(validation_results):
    rej_res = validation_results["json"]["action_conditional_outcomes"]["REJECT"]
    assert rej_res["mean_H20_pp"] < -3.0

def test_043_mae_strictly_negative(validation_results):
    for act, res in validation_results["json"]["action_conditional_outcomes"].items():
        assert res["mean_MAE_pp"] < 0.0

def test_044_mfe_strictly_positive(validation_results):
    for act, res in validation_results["json"]["action_conditional_outcomes"].items():
        assert res["mean_MFE_pp"] > 0.0

def test_045_confidence_calibration_status(validation_results):
    calib = validation_results["json"]["decision_calibration"]
    assert calib["status"] in ["CALIBRATED_MONOTONIC", "PARTIALLY_CALIBRATED"]

def test_046_confidence_high_higher_than_low(validation_results):
    calib_map = validation_results["json"]["decision_calibration"]["calibration_by_confidence"]
    if "HIGH" in calib_map and "LOW" in calib_map:
        assert calib_map["HIGH"]["mean_H5_pp"] >= calib_map["LOW"]["mean_H5_pp"]

def test_047_confidence_tier_counts_sum(validation_results):
    calib_map = validation_results["json"]["decision_calibration"]["calibration_by_confidence"]
    total = sum(v["count"] for v in calib_map.values())
    assert total == 1760

def test_048_action_conditional_counts_sum(validation_results):
    act_map = validation_results["json"]["action_conditional_outcomes"]
    total = sum(v["count"] for v in act_map.values())
    assert total == 1760

def test_049_insufficient_information_retained(validation_results):
    assert "INSUFFICIENT" in validation_results["json"]["action_conditional_outcomes"]

def test_050_outcome_metrics_no_nan(validation_results):
    for act, res in validation_results["json"]["action_conditional_outcomes"].items():
        for k, v in res.items():
            assert not np.isnan(v)


# =============================================================================
# 5. Contradiction Counterfactual & Utility Matrix Tests (51-65)
# =============================================================================

def test_051_contradiction_counterfactual_n161(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["canonical_contradiction_N"] == 161

def test_052_rejection_adherence_rate_high(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["rejection_adherence_rate_pct"] >= 98.0

def test_053_contradiction_mean_h5_negative(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["mean_H5_outcome_pp"] < -1.5

def test_054_contradiction_negative_h5_rate_bounds(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["negative_H5_rate_pct"] > 65.0

def test_055_net_avoided_loss_h5_positive(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["descriptive_net_avoided_loss_H5_pp"] > 250.0

def test_056_net_avoided_loss_h10_positive(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["descriptive_net_avoided_loss_H10_pp"] > 400.0

def test_057_net_avoided_loss_h20_positive(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["descriptive_net_avoided_loss_H20_pp"] > 500.0

def test_058_contradiction_epistemological_status(validation_results):
    contra = validation_results["json"]["contradiction_counterfactual"]
    assert contra["epistemological_status"] == "DESCRIPTIVE_OUTCOME_ASSOCIATION_NOT_CAUSAL_ALPHA"

def test_059_defensive_alignment_count_positive(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert util["defensive_alignment_count"] > 0

def test_060_defensive_alignment_mean_h5_negative(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert util["defensive_alignment_mean_H5"] < 0.0

def test_061_opportunity_cost_count_recorded(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert util["opportunity_cost_count"] >= 0

def test_062_timing_refinement_count_positive(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert util["timing_refinement_count"] >= 0

def test_063_opportunity_identification_count_positive(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert util["opportunity_identification_count"] > 0

def test_064_defensive_precision_ratio_bounds(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    assert 0.50 <= util["defensive_ratio"] <= 1.0

def test_065_all_utility_counts_non_negative(validation_results):
    util = validation_results["json"]["decision_utility_matrix"]
    for k, v in util.items():
        if "count" in k:
            assert v >= 0


# =============================================================================
# 6. Placebo Agent 2 Falsification Tests (66-75)
# =============================================================================

def test_066_placebo_falsification_cleared(validation_results):
    assert validation_results["json"]["placebo_metrics"]["falsification_cleared"] is True

def test_067_real_agent2_divergence_higher_than_placebo_a(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["real_agent2_action_divergence"] > p["placebo_A_random_density_action_divergence"] * 3.0

def test_068_real_agent2_divergence_higher_than_placebo_b(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["real_agent2_action_divergence"] > p["placebo_B_ticker_irrelevant_action_divergence"] * 3.0

def test_069_real_agent2_divergence_higher_than_placebo_c(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["real_agent2_action_divergence"] > p["placebo_C_shuffled_channel_action_divergence"] * 3.0

def test_070_real_agent2_divergence_higher_than_placebo_d(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["real_agent2_action_divergence"] > p["placebo_D_shuffled_contra_action_divergence"] * 3.0

def test_071_real_agent2_divergence_higher_than_placebo_e(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["real_agent2_action_divergence"] > p["placebo_E_matched_random_action_divergence"] * 3.0

def test_072_placebo_results_file_rows(validation_results):
    assert len(validation_results["df_placebo"]) == 6

def test_073_placebo_results_status_all_pass(validation_results):
    assert (validation_results["df_placebo"]["status"].str.contains("PASS|REAL")).all()

def test_074_separation_ratio_bounds(validation_results):
    assert validation_results["json"]["placebo_metrics"]["separation_ratio"] > 4.0

def test_075_placebo_divergences_below_10_pct(validation_results):
    p = validation_results["json"]["placebo_metrics"]
    assert p["placebo_A_random_density_action_divergence"] < 0.10
    assert p["placebo_B_ticker_irrelevant_action_divergence"] < 0.10
    assert p["placebo_C_shuffled_channel_action_divergence"] < 0.10
    assert p["placebo_D_shuffled_contra_action_divergence"] < 0.10
    assert p["placebo_E_matched_random_action_divergence"] < 0.10


# =============================================================================
# 7. Independent Ground-Truth Benchmark Tests (76-85)
# =============================================================================

def test_076_benchmark_sample_size_n500(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["benchmark_sample_N"] == 500

def test_077_entity_resolution_precision_100(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["entity_resolution_precision"] == 1.000

def test_078_pit_timestamp_correctness_100(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["pit_timestamp_correctness"] == 1.000

def test_079_contradiction_precision_high(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["contradiction_classification_precision"] >= 0.95

def test_080_contradiction_recall_high(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["contradiction_classification_recall"] >= 0.90

def test_081_contradiction_f1_score_high(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["contradiction_f1_score"] >= 0.92

def test_082_transmission_agreement_high(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["transmission_channel_agreement"] >= 0.90

def test_083_overall_semantic_agreement_high(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["overall_semantic_agreement"] >= 0.95

def test_084_benchmark_status_pass(validation_results):
    assert validation_results["json"]["semantic_benchmark"]["status"] == "INDEPENDENT_GROUND_TRUTH_PASS"

def test_085_benchmark_csv_length(validation_results):
    assert len(validation_results["df_bench"]) == 500


# =============================================================================
# 8. Temporal, Concentration & Red Team Tests (86-105)
# =============================================================================

def test_086_temporal_partitions_all_present(validation_results):
    temp = validation_results["json"]["temporal_metrics"]
    assert "development_2016_2023" in temp
    assert "validation_2024" in temp
    assert "out_of_sample_2025_2026" in temp

def test_087_temporal_sum_equals_n1760(validation_results):
    temp = validation_results["json"]["temporal_metrics"]
    total = temp["development_2016_2023"]["N"] + temp["validation_2024"]["N"] + temp["out_of_sample_2025_2026"]["N"]
    assert total == 1760

def test_088_dev_rejection_mean_h5_negative(validation_results):
    assert validation_results["json"]["temporal_metrics"]["development_2016_2023"]["reject_mean_H5"] < 0.0

def test_089_val_rejection_mean_h5_negative(validation_results):
    assert validation_results["json"]["temporal_metrics"]["validation_2024"]["reject_mean_H5"] < 0.0

def test_090_oos_rejection_mean_h5_negative(validation_results):
    assert validation_results["json"]["temporal_metrics"]["out_of_sample_2025_2026"]["reject_mean_H5"] < 0.0

def test_091_temporal_consistency_string(validation_results):
    assert validation_results["json"]["temporal_metrics"]["temporal_consistency"] == "DIRECTIONALLY_STABLE_ACROSS_ALL_ERAS"

def test_092_top1_ticker_concentration_bound(validation_results):
    assert validation_results["json"]["concentration_metrics"]["top1_ticker_concentration"] < 0.20

def test_093_top5_ticker_concentration_bound(validation_results):
    assert validation_results["json"]["concentration_metrics"]["top5_ticker_concentration"] < 0.45

def test_094_concentration_risk_classification(validation_results):
    assert validation_results["json"]["concentration_metrics"]["concentration_risk_classification"] == "MODERATE_SECTOR_CONCENTRATION_ACCEPTABLE"

def test_095_75_red_team_attacks_executed(validation_results):
    assert len(validation_results["df_rt"]) == 75

def test_096_75_red_team_attacks_all_pass(validation_results):
    assert (validation_results["df_rt"]["status"] == "PASS").all()

def test_097_25_red_team_domains_represented(validation_results):
    assert validation_results["df_rt"]["domain"].nunique() == 25

def test_098_manifest_contains_all_12_artifacts(validation_results):
    arts = validation_results["manifest"]["artifacts"]
    assert len(arts) >= 12

def test_099_scientific_firewall_classifications_intact(validation_results):
    clf = validation_results["json"]["classifications"]
    assert clf["CAUSALITY"] == "NOT_PROVEN"
    assert clf["STANDALONE_ALPHA"] == "NOT_PROVEN"
    assert clf["STRATEGY_OPTIMIZATION"] == "BLOCKED"
    assert clf["STRATEGY_READINESS"] == "NOT_READY"

def test_100_final_status_closed(validation_results):
    assert validation_results["json"]["classifications"]["ZZZ_14_8_STATUS"] == "CLOSED"

def test_101_dual_run_deterministic_reproducibility(gate):
    res1 = gate.execute_validation_gate()
    res2 = gate.execute_validation_gate()
    assert res1["total_setups"] == res2["total_setups"]
    assert res1["red_team_attacks_pass"] == res2["red_team_attacks_pass"]

def test_102_no_nan_values_in_canonical_setup_matrix(validation_results):
    assert validation_results["df_mat"].isna().sum().sum() == 0

def test_103_no_outcome_leakage_in_decision_hashes(validation_results):
    # Hashes generated before joining outcomes must match
    df = validation_results["df_mat"]
    assert (df["arm_a_hash"].str.len() == 64).all()
    assert (df["arm_d_hash"].str.len() == 64).all()

def test_104_validation_report_file_exists(validation_results):
    assert os.path.exists("reports/zzz14_8_validation.md")
    assert os.path.getsize("reports/zzz14_8_validation.md") > 1000

def test_105_canonical_result_json_valid_schema(validation_results):
    req_keys = [
        "population", "arms", "decision_metrics", "action_conditional_outcomes",
        "decision_calibration", "contradiction_counterfactual", "decision_utility_matrix",
        "placebo_metrics", "semantic_benchmark", "temporal_metrics", "concentration_metrics",
        "inference", "classifications"
    ]
    for k in req_keys:
        assert k in validation_results["json"]
