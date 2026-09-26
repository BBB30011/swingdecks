"""
tests/test_zzz14812_outcome_aggregation.py
============================================
Automated Test Suite for Batch ZZZ.14.8.1.2: Canonical Transition Outcome Aggregation Reconciliation Gate.

Epistemological & Governance Mandate:
- N=1,760 setups, 80 equities, 2016-2026.
- Exactly 3 Agents. Zero Agent 4.
- 5x5 complete categorical transition outcome aggregation (25 cells).
- Exact reconciliation of key transitions:
    - ACT -> REJECT: N=40, 35 neg, 5 pos, canonical mean H5 = -1.9705 pp (superseding narrative -2.1742 pp).
    - WATCH -> ACT: N=354, 127 neg, 227 pos, canonical mean H5 = +0.9775 pp (superseding narrative +1.2984 pp).
- 50+ targeted unit and adversarial tests.
"""

import os
import json
import hashlib
import pytest
import numpy as np
import pandas as pd

from core.zzz14812_outcome_aggregation_gate import ZZZ14812OutcomeAggregationGate


@pytest.fixture(scope="module")
def gate_output():
    gate = ZZZ14812OutcomeAggregationGate()
    result = gate.run_gate()
    df_ledger = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_8_1_2_canonical_transition_outcomes.csv"))
    df_rec = pd.read_csv(os.path.join(gate.reports_dir, "zzz14_8_1_2_reconciliation.csv"), dtype=str, keep_default_na=False)
    with open(os.path.join(gate.reports_dir, "zzz14_8_1_2_validation.json"), "r", encoding="utf-8") as f:
        val_json = json.load(f)
    with open(os.path.join(gate.reports_dir, "zzz14_8_1_2_source_audit.json"), "r", encoding="utf-8") as f:
        audit_json = json.load(f)
    with open(os.path.join(gate.reports_dir, "zzz14_8_1_2_manifest.json"), "r", encoding="utf-8") as f:
        manifest_json = json.load(f)
    return {
        "gate": gate,
        "result": result,
        "df_ledger": df_ledger,
        "df_rec": df_rec,
        "val_json": val_json,
        "audit_json": audit_json,
        "manifest_json": manifest_json
    }


# -------------------------------------------------------------
# 1. Population & Setup Uniqueness Tests (Mandatory 1-4)
# -------------------------------------------------------------

