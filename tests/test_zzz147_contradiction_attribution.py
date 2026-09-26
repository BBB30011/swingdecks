"""
tests/test_zzz147_contradiction_attribution.py

Unit test suite for Batch ZZZ.14.7:
Contradiction Information Attribution Main Orchestrator & Benchmark Engine.
Contains 20 automated unit tests verifying:
1. Orchestrator initialization and sub-engine wiring.
2. Information value decomposition across all 161 contradiction disclosures.
3. Semantic novelty and redundancy audit classifications.
4. Independent reference benchmark (N=500 ground truth items).
5. Full gate execution pipeline (execute_full_scientific_gate).
6. Single Source of Truth Canonical Results JSON (zzz14_7_canonical_results.json) schema.
7. Verification of all generated CSV and JSON report artifacts.
8. Artifact manifest completeness and SHA-256 hashes.
9. Separation of Question A, B, and C answers.
10. Scientific governance invariants (CAUSALITY=NOT_PROVEN, STANDALONE_ALPHA=NOT_PROVEN, STRATEGY_READINESS=NOT_READY).
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz147_contradiction_attribution import ZZZ147ContradictionAttributionEngine


@pytest.fixture(scope="module")
def attribution_engine():
    return ZZZ147ContradictionAttributionEngine()


@pytest.fixture(scope="module")
def gate_execution(attribution_engine):
    manifest = attribution_engine.execute_full_scientific_gate()
    canon_path = "reports/zzz14_7_canonical_results.json"
    with open(canon_path, "r") as f:
        canon_json = json.load(f)
    return canon_json, manifest


# 1. Orchestrator Initialization & Sub-Engines
def test_orchestrator_initialization(attribution_engine):
    assert attribution_engine.ladder_engine is not None
    assert attribution_engine.inference_engine is not None
    assert attribution_engine.firewall_engine is not None
    assert attribution_engine.drift_engine is not None


# 2. Information Value Decomposition Shape
def test_information_attribution_decomposition_shape(attribution_engine):
    df_matrix, df_population, _ = attribution_engine.ladder_engine.load_canonical_data()
    df_ladder, _ = attribution_engine.ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    df_attr, summary = attribution_engine.decompose_information_attribution(df_ladder)
    assert len(df_attr) == 161
    assert summary["total_contradiction_items"] == 161


# 3. Information Contribution Categories
def test_information_contribution_categories(attribution_engine):
    df_matrix, df_population, _ = attribution_engine.ladder_engine.load_canonical_data()
    df_ladder, _ = attribution_engine.ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    df_attr, summary = attribution_engine.decompose_information_attribution(df_ladder)
    valid_categories = {
        "CONTRADICTORY_INFORMATION", "NEW_SEMANTIC_INFORMATION", "REFINEMENT", "UNKNOWN", "DUPLICATE"
    }
    assert set(df_attr["information_contribution"].unique()).issubset(valid_categories)


# 4. Semantic Novelty Distribution
def test_semantic_novelty_distribution(attribution_engine):
    df_matrix, df_population, _ = attribution_engine.ladder_engine.load_canonical_data()
    df_ladder, _ = attribution_engine.ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    df_attr, summary = attribution_engine.decompose_information_attribution(df_ladder)
    assert "SEMANTICALLY_NOVEL" in summary["novelty_breakdown"]
    assert "OBSERVED" in summary["semantic_novelty_verdict"]


# 5. Independent Reference Benchmark (N=500)
def test_independent_reference_benchmark_n500(attribution_engine):
    df_bench, summary = attribution_engine.evaluate_independent_semantic_benchmark(n_benchmark=500)
    assert len(df_bench) == 9
    assert summary["total_benchmark_items"] == 500
    assert summary["overall_mean_score_pct"] >= 95.0
    assert summary["benchmark_verdict"] == "PASS"


# 6. Full Gate Execution Success
def test_full_gate_execution_success(gate_execution):
    canon_json, manifest = gate_execution
    assert canon_json is not None
    assert manifest is not None


# 7. Single Source of Truth Canonical Results JSON Schema
def test_canonical_results_json_schema(gate_execution):
    canon_json, _ = gate_execution
    required_root_keys = [
        "batch", "gate_title", "timestamp", "hashes", "population_metrics",
        "primary_estimand", "nested_model_comparison", "coverage_confounding",
        "event_cluster_sensitivities", "placebo_metrics", "negative_control_metrics",
        "decision_attribution_channels", "temporal_oos_metrics",
        "longitudinal_drift_metrics", "semantic_benchmark", "firewall_and_red_team",
        "gate_answers", "final_classifications"
    ]
    for k in required_root_keys:
        assert k in canon_json, f"Missing required root key in canonical json: {k}"


# 8. Primary Estimand Values in Canonical JSON
def test_primary_estimand_in_json(gate_execution):
    canon_json, _ = gate_execution
    prim = canon_json["primary_estimand"]
    assert prim["estimand_id"] == "ATT_INFO_161"
    assert np.isclose(prim["effect_pp"], -2.863, atol=0.05)
    assert prim["p_ols"] < 0.001
    assert prim["p_date_clustered"] < 0.001
    assert prim["p_wild_bootstrap"] < 0.001


# 9. Separation of Questions A, B, and C in Canonical JSON
def test_three_questions_answers(gate_execution):
    canon_json, _ = gate_execution
    answers = canon_json["gate_answers"]
    assert "YES" in answers["question_a_semantic_novelty"]
    assert "OBSERVED" in answers["question_b_incremental_discrimination"]
    assert "NOT_PROVEN" in answers["question_c_trading_alpha"]


# 10. Governance Invariants in Closing Block
def test_governance_invariants_closing_block(gate_execution):
    canon_json, _ = gate_execution
    fc = canon_json["final_classifications"]
    assert fc["POPULATION_IDENTITY"] == "EXACT"
    assert fc["INFORMATION_INTEGRITY"] == "PASS"
    assert fc["INFORMATION_NOVELTY"] == "OBSERVED"
    assert fc["INCREMENTAL_INFORMATION"] == "OBSERVED"
    assert fc["INCREMENTAL_DISCRIMINATION"] == "OBSERVED"
    assert fc["INFERENCE_ROBUSTNESS"] == "ROBUST"
    assert fc["COVERAGE_CONFOUNDING"] == "LOW"
    assert fc["TEMPORAL_GENERALIZATION"] == "SUPPORTED"
    assert fc["CAUSALITY"] == "NOT_PROVEN"
    assert fc["STANDALONE_ALPHA"] == "NOT_PROVEN"
    assert fc["STRATEGY_OPTIMIZATION"] == "BLOCKED"
    assert fc["STRATEGY_READINESS"] == "NOT_READY"
    assert fc["REPRODUCIBILITY"] == "PASS"
    assert fc["RED_TEAM"] == "PASS"
    assert fc["SCIENTIFIC_FIREWALL"] == "PASS"
    assert fc["ZZZ_14_8_STATUS"] == "ELIGIBLE"
    assert fc["FINAL_CLASSIFICATION"] == "INCREMENTAL_DISCRIMINATION_OBSERVED_CAUSAL_ALPHA_NOT_PROVEN"


# 11. Artifact Manifest Existence & Integrity
def test_manifest_artifacts_exist(gate_execution):
    _, manifest = gate_execution
    for path in manifest["artifacts_generated"]:
        assert os.path.exists(path), f"Artifact file missing: {path}"
        assert os.path.getsize(path) > 0


# 12. Setup Matrix Report File Exists
def test_setup_matrix_report_file():
    path = "reports/zzz14_7_setup_matrix.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 1760


# 13. Information Attribution Report File Exists
def test_information_attribution_report_file():
    path = "reports/zzz14_7_information_attribution.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 161


# 14. Support Report File Exists
def test_support_report_file():
    path = "reports/zzz14_7_support.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 1760


# 15. Inference Matrix Report File Exists
def test_inference_matrix_report_file():
    path = "reports/zzz14_7_inference_matrix.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 7


# 16. Placebo Report File Exists
def test_placebo_report_file():
    path = "reports/zzz14_7_placebo.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 7


# 17. Negative Controls Report File Exists
def test_negative_controls_report_file():
    path = "reports/zzz14_7_negative_controls.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 3


# 18. OOS Report File Exists
def test_oos_report_file():
    path = "reports/zzz14_7_oos.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 3


# 19. Drift Report File Exists
def test_drift_report_file():
    path = "reports/zzz14_7_drift.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 4


# 20. Red Team Report File Exists
def test_red_team_report_file():
    path = "reports/zzz14_7_red_team.csv"
    assert os.path.exists(path)
    df = pd.read_csv(path)
    assert len(df) == 63
    assert (df["status"] == "PASS").all()
