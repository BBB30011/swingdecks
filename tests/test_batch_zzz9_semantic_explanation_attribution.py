"""
tests/test_batch_zzz9_semantic_explanation_attribution.py

Regression and Validation Tests for Batch ZZZ.9:
Historical Semantic Explanation & Attribution Expansion.
"""

import os
import sys
import pytest
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.semantic_substrate_engine import SemanticSubstrateEngine
from core.semantic_attribution_engine import SemanticAttributionEngine, ReconstructedContextAtT
from core.attribution_schemas import SpecificityStatus, RedTeamStatus, CoverageState

@pytest.fixture(scope="module")
def substrate_engine():
    return SemanticSubstrateEngine("tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def attribution_engine():
    return SemanticAttributionEngine("tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def sample_dataset():
    parquet_path = "gates/evidence/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "gates/evidence/zzz81_ablation_results.parquet"
    assert os.path.exists(parquet_path), f"Required data parquet {parquet_path} not found"
    df = pd.read_parquet(parquet_path)
    return df

def test_01_substrate_population_and_entity_resolution(substrate_engine):
    """Verifies that the DuckDB semantic substrate populates and resolves entities conservatively."""
    counts = substrate_engine.populate_substrate()
    assert counts["dim_entity"] >= 18
    assert counts["dim_entity_alias"] >= 24
    assert counts["fact_exposure"] >= 7
    assert counts["fact_relationship"] >= 10
    
    # Exact and alias resolution
    res_adro = substrate_engine.resolve_entity("ADRO")
    assert res_adro["entity_id"] == "ENT_ADRO"
    assert res_adro["confidence"] >= 0.95
    
    res_name = substrate_engine.resolve_entity("Bank Central Asia")
    assert res_name["entity_id"] == "ENT_BBCA"
    
    # Unresolved unknown
    res_unresolved = substrate_engine.resolve_entity("NON_EXISTENT_TICKER_XYZ")
    assert res_unresolved["entity_id"] == "UNRESOLVED"
    assert res_unresolved["confidence"] == 0.0

def test_02_pit_temporal_boundary_and_future_exclusion(attribution_engine):
    """Verifies that future events (published > T) are strictly excluded from reconstruction."""
    candidate_row = {
        "symbol": "ADRO",
        "date": "2025-10-01T00:00:00+0700",
        "quant_score": 85.0,
        "rel_vol": 1.5,
        "signal_day_return": 0.03
    }
    day_universe = [{"symbol": "ADRO", "ret_c_prev_to_close": 0.03}, {"symbol": "ITMG", "ret_c_prev_to_close": 0.02}]
    
    ctx = attribution_engine.reconstruct_candidate_context_at_t(candidate_row, day_universe)
    assert ctx.entity_id == "ENT_ADRO"
    assert ctx.red_team_result.time_leakage == "PASS"

def test_03_temporal_relationship_and_exposure_queries(attribution_engine):
    """Verifies that exposures and relationships obey PIT valid_from / valid_to bounds."""
    # INCO acquired MIND ID relationship on 2024-06-28
    cand_inco_2025 = {
        "symbol": "INCO",
        "date": "2025-11-01T00:00:00+0700",
        "quant_score": 90.0,
        "rel_vol": 1.4,
        "signal_day_return": 0.02
    }
    ctx_inco = attribution_engine.reconstruct_candidate_context_at_t(cand_inco_2025, [])
    assert ctx_inco.commodity_context["has_commodity_exposure"] is True
    assert any(e["target"] == "ENT_NICKEL" for e in ctx_inco.commodity_context["exposures"])
    assert ctx_inco.ownership_context["has_known_controller"] is True

def test_04_peer_counterfactual_and_differential_arithmetic(attribution_engine):
    """Verifies peer counterfactual arithmetic: expected vs actual movers."""
    cand_itmg = {
        "symbol": "ITMG",
        "date": "2026-01-05T00:00:00+0700",
        "quant_score": 95.0,
        "rel_vol": 2.1,
        "signal_day_return": 0.04
    }
    day_universe = [
        {"symbol": "ITMG", "ret_c_prev_to_close": 0.04},
        {"symbol": "ADRO", "ret_c_prev_to_close": 0.03},
        {"symbol": "PTBA", "ret_c_prev_to_close": 0.025},
        {"symbol": "BBCA", "ret_c_prev_to_close": 0.00}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand_itmg, day_universe)
    
    cf = ctx.peer_counterfactual
    assert "ADRO" in cf["expected_affected_universe"]
    assert "PTBA" in cf["expected_affected_universe"]
    assert "ITMG" in cf["actual_movers"]
    assert ctx.sector_context["specificity_status"] == "SECTOR_WIDE"
    assert np.isclose(ctx.sector_context["peer_mean_return"], 0.0275, atol=1e-4)
    assert np.isclose(ctx.sector_context["differential_return"], 0.0125, atol=1e-4)

def test_05_preservation_of_unknown_and_no_hallucinations(attribution_engine):
    """Verifies that missing fundamental filings and news default to UNKNOWN without hallucination."""
    cand_tlkm = {
        "symbol": "TLKM",
        "date": "2025-10-15T00:00:00+0700",
        "quant_score": 80.0,
        "rel_vol": 1.3,
        "signal_day_return": 0.01
    }
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand_tlkm, [])
    assert ctx.fundamental_context["disclosure_status"] == "NO_EVIDENCE_IN_DATASET"
    assert "Quarterly fundamental filing disclosures not populated at T" in ctx.unknowns

def test_06_red_team_adversarial_checks(attribution_engine):
    """Verifies that the Red Team performs 4-dimension adversarial audits."""
    cand_adro = {
        "symbol": "ADRO",
        "date": "2026-01-10T00:00:00+0700",
        "quant_score": 85.0,
        "rel_vol": 1.8,
        "signal_day_return": 0.04
    }
    day_universe = [{"symbol": "ADRO", "ret_c_prev_to_close": 0.04}, {"symbol": "ITMG", "ret_c_prev_to_close": 0.03}]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand_adro, day_universe)
    
    rt = ctx.red_team_result
    assert rt.time_leakage == "PASS"
    assert rt.logic_consistency == "PASS"
    assert rt.overall_status in (RedTeamStatus.PASS, RedTeamStatus.WEAK)

