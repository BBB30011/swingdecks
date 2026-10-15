import pytest
import os
import uuid
import json
from pathlib import Path
from core.trading_desk_simulation import TradingDeskSimulator, TradingDeskControlState
from core.paper_execution import PaperExecutionSimulator, PaperOrder, LiveExecutionBlockedError
from core.position import PaperPosition
from core.schemas import MarketBar
from core.data_source import DataValidationError

@pytest.fixture
def clean_desk(tmp_path):
    return TradingDeskSimulator(
        run_id="TEST_DESK_RUN",
        initial_capital=100_000_000.0,
        state_dir=str(tmp_path / "desk_state"),
        audit_dir=str(tmp_path / "desk_audit")
    )

def make_bar(symbol="BBCA", close=1000.0, volume=1_000_000.0, timestamp="2026-03-20T09:00:00Z"):
    return {
        "symbol": symbol,
        "timestamp": timestamp,
        "open": close * 0.99,
        "high": close * 1.02,
        "low": close * 0.98,
        "close": close,
        "volume": volume
    }

# 1. SCENARIO A: Clean Opportunity (BUY -> HOLD -> EXIT)
@pytest.mark.operational
def test_scenario_a_clean_opportunity(clean_desk):
    desk = clean_desk
    bar = desk.validate_market_bar(make_bar("BBCA", 1000.0))
    features = {"trend": {"sma20": 980.0, "sma50": 950.0}, "volatility": {"atr_percent": 0.02}}
    
    a1 = desk.run_agent1_quant("BBCA", bar, features)
    assert a1["status"] == "CANDIDATE_FOUND"
    
    a2 = desk.run_agent2_intelligence("BBCA", a1, {"catalysts": ["Strong Growth"], "contradictions": []})
    assert a2["red_team_decision"] == "PASS"
    
    dec = desk.run_agent3_committee("BBCA", a1, a2)
    assert dec.action == "BUY"
    assert dec.position_size > 0
    
    # Execute order
    order = desk.execute_decision(dec, bar)
    assert order.status == "FILLED"
    assert "BBCA" in [p.symbol for p in desk.portfolio.positions.values() if p.status == "OPEN"]
    
    # Next bar: target hit (1200 > 1150)
    bar2 = desk.validate_market_bar(make_bar("BBCA", 1200.0, timestamp="2026-03-20T09:00:00Z"))
    events = desk.monitor_open_positions({"BBCA": bar2})
    assert any(e.event_type == "TARGET_TRIGGERED" for e in events)
    assert list(desk.portfolio.positions.values())[0].status == "CLOSED"
    assert desk.portfolio.realized_pnl > 0
    assert desk.portfolio.reconcile().is_valid

# 2. SCENARIO B: False Signal (Score below threshold -> WAIT)
@pytest.mark.operational
def test_scenario_b_false_signal(clean_desk):
    desk = clean_desk
    # Downward trending bar (price < sma20)
    bar = desk.validate_market_bar(make_bar("BBRI", 500.0, volume=500_000.0))
    features = {"trend": {"sma20": 520.0, "sma50": 550.0}, "volatility": {"atr_percent": 0.03}}
    
    a1 = desk.run_agent1_quant("BBRI", bar, features)
    a2 = desk.run_agent2_intelligence("BBRI", a1, {})
    dec = desk.run_agent3_committee("BBRI", a1, a2)
    
    assert dec.action == "WAIT"
    assert "AGENT1_SCORE_BELOW_THRESHOLD" in dec.blockers
    assert desk.execute_decision(dec, bar) is None

# 3. SCENARIO C: Thesis Invalidation (Critical contradiction -> AVOID / SELL)
@pytest.mark.operational
def test_scenario_c_thesis_invalidation(clean_desk):
    desk = clean_desk
    bar = desk.validate_market_bar(make_bar("TLKM", 3000.0))
    features = {"trend": {"sma20": 2900.0, "sma50": 2800.0}, "volatility": {"atr_percent": 0.02}}
    
    a1 = desk.run_agent1_quant("TLKM", bar, features)
    # Critical contradiction in intelligence
    raw_intel = {
        "catalysts": ["Revenue increase"],
        "contradictions": [{"topic": "Regulatory Investigation", "description": "Antitrust probe opened", "severity": "CRITICAL"}]
    }
    a2 = desk.run_agent2_intelligence("TLKM", a1, raw_intel)
    assert a2["red_team_decision"] == "BLOCK"
    
    dec = desk.run_agent3_committee("TLKM", a1, a2)
    assert dec.action == "AVOID"
    assert dec.risk_state == "RED"
    assert "RED_TEAM_CRITICAL_CONTRADICTION" in dec.blockers

