"""
tests/test_zzz149_frozen_decision_oos.py
==========================================
Automated Test Suite for Batch ZZZ.14.9: Frozen Decision Rule OOS Utility & Temporal Generalization Gate.

Epistemological & Governance Mandate:
- N=1,760 setups, 80 equities, 2016-2026.
- Exactly 3 Agents. Zero Agent 4.
- Evaluates temporal generalization of frozen decision state across:
    - Development: 2016-2023 (N=1,280)
    - Validation: 2024 (N=160)
    - Out-of-Sample (OOS): 2025-2026 (N=320)
- 75+ targeted unit and adversarial tests.
"""

import os
import sys
import json
import hashlib
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath("."))
from core.zzz149_frozen_decision_oos_gate import ZZZ149FrozenDecisionOOSGate


@pytest.fixture(scope="module")
def gate_output():
    gate = ZZZ149FrozenDecisionOOSGate()
    result = gate.run_gate()
    df_mat = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_frozen_decision_oos_matrix.csv"))
    df_gen = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_temporal_generalization.csv"), keep_default_na=False)
    df_trans = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_transition_oos.csv"), keep_default_na=False)
    df_stab = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_decision_stability.csv"))
    df_plac = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_placebo.csv"))
    df_cov = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_9_coverage_audit.csv"))
    with open(os.path.join(gate.reports_dir, "zzz14_9_inference.json"), "r", encoding="utf-8") as f:
        inf_json = json.load(f)
    with open(os.path.join(gate.reports_dir, "zzz14_9_validation.json"), "r", encoding="utf-8") as f:
        val_json = json.load(f)
    with open(os.path.join(gate.reports_dir, "zzz14_9_manifest.json"), "r", encoding="utf-8") as f:
        manifest_json = json.load(f)
    return {
        "gate": gate,
        "result": result,
        "df_mat": df_mat,
        "df_gen": df_gen,
        "df_trans": df_trans,
        "df_stab": df_stab,
        "df_plac": df_plac,
        "df_cov": df_cov,
        "inf_json": inf_json,
        "val_json": val_json,
        "manifest_json": manifest_json
    }


# -------------------------------------------------------------
# 1. Population & Temporal Split Tests (1-7)
# -------------------------------------------------------------

def test_001_population_n1760(gate_output):
    df_mat = gate_output["df_mat"]
    assert len(df_mat) == 1760


def test_002_unique_setup_ids_n1760(gate_output):
    df_mat = gate_output["df_mat"]
    assert df_mat["setup_id"].nunique() == 1760


def test_003_zero_duplicate_setups(gate_output):
    df_mat = gate_output["df_mat"]
    assert df_mat["setup_id"].duplicated().sum() == 0


def test_004_dev_partition_count_1280(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["temporal_partition"] == "DEV").sum() == 1280


def test_005_val_partition_count_160(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["temporal_partition"] == "VAL").sum() == 160


def test_006_oos_partition_count_320(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["temporal_partition"] == "OOS").sum() == 320


def test_007_partition_sum_equals_1760(gate_output):
    df_mat = gate_output["df_mat"]
    p_counts = df_mat["temporal_partition"].value_counts()
    assert p_counts["DEV"] + p_counts["VAL"] + p_counts["OOS"] == 1760


# -------------------------------------------------------------
# 2. Pre-T Decision Freeze & PIT Integrity Tests (8-14)
# -------------------------------------------------------------

def test_008_decision_hash_before_outcome_flag(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["decision_hash_before_outcome"] == "PASS").all()


def test_009_pit_status_isolated(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["pit_status"] == "POINT_IN_TIME_ISOLATED").all()


def test_010_arm_b_hash_len_64(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["arm_b_hash"].str.len() == 64).all()


def test_011_arm_d_hash_len_64(gate_output):
    df_mat = gate_output["df_mat"]
    assert (df_mat["arm_d_hash"].str.len() == 64).all()


def test_012_categorical_action_states_only(gate_output):
    df_mat = gate_output["df_mat"]
    valid_actions = {"ACT", "WATCH", "WAIT", "REJECT", "INSUFFICIENT"}
    assert set(df_mat["arm_d_action"].unique()).issubset(valid_actions)
    assert set(df_mat["arm_b_action"].unique()).issubset(valid_actions)


def test_013_confidence_levels_valid(gate_output):
    df_mat = gate_output["df_mat"]
    valid_confs = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
    assert set(df_mat["arm_d_conf"].unique()).issubset(valid_confs)


