"""
tests/test_zzz145_ai_attribution.py

Unit test suite for Batch ZZZ.14.5:
AI Information Attribution, Ablation & Incremental Discrimination Scientific Gate.
Contains 28 comprehensive automated unit tests validating:
1. Frozen Setup Population & 5 Information Partitions (N=1,760 across 80 tickers, 2016-2026).
2. Independent Reference Benchmark Ground Truth Set (N=500 items).
3. Retrieval Quality, Entity Resolution, and Contradiction Detection.
4. AI Ablation Ladder (A0 to A5) stepwise evaluation.
5. Information Novelty & Redundancy Metric Decomposition.
6. Falsification Battery (Real AI vs Structure-Matched Random vs Placebo).
7. Nested Econometric Attribution Models (M0 to M3).
8. Cross-Dimensional Audits (Ticker, Event, Regime, Coverage, Cycle, Drift).
9. Model & Prompt Provenance Registry.
10. 62-Attack Adversarial AI Red Team Battery.
11. Dual-Run Exact Deterministic Reproducibility.
12. 23-Dimension Scientific Result Matrix & Scientific Classifications.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz145_ai_attribution import (
    ZZZ145AIAttributionEngine,
    CANONICAL_12_TICKERS,
    EXTENDED_80_UNIVERSE,
    COMMODITY_TICKERS,
    EVENT_CLASSES,
    MARKET_REGIMES,
    TIME_PERIODS,
    TRANSMISSION_CHANNELS
)


@pytest.fixture(scope="module")
def engine():
    return ZZZ145AIAttributionEngine()


@pytest.fixture(scope="module")
def setup_population(engine):
    return engine.load_frozen_setup_population()


@pytest.fixture(scope="module")
def ref_benchmark(engine):
    return engine.build_reference_benchmark_ground_truth(n_items=500)


# 1. Setup Population Structure & 80-Ticker Universe
def test_01_setup_population_structure(setup_population):
    df_pop, metadata = setup_population
    assert len(df_pop) == 1760
    assert metadata["total_tickers"] == 80
    assert metadata["total_setups"] == 1760
    assert set(EXTENDED_80_UNIVERSE).issubset(set(df_pop["ticker"].unique()))
    assert metadata["time_horizon"] == "2016-2026"


# 2. 5 Information Partitions Present
def test_02_information_partitions_present(setup_population):
    df_pop, _ = setup_population
    # X_DETERMINISTIC
    assert {"ticker", "sector", "is_commodity", "is_canonical", "pre_5_1", "relative_volume", "momentum_score"}.issubset(set(df_pop.columns))
    # X_CONTEXT
    assert {"market_regime", "market_regime_num", "time_era", "decision_date"}.issubset(set(df_pop.columns))
    # X_COVERAGE
    assert {"coverage_tier", "archive_depth", "raw_event_count"}.issubset(set(df_pop.columns))
    # X_OUTCOME
    assert "excess_H5_pct" in df_pop.columns


# 3. Independent Reference Benchmark Set (N=500 items)
def test_03_reference_benchmark_schema(ref_benchmark):
    assert len(ref_benchmark) == 500
    expected_cols = [
        "reference_id", "ticker", "event_class", "time_era", "market_regime",
        "source_quality", "gt_entity_correct", "gt_event_correct", "gt_pit_correct",
        "gt_relevance", "gt_is_contradiction", "gt_is_material", "gt_novelty_category",
        "ai_entity_correct", "ai_pit_correct", "ai_relevance_class",
        "ai_contradiction_detected", "ai_selected", "material_retained"
    ]
    for col in expected_cols:
        assert col in ref_benchmark.columns


# 4. Reference Set Retrieval Quality (Precision, Recall, F1)
def test_04_reference_retrieval_metrics(ref_benchmark):
    tp = sum((ref_benchmark["ai_selected"]) & (ref_benchmark["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    fp = sum((ref_benchmark["ai_selected"]) & (~ref_benchmark["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    fn = sum((~ref_benchmark["ai_selected"]) & (ref_benchmark["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    
    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    
    assert prec >= 0.90
    assert rec >= 0.85
    assert f1 >= 0.88


# 5. Reference Set Entity Resolution Accuracy
def test_05_reference_entity_resolution(ref_benchmark):
    acc = float(ref_benchmark["ai_entity_correct"].mean())
    assert acc >= 0.95


# 6. Reference Set Contradiction Recall
def test_06_reference_contradiction_recall(ref_benchmark):
    contra_gt = ref_benchmark[ref_benchmark["gt_is_contradiction"]]
    if len(contra_gt) > 0:
        recall = float(contra_gt["ai_contradiction_detected"].mean())
        assert recall >= 0.90


# 7. AI Ablation Ladder Execution (A0 to A5)
def test_07_ablation_ladder_execution(engine, setup_population):
    df_pop, _ = setup_population
    df_setups, df_matrix, summary = engine.execute_ai_ablation_ladder(df_pop)
    assert len(df_setups) == 1760
    assert len(df_matrix) == 6
    expected_layers = [
        "A0_DETERMINISTIC_BASELINE", "A1_AI_RELEVANCE", "A2_AI_TRANSMISSION",
        "A3_AI_CONTRADICTION", "A4_AI_RELATIONSHIP", "A5_FULL_AI_STATE"
    ]
    assert list(df_matrix["ablation_layer"]) == expected_layers


# 8. Ablation Noise Reduction & Material Retention
def test_08_ablation_noise_and_material_retention(engine, setup_population):
    df_pop, _ = setup_population
    df_setups, df_matrix, summary = engine.execute_ai_ablation_ladder(df_pop)
    a0_ev = int(df_matrix.loc[df_matrix["ablation_layer"] == "A0_DETERMINISTIC_BASELINE", "total_events"].values[0])
    a5_ev = int(df_matrix.loc[df_matrix["ablation_layer"] == "A5_FULL_AI_STATE", "total_events"].values[0])
    
    a0_mat = int(df_matrix.loc[df_matrix["ablation_layer"] == "A0_DETERMINISTIC_BASELINE", "total_material_events"].values[0])
    a5_mat = int(df_matrix.loc[df_matrix["ablation_layer"] == "A5_FULL_AI_STATE", "total_material_events"].values[0])
    
    # Event compression ~60% reduction
    compression = a5_ev / a0_ev
    assert compression < 0.50
    # Material retention >= 90%
    retention = a5_mat / a0_mat
    assert retention >= 0.90


# 9. Ablation Contradiction Detection Count
def test_09_ablation_contradiction_count(engine, setup_population):
    df_pop, _ = setup_population
    _, df_matrix, summary = engine.execute_ai_ablation_ladder(df_pop)
    a5_contra = int(df_matrix.loc[df_matrix["ablation_layer"] == "A5_FULL_AI_STATE", "total_contradictions_flagged"].values[0])
    assert a5_contra > 0


# 10. Information Novelty Categories Breakdown
def test_10_information_novelty_categories(engine, ref_benchmark):
    df_novelty, _, summary = engine.execute_information_novelty_and_redundancy(ref_benchmark)
    assert len(df_novelty) >= 4
    categories = set(df_novelty["novelty_category"])
    assert "KNOWN_BY_DETERMINISTIC" in categories
    assert "REFINEMENT_OF_KNOWN_INFORMATION" in categories
    assert "NEW_SEMANTIC_INFORMATION" in categories


# 11. Information Redundancy Metrics
def test_11_information_redundancy_metrics(engine, ref_benchmark):
    _, df_redundancy, summary = engine.execute_information_novelty_and_redundancy(ref_benchmark)
    metric_map = dict(zip(df_redundancy["metric_name"], df_redundancy["value_pct"]))
    assert "REDUNDANCY_RATE" in metric_map
    assert "REFINEMENT_RATE" in metric_map
    assert "NOVEL_INFORMATION_RATE" in metric_map
    assert "CONTRADICTION_RATE" in metric_map
    assert metric_map["REDUNDANCY_RATE"] == 32.4
    assert metric_map["REFINEMENT_RATE"] == 38.6


# 12. Falsification Suite Execution
def test_12_falsification_suite_execution(engine, setup_population):
    df_pop, _ = setup_population
    df_falsify, df_placebo, summary = engine.execute_falsification_suite(df_pop)
    assert len(df_falsify) == 3
    assert set(df_falsify["selector_type"]) == {"REAL_AI_SELECTOR", "STRUCTURE_MATCHED_RANDOM", "SEMANTIC_PLACEBO_SELECTOR"}


# 13. Real AI Outperforms Structure-Matched Random Selector
def test_13_real_ai_vs_random_selector(engine, setup_population):
    df_pop, _ = setup_population
    df_falsify, _, summary = engine.execute_falsification_suite(df_pop)
    real_ret = float(df_falsify.loc[df_falsify["selector_type"] == "REAL_AI_SELECTOR", "top_quintile_excess_h5_pct"].values[0])
    rand_ret = float(df_falsify.loc[df_falsify["selector_type"] == "STRUCTURE_MATCHED_RANDOM", "top_quintile_excess_h5_pct"].values[0])
    assert real_ret > rand_ret


# 14. Real AI Outperforms Placebo Selector
def test_14_real_ai_vs_placebo_selector(engine, setup_population):
    df_pop, _ = setup_population
    df_falsify, _, summary = engine.execute_falsification_suite(df_pop)
    real_ret = float(df_falsify.loc[df_falsify["selector_type"] == "REAL_AI_SELECTOR", "top_quintile_excess_h5_pct"].values[0])
    plac_ret = float(df_falsify.loc[df_falsify["selector_type"] == "SEMANTIC_PLACEBO_SELECTOR", "top_quintile_excess_h5_pct"].values[0])
    assert real_ret > plac_ret


# 15. Placebo Detailed Probes Pass
def test_15_placebo_probes_pass(engine, setup_population):
    df_pop, _ = setup_population
    _, df_placebo, _ = engine.execute_falsification_suite(df_pop)
    assert len(df_placebo) == 4
    for _, row in df_placebo.iterrows():
        assert "PASS" in row["verdict"]
        assert row["p_value"] > 0.05


# 16. Nested Econometric Attribution Models (M0 to M3)
def test_16_nested_econometric_models(engine, setup_population):
    df_pop, _ = setup_population
    df_nested, summary = engine.execute_nested_econometric_attribution(df_pop)
    assert len(df_nested) == 4
    expected_models = [
        "MODEL_0_DETERMINISTIC_ONLY",
        "MODEL_1_DETERMINISTIC_PLUS_AI",
        "MODEL_2_DETERMINISTIC_AI_CONTEXT",
        "MODEL_3_FULL_NESTED_WITH_COVERAGE"
    ]
    assert list(df_nested["model_id"]) == expected_models


# 17. M3 AI Coefficient Robustness under Controls
def test_17_m3_ai_coefficient_robustness(engine, setup_population):
    df_pop, _ = setup_population
    df_nested, summary = engine.execute_nested_econometric_attribution(df_pop)
    m3_coef = float(df_nested.loc[df_nested["model_id"] == "MODEL_3_FULL_NESTED_WITH_COVERAGE", "ai_coefficient_pp"].values[0])
    assert m3_coef > 0.0


# 18. Cross-Ticker Attribution (80 Tickers Heterogeneity)
def test_18_cross_ticker_attribution(engine, setup_population):
    df_pop, _ = setup_population
    df_ticker, _, _, _, _, _ = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_ticker) == 80
    assert set(EXTENDED_80_UNIVERSE) == set(df_ticker["ticker"])


# 19. Cross-Event Attribution (12 Event Classes)
def test_19_cross_event_attribution(engine, setup_population):
    df_pop, _ = setup_population
    _, df_event, _, _, _, _ = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_event) == 12
    assert set(EVENT_CLASSES) == set(df_event["event_class"])


# 20. Cross-Regime Attribution (4 Regimes)
def test_20_cross_regime_attribution(engine, setup_population):
    df_pop, _ = setup_population
    _, _, df_regime, _, _, _ = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_regime) == 4
    assert set(MARKET_REGIMES) == set(df_regime["market_regime"])


# 21. Coverage Attribution (4 Coverage Tiers)
def test_21_coverage_attribution(engine, setup_population):
    df_pop, _ = setup_population
    _, _, _, df_cov, _, _ = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_cov) == 4
    assert set(df_cov["coverage_stratum"]) == {"HIGH_COVERAGE", "MEDIUM_COVERAGE", "LOW_COVERAGE", "ARCHIVAL_GAP"}


# 22. Cross-Cycle Attribution (4 Historical Eras)
def test_22_cross_cycle_attribution(engine, setup_population):
    df_pop, _ = setup_population
    _, _, _, _, df_cycle, _ = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_cycle) == 4
    assert set(df_cycle["calendar_period"]) == {"2016-2018", "2019-2021", "2022-2024", "2025-2026"}


# 23. AI Drift Audit
def test_23_ai_drift_audit(engine, setup_population):
    df_pop, _ = setup_population
    _, _, _, _, _, df_drift = engine.execute_cross_dimensional_and_drift_audits(df_pop)
    assert len(df_drift) == 4
    expected_dims = {"SEMANTIC_DRIFT", "SOURCE_DRIFT", "ENTITY_DRIFT", "MODEL_DRIFT"}
    assert set(df_drift["drift_dimension"]) == expected_dims


# 24. Model & Prompt Provenance Registry
def test_24_model_provenance_registry(engine):
    df_prov = engine.build_model_provenance_registry()
    assert len(df_prov) == 8
    expected_components = {
        "MODEL_IDENTIFIER", "SYSTEM_PROMPT_HASH", "SELECTOR_PROMPT_HASH",
        "EVENT_ONTOLOGY_VERSION", "SCHEMA_VERSION", "PREPROCESSOR_VERSION",
        "TEMPERATURE", "GLOBAL_SEED"
    }
    assert set(df_prov["component"]) == expected_components


# 25. 62-Attack Red Team Battery Completeness & 100% Pass
def test_25_red_team_battery_pass(engine):
    df_red = engine.execute_62_ai_red_team_attacks()
    assert len(df_red) == 62
    assert (df_red["status"] == "PASS").all()
    categories = set(df_red["category"])
    assert categories == {"PIT", "Entity", "Semantic", "Coverage", "Outcome Leakage", "Selection Bias", "Model Behavior"}


# 26. Dual-Run Exact Deterministic Reproducibility
def test_26_dual_run_reproducibility(engine, setup_population):
    df_pop, _ = setup_population
    df_repro, summary = engine.execute_dual_run_reproducibility(df_pop)
    assert summary["hash_identical"] is True
    assert (df_repro["verdict"] == "EXACT_MATCH").all()


# 27. Scientific Result Matrix Dimensions (23 Dimensions)
def test_27_scientific_result_matrix_dimensions(engine, setup_population):
    df_pop, _ = setup_population
    _, df_abl, _ = engine.execute_ai_ablation_ladder(df_pop)
    df_nested, _ = engine.execute_nested_econometric_attribution(df_pop)
    df_falsify, _, _ = engine.execute_falsification_suite(df_pop)
    df_matrix = engine.build_scientific_result_matrix(df_abl, df_nested, df_falsify)
    assert len(df_matrix) == 23


# 28. Scientific Classifications Adherence
def test_28_scientific_classifications_adherence(engine, setup_population):
    df_pop, _ = setup_population
    _, df_abl, _ = engine.execute_ai_ablation_ladder(df_pop)
    df_nested, _ = engine.execute_nested_econometric_attribution(df_pop)
    df_falsify, _, _ = engine.execute_falsification_suite(df_pop)
    df_matrix = engine.build_scientific_result_matrix(df_abl, df_nested, df_falsify)
    valid_classifications = {
        "PROVEN", "OBSERVED", "CONDITIONAL", "INCONCLUSIVE",
        "NOT_ESTIMABLE", "NOT_PROVEN", "BLOCKED"
    }
    for c in df_matrix["classification"]:
        assert c in valid_classifications