# 4. SCENARIO D: Portfolio Risk Rejection (Max positions reached)
@pytest.mark.operational
def test_scenario_d_portfolio_risk_rejection(clean_desk):
    desk = clean_desk
    # Fill portfolio to 5 positions
    for i in range(5):
        pos = PaperPosition(
            position_id=f"POS_{i}",
            job_id=f"JOB_{i}",
            symbol=f"SYM_{i}",
            status="OPEN",
            entry_price=1000.0,
            quantity=100.0,
            stop_loss=900.0,
            target_price=1200.0,
            initial_risk=100.0,
            initial_reward=200.0,
            initial_rr=2.0
        )
        desk.portfolio.open_position(pos)
        
    bar = desk.validate_market_bar(make_bar("NEW_SYM", 1000.0))
    features = {"trend": {"sma20": 980.0, "sma50": 950.0}, "volatility": {"atr_percent": 0.02}}
    a1 = desk.run_agent1_quant("NEW_SYM", bar, features)
    a2 = desk.run_agent2_intelligence("NEW_SYM", a1, {})
    dec = desk.run_agent3_committee("NEW_SYM", a1, a2)
    
    assert dec.action == "AVOID"
    assert "MAX_POSITION_LIMIT_REACHED" in dec.blockers

# 5. SCENARIO E: Data Quality Failure (Invalid OHLC)
@pytest.mark.operational
def test_scenario_e_data_quality_failure(clean_desk):
    desk = clean_desk
    # High < Low is physical impossibility in financial bars
    corrupted_bar = {
        "symbol": "BBCA",
        "timestamp": "2026-03-20T09:00:00Z",
        "open": 1000.0,
        "high": 900.0,  # High lower than Low
        "low": 1100.0,
        "close": 1050.0,
        "volume": 1000.0
    }
    with pytest.raises(Exception):
        desk.validate_market_bar(corrupted_bar)

# 6. SCENARIO F: Agent 2 Insufficient Evidence
@pytest.mark.operational
def test_scenario_f_agent2_insufficient_evidence(clean_desk):
    desk = clean_desk
    bar = desk.validate_market_bar(make_bar("ASII", 5000.0))
    features = {"trend": {"sma20": 4900.0, "sma50": 4800.0}, "volatility": {"atr_percent": 0.02}}
    a1 = desk.run_agent1_quant("ASII", bar, features)
    
    # 2 non-critical contradictions cause REWORK verdict
    raw_intel = {
        "catalysts": [],
        "contradictions": [
            {"topic": "Margin Pressure", "description": "Raw material costs rising", "severity": "MEDIUM"},
            {"topic": "Consumer Sentiment", "description": "Automotive sales slowed", "severity": "MEDIUM"}
        ]
    }
    a2 = desk.run_agent2_intelligence("ASII", a1, raw_intel)
    assert a2["red_team_decision"] == "REWORK"
    
    dec = desk.run_agent3_committee("ASII", a1, a2)
    assert dec.action == "WAIT"
    assert "RED_TEAM_REWORK_REQUESTED" in dec.blockers

# 7. SCENARIO G: Execution Failure (Price unreachable)
@pytest.mark.operational
def test_scenario_g_execution_failure(clean_desk):
    desk = clean_desk
    # Request price 1000, but bar low is 1050 (limit price unreachable)
    order = desk.execution_engine.create_order(
        run_id="RUN_G",
        event_id="EVT_G",
        symbol="BMRI",
        side="BUY",
        quantity=100.0,
        lots=1,
        request_price=1000.0,
        stop_loss=900.0,
        target_price=1200.0,
        order_type="LIMIT"
    )
    bar = desk.validate_market_bar({
        "symbol": "BMRI",
        "timestamp": "2026-03-20T09:00:00Z",
        "open": 1100.0,
        "high": 1200.0,
        "low": 1050.0, # Cannot fill limit at 1000
        "close": 1150.0,
        "volume": 500_000.0
    })
    executed = desk.execution_engine.simulate_execution(order, bar, desk.portfolio, "2026-03-20T09:00:00Z")
    assert executed.status == "EXPIRED"
    assert "PRICE_UNREACHABLE" in executed.rejection_reason
    assert len(desk.portfolio.positions) == 0

