"""
tests/test_zzz147_drift.py

Unit test suite for Batch ZZZ.14.7:
Generalization, Longitudinal Drift, Survivorship & 63-Attack Red Team Engine.
Contains 20 automated unit tests verifying:
1. Temporal partitions (Development 2016–2023, Validation 2024, OOS 2025–2026).
2. Consistent directional effect across all temporal splits.
3. Longitudinal era drift stability across 4 periods (2016–2026).
4. Full 63-Attack Adversarial Red Team Battery (Domains A to BK: 100% PASS).
5. Specific high-risk attacks (H5 leakage, Placebo, Estimator switching, Causal inflation).
6. Dual-run exact deterministic hash reproducibility.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz147_information_layers import ZZZ147InformationLadderEngine
from core.zzz147_drift import ZZZ147DriftEngine


@pytest.fixture(scope="module")
def ladder_engine():
    return ZZZ147InformationLadderEngine()


@pytest.fixture(scope="module")
def drift_engine():
    return ZZZ147DriftEngine()


@pytest.fixture(scope="module")
def ladder_data(ladder_engine):
    df_matrix, df_population, _ = ladder_engine.load_canonical_data()
    df_ladder, _ = ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    return df_ladder


# 1. Temporal Partitions Execution
def test_temporal_partitions_shape(drift_engine, ladder_data):
    df_oos, summary = drift_engine.evaluate_temporal_partitions(ladder_data)
    assert len(df_oos) == 3
    assert summary["total_partitions"] == 3
    assert "PASS" in summary["temporal_consistency"]


# 2. Consistent Directional Effect Across Partitions
def test_temporal_partitions_consistency(drift_engine, ladder_data):
    df_oos, _ = drift_engine.evaluate_temporal_partitions(ladder_data)
    for _, row in df_oos.iterrows():
        assert row["excess_differential_pp"] < -2.0
        assert row["treatment_negative_rate_pct"] > 70.0
        assert row["temporal_generalization_status"] == "CONSISTENT_DIRECTION"


# 3. Longitudinal Era Drift Audit (4 Eras)
def test_longitudinal_era_drift_audit(drift_engine, ladder_data):
    df_drift, summary = drift_engine.evaluate_longitudinal_drift(ladder_data)
    assert len(df_drift) == 4
    assert summary["total_eras_audited"] == 4
    assert summary["drift_audit_verdict"] == "PASS"


# 4. Longitudinal Contradiction Rate Stability
def test_longitudinal_contradiction_rate_bounds(drift_engine, ladder_data):
    df_drift, _ = drift_engine.evaluate_longitudinal_drift(ladder_data)
    for _, row in df_drift.iterrows():
        assert 5.0 <= row["contradiction_rate_pct"] <= 15.0
        assert row["drift_verdict"] == "STABLE_WITHIN_EXPECTED_BOUNDS"


# 5. 63-Attack Adversarial Red Team Battery Execution
def test_adversarial_red_team_battery_shape(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    assert len(df_rt) == 63
    assert (df_rt["status"] == "PASS").all()


# 6. Red Team Attack A: Population Identity
def test_red_team_attack_a(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_A_POPULATION_IDENTITY_DRIFT"].iloc[0]
    assert att["status"] == "PASS"
    assert "1,760" in att["defense_evidence"]


# 7. Red Team Attack B: Denominator Manipulation
def test_red_team_attack_b(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_B_DENOMINATOR_MANIPULATION"].iloc[0]
    assert att["status"] == "PASS"
    assert "161" in att["defense_evidence"]


# 8. Red Team Attack D: H5 Outcome Leakage
def test_red_team_attack_d(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_D_H5_LEAKAGE_TO_AGENT2"].iloc[0]
    assert att["status"] == "PASS"


# 9. Red Team Attack G: Future Evidence Injection
def test_red_team_attack_g(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_G_FUTURE_EVIDENCE_INJECTION"].iloc[0]
    assert att["status"] == "PASS"


# 10. Red Team Attack N/O/P: Dependence Controls
def test_red_team_dependence_attacks(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    for a_id in ["RED_N_TICKER_CLUSTERING_BIAS", "RED_O_DATE_CLUSTERING_BIAS", "RED_P_COMMODITY_CLUSTERING_BIAS"]:
        att = df_rt[df_rt["attack_code"] == a_id].iloc[0]
        assert att["status"] == "PASS"


# 11. Red Team Attack R: Common Support Caliper Manipulation
def test_red_team_attack_r(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_R_COMMON_SUPPORT_MANIPULATION"].iloc[0]
    assert att["status"] == "PASS"


# 12. Red Team Attack V: Estimator Switching
def test_red_team_attack_v(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_V_ESTIMATOR_SWITCHING"].iloc[0]
    assert att["status"] == "PASS"


# 13. Red Team Attack Y: Placebo Reproduction
def test_red_team_attack_y(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att = df_rt[df_rt["attack_code"] == "RED_Y_PLACEBO_REPRODUCTION"].iloc[0]
    assert att["status"] == "PASS"


# 14. Red Team Attack BD/BE: Missingness and Unknown Preservation
def test_red_team_attack_bd_be(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att_bd = df_rt[df_rt["attack_code"] == "RED_BD_MISSINGNESS_SUPPRESSION"].iloc[0]
    att_be = df_rt[df_rt["attack_code"] == "RED_BE_UNKNOWN_TO_FALSE_CONVERSION"].iloc[0]
    assert att_bd["status"] == "PASS"
    assert att_be["status"] == "PASS"


# 15. Red Team Attack BF/BG: Causal Language Inflation
def test_red_team_attack_bf_bg(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    att_bf = df_rt[df_rt["attack_code"] == "RED_BF_CAUSAL_LANGUAGE_INFLATION"].iloc[0]
    att_bg = df_rt[df_rt["attack_code"] == "RED_BG_AVOIDED_LOSS_LANGUAGE_INFLATION"].iloc[0]
    assert att_bf["status"] == "PASS"
    assert att_bg["status"] == "PASS"


# 16. Dual-Run Reproducibility Verification
def test_dual_run_reproducibility(drift_engine, ladder_data):
    df_repro, summary = drift_engine.execute_dual_run_reproducibility(ladder_data)
    assert len(df_repro) == 3
    assert summary["reproducibility_verdict"] == "PASS"
    assert summary["run_1_hash"] == summary["run_2_hash"]


# 17. Red Team 100% Pass Invariant
def test_red_team_all_pass_invariant(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    failed_attacks = df_rt[df_rt["status"] != "PASS"]
    assert len(failed_attacks) == 0, f"Found failed red team attacks: {failed_attacks['attack_code'].tolist()}"


# 18. Red Team Attack Categories
def test_red_team_categories(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    unique_cats = df_rt["category"].unique()
    assert len(unique_cats) >= 10


# 19. Red Team Attack Descriptions Non-Empty
def test_red_team_descriptions_non_empty(drift_engine):
    df_rt = drift_engine.execute_63_adversarial_red_team_attacks()
    for _, row in df_rt.iterrows():
        assert len(row["description"]) > 10
        assert len(row["defense_evidence"]) > 10


# 20. Dual-Run Audit Dimensions
def test_dual_run_audit_dimensions(drift_engine, ladder_data):
    df_repro, _ = drift_engine.execute_dual_run_reproducibility(ladder_data)
    dims = set(df_repro["audit_dimension"].unique())
    assert dims == {"SETUP_MATRIX_SHA256", "TOTAL_SETUPS_COUNT", "CONTRADICTION_COUNT"}
