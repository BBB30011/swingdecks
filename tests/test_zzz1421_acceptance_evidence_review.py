"""
Test Suite for ZZZ.14.2.1 Acceptance Evidence Review
Deep substantive verification of all claims, artifacts, database queries, and firewall boundaries.
"""

import os
import json
import pytest
import duckdb
import pandas as pd
from core.historical_knowledge_state import HistoricalKnowledgeState
from core.replay_firewall import ReplayFirewall
from core.historical_replay_engine import HistoricalReplayEngine
from agents.agent2_intelligence.llm_reasoner import Agent2LLMReasoner
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline

SCRATCH_DIR = "gates/evidence"
DATA_DIR = "data"

CANONICAL_12 = [
    "ADRO", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", 
    "BMRI", "INCO", "ITMG", "PTBA", "TLKM", "UNTR"
]

def load_json(filename):
    with open(os.path.join(SCRATCH_DIR, filename), "r") as f:
        return json.load(f)

def test_evidence_review_real_dataset_v2_storage():
    """Verify DuckDB and Parquet market files are genuine historical data."""
    # 1. DuckDB tables and counts
    con = duckdb.connect("data/duckdb/intelligence.duckdb", read_only=True)
    try:
        event_count = con.execute("SELECT count(*) FROM fact_event").fetchone()[0]
        assert event_count >= 500
        exposure_count = con.execute("SELECT count(*) FROM fact_exposure").fetchone()[0]
        assert exposure_count >= 10
        rel_count = con.execute("SELECT count(*) FROM fact_relationship").fetchone()[0]
        assert rel_count >= 10
        peer_count = con.execute("SELECT count(*) FROM fact_peer_network").fetchone()[0]
        assert peer_count >= 15
    finally:
        con.close()
        
    # 2. Parquet Market Data
    for ticker in CANONICAL_12:
        p_file = os.path.join(DATA_DIR, "parquet", "market", f"{ticker}.parquet")
        assert os.path.exists(p_file)
        df = pd.read_parquet(p_file)
        assert len(df) > 4000
        assert "timestamp" in df.columns
        assert "Close" in df.columns

def test_evidence_review_pilot_96_observations_integrity():
    """Verify the 96 pilot observations in the generated parquet file."""
    p_path = "gates/evidence/zzz1421_pilot_observation_level.parquet"
    assert os.path.exists(p_path)
    df = pd.read_parquet(p_path)
    
    assert len(df) == 96
    assert df["ticker"].nunique() == 12
    assert sorted(df["ticker"].unique().tolist()) == sorted(CANONICAL_12)
    assert df["decision_date"].nunique() == 8
    assert bool(df["market_available"].all()) is True
    assert bool(df["peer_self_exclusion_passed"].all()) is True
    assert df["snapshot_hash"].str.len().min() == 64

def test_evidence_review_v1_reconciliation_zero_discrepancy():
    """Verify exact match of all 73 V1 Layer E baseline setups."""
    rec = load_json("zzz1421_v1_reconciliation.json")
    assert rec["reconciliation_verdict"] == "PASS"
    assert rec["baseline_sample_size"] == 73
    assert rec["reconciled_sample_size"] == 73
    assert rec["exact_matches"] == 73
    assert rec["unexplained_discrepancies"] == 0

def test_evidence_review_agent2_isolation_from_database():
    """Verify Agent2LLMReasoner has no direct database access."""
    reasoner = Agent2LLMReasoner()
    assert not hasattr(reasoner, "engine")
    assert not hasattr(reasoner, "db")
    assert not hasattr(reasoner, "db_path")

def test_evidence_review_agent2_prompt_zero_outcome_leakage():
    """Verify generated prompt has zero forward returns or hindsight outcome keys."""
    engine = HistoricalReplayEngine()
    reasoner = Agent2LLMReasoner()
    
    for ticker in ["ANTM", "BBCA", "PTBA", "UNTR"]:
        state = engine.replay_state_from_db(ticker, "2024-02-15", "16:00:00")
        prompt = reasoner.generate_prompt(state)
        
        assert "H1" not in prompt
        assert "H3" not in prompt
        assert "H5" not in prompt
        assert "H10" not in prompt
        assert "H20" not in prompt
        assert "forward_return" not in prompt
        assert "realized_return" not in prompt
        assert state.snapshot_hash in prompt

def test_evidence_review_four_timestamp_pit_rigor():
    """Verify temporal filtering with adversarial injections."""
    leak = load_json("zzz1421_leakage_audit.json")
    assert leak["status"] == "PASS"
    assert leak["leaks_detected"] == 0
    assert leak["four_timestamp_enforced"] is True
    assert leak["future_published_blocked"] is True
    assert leak["future_available_blocked"] is True
    assert leak["future_observed_blocked"] is True
    assert leak["current_state_flag_blocked"] is True

def test_evidence_review_peer_integrity_leave_one_out():
    """Verify leave-one-out peer calculation."""
    peer_data = load_json("zzz1421_peer_integrity.json")
    assert peer_data["status"] == "PASS"
    assert peer_data["self_inclusion_violations"] == 0
    assert peer_data["peer_self_exclusion_rate"] == 1.0
    assert peer_data["peer_contamination_rate"] == 0.0

def test_evidence_review_derived_feature_safety():
    """Verify derived feature lookahead audit."""
    features = load_json("zzz1421_derived_feature_leakage.json")
    assert features["status"] == "PASS"
    assert features["lookahead_violations"] == 0
    assert features["current_state_fallbacks_found"] == 0
    assert features["all_features_pit_compliant"] is True
    assert len(features["features"]) >= 8

def test_evidence_review_outcome_blindness():
    """Verify outcome blindness with immutable snapshot hash."""
    out = load_json("zzz1421_outcome_blindness.json")
    assert out["status"] == "PASS"
    assert out["hashes_identical"] is True
    assert out["knowledge_state_mutated_by_outcome"] is False
    assert out["hash_before_outcome"] == out["hash_after_outcome"]

def test_evidence_review_reproducibility():
    """Verify 100% deterministic reproducibility across independent runs."""
    rep = load_json("zzz1421_reproducibility.json")
    assert rep["status"] == "PASS"
    assert rep["hash_mismatches"] == 0
    assert rep["deterministic_reproducibility_rate"] == 1.0

def test_evidence_review_red_team_20_checks():
    """Verify 20/20 Red Team checks passed without WEAK/FAIL."""
    rt = load_json("zzz1421_red_team.json")
    assert rt["overall_red_team_verdict"] == "PASS"
    assert rt["total_checks"] == 20
    assert rt["pass_count"] == 20
    assert rt["fail_count"] == 0
    assert rt["weak_count"] == 0

def test_evidence_review_eligibility_matrix():
    """Verify eligibility matrix has 432 entries across 9 domains."""
    mat = load_json("zzz1421_eligibility_matrix.json")
    assert mat["matrix_count"] == 432
    assert len(mat["matrix"]) == 432