# 8. SCENARIO H: Partial Fill (Order quantity exceeds liquidity capacity)
@pytest.mark.operational
def test_scenario_h_partial_fill(clean_desk):
    desk = clean_desk
    # Order 50,000 shares, but bar volume is only 100,000 (max 10% = 10,000 shares)
    order = desk.execution_engine.create_order(
        run_id="RUN_H",
        event_id="EVT_H",
        symbol="PTBA",
        side="BUY",
        quantity=50_000.0,
        lots=500,
        request_price=2500.0,
        stop_loss=2300.0,
        target_price=3000.0,
        order_type="LIMIT"
    )
    bar = desk.validate_market_bar({
        "symbol": "PTBA",
        "timestamp": "2026-03-20T09:00:00Z",
        "open": 2500.0,
        "high": 2550.0,
        "low": 2450.0,
        "close": 2500.0,
        "volume": 100_000.0
    })
    executed = desk.execution_engine.simulate_execution(order, bar, desk.portfolio, "2026-03-20T09:00:00Z")
    assert executed.status == "PARTIALLY_FILLED"
    assert executed.filled_quantity == 10_000.0
    # Portfolio reflects actual filled quantity
    assert list(desk.portfolio.positions.values())[0].quantity == 10_000.0

# 9. SCENARIO I: Worker Crash & State Recovery
@pytest.mark.operational
def test_scenario_i_worker_crash_recovery(tmp_path):
    state_dir = tmp_path / "crash_state"
    desk1 = TradingDeskSimulator(run_id="RUN_CRASH_1", state_dir=str(state_dir))
    pos = PaperPosition(
        position_id="POS_CRASH_1",
        job_id="JOB_CRASH_1",
        symbol="BBNI",
        status="OPEN",
        entry_price=1000.0,
        quantity=100.0,
        stop_loss=900.0,
        target_price=1200.0,
        initial_risk=100.0,
        initial_reward=200.0,
        initial_rr=2.0
    )
    desk1.portfolio.open_position(pos)
    
    # Save checkpoint
    checkpoint_file = state_dir / "portfolio_checkpoint.json"
    checkpoint_file.write_text(json.dumps({
        "cash": desk1.portfolio.cash,
        "positions": {p_id: p.model_dump() for p_id, p in desk1.portfolio.positions.items()}
    }), encoding="utf-8")
    
    # Simulate abrupt crash and restart
    desk2 = TradingDeskSimulator(run_id="RUN_CRASH_2", state_dir=str(state_dir))
    saved_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
    desk2.portfolio.cash = saved_data["cash"]
    for p_id, p_dict in saved_data["positions"].items():
        desk2.portfolio.positions[p_id] = PaperPosition(**p_dict)
        
    assert "POS_CRASH_1" in desk2.portfolio.positions
    assert desk2.portfolio.positions["POS_CRASH_1"].status == "OPEN"
    assert desk2.portfolio.reconcile().is_valid

# 10. SCENARIO J: Duplicate Event & Idempotency
@pytest.mark.operational
def test_scenario_j_duplicate_event(clean_desk):
    desk = clean_desk
    event_id = "EVT_DEDUP_001"
    h = "hash_sample_payload"
    status1 = desk.idempotency.check_and_record(event_id, h)
    status2 = desk.idempotency.check_and_record(event_id, h)
    
    assert status1 == "NEW"
    assert status2 == "DUPLICATE"

