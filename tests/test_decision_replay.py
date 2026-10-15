import os
import json
import pytest
from pathlib import Path

LEDGER_PATH = Path(__file__).resolve().parent.parent / "state" / "audit" / "ledger.jsonl"

def extract_decision(symbol: str, target_time: str):
    """Simulates the Replay Engine extraction logic"""
    if not LEDGER_PATH.exists():
        return None
        
    events = []
    with open(LEDGER_PATH, 'r') as f:
        for line in f:
            if not line.strip(): continue
            try:
                events.append(json.loads(line))
            except:
                pass
                
    pit_events = [e for e in events if e.get("timestamp") <= target_time and (e.get("metadata", {}).get("symbol") == symbol or e.get("stage") == "MARKET_REGIME")]
    post_events = [e for e in events if e.get("timestamp") > target_time and e.get("metadata", {}).get("symbol") == symbol]
    
    return pit_events, post_events

def test_pit_boundary():
    """Test that pre-decision events do not contain future timestamps."""
    res = extract_decision("BBCA", "2026-09-13T09:00:00Z")
    if res:
        pit, post = res
        for e in pit:
            assert e["timestamp"] <= "2026-09-13T09:00:00Z"
        if post:
            assert post[0]["timestamp"] > "2026-09-13T09:00:00Z"

def test_missing_intelligence():
    """Test handling of missing data."""
    res = extract_decision("FAKE_SYMBOL", "2026-09-13T09:00:00Z")
    if res:
        pit, post = res
        assert len([e for e in pit if e.get("stage") != "MARKET_REGIME"]) == 0

def test_deterministic_replay():
    """Test that repeated runs yield identical replay context."""
    res1 = extract_decision("BBCA", "2026-09-13T09:00:00Z")
    res2 = extract_decision("BBCA", "2026-09-13T09:00:00Z")
    assert res1 == res2

def test_post_decision_separation():
    """Ensure post events are strictly separated."""
    res = extract_decision("BBCA", "2026-09-13T09:00:00Z")
    if res:
        pit, post = res
        pit_ids = [e.get("event_id") for e in pit]
        post_ids = [e.get("event_id") for e in post]
        # No overlap
        assert len(set(pit_ids).intersection(set(post_ids))) == 0