def test_001_population_n1760(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert len(df_ledger) == 1760


def test_002_unique_setup_ids_n1760(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert df_ledger["setup_id"].nunique() == 1760


def test_003_zero_duplicate_setups(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert df_ledger["setup_id"].duplicated().sum() == 0


def test_004_zero_missing_setups(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["reconciliation_verdicts"]["population_integrity"] == "PASS"


# -------------------------------------------------------------
# 2. Transition Identity & 25-Cell Matrix Tests (Mandatory 5-8)
# -------------------------------------------------------------

def test_005_transition_identity_formula(gate_output):
    df_ledger = gate_output["df_ledger"]
    expected_transition = df_ledger["arm_b_action"] + " -> " + df_ledger["arm_d_action"]
    assert (df_ledger["transition"] == expected_transition).all()


def test_006_twenty_five_cells_complete(gate_output):
    df_rec = gate_output["df_rec"]
    assert len(df_rec) == 25


def test_007_global_transition_sum_1760(gate_output):
    df_rec = gate_output["df_rec"]
    assert df_rec["reconstructed_N"].astype(int).sum() == 1760


def test_008_arm_b_row_totals_reconciliation(gate_output):
    df_rec = gate_output["df_rec"].copy()
    df_rec["reconstructed_N"] = df_rec["reconstructed_N"].astype(int)
    b_sums = df_rec.groupby("arm_b_action")["reconstructed_N"].sum().to_dict()
    assert b_sums["ACT"] == 462
    assert b_sums["WATCH"] == 625
    assert b_sums["WAIT"] == 592
    assert b_sums["REJECT"] == 0
    assert b_sums["INSUFFICIENT"] == 81


def test_009_arm_d_column_totals_reconciliation(gate_output):
    df_rec = gate_output["df_rec"].copy()
    df_rec["reconstructed_N"] = df_rec["reconstructed_N"].astype(int)
    d_sums = df_rec.groupby("arm_d_action")["reconstructed_N"].sum().to_dict()
    assert d_sums["ACT"] == 828
    assert d_sums["WATCH"] == 307
    assert d_sums["WAIT"] == 360
    assert d_sums["REJECT"] == 161
    assert d_sums["INSUFFICIENT"] == 104


# -------------------------------------------------------------
# 3. Outcome Source & Definition Identity (Mandatory 9-13)
# -------------------------------------------------------------

def test_010_h5_source_identity(gate_output):
    audit_json = gate_output["audit_json"]
    assert audit_json["formula_audit"]["status"] == "PASS_IDENTICAL_FORMULA"


def test_011_h10_source_identity(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert not df_ledger["H10"].isna().any()


def test_012_h20_source_identity(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert not df_ledger["H20"].isna().any()


def test_013_mae_source_identity(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert not df_ledger["MAE"].isna().any()
    assert (df_ledger["MAE"] <= 0.0).all()


def test_014_mfe_source_identity(gate_output):
    df_ledger = gate_output["df_ledger"]
    assert not df_ledger["MFE"].isna().any()
    assert (df_ledger["MFE"] >= 0.0).all()


# -------------------------------------------------------------
# 4. Key Transition Outcomes: ACT -> REJECT & WATCH -> ACT (Mandatory 14-17)
# -------------------------------------------------------------

def test_015_act_to_reject_count_n40(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "ACT -> REJECT"].iloc[0]
    assert int(row["reconstructed_N"]) == 40


def test_016_act_to_reject_negative_positive_split(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "ACT -> REJECT"].iloc[0]
    assert int(row["negative_H5_count"]) == 35
    assert int(row["positive_H5_count"]) == 5


def test_017_act_to_reject_canonical_mean_h5(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "ACT -> REJECT"].iloc[0]
    assert abs(float(row["raw_mean_H5"]) - (-1.9705)) < 1e-4
    assert row["display_mean_H5"] == "-1.9705"


def test_018_act_to_reject_canonical_median_h5(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "ACT -> REJECT"].iloc[0]
    assert abs(float(row["raw_median_H5"]) - (-1.4900)) < 1e-4
    assert row["display_median_H5"] == "-1.4900"


def test_019_watch_to_act_count_n354(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "WATCH -> ACT"].iloc[0]
    assert int(row["reconstructed_N"]) == 354


def test_020_watch_to_act_negative_positive_split(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "WATCH -> ACT"].iloc[0]
    assert int(row["negative_H5_count"]) == 127
    assert int(row["positive_H5_count"]) == 227


def test_021_watch_to_act_canonical_mean_h5(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "WATCH -> ACT"].iloc[0]
    assert abs(float(row["raw_mean_H5"]) - 0.9774576) < 1e-4
    assert row["display_mean_H5"] == "+0.9775"


def test_022_watch_to_act_canonical_median_h5(gate_output):
    df_rec = gate_output["df_rec"]
    row = df_rec[df_rec["transition"] == "WATCH -> ACT"].iloc[0]
    assert abs(float(row["raw_median_H5"]) - 0.9100) < 1e-4
    assert row["display_median_H5"] == "+0.9100"


# -------------------------------------------------------------
# 5. Arithmetic & Precision Tests (Mandatory 18-24)
# -------------------------------------------------------------

def test_023_negative_plus_positive_equals_n_all_transitions(gate_output):
    df_rec = gate_output["df_rec"]
    assert (df_rec["sum_neg_pos"].astype(int) == df_rec["reconstructed_N"].astype(int)).all()
    assert (df_rec["neg_pos_sum_delta"].astype(int) == 0).all()


def test_024_zero_count_transitions_represented_as_na(gate_output):
    df_rec = gate_output["df_rec"]
    zeros = df_rec[df_rec["reconstructed_N"].astype(int) == 0]
    assert len(zeros) == 12
    for _, r in zeros.iterrows():
        assert r["display_mean_H5"] == "NA"
        assert r["display_median_H5"] == "NA"
        assert r["display_mean_H10"] == "NA"
        assert r["display_mean_H20"] == "NA"


def test_025_non_zero_transitions_all_valid_stats(gate_output):
    df_rec = gate_output["df_rec"]
    non_zeros = df_rec[df_rec["reconstructed_N"].astype(int) > 0]
    assert len(non_zeros) == 13
    for _, r in non_zeros.iterrows():
        assert r["display_mean_H5"] != "NA"
        assert r["display_median_H5"] != "NA"


def test_026_reconciliation_status_all_pass(gate_output):
    df_rec = gate_output["df_rec"]
    assert (df_rec["reconciliation_status"] == "PASS").all()


# -------------------------------------------------------------
# 6. Contradiction & Governance Tests (Mandatory 25-30)
# -------------------------------------------------------------

def test_027_contradiction_population_n161(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["reconciliation_verdicts"]["contradiction_population_N"] == 161


def test_028_contradiction_component_transitions_sum_161(gate_output):
    df_rec = gate_output["df_rec"].set_index("transition")
    act_rej_n = int(df_rec.loc["ACT -> REJECT", "reconstructed_N"])
    wat_rej_n = int(df_rec.loc["WATCH -> REJECT", "reconstructed_N"])
    wai_rej_n = int(df_rec.loc["WAIT -> REJECT", "reconstructed_N"])
    ins_rej_n = int(df_rec.loc["INSUFFICIENT -> REJECT", "reconstructed_N"])
    assert act_rej_n + wat_rej_n + wai_rej_n + ins_rej_n == 161


def test_029_outcome_blindness_zero_leak(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["reconciliation_verdicts"]["outcome_blindness"] == "PASS"


def test_030_source_hash_integrity(gate_output):
    audit_json = gate_output["audit_json"]
    hashes = audit_json["source_artifacts"]
    assert len(hashes) == 3
    assert all(len(h) == 64 for h in hashes.values())


def test_031_manifest_contains_5_artifacts(gate_output):
    manifest = gate_output["manifest_json"]
    assert len(manifest) == 5
    assert all(len(h) == 64 for h in manifest.values())


def test_032_unresolved_numerical_discrepancies_zero(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["reconciliation_verdicts"]["unresolved_numerical_discrepancies"] == 0


def test_033_scientific_firewall_verifications(gate_output):
    val_json = gate_output["val_json"]
    verdicts = val_json["reconciliation_verdicts"]
    assert verdicts["causality"] == "NOT_PROVEN"
    assert verdicts["standalone_alpha"] == "NOT_PROVEN"
    assert verdicts["strategy_optimization"] == "BLOCKED"
    assert verdicts["strategy_readiness"] == "NOT_READY"
    assert verdicts["zzz_14_8_1_2_status"] == "CLOSED"
    assert verdicts["zzz_14_8_1_status"] == "CLOSED"


# -------------------------------------------------------------
# 7. Adversarial Red Team Attacks (Mandatory 31-50)
# -------------------------------------------------------------

def test_034_red_team_total_attacks_35(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["red_team_summary"]["total_attacks"] == 35


def test_035_red_team_all_attacks_pass(gate_output):
    val_json = gate_output["val_json"]
    assert val_json["red_team_summary"]["red_team_verdict"] == "PASS"
    assert val_json["red_team_summary"]["passed_attacks"] == 35
    assert val_json["red_team_summary"]["failed_attacks"] == 0


@pytest.mark.parametrize("atk_idx", range(1, 36))
def test_036_to_070_individual_red_team_attacks(gate_output, atk_idx):
    val_json = gate_output["val_json"]
    atk_id = f"ATK-{atk_idx:02d}"
    atk = next((a for a in val_json["red_team_attacks"] if a["attack_id"] == atk_id), None)
    assert atk is not None, f"Attack {atk_id} not found in validation JSON"
    assert atk["defense_status"] == "PASS", f"Attack {atk_id} failed defense test"


# -------------------------------------------------------------
# 8. Deterministic Dual-Run Reproducibility
# -------------------------------------------------------------

def test_071_dual_run_exact_hash_reproducibility():
    gate1 = ZZZ14812OutcomeAggregationGate()
    res1 = gate1.run_gate()
    h1 = res1["manifest"]["reports/zzz14_8_1_2_reconciliation.csv"]

    gate2 = ZZZ14812OutcomeAggregationGate()
    res2 = gate2.run_gate()
    h2 = res2["manifest"]["reports/zzz14_8_1_2_reconciliation.csv"]

    assert h1 == h2
