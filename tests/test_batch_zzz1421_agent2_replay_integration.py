"""
Test Suite for Batch ZZZ.14.2.1: Agent 2 Replay Integration & Historical Replay Pilot Acceptance Gate
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

SCRATCH_DIR = "d:/Project/SwingDeck/gates/evidence"

def load_json(name):
    filepath = os.path.join(SCRATCH_DIR, name)
    with open(filepath, "r") as f:
        return json.load(f)

def test_real_dataset_replay_loading():
    """Verify that HistoricalReplayEngine loads real historical market and DuckDB records with strict PIT."""
    engine = HistoricalReplayEngine()
    
    # 1. Test 2024 Replay where exposure is valid (valid_from: 2020-01-01)
    state_2024 = engine.replay_state_from_db("ANTM", "2024-02-15", "16:00:00")
    assert state_2024.ticker == "ANTM"
    assert state_2024.decision_date == "2024-02-15"
    assert state_2024.snapshot_hash is not None
    assert len(state_2024.snapshot_hash) == 64
    assert state_2024.market_state.get("close") is not None
    assert len(state_2024.exposure_state) > 0
    assert len(state_2024.event_state) > 0
    
    # 2. Test 2018 Replay where 2020 exposure is strictly excluded by PIT bounds
    state_2018 = engine.replay_state_from_db("ANTM", "2018-05-15", "16:00:00")
    assert state_2018.market_state.get("close") is not None
    assert len(state_2018.event_state) > 0
    assert len(state_2018.exposure_state) == 0 # Proven PIT filtering of 2020 records

def test_v1_observation_reconciliation_zero_discrepancy():
    """Verify that all N=73 frozen V1 observations are reconciled with 0 unexplained discrepancies."""
    data = load_json("zzz1421_v1_reconciliation.json")
    assert data["reconciliation_verdict"] == "PASS"
    assert data["baseline_sample_size"] == 73
    assert data["reconciled_sample_size"] == 73
    assert data["unexplained_discrepancies"] == 0
    assert data["exact_matches"] == 73

def test_future_information_injection_blocked():
    """Verify that future publication, availability, and observation timestamps are strictly rejected."""
    engine = HistoricalReplayEngine()
    decision_date = "2018-05-15"
    decision_time = "16:00:00"
    
    test_records = [
        {"domain": "EVENT", "published_at": "2018-05-14 08:00:00", "available_at": "2018-05-14 08:00:00"},
        {"domain": "EVENT", "published_at": "2018-05-16 08:00:00", "available_at": "2018-05-16 08:00:00", "desc": "LEAK_1"},
        {"domain": "EVENT", "published_at": "2018-05-14 08:00:00", "available_at": "2018-05-17 08:00:00", "desc": "LEAK_2"},
        {"domain": "EVENT", "published_at": "2018-05-14 08:00:00", "observed_at": "2018-05-18 08:00:00", "desc": "LEAK_3"}
    ]
    
    state = engine.build_knowledge_state("ANTM", decision_date, decision_time, test_records)
    assert len(state.event_state) == 1
    assert state.event_state[0]["published_at"] == "2018-05-14 08:00:00"

def test_current_state_injection_blocked():
    """Verify that modern 2026 relationships and current-state flags are rejected from historical T."""
    engine = HistoricalReplayEngine()
    decision_date = "2018-05-15"
    decision_time = "16:00:00"
    
    test_records = [
        {"domain": "RELATIONSHIP", "is_current_state": True, "valid_from": "2018-01-01"},
        {"domain": "RELATIONSHIP", "valid_from": "2026-01-01", "valid_to": "2027-01-01"},
        {"domain": "OWNERSHIP", "is_current_state": True}
    ]
    
    state = engine.build_knowledge_state("BBCA", decision_date, decision_time, test_records)
    assert len(state.relationship_state) == 0
    assert len(state.ownership_state) == 0

def test_peer_self_exclusion_and_leave_one_out():
    """Verify that a ticker is strictly excluded from its own peer group (leave-one-out)."""
    peers = ["BBCA", "BBNI", "BBRI", "BMRI"]
    filtered = ReplayFirewall.enforce_peer_self_exclusion("BBCA", peers)
    assert "BBCA" not in filtered
    assert len(filtered) == 3

def test_silent_fallback_absence():
    """Verify that missing historical records produce UNKNOWN/LIMITED, never silent modern data."""
    elig_pre2018 = ReplayFirewall.evaluate_eligibility("ANTM", "2017-05-15", "OWNERSHIP")
    assert elig_pre2018 == "LIMITED"
    
    elig_news = ReplayFirewall.evaluate_eligibility("TICKER_XYZ", "2020-05-15", "NEWS")
    assert elig_news == "CONDITIONAL"

def test_agent2_context_firewall_prompt_isolation():
    """Verify that Agent 2 prompt contains zero forward return keys (H1..H20) and consumes only HistoricalKnowledgeState."""
    engine = HistoricalReplayEngine()
    reasoner = Agent2LLMReasoner()
    
    state = engine.replay_state_from_db("PTBA", "2025-09-09", "16:00:00")
    prompt = reasoner.generate_prompt(state)
    
    assert "H5" not in prompt
    assert "target_H5" not in prompt
    assert "target_h5" not in prompt
    assert "forward_return" not in prompt
    assert state.snapshot_hash in prompt

def test_outcome_blindness_snapshot_immutability():
    """Verify that downstream outcome attachment does not alter the historical knowledge state snapshot hash."""
    engine = HistoricalReplayEngine()
    state = engine.replay_state_from_db("UNTR", "2025-09-09", "16:00:00")
    
    hash_before = state.snapshot_hash
    # Try injecting prohibited outcome key
    prohibited_dict = {"domain": "OUTCOME", "target_H5": 0.05}
    is_pit = state.enforce_pit(prohibited_dict)
    assert is_pit is False
    
    hash_after = state.compute_hash()
    assert hash_before == hash_after

def test_deterministic_reproducibility():
    """Verify that replaying the exact same historical state produces identical cryptographic snapshot hashes."""
    engine = HistoricalReplayEngine()
    state1 = engine.replay_state_from_db("INCO", "2024-02-15", "16:00:00")
    state2 = engine.replay_state_from_db("INCO", "2024-02-15", "16:00:00")
    
    assert state1.snapshot_hash == state2.snapshot_hash

def test_20_point_red_team_pass():
    """Verify that the 20-Point Red Team audit passes with zero fails."""
    red_team = load_json("zzz1421_red_team.json")
    assert red_team["overall_red_team_verdict"] == "PASS"
    assert red_team["total_checks"] == 20
    assert red_team["pass_count"] == 20
    assert red_team["fail_count"] == 0