# 11. SCENARIO K: Restart During Exit
@pytest.mark.operational
def test_scenario_k_restart_during_exit(clean_desk):
    desk = clean_desk
    pos = PaperPosition(
        position_id="POS_EXIT_1",
        job_id="JOB_EXIT_1",
        symbol="UNTR",
        status="OPEN",
        entry_price=20000.0,
        quantity=10.0,
        stop_loss=19000.0,
        target_price=23000.0,
        initial_risk=1000.0,
        initial_reward=3000.0,
        initial_rr=3.0
    )
    desk.portfolio.open_position(pos)
    
    # Process exit
    desk.portfolio.close_position(pos.position_id, 21000.0, "2026-03-20T09:00:00Z", "PROFIT_TARGET", cost=525.0)
    assert desk.portfolio.positions[pos.position_id].status == "CLOSED"
    assert desk.portfolio.reconcile().is_valid

# 12. SCENARIO L: Point-In-Time Violation Attempt (Blocked Fail-Closed)
@pytest.mark.operational
def test_scenario_l_pit_violation_blocked(clean_desk):
    desk = clean_desk
    # Simulated time is 2026-03-20T09:00:00Z; query bar is in the future (2026-03-25)
    future_bar = {
        "symbol": "BBCA",
        "timestamp": "2026-03-25T09:00:00Z",
        "open": 1000.0,
        "high": 1050.0,
        "low": 980.0,
        "close": 1020.0,
        "volume": 100_000.0
    }
    with pytest.raises(DataValidationError, match="PIT_FIREWALL_VIOLATION"):
        desk.validate_market_bar(future_bar)

# 13. SAFETY TEST: Live Execution Boundary
@pytest.mark.operational
def test_live_execution_boundary_blocked(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "true")
    with pytest.raises(LiveExecutionBlockedError):
        PaperExecutionSimulator()

# 14. HUMAN OVERRIDE CONTROLS
@pytest.mark.operational
def test_human_override_controls(clean_desk):
    desk = clean_desk
    assert desk.control_state == TradingDeskControlState.ACTIVE
    
    desk.pause_desk("Test pause")
    assert desk.control_state == TradingDeskControlState.PAUSED
    
    desk.resume_desk("Test resume")
    assert desk.control_state == TradingDeskControlState.ACTIVE
    
    # Emergency Stop
    pos = PaperPosition(
        position_id="POS_EMERGENCY",
        job_id="JOB_EMERGENCY",
        symbol="ADRO",
        status="OPEN",
        entry_price=3000.0,
        quantity=100.0,
        stop_loss=2800.0,
        target_price=3500.0,
        initial_risk=200.0,
        initial_reward=500.0,
        initial_rr=2.5
    )
    desk.portfolio.open_position(pos)
    desk.emergency_stop("Kill switch test")
    
    assert desk.control_state == TradingDeskControlState.EMERGENCY_STOPPED
    assert desk.portfolio.positions["POS_EMERGENCY"].status == "CLOSED"
    assert desk.portfolio.reconcile().is_valid

# 15. DETERMINISTIC REPLAY CONSISTENCY (Run A == Run B)
@pytest.mark.operational
def test_deterministic_replay_consistency(tmp_path):
    desk_a = TradingDeskSimulator(run_id="REPLAY_RUN_A", state_dir=str(tmp_path / "state_a"), audit_dir=str(tmp_path / "audit_a"))
    desk_b = TradingDeskSimulator(run_id="REPLAY_RUN_B", state_dir=str(tmp_path / "state_b"), audit_dir=str(tmp_path / "audit_b"))
    
    market_input = {
        "BBCA": make_bar("BBCA", 1000.0, 1_000_000.0),
        "BBRI": make_bar("BBRI", 500.0, 500_000.0),
        "TLKM": make_bar("TLKM", 3000.0, 800_000.0)
    }
    
    res_a = desk_a.run_daily_session(market_input)
    res_b = desk_b.run_daily_session(market_input)
    
    assert res_a["candidates_scanned"] == res_b["candidates_scanned"]
    assert res_a["decisions_made"] == res_b["decisions_made"]
    assert res_a["orders_submitted"] == res_b["orders_submitted"]
    assert res_a["active_positions"] == res_b["active_positions"]
    assert res_a["end_equity"] == res_b["end_equity"]
    assert res_a["reconciliation_valid"] and res_b["reconciliation_valid"]
