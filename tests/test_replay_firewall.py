import pytest
from core.replay_firewall import ReplayFirewall

def test_replay_firewall_eligibility():
    # Market domain
    assert ReplayFirewall.evaluate_eligibility("BBCA", "2020-01-01", "MARKET") == "READY"
    assert ReplayFirewall.evaluate_eligibility("BBCA", "1999-12-31", "MARKET") == "BLOCKED"
    
    # Corporate action domain
    assert ReplayFirewall.evaluate_eligibility("BBCA", "2018-05-01", "CORPORATE_ACTION") == "READY"
    assert ReplayFirewall.evaluate_eligibility("BBCA", "2014-05-01", "CORPORATE_ACTION") == "LIMITED"
    
    # News domain with Top 20 vs non-Top 20
    assert ReplayFirewall.evaluate_eligibility("BBCA", "2021-01-01", "NEWS") == "READY"
    assert ReplayFirewall.evaluate_eligibility("UNTR", "2021-01-01", "NEWS") == "READY"
    assert ReplayFirewall.evaluate_eligibility("SOME_OTHER", "2021-01-01", "NEWS") == "CONDITIONAL"
    assert ReplayFirewall.evaluate_eligibility("BBCA", "2015-01-01", "NEWS") == "LIMITED"
    
    # Invalid date format
    assert ReplayFirewall.evaluate_eligibility("BBCA", "INVALID_DATE", "MARKET") == "BLOCKED"

def test_prevent_future_leak():
    decision_dt = "2020-01-02T08:30:00"
    
    # Record from the past (valid)
    past_rec = {"published_at": "2020-01-01T17:00:00", "available_at": "2020-01-01T17:05:00"}
    assert ReplayFirewall.prevent_future_leak(past_rec, decision_dt) is True
    
    # Record published in future (leak)
    future_rec = {"published_at": "2020-01-02T10:00:00"}
    assert ReplayFirewall.prevent_future_leak(future_rec, decision_dt) is False
    
    # Record available in future (leak)
    future_avail = {"available_at": "2020-01-02T09:00:00"}
    assert ReplayFirewall.prevent_future_leak(future_avail, decision_dt) is False
    
    # Timestamp column check
    future_ts = {"timestamp": "2020-01-03 00:00:00"}
    assert ReplayFirewall.prevent_future_leak(future_ts, decision_dt) is False

def test_prevent_current_state_leak():
    # current state flag
    assert ReplayFirewall.prevent_current_state_leak({"is_current_state": True}) is False
    assert ReplayFirewall.prevent_current_state_leak({"is_current_state": False}) is True
    
    # valid_from / valid_to bounds
    decision_date = "2020-01-02"
    assert ReplayFirewall.prevent_current_state_leak({"valid_from": "2020-01-05"}, decision_date) is False
    assert ReplayFirewall.prevent_current_state_leak({"valid_to": "2019-12-31"}, decision_date) is False
    assert ReplayFirewall.prevent_current_state_leak({"valid_from": "2019-01-01", "valid_to": "2025-01-01"}, decision_date) is True

def test_prevent_outcome_leak():
    # Clean record
    clean_rec = {"ticker": "BBCA", "open": 3000, "close": 3050, "volume": 1000000}
    assert ReplayFirewall.prevent_outcome_leak(clean_rec) is True
    
    # Forward horizon return fields
    for field in ["H1", "H5", "target_H5", "peer_H5", "forward_return", "mae_h5", "mfe_h5"]:
        leaky_rec = {"ticker": "BBCA", field: 0.05}
        assert ReplayFirewall.prevent_outcome_leak(leaky_rec) is False, f"Failed to block {field}"

def test_enforce_peer_self_exclusion():
    target = "BBCA"
    peers = ["BBCA", "ENT_BBCA", "BBNI", "BMRI", "BBRI"]
    filtered = ReplayFirewall.enforce_peer_self_exclusion(target, peers)
    assert "BBCA" not in filtered
    assert "ENT_BBCA" not in filtered
    assert filtered == ["BBNI", "BMRI", "BBRI"]