def test_014_total_contradictions_sum_161(gate_output):
    df_mat = gate_output["df_mat"]
    assert int(df_mat["contradiction_indicator"].sum()) == 161


# -------------------------------------------------------------
# 3. Temporal Generalization Metrics Tests (15-25)
# -------------------------------------------------------------

def test_015_dev_contradiction_count_128(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert int(df_gen.loc["DEV", "contradiction_setups_N"]) == 128


def test_016_val_contradiction_count_12(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert int(df_gen.loc["VAL", "contradiction_setups_N"]) == 12


def test_017_oos_contradiction_count_21(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert int(df_gen.loc["OOS", "contradiction_setups_N"]) == 21


def test_018_dev_rejection_mean_h5_negative(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["DEV", "mean_H5_rejections_pp"]) < 0.0
    assert abs(float(df_gen.loc["DEV", "mean_H5_rejections_pp"]) - (-1.9328)) < 1e-3


def test_019_val_rejection_mean_h5_negative(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["VAL", "mean_H5_rejections_pp"]) < 0.0
    assert abs(float(df_gen.loc["VAL", "mean_H5_rejections_pp"]) - (-1.3733)) < 1e-3


def test_020_oos_rejection_mean_h5_negative(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["OOS", "mean_H5_rejections_pp"]) < 0.0
    assert abs(float(df_gen.loc["OOS", "mean_H5_rejections_pp"]) - (-1.6490)) < 1e-3


def test_021_dev_rejection_negative_rate_high(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["DEV", "negative_H5_rate_rejections_pct"]) > 70.0


def test_022_val_rejection_negative_rate_high(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["VAL", "negative_H5_rate_rejections_pct"]) > 75.0


def test_023_oos_rejection_negative_rate_high(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    assert float(df_gen.loc["OOS", "negative_H5_rate_rejections_pct"]) > 70.0


def test_024_difference_rejection_minus_non_rejection_negative_all_partitions(gate_output):
    df_gen = gate_output["df_gen"].set_index("temporal_partition")
    for p in ["DEV", "VAL", "OOS", "FULL"]:
        assert float(df_gen.loc[p, "diff_rejection_vs_non_rejection_H5_pp"]) < -2.0


def test_025_all_partition_generalization_verdicts_pass(gate_output):
    df_gen = gate_output["df_gen"]
    assert (df_gen["generalization_verdict"] == "PASS").all()


# -------------------------------------------------------------
# 4. Key Transition Outcomes Across Partitions Tests (26-33)
# -------------------------------------------------------------

def test_026_act_to_reject_dev_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "ACT -> REJECT") & (df_trans["temporal_partition"] == "DEV")].iloc[0]
    assert int(row["count_N"]) == 27
    assert float(row["mean_H5_pp"]) < 0.0


def test_027_act_to_reject_val_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "ACT -> REJECT") & (df_trans["temporal_partition"] == "VAL")].iloc[0]
    assert int(row["count_N"]) == 5
    assert float(row["mean_H5_pp"]) < 0.0
    assert row["sample_support_status"] == "LOW_SAMPLE_SUPPORT"


def test_028_act_to_reject_oos_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "ACT -> REJECT") & (df_trans["temporal_partition"] == "OOS")].iloc[0]
    assert int(row["count_N"]) == 8
    assert float(row["mean_H5_pp"]) < 0.0
    assert row["sample_support_status"] == "LOW_SAMPLE_SUPPORT"


def test_029_act_to_reject_full_count_40(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "ACT -> REJECT") & (df_trans["temporal_partition"] == "FULL")].iloc[0]
    assert int(row["count_N"]) == 40
    assert abs(float(row["mean_H5_pp"]) - (-1.9705)) < 1e-3


def test_030_watch_to_act_dev_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "WATCH -> ACT") & (df_trans["temporal_partition"] == "DEV")].iloc[0]
    assert int(row["count_N"]) == 243
    assert float(row["mean_H5_pp"]) > 0.0


def test_031_watch_to_act_val_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "WATCH -> ACT") & (df_trans["temporal_partition"] == "VAL")].iloc[0]
    assert int(row["count_N"]) == 39
    assert float(row["mean_H5_pp"]) > 0.0


def test_032_watch_to_act_oos_count_and_mean(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "WATCH -> ACT") & (df_trans["temporal_partition"] == "OOS")].iloc[0]
    assert int(row["count_N"]) == 72
    assert float(row["mean_H5_pp"]) > 0.0


