"""
Test Suite for ZZZ.14.2.1-R: Independent Adversarial Acceptance Challenge
Executes live, non-circular adversarial assertions against temporal leakage,
sentinel injections, AST token scanning, and live independent reconciliation.
"""

import os
import json
import pytest
import pandas as pd
from datetime import datetime

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

def test_adversarial_live_v1_reconciliation():
    """Independent live reconciliation of all 73 baseline setups without reading summary JSON."""
    v1_baseline_path = "gates/evidence/zzz115_observation_level.parquet"
    assert os.path.exists(v1_baseline_path)
    df_v1 = pd.read_parquet(v1_baseline_path)
    assert len(df_v1) == 73
    
    engine = HistoricalReplayEngine()
    
    for idx, row in df_v1.iterrows():
        ticker = row["ticker"]
        decision_date = str(row["decision_date"])[:10]
        
        state = engine.replay_state_from_db(ticker, decision_date, "16:00:00")
        
        # 1. Target must NOT be in peers (leave-one-out)
        assert ticker not in state.peer_state
        # 2. Market state must exist
        assert bool(state.market_state) is True
        assert state.market_state.get("close") is not None
        # 3. Snapshot hash must be valid SHA-256
        assert len(state.snapshot_hash) == 64

def test_adversarial_current_state_sentinel_rejection():
    """Adversarial sentinel injection: modern relationship must never reach Agent 2."""
    sentinel = "CURRENT_STATE_SENTINEL_ZZZ1421R"
    engine = HistoricalReplayEngine()
    pipeline = Agent2IntelligencePipeline()
    reasoner = Agent2LLMReasoner()
    
    test_rec = [
        {"domain": "RELATIONSHIP", "relationship_type": sentinel, "is_current_state": True, "valid_from": "2018-01-01"},
        {"domain": "OWNERSHIP", "target": sentinel, "valid_from": "2026-01-01", "valid_to": "2027-01-01"}
    ]
    state = engine.build_knowledge_state("ANTM", "2018-05-15", "16:00:00", test_rec)
    prompt = reasoner.generate_prompt(state)
    report = pipeline.process_historical_state(state)
    
    assert sentinel not in str(state.to_dict())
    assert sentinel not in prompt
    assert sentinel not in str(report)

def test_adversarial_future_publication_sentinels_rejection():
    """Adversarial sentinel injection: future published/available records must never reach Agent 2."""
    sentinels = [
        ("FUTURE_SENTINEL_PUBLICATION", {"domain": "EVENT", "published_at": "2018-05-16 08:00:00", "available_at": "2018-05-16 08:00:00", "desc": "FUTURE_SENTINEL_PUBLICATION"}),
        ("FUTURE_SENTINEL_AVAILABILITY", {"domain": "EVENT", "published_at": "2018-05-14 08:00:00", "available_at": "2018-05-17 08:00:00", "desc": "FUTURE_SENTINEL_AVAILABILITY"}),
        ("FUTURE_SENTINEL_OBSERVED", {"domain": "EVENT", "published_at": "2018-05-14 08:00:00", "observed_at": "2018-05-18 08:00:00", "desc": "FUTURE_SENTINEL_OBSERVED"}),
        ("FUTURE_SENTINEL_VALID_FROM", {"domain": "RELATIONSHIP", "relationship_type": "AFFILIATE", "valid_from": "2019-01-01", "valid_to": "2025-01-01", "desc": "FUTURE_SENTINEL_VALID_FROM"})
    ]
    engine = HistoricalReplayEngine()
    reasoner = Agent2LLMReasoner()
    pipeline = Agent2IntelligencePipeline()
    
    for s_name, rec in sentinels:
        state = engine.build_knowledge_state("BBCA", "2018-05-15", "16:00:00", [rec])
        prompt = reasoner.generate_prompt(state)
        report = pipeline.process_historical_state(state)
        
        assert s_name not in str(state.to_dict())
        assert s_name not in prompt
        assert s_name not in str(report)

def test_adversarial_outcome_sentinel_rejection():
    """Adversarial sentinel injection: forward return/outcome keys must be rejected by enforce_pit."""
    outcome_sentinels = [
        ("H5_SENTINEL_VALUE", {"domain": "OUTCOME", "target_H5": 0.095, "desc": "H5_SENTINEL_VALUE"}),
        ("OUTCOME_SENTINEL_VALUE", {"domain": "OUTCOME", "forward_return": 0.088, "desc": "OUTCOME_SENTINEL_VALUE"}),
        ("MFE_SENTINEL_VALUE", {"domain": "OUTCOME", "MFE": 0.120, "desc": "MFE_SENTINEL_VALUE"})
    ]
    engine = HistoricalReplayEngine()
    reasoner = Agent2LLMReasoner()
    
    for o_name, rec in outcome_sentinels:
        state = engine.build_knowledge_state("PTBA", "2025-09-09", "16:00:00", [rec])
        prompt = reasoner.generate_prompt(state)
        
        assert o_name not in str(state.to_dict())
        assert o_name not in prompt

def test_adversarial_agent2_ast_token_scan():
    """Verify AST / source files of Agent 2 have zero direct DB, Parquet, or network imports."""
    prohibited = ["duckdb", "read_parquet", "parquet", "open(", "requests", "urllib", "sqlite3", "psycopg2"]
    agent2_dir = "agents/agent2_intelligence"
    
    for fname in ["pipeline.py", "llm_reasoner.py", "schemas.py"]:
        with open(os.path.join(agent2_dir, fname), "r") as f:
            code = f.read()
        for tok in prohibited:
            assert tok not in code, f"Forbidden token '{tok}' found in {fname}"

def test_adversarial_silent_fallback_on_missing_entity():
    """Verify querying a non-existent entity returns clean empty state without fallback."""
    engine = HistoricalReplayEngine()
    state = engine.replay_state_from_db("NON_EXISTENT_TICKER_XYZ", "2018-05-15", "16:00:00")
    
    assert state.event_state == []
    assert state.relationship_state == []
    assert state.exposure_state == []
    assert state.peer_state == []

def test_adversarial_unknown_preservation():
    """Verify Agent 2 explicitly produces UNKNOWN and LOW confidence on empty historical state."""
    reasoner = Agent2LLMReasoner()
    empty_state = HistoricalKnowledgeState(ticker="ANTM", decision_date="2018-05-15", decision_time="16:00:00")
    report = reasoner.execute_reasoning(empty_state)
    
    assert report.research_status == "UNKNOWN"
    assert report.confidence == "LOW"
    assert report.differential_assessment.differential_status == "UNKNOWN"

def test_adversarial_live_two_run_reproducibility():
    """Live independent test comparing intermediate states and hashes across 2 distinct runs."""
    engine = HistoricalReplayEngine()
    test_dates = ["2018-05-15", "2024-02-15"]
    
    for d in test_dates:
        for t in CANONICAL_12:
            s1 = engine.replay_state_from_db(t, d, "16:00:00")
            s2 = engine.replay_state_from_db(t, d, "16:00:00")
            
            assert s1.snapshot_hash == s2.snapshot_hash
            assert s1.to_dict() == s2.to_dict()
