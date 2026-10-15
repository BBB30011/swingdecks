import sys
from pathlib import Path
import json
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.drift_observatory import DriftObservatory, DriftCategory, DriftStatus, QualityStatus

@pytest.fixture
def temp_ledger(tmp_path):
    ledger_file = tmp_path / "ledger_drift.jsonl"
    events = []
    # Generate 10 days of baseline
    for i in range(10, 20):
        events.append({"event_id": f"E_A1_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "AGENT_1_QUANT", "metadata": {"symbol": "BBCA", "status": "WATCH"}})
        events.append({"event_id": f"E_A3_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "metadata": {"symbol": "BBCA", "action": "WAIT"}})
        events.append({"event_id": f"E_REG_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "MARKET_REGIME", "metadata": {"regime": "SIDEWAYS"}})
        
    # Generate 10 days of current with drift (action changed to BUY, regime changed to BULL)
    for i in range(20, 30):
        events.append({"event_id": f"E_A1_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "AGENT_1_QUANT", "metadata": {"symbol": "BBCA", "status": "CANDIDATE_FOUND"}})
        events.append({"event_id": f"E_A2_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "AGENT_2_INTEL", "metadata": {"symbol": "BBCA", "catalysts": ["Earnings"]}})
        events.append({"event_id": f"E_A3_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "metadata": {"symbol": "BBCA", "action": "BUY"}})
        events.append({"event_id": f"E_REG_{i}", "timestamp": f"2026-09-{i}T09:00:00Z", "stage": "MARKET_REGIME", "metadata": {"regime": "BULL"}})
        
    with open(ledger_file, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
            
    return ledger_file

def test_baseline_and_window_calculation(temp_ledger):
    obs = DriftObservatory(ledger_path=str(temp_ledger))
    baseline, current = obs._get_windows()
    assert len(baseline) > 0
    assert len(current) > 0
    assert baseline[-1].get("timestamp") < current[0].get("timestamp")

def test_regime_and_decision_drift(temp_ledger):
    obs = DriftObservatory(ledger_path=str(temp_ledger))
    matrix = obs.get_drift_matrix()
    
    # We deliberately injected a change from WAIT to BUY and SIDEWAYS to BULL
    assert matrix["REGIME"] == DriftStatus.CHANGED
    assert matrix["AGENT 3"] == DriftStatus.CHANGED
    
    # Agent 2 coverage appeared in the current window but not baseline
    assert matrix["AGENT 2"] == DriftStatus.CHANGED

def test_recent_drift_events(temp_ledger):
    obs = DriftObservatory(ledger_path=str(temp_ledger))
    events = obs.get_recent_drift_events()
    assert len(events) > 0
    assert events[0]["category"] == DriftCategory.AGENT3
    assert events[0]["status"] == "CHANGED"
    assert "BUY" in events[0]["evidence"]

def test_pit_drift_and_system_health(temp_ledger):
    # Add a PIT block to the ledger
    with open(temp_ledger, "a") as f:
        f.write(json.dumps({"event_id": "PIT_FAIL", "timestamp": "2026-09-30T09:00:00Z", "stage": "SYSTEM", "event_type": "PIT_VIOLATION_ATTEMPT"}) + "\n")
        
    obs = DriftObservatory(ledger_path=str(temp_ledger))
    health = obs.get_system_health()
    assert health["PIT"] == "BLOCKED"
    
    quality = obs.get_quality_matrix()
    assert quality["PIT"] == QualityStatus.BLOCKED

def test_replay_and_accounting_drift(temp_ledger):
    with open(temp_ledger, "a") as f:
        f.write(json.dumps({"event_id": "REP_FAIL", "timestamp": "2026-09-30T09:00:00Z", "stage": "SYSTEM", "event_type": "REPLAY_MISMATCH"}) + "\n")
        f.write(json.dumps({"event_id": "ACC_FAIL", "timestamp": "2026-09-30T09:00:00Z", "stage": "SYSTEM", "event_type": "ACCOUNTING_ANOMALY"}) + "\n")
        
    obs = DriftObservatory(ledger_path=str(temp_ledger))
    quality = obs.get_quality_matrix()
    assert quality["REPLAY"] == QualityStatus.WARNING
    assert quality["ACCOUNTING"] == QualityStatus.BLOCKED

def test_insufficient_data(tmp_path):
    ledger_file = tmp_path / "ledger_short.jsonl"
    events = [
        {"event_id": "E1", "timestamp": "2026-09-10T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "metadata": {"action": "WAIT"}},
        {"event_id": "E2", "timestamp": "2026-09-11T09:00:00Z", "stage": "AGENT_3_COMMITTEE", "metadata": {"action": "BUY"}}
    ]
    with open(ledger_file, "w") as f:
        for e in events: f.write(json.dumps(e) + "\n")
        
    obs = DriftObservatory(ledger_path=str(ledger_file))
    matrix = obs.get_drift_matrix()
    # N < 5 should trigger DATA_INSUFFICIENT
    assert matrix["AGENT 3"] == DriftStatus.DATA_INSUFFICIENT

def test_fail_closed_on_missing_ledger(tmp_path):
    obs = DriftObservatory(ledger_path=str(tmp_path / "nonexistent.jsonl"))
    health = obs.get_system_health()
    assert health["DATA"] == "FAIL"
    
    quality = obs.get_quality_matrix()
    assert quality["TRACEABILITY"] == QualityStatus.UNKNOWN
    
    matrix = obs.get_drift_matrix()
    assert matrix["AGENT 3"] == DriftStatus.DATA_INSUFFICIENT