def test_033_watch_to_act_full_count_354(gate_output):
    df_trans = gate_output["df_trans"]
    row = df_trans[(df_trans["transition"] == "WATCH -> ACT") & (df_trans["temporal_partition"] == "FULL")].iloc[0]
    assert int(row["count_N"]) == 354
    assert abs(float(row["mean_H5_pp"]) - 0.9775) < 1e-3


# -------------------------------------------------------------
# 5. Placebo & Coverage Tests (34-40)
# -------------------------------------------------------------

def test_034_placebo_falsification_cleared(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["placebo_battery"]["falsification_cleared"] is True


def test_035_real_agent2_separation_ratio_large(gate_output):
    df_plac = gate_output["df_plac"]
    p_dev = df_plac[(df_plac["temporal_partition"] == "DEV") & (df_plac["probe_code"] != "REAL_AGENT2")]
    assert (p_dev["separation_ratio_vs_real"] > 3.0).all()


def test_036_coverage_confounding_controlled(gate_output):
    df_cov = gate_output["df_cov"]
    assert (df_cov["coverage_confounding_verdict"] == "CONTROLLED").all()


def test_037_decision_stability_100_pct_exact(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["decision_stability"]["exact_matches"] == 1760
    assert val_json["decision_stability"]["reproducibility_verdict"] == "PASS"


def test_038_inference_beta_negative_across_all_partitions(gate_output):
    inf_json = gate_output["inf_json"]
    for p in ["DEV", "VAL", "OOS", "FULL"]:
        assert inf_json["partitions"][p]["beta_contradiction_pp"] < 0.0


def test_039_inference_classification_consistent(gate_output):
    inf_json = gate_output["inf_json"]
    for p in ["DEV", "VAL", "OOS", "FULL"]:
        assert inf_json["partitions"][p]["inference_classification"] == "DIRECTIONALLY_CONSISTENT"


def test_040_manifest_contains_all_artifacts(gate_output):
    manifest = gate_output["manifest_json"]
    assert len(manifest) >= 8
    assert all(len(h) == 64 for h in manifest.values())


# -------------------------------------------------------------
# 6. Scientific Firewall & Governance (41-45)
# -------------------------------------------------------------

def test_041_causality_not_proven(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["final_classifications"]["causality"] == "NOT_PROVEN"


def test_042_standalone_alpha_not_proven(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["final_classifications"]["standalone_alpha"] == "NOT_PROVEN"


def test_043_strategy_optimization_blocked(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["final_classifications"]["strategy_optimization"] == "BLOCKED"


def test_044_strategy_readiness_not_ready(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["final_classifications"]["strategy_readiness"] == "NOT_READY"


def test_045_zzz_14_9_status_closed(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["final_classifications"]["zzz_14_9_status"] == "CLOSED"


# -------------------------------------------------------------
# 7. Targeted Adversarial Red Team Attacks (46-105)
# -------------------------------------------------------------

def test_046_red_team_total_attacks_60(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["red_team_summary"]["total_attacks"] == 60


def test_047_red_team_all_attacks_pass(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["red_team_summary"]["red_team_verdict"] == "PASS"
    assert val_json["red_team_summary"]["passed_attacks"] == 60
    assert val_json["red_team_summary"]["failed_attacks"] == 0


@pytest.mark.parametrize("atk_idx", range(1, 61))
def test_048_to_107_individual_red_team_attacks(gate_output, atk_idx):
    with open(os.path.join(gate_output["gate"].reports_dir, "zzz14_9_red_team.json"), "r", encoding="utf-8") as f:
        rt_data = json.load(f)
    atk_id = f"ATK-{atk_idx:02d}"
    atk = next((a for a in rt_data["attacks"] if a["attack_id"] == atk_id), None)
    assert atk is not None, f"Attack {atk_id} not found in red team JSON"
    assert atk["defense_status"] == "PASS", f"Attack {atk_id} failed defense test"


# -------------------------------------------------------------
# 8. Deterministic Dual-Run Reproducibility
# -------------------------------------------------------------

def test_108_dual_run_exact_hash_reproducibility():
    gate1 = ZZZ149FrozenDecisionOOSGate()
    res1 = gate1.run_gate()
    h1 = res1["manifest"]["reports/zzz14_9_temporal_generalization.csv"]

    gate2 = ZZZ149FrozenDecisionOOSGate()
    res2 = gate2.run_gate()
    h2 = res2["manifest"]["reports/zzz14_9_temporal_generalization.csv"]

    assert h1 == h2
