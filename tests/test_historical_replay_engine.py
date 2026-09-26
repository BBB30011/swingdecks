import json
import os
import pytest
import sys
sys.path.append("d:/Project/SwingDeck")
from core.historical_replay_engine import HistoricalReplayEngine

def test_historical_knowledge_future_leak():
    engine = HistoricalReplayEngine()
    ticker = "ANTM"
    decision_date = "2018-05-15"
    decision_time = "15:00:00"
    
    raw = [
        {"domain": "EVENT", "available_at": "2018-05-14 08:00:00"}, # Valid
        {"domain": "EVENT", "available_at": "2018-05-16 08:00:00"}  # Future
    ]
    
    state = engine.build_knowledge_state(ticker, decision_date, decision_time, raw)
    assert len(state.event_state) == 1
    assert state.event_state[0]["available_at"] == "2018-05-14 08:00:00"

def test_historical_knowledge_current_leak():
    engine = HistoricalReplayEngine()
    ticker = "ANTM"
    decision_date = "2018-05-15"
    decision_time = "15:00:00"
    
    raw = [
        {"domain": "RELATIONSHIP", "available_at": "2026-05-14 08:00:00", "is_current_state": True}
    ]
    
    state = engine.build_knowledge_state(ticker, decision_date, decision_time, raw)
    assert len(state.relationship_state) == 0

def test_deterministic_hash():
    engine = HistoricalReplayEngine()
    state1 = engine.build_knowledge_state("ANTM", "2018-05-15", "15:00:00", [])
    state2 = engine.build_knowledge_state("ANTM", "2018-05-15", "15:00:00", [])
    assert state1.snapshot_hash == state2.snapshot_hash