def test_07_thesis_and_outcome_evaluation(attribution_engine):
    """Verifies thesis generation and post-T forward outcome alignment."""
    cand_ptba = {
        "symbol": "PTBA",
        "date": "2026-03-02T00:00:00+0700",
        "quant_score": 90.0,
        "rel_vol": 1.6,
        "signal_day_return": 0.03,
        "H5": 0.045
    }
    day_universe = [{"symbol": "PTBA", "ret_c_prev_to_close": 0.03}, {"symbol": "ADRO", "ret_c_prev_to_close": 0.02}]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand_ptba, day_universe)
    
    assert ctx.thesis_classification == "SUPPORTED"
    assert ctx.outcome_alignment == "THESIS_SUPPORTED_BY_OUTCOME"

def test_08_reconstruction_of_all_73_layer_e_candidates(sample_dataset, attribution_engine):
    """Verifies that all 73 Layer E candidates are successfully reconstructed at T."""
    if "sel_layer_e" in sample_dataset.columns:
        layer_e_df = sample_dataset[sample_dataset["sel_layer_e"]]
    else:
        layer_e_df = sample_dataset
    assert len(layer_e_df) == 73
    
    contexts, summary_df = attribution_engine.evaluate_all_layer_e_candidates(sample_dataset)
    assert len(contexts) == 73
    assert len(summary_df) == 73
    
    # Supported theses must be predominantly Commodity-Exposed
    supp_df = summary_df[summary_df["thesis_classification"] == "SUPPORTED"]
    assert supp_df["has_commodity_exposure"].all()
    assert supp_df["H5"].mean() > 0.010
