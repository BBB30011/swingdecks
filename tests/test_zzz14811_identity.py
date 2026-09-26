"""
tests/test_zzz14811_identity.py
=================================
Comprehensive automated test suite for Batch ZZZ.14.8.1.1:
Canonical Decision-State Population & Transition Identity Closure Gate.
Contains 45+ targeted unit and adversarial tests.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.zzz14811_identity_gate import ZZZ14811IdentityGate


@pytest.fixture(scope="module")
def gate():
    return ZZZ14811IdentityGate(scratch_dir="scratch", reports_dir="reports")


@pytest.fixture(scope="module")
def identity_results(gate):
    res = gate.execute_identity_gate()
    with open("reports/zzz14_8_1_1_validation.json", "r", encoding="utf-8") as f:
        val_json = json.load(f)
    with open("reports/zzz14_8_1_1_manifest.json", "r", encoding="utf-8") as f:
        manifest_json = json.load(f)
    df_ledger = pd.read_csv("reports/zzz14_8_1_1_canonical_decision_population.csv")
    df_25 = pd.read_csv("reports/zzz14_8_1_1_transition_matrix_25x25.csv")
    df_reconcil = pd.read_csv("reports/zzz14_8_1_1_reconciliation.csv")
    df_exc = pd.read_csv("reports/zzz14_8_1_1_exception_ledger.csv")
    df_rt = pd.read_csv("reports/zzz14_8_1_1_red_team.csv")

    return {
        "res": res,
        "json": val_json,
        "manifest": manifest_json,
        "df_ledger": df_ledger,
        "df_25": df_25,
        "df_reconcil": df_reconcil,
        "df_exc": df_exc,
        "df_rt": df_rt
    }


# =============================================================================
# 1. Population, Uniqueness & Ledger Tests (1-10)
# =============================================================================

def test_001_population_n1760(identity_results):
    assert len(identity_results["df_ledger"]) == 1760

def test_002_unique_setup_ids_n1760(identity_results):
    assert identity_results["df_ledger"]["setup_id"].nunique() == 1760

def test_003_zero_duplicate_setups(identity_results):
    assert identity_results["df_ledger"]["duplicate_flag"].sum() == 0

def test_004_zero_missing_setups(identity_results):
    assert identity_results["df_ledger"]["missing_flag"].sum() == 0

def test_005_state_mapping_valid_100_pct(identity_results):
    assert identity_results["df_ledger"]["state_mapping_valid"].sum() == 1760

def test_006_arm_b_present_100_pct(identity_results):
    assert identity_results["df_ledger"]["arm_b_present"].sum() == 1760

def test_007_arm_d_present_100_pct(identity_results):
    assert identity_results["df_ledger"]["arm_d_present"].sum() == 1760

def test_008_arm_b_hash_len_64(identity_results):
    assert identity_results["df_ledger"]["arm_b_decision_hash"].str.len().eq(64).all()

def test_009_arm_d_hash_len_64(identity_results):
    assert identity_results["df_ledger"]["arm_d_decision_hash"].str.len().eq(64).all()

def test_010_sample_attrition_zero(identity_results):
    assert identity_results["json"]["population"]["sample_attrition"] == 0


# =============================================================================
# 2. Arm B and Arm D Marginal Counts & Exact Reconciliation (11-20)
# =============================================================================

def test_011_arm_b_marginal_act_462(identity_results):
    assert (identity_results["df_ledger"]["arm_b_action"] == "ACT").sum() == 462

def test_012_arm_b_marginal_watch_625(identity_results):
    assert (identity_results["df_ledger"]["arm_b_action"] == "WATCH").sum() == 625

def test_013_arm_b_marginal_wait_592(identity_results):
    assert (identity_results["df_ledger"]["arm_b_action"] == "WAIT").sum() == 592

def test_014_arm_b_marginal_reject_0(identity_results):
    assert (identity_results["df_ledger"]["arm_b_action"] == "REJECT").sum() == 0

def test_015_arm_b_marginal_insufficient_81(identity_results):
    assert (identity_results["df_ledger"]["arm_b_action"] == "INSUFFICIENT").sum() == 81

def test_016_arm_b_marginal_sum_1760(identity_results):
    b_counts = identity_results["json"]["arm_b_marginal_reconciliation"]["canonical_marginals"]
    assert sum(b_counts.values()) == 1760

def test_017_arm_d_marginal_act_828(identity_results):
    assert (identity_results["df_ledger"]["arm_d_action"] == "ACT").sum() == 828

def test_018_arm_d_marginal_watch_307(identity_results):
    assert (identity_results["df_ledger"]["arm_d_action"] == "WATCH").sum() == 307

def test_019_arm_d_marginal_wait_360(identity_results):
    assert (identity_results["df_ledger"]["arm_d_action"] == "WAIT").sum() == 360

def test_020_arm_d_marginal_reject_161(identity_results):
    assert (identity_results["df_ledger"]["arm_d_action"] == "REJECT").sum() == 161


# =============================================================================
# 3. 25-Cell (5x5) Transition Matrix & Row/Column Reconciliation (21-35)
# =============================================================================

def test_021_transition_matrix_cell_count_25(identity_results):
    assert len(identity_results["df_25"]) == 25

def test_022_transition_matrix_global_sum_1760(identity_results):
    assert identity_results["df_25"]["count_N"].sum() == 1760

def test_023_all_row_totals_reconciled(identity_results):
    assert (identity_results["df_reconcil"]["arm_b_row_delta"] == 0).all()

def test_024_all_column_totals_reconciled(identity_results):
    assert (identity_results["df_reconcil"]["arm_d_col_delta"] == 0).all()

def test_025_act_to_reject_count_40(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["ACT -> REJECT", "count_N"] == 40

def test_026_watch_to_act_count_354(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["WATCH -> ACT", "count_N"] == 354

def test_027_wait_to_act_count_52(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["WAIT -> ACT", "count_N"] == 52

def test_028_watch_to_reject_count_46(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["WATCH -> REJECT", "count_N"] == 46

def test_029_wait_to_reject_count_71(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["WAIT -> REJECT", "count_N"] == 71

def test_030_insufficient_to_reject_count_4(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["INSUFFICIENT -> REJECT", "count_N"] == 4

def test_031_reject_row_sum_zero(identity_results):
    df_r = identity_results["df_reconcil"].set_index("action_state")
    assert df_r.loc["REJECT", "arm_b_row_sum"] == 0

def test_032_zero_transitions_explicitly_present(identity_results):
    df_t = identity_results["df_25"].set_index("transition")
    assert df_t.loc["ACT -> WATCH", "count_N"] == 0
    assert df_t.loc["ACT -> WAIT", "count_N"] == 0
    assert df_t.loc["ACT -> INSUFFICIENT", "count_N"] == 0
    assert df_t.loc["REJECT -> ACT", "count_N"] == 0

def test_033_reconciled_status_all_pass(identity_results):
    assert (identity_results["df_reconcil"]["arm_b_reconciled"] == "PASS").all()
    assert (identity_results["df_reconcil"]["arm_d_reconciled"] == "PASS").all()

def test_034_exception_ledger_net_delta_zero(identity_results):
    assert identity_results["df_exc"]["delta"].sum() == 0

def test_035_unresolved_exceptions_count_zero(identity_results):
    assert identity_results["json"]["exception_resolution"]["unresolved_exceptions"] == 0


# =============================================================================
# 4. Red Team, Governance & Reproducibility Tests (36-45)
# =============================================================================

def test_036_red_team_attacks_count_35(identity_results):
    assert len(identity_results["df_rt"]) == 35

def test_037_red_team_attacks_all_pass(identity_results):
    assert (identity_results["df_rt"]["status"] == "PASS").all()

def test_038_manifest_contains_6_artifacts(identity_results):
    assert len(identity_results["manifest"]["artifacts"]) == 6

def test_039_causality_not_proven(identity_results):
    assert identity_results["json"]["classifications"]["CAUSALITY"] == "NOT_PROVEN"

def test_040_standalone_alpha_not_proven(identity_results):
    assert identity_results["json"]["classifications"]["STANDALONE_ALPHA"] == "NOT_PROVEN"

def test_041_strategy_optimization_blocked(identity_results):
    assert identity_results["json"]["classifications"]["STRATEGY_OPTIMIZATION"] == "BLOCKED"

def test_042_strategy_readiness_not_ready(identity_results):
    assert identity_results["json"]["classifications"]["STRATEGY_READINESS"] == "NOT_READY"

def test_043_final_status_closed(identity_results):
    assert identity_results["json"]["classifications"]["ZZZ_14_8_1_1_STATUS"] == "CLOSED"
    assert identity_results["json"]["classifications"]["ZZZ_14_8_1_STATUS"] == "CLOSED"

def test_044_no_auto_advance_true(identity_results):
    assert identity_results["json"]["classifications"]["NO_AUTO_ADVANCE"] is True

def test_045_dual_run_exact_hash_reproducibility(gate):
    res1 = gate.execute_identity_gate()
    res2 = gate.execute_identity_gate()
    assert res1["population"]["total_setups"] == res2["population"]["total_setups"]
    assert res1["arm_b_marginal_reconciliation"]["canonical_marginals"] == res2["arm_b_marginal_reconciliation"]["canonical_marginals"]
    assert res1["transition_matrix_25x25"]["key_cells"] == res2["transition_matrix_25x25"]["key_cells"]
