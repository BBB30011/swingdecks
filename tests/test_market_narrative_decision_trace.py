import sys
from pathlib import Path
import json
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.decision_trace import DecisionTraceAPI, DecisionTraceEvent
from core.market_narrative import MarketNarrativeEngine

# Fixture to create a temporary ledger
@pytest.fixture
def temp_ledger(tmp_path):
    ledger_file = tmp_path / "ledger.jsonl"
    events = [
        # T0 Event
        {"event_id": "EVT1", "timestamp": "2026-09-10T09:00:00Z", "stage": "AGENT_1_QUANT", "event_type": "SCANNER_COMPLETED", "metadata": {"symbol": "BBCA", "status": "WATCH"}},
        {"event_id": "EVT2", "timestamp": "2026-09-10T09:00:00Z", "stage": "AGENT_2_INTEL", "event_type": "INTEL_ANALYZED", "metadata": {"symbol": "BBCA", "catalysts": ["Earnings"], "red_team_decision": "PASS", "contradiction_count": 0}},
        {"event_id": "EVT3", "timestamp": "2026-09-10T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "event_type": "DECISION_FINALIZED", "metadata": {"symbol": "BBCA", "action": "WAIT"}},
        
        # T1 Event (Delta)
        {"event_id": "EVT4", "timestamp": "2026-09-11T09:00:00Z", "stage": "AGENT_1_QUANT", "event_type": "SCANNER_COMPLETED", "metadata": {"symbol": "BBCA", "status": "CANDIDATE_FOUND", "delta_status": "UPDATED"}},
        {"event_id": "EVT5", "timestamp": "2026-09-11T09:00:00Z", "stage": "AGENT_2_INTEL", "event_type": "INTEL_ANALYZED", "metadata": {"symbol": "BBCA", "intel_delta_status": "REMOVED", "red_team_delta_status": "UPDATED", "red_team_decision": "BLOCK", "contradiction_count": 2}},
        {"event_id": "EVT6", "timestamp": "2026-09-11T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "event_type": "DECISION_FINALIZED", "metadata": {"symbol": "BBCA", "action": "AVOID", "reason": "Red team block", "risk_state": "RED"}},
        
        # T2 Event (Outcome)
        {"event_id": "EVT7", "timestamp": "2026-09-12T09:00:00Z", "stage": "POSITION_MONITOR", "event_type": "POSITION_EXITED", "metadata": {"symbol": "BBCA", "exit_price": 1000}}
    ]
    with open(ledger_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
            
    return ledger_file

def test_timeline_ordering(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    timeline = api.get_timeline("BBCA")
    assert len(timeline) == 3
    assert timeline[0]["timestamp"] == "2026-09-10T09:00:00Z"
    assert timeline[1]["timestamp"] == "2026-09-11T09:00:00Z"

def test_decision_change(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    trace = api.build_trace("BBCA", "2026-09-11T09:00:00Z")
    assert trace.decision_change == "DOWNGRADE"  # WAIT to AVOID
    assert trace.market_delta["agent1_delta"] == "UPDATED"
    
def test_evidence_linking_and_pit(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    trace = api.build_trace("BBCA", "2026-09-11T09:00:00Z")
    assert "EVT4" in trace.evidence_refs
    assert "EVT5" in trace.evidence_refs
    assert trace.pit_status == "PASS"

def test_narrative_generation(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    engine = MarketNarrativeEngine(trace_api=api)
    narrative = engine.build_narrative("BBCA", "2026-09-11T09:00:00Z")
    
    # Check language firewall
    assert "Agent 1 detected market change classified as: UPDATED" in narrative
    assert "caused" not in narrative.lower() # No causality assumption
    assert "Current:\nAVOID" in narrative
    assert "Decision Change:\nDOWNGRADE" in narrative
    assert "WHAT HAPPENED AFTERWARD" in narrative
    
def test_missing_evidence(tmp_path):
    ledger_file = tmp_path / "ledger_empty.jsonl"
    with open(ledger_file, "w") as f:
        f.write("")
    api = DecisionTraceAPI(ledger_path=str(ledger_file))
    trace = api.build_trace("UNKN", "2026-09-10T09:00:00Z")
    assert trace.source_completeness == "NOT_AVAILABLE"
    
    engine = MarketNarrativeEngine(trace_api=api)
    narrative = engine.build_narrative("UNKN")
    assert "NO_RECORDED_EVENTS" in narrative

def test_post_decision_separation(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    outcomes = api.get_post_decision_outcomes("BBCA", "2026-09-11T09:00:00Z")
    assert len(outcomes["subsequent_events"]) == 1
    assert outcomes["subsequent_events"][0]["stage"] == "POSITION_MONITOR"
    
    # Outcomes shouldn't alter the trace
    trace = api.build_trace("BBCA", "2026-09-11T09:00:00Z")
    assert not trace.post_decision_outcome

def test_determinism(temp_ledger):
    api = DecisionTraceAPI(ledger_path=str(temp_ledger))
    trace1 = api.build_trace("BBCA", "2026-09-11T09:00:00Z")
    trace2 = api.build_trace("BBCA", "2026-09-11T09:00:00Z")
    assert trace1.get_hash() == trace2.get_hash()
    
    engine = MarketNarrativeEngine(trace_api=api)
    n1 = engine.build_narrative("BBCA", "2026-09-11T09:00:00Z")
    n2 = engine.build_narrative("BBCA", "2026-09-11T09:00:00Z")
    assert n1 == n2

def test_no_change_decision(tmp_path):
    ledger_file = tmp_path / "ledger2.jsonl"
    events = [
        {"event_id": "E1", "timestamp": "T1", "stage": "AGENT_3_COMMITTEE", "metadata": {"symbol": "ADRO", "action": "HOLD"}},
        {"event_id": "E2", "timestamp": "T2", "stage": "AGENT_3_COMMITTEE", "metadata": {"symbol": "ADRO", "action": "HOLD"}}
    ]
    with open(ledger_file, "w") as f:
        for e in events: f.write(json.dumps(e) + "\n")
        
    api = DecisionTraceAPI(ledger_path=str(ledger_file))
    trace = api.build_trace("ADRO", "T2")
    assert trace.decision_change == "NO_CHANGE"
