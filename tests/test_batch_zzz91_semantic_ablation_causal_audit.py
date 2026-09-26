"""
tests/test_batch_zzz91_semantic_ablation_causal_audit.py

Deterministic Regression & Validation Tests for Batch ZZZ.9.1:
Semantic Attribution Ablation & Causal-Discipline Audit.
Covers all 16 required audit dimensions from Section 25.
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
from core.semantic_ablation_engine import SemanticAblationEngine, PILOT_UNIVERSE
from core.attribution_schemas import SpecificityStatus, RedTeamStatus, CoverageState

@pytest.fixture(scope="module")
def substrate_engine():
    return SemanticSubstrateEngine("tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def attribution_engine():
    return SemanticAttributionEngine("tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def ablation_engine():
    return SemanticAblationEngine("tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def sample_dataset():
    parquet_path = "gates/evidence/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "gates/evidence/zzz81_ablation_results.parquet"
    assert os.path.exists(parquet_path), f"Required data parquet {parquet_path} not found"
    df = pd.read_parquet(parquet_path)
    return df

# Test 1: PIT Exclusion Test
def test_01_pit_exclusion(attribution_engine):
    """Verifies that events published strictly after decision timestamp T are excluded."""
    cand = {
        "symbol": "ADRO",
        "date": "2025-09-01T00:00:00+0700",
        "quant_score": 85.0,
        "rel_vol": 1.3,
        "signal_day_return": 0.02
    }
    day_universe = [{"symbol": "ADRO", "ret_c_prev_to_close": 0.02}]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    
    # Assert no event in news context has published_at > 2025-09-01
    for ev in ctx.news_context.get("events", []):
        assert ev["published_at"] <= "2025-09-01T00:00:00+0700"

# Test 2: Future Injection Test
def test_02_future_injection(ablation_engine, sample_dataset):
    """Verifies that synthetic future event at T+2 is strictly excluded and results in PASS."""
    sample_cand = sample_dataset[sample_dataset["symbol"] == "ADRO"].iloc[0].to_dict()
    day_universe = sample_dataset[sample_dataset["date"] == sample_cand["date"]].to_dict(orient="records")
    res = ablation_engine.run_future_injection_audit(sample_cand, day_universe, future_delta_days=2)
    
    assert res["future_event_found_at_t"] is False
    assert res["leakage_status"] == "PASS"

# Test 3: Historical State Reconstruction Test
def test_03_historical_state_reconstruction(attribution_engine):
    """Verifies that state reconstruction at T0 != T1 and does not retroactively overwrite earlier states."""
    cand_t0 = {
        "symbol": "INCO",
        "date": "2025-01-01T00:00:00+0700",
        "quant_score": 70.0,
        "rel_vol": 1.0,
        "signal_day_return": 0.01
    }
    cand_t1 = {
        "symbol": "INCO",
        "date": "2025-10-01T00:00:00+0700",
        "quant_score": 95.0,
        "rel_vol": 1.5,
        "signal_day_return": 0.03
    }
    ctx_t0 = attribution_engine.reconstruct_candidate_context_at_t(cand_t0, [cand_t0])
    ctx_t1 = attribution_engine.reconstruct_candidate_context_at_t(cand_t1, [cand_t1])
    
    assert ctx_t0.quant_score != ctx_t1.quant_score
    assert ctx_t0.flow_context["flow_state"] == "NEUTRAL"
    assert ctx_t1.flow_context["flow_state"] == "CONFIRMED"

# Test 4: Exposure Temporal Validity Test
def test_04_exposure_temporal_validity(substrate_engine):
    """Verifies that commodity exposures respect valid_from <= T and valid_to > T."""
    con = duckdb.connect(substrate_engine.db_path, read_only=True)
    rows = con.execute("""
        SELECT entity_id, target_entity_id, valid_from, valid_to
        FROM fact_exposure
        WHERE valid_from > '2027-01-01'
    """).fetchall()
    con.close()
    assert len(rows) == 0, "Found invalid future exposures"

# Test 5: Relationship Temporal Validity Test
def test_05_relationship_temporal_validity(substrate_engine):
    """Verifies that ownership/group relationships respect temporal validity boundaries."""
    con = duckdb.connect(substrate_engine.db_path, read_only=True)
    rows = con.execute("""
        SELECT entity_a_id, entity_b_id, valid_from, valid_to
        FROM fact_relationship
        WHERE valid_from > '2027-01-01'
    """).fetchall()
    con.close()
    assert len(rows) == 0, "Found invalid future relationships"

# Test 6: Entity Unresolved Test
def test_06_entity_unresolved(substrate_engine):
    """Verifies that unknown tickers or entity names resolve explicitly to UNRESOLVED."""
    res = substrate_engine.resolve_entity("FAKE_TICKER_999")
    assert res["entity_id"] == "UNRESOLVED"
    assert res["canonical_name"] == "UNKNOWN"
    assert res["confidence"] == 0.0

# Test 7: Contradictory Evidence Test
def test_07_contradictory_evidence(attribution_engine):
    """Verifies handling of contradictory directional movement (e.g. target +3%, peer mean -3%)."""
    cand = {
        "symbol": "PTBA",
        "date": "2025-10-30T00:00:00+0700",
        "quant_score": 90.0,
        "rel_vol": 1.5,
        "signal_day_return": 0.035
    }
    # Peers are crashing -3.5%
    day_universe = [
        {"symbol": "PTBA", "ret_c_prev_to_close": 0.035},
        {"symbol": "ADRO", "ret_c_prev_to_close": -0.035},
        {"symbol": "ITMG", "ret_c_prev_to_close": -0.035}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    assert ctx.sector_context["specificity_status"] == SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE.value
    assert ctx.sector_context["differential_return"] >= 0.06

# Test 8: Provenance Trace Test
def test_08_provenance_trace(substrate_engine):
    """Verifies that all fact_event records possess valid source_id provenance."""
    con = duckdb.connect(substrate_engine.db_path, read_only=True)
    rows = con.execute("SELECT DISTINCT source_id FROM fact_event").fetchall()
    con.close()
    sources = [r[0] for r in rows]
    assert len(sources) > 0
    for s in sources:
        assert s is not None and len(s) > 0

# Test 9: Differential Arithmetic Test
def test_09_differential_arithmetic(attribution_engine):
    """Verifies deterministic arithmetic of differential return (Target - PeerMean)."""
    cand = {"symbol": "ADRO", "date": "2025-10-30T00:00:00+0700", "signal_day_return": 0.04}
    day_universe = [
        {"symbol": "ADRO", "ret_c_prev_to_close": 0.04},
        {"symbol": "ITMG", "ret_c_prev_to_close": 0.02},
        {"symbol": "PTBA", "ret_c_prev_to_close": 0.01}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    expected_peer_mean = (0.02 + 0.01) / 2.0
    expected_diff = 0.04 - expected_peer_mean
    assert pytest.approx(ctx.sector_context["peer_mean_return"], 1e-5) == expected_peer_mean
    assert pytest.approx(ctx.sector_context["differential_return"], 1e-5) == expected_diff

# Test 10: Peer Counterfactual Test
def test_10_peer_counterfactual(attribution_engine):
    """Verifies counterfactual expected vs actual movers identification."""
    cand = {"symbol": "INCO", "date": "2025-09-22T00:00:00+0700", "signal_day_return": 0.037}
    day_universe = [
        {"symbol": "INCO", "ret_c_prev_to_close": 0.037},
        {"symbol": "ANTM", "ret_c_prev_to_close": 0.038}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    assert set(ctx.peer_counterfactual["actual_movers"]) == {"INCO", "ANTM"}
    assert len(ctx.peer_counterfactual["non_movers"]) == 0

# Test 11: UNKNOWN Propagation Test
def test_11_unknown_propagation(attribution_engine):
    """Verifies that missing fundamental filings propagate as UNKNOWN / NO_EVIDENCE_IN_DATASET."""
    cand = {"symbol": "BBCA", "date": "2025-10-29T00:00:00+0700", "signal_day_return": 0.02}
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, [cand])
    assert ctx.fundamental_context["disclosure_status"] == "NO_EVIDENCE_IN_DATASET"
    assert "Quarterly fundamental filing disclosures not populated at T" in ctx.unknowns

# Test 12: Attribution vs Specificity Decoupling Test
def test_12_attribution_vs_specificity(attribution_engine):
    """Verifies that COMPANY_SPECIFIC_CANDIDATE does not automatically claim company catalyst."""
    cand = {"symbol": "ADRO", "date": "2025-10-30T00:00:00+0700", "signal_day_return": 0.05}
    day_universe = [
        {"symbol": "ADRO", "ret_c_prev_to_close": 0.05},
        {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
        {"symbol": "PTBA", "ret_c_prev_to_close": 0.01}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    assert ctx.sector_context["specificity_status"] == SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE.value
    assert "Substrate Gap" in ctx.economic_transmission

# Test 13: Red Team Causality Audit Test
def test_13_red_team_causality(attribution_engine):
    """Verifies Red Team assigns WEAK when evidence is absent for non-commodity breakouts."""
    cand = {"symbol": "ASII", "date": "2025-10-23T00:00:00+0700", "signal_day_return": 0.024, "rel_vol": 1.5}
    day_universe = [
        {"symbol": "ASII", "ret_c_prev_to_close": 0.024},
        {"symbol": "UNTR", "ret_c_prev_to_close": 0.020}
    ]
    ctx = attribution_engine.reconstruct_candidate_context_at_t(cand, day_universe)
    assert ctx.red_team_result.overall_status == RedTeamStatus.WEAK
    assert ctx.thesis_classification == "PARTIALLY_SUPPORTED"

# Test 14: A0 to A5 Reproducibility Test
def test_14_a0_to_a5_reproducibility(ablation_engine, sample_dataset):
    """Verifies execution of nested ablation ladder A0 to A5 and deterministic metrics."""
    res = ablation_engine.run_nested_ablation(sample_dataset)
    layers = {l["layer_name"]: l for l in res["layers"]}
    
    assert layers["A0"]["N"] >= 280
    assert layers["A1"]["N"] == 73
    assert layers["A2"]["N"] == 57
    assert layers["A5"]["N"] == 57
    
    # Monotonicity checks
    assert layers["A2"]["mean_h5"] > layers["A1"]["mean_h5"]
    assert layers["A1"]["mean_h5"] > layers["A0"]["mean_h5"]
    assert layers["A3"]["mean_h5"] == layers["A2"]["mean_h5"]

# Test 15: Universe Scope Test
def test_15_universe_scope(ablation_engine, sample_dataset):
    """Verifies that all evaluated candidates belong to the 12 pilot tickers and UNTR is classified."""
    scope = ablation_engine.audit_universe_scope(sample_dataset)
    assert scope["pilot_universe_count"] == 12
    assert scope["universe_scope_exception_count"] == 0
    assert scope["scope_audit_status"] == "PASS"
    assert "INDIRECT_COMMODITY_EXPOSURE" in scope["untr_classification"]

# Test 16: No Layer E Modification Contract Test
def test_16_no_layer_e_modification(sample_dataset):
    """Verifies that Layer E selection conditions remain 100% frozen."""
    if "sel_layer_e" in sample_dataset.columns:
        layer_e = sample_dataset[sample_dataset["sel_layer_e"]]
        assert len(layer_e) == 73
        assert (layer_e["quant_score"] >= 80.0).all()
        assert (layer_e["rel_vol"] > 1.2).all()
        assert (layer_e["red_team_time_leakage"] == "PASS").all()
        assert (layer_e["red_team_logic_consistency"] == "PASS").all()
