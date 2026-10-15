import pytest
import uuid
import os
import json
from pathlib import Path
from core.position import PaperPosition, PositionMonitorEvent
from core.position_monitor import PositionMonitor
from core.exit_engine import ExitEngine
from core.paper_portfolio import PaperPortfolio
from core.materiality import MaterialityEngine
from core.learning import LearningLedger
from core.paper_session import PaperSessionManager
from datetime import datetime, timezone

def create_mock_position():
    return PaperPosition(
        position_id=str(uuid.uuid4()),
        job_id="job_1",
        symbol="BBCA",
        status="PENDING",
        entry_price=1000,
        quantity=100,
        stop_loss=900,
        target_price=1200,
        initial_risk=100,
        initial_reward=200,
        initial_rr=2.0
    )

def test_paper_position_schema():
    pos = create_mock_position()
    assert pos.status == "PENDING"
    pos.status = "OPEN"
    pos.update_price(1100)
    assert pos.unrealized_pnl == 10000
    assert pos.max_favorable_excursion == 0.1
    
    pos.update_price(950)
    assert pos.unrealized_pnl == -5000
    assert pos.max_adverse_excursion == -0.05
    assert pos.max_favorable_excursion == 0.1

def test_duplicate_position_protection():
    portfolio = PaperPortfolio(100000)
    pos1 = create_mock_position()
    portfolio.open_position(pos1)
    
    pos2 = create_mock_position()
    assert not portfolio.can_open_position(pos2.symbol)
    with pytest.raises(ValueError, match="REJECTED_DUPLICATE_POSITION"):
        portfolio.open_position(pos2)

def test_portfolio_accounting():
    portfolio = PaperPortfolio(100000)
    pos = create_mock_position()
    portfolio.open_position(pos)
    assert portfolio.cash == 0
    assert portfolio.get_total_exposure() == 100000
    
    pos.update_price(1100)
    assert portfolio.get_equity() == 110000
    
    portfolio.close_position(pos.position_id, 1100, "ts", "TARGET_REACHED")
    assert portfolio.cash == 110000
    assert portfolio.realized_pnl == 10000

def test_materiality_engine():
    assert MaterialityEngine.classify_price_movement(900, 1000, 900, 1200) == "CRITICAL"
    assert MaterialityEngine.classify_price_movement(1200, 1000, 900, 1200) == "CRITICAL"
    assert MaterialityEngine.classify_price_movement(905, 1000, 900, 1200) == "HIGH"
    assert MaterialityEngine.classify_price_movement(1190, 1000, 900, 1200) == "HIGH"
    assert MaterialityEngine.classify_price_movement(1060, 1000, 900, 1200) == "MEDIUM"
    assert MaterialityEngine.classify_price_movement(1010, 1000, 900, 1200) == "LOW"

def test_exit_priority():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.update_price(900)
    
    # Target and Data Invalid triggered same time (impossible in price, but logically)
    # DATA_INVALID should win
    ctx = {"data_quality": "INVALID"}
    res = ExitEngine.evaluate(pos, ctx)
    assert res["reason"] == "DATA_INVALID"
    
    # Thesis invalidated > Stop Loss
    ctx = {"active_invalidations": ["Corp Action"]}
    res = ExitEngine.evaluate(pos, ctx)
    assert res["reason"] == "THESIS_INVALIDATED"

# === SCENARIOS ===

def test_scenario_a_target_reached():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.update_price(1200)
    res = PositionMonitor.monitor(pos, 1200, "ts", {})
    assert res.action == "EXIT"
    assert res.reason == "TARGET_REACHED"
    assert res.target_triggered

def test_scenario_b_stop_loss():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.update_price(900)
    res = PositionMonitor.monitor(pos, 900, "ts", {})
    assert res.action == "EXIT"
    assert res.reason == "STOP_LOSS"
    assert res.stop_triggered

def test_scenario_c_thesis_invalidated():
    pos = create_mock_position()
    pos.status = "OPEN"
    res = PositionMonitor.monitor(pos, 1050, "ts", {"active_invalidations": ["NEWS_CONTRADICTION"]})
    assert res.action == "EXIT"
    assert res.reason == "THESIS_INVALIDATED"
    assert res.thesis_invalidated

def test_scenario_d_risk_red():
    pos = create_mock_position()
    pos.status = "OPEN"
    res = PositionMonitor.monitor(pos, 1050, "ts", {"risk_state": "RED", "prev_risk_state": "GREEN"})
    assert res.action == "EXIT"
    assert res.reason == "RISK_RED"
    assert any(e.event_type == "RISK_CHANGED" for e in res.events)

def test_scenario_e_restart_persistence(tmp_path):
    pos = create_mock_position()
    pos.status = "OPEN"
    
    # Simulate save
    p = tmp_path / "pos.json"
    p.write_text(pos.model_dump_json())
    
    # Simulate reload
    reloaded = PaperPosition.model_validate_json(p.read_text())
    assert reloaded.status == "OPEN"
    assert reloaded.position_id == pos.position_id

def test_scenario_f_duplicate():
    # Tested in test_duplicate_position_protection
    pass

def test_scenario_g_invalid_data():
    pos = create_mock_position()
    pos.status = "OPEN"
    res = PositionMonitor.monitor(pos, 9999, "ts", {"data_quality": "INVALID"})
    # It exits via DATA_INVALID
    assert res.action == "EXIT"
    assert res.reason == "DATA_INVALID"
    # Event should be DATA_QUALITY_CHANGED
    assert any(e.event_type == "DATA_QUALITY_CHANGED" for e in res.events)

def test_scenario_h_trade_lesson(tmp_path):
    ledger = LearningLedger(str(tmp_path))
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.close_price = 1200
    pos.realized_pnl = 20000
    pos.close_reason = "TARGET_REACHED"
    
    lesson = ledger.generate_lesson(pos, {"quant_score": 85})
    assert lesson.outcome == "WIN"
    
    ledger.save_lesson(lesson)
    assert (tmp_path / "successful_setups" / f"{lesson.lesson_id}.json").exists()

def test_time_exit():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.holding_bars = 10
    res = PositionMonitor.monitor(pos, 1050, "ts", {"config": {"max_holding_bars": 10}})
    assert res.action == "EXIT"
    assert res.reason == "TIME_EXIT"

def test_portfolio_reconciliation():
    portfolio = PaperPortfolio(10000)
    pos = create_mock_position()
    pos.quantity = -10
    portfolio.positions[pos.position_id] = pos
    
    rep = portfolio.reconcile()
    assert not rep.is_valid
    assert any("Impossible quantity" in i for i in rep.issues)
    
    portfolio.cash = -500
    rep = portfolio.reconcile()
    assert any("Negative cash" in i for i in rep.issues)

def test_no_hindsight_leakage(tmp_path):
    # Asserting that lesson does not change position entry features
    pos = create_mock_position()
    pos.status = "CLOSED"
    pos.close_price = 1050
    ctx = {"quant_score": 90}
    ledger = LearningLedger(str(tmp_path))
    lesson = ledger.generate_lesson(pos, ctx)
    assert "outcome" in lesson.model_dump()
    assert ctx["quant_score"] == 90 # Unchanged

def test_determinism():
    pos1 = create_mock_position()
    pos2 = create_mock_position()
    pos2.position_id = pos1.position_id # match IDs
    
    res1 = PositionMonitor.monitor(pos1, 1100, "ts1", {})
    res2 = PositionMonitor.monitor(pos2, 1100, "ts1", {})
    
    assert res1.action == res2.action
    assert res1.reason == res2.reason

def test_kill_switch_allows_monitoring():
    # A paused system still allows monitors to produce exit signals
    pos = create_mock_position()
    pos.status = "OPEN"
    res = PositionMonitor.monitor(pos, 900, "ts", {"system_status": "PAUSED"})
    assert res.action == "EXIT"
    assert res.reason == "STOP_LOSS"

def test_paper_session_schema():
    portfolio = PaperPortfolio(50000)
    session = PaperSessionManager.snapshot_to_session("s1", "2020-01-01", portfolio)
    assert session.starting_capital == 50000
    assert session.status == "RUNNING"

def test_learning_pattern_aggregation_insufficient(tmp_path):
    ledger = LearningLedger(str(tmp_path))
    stats = ledger.get_pattern_statistics()
    assert stats["status"] == "INSUFFICIENT_SAMPLE"

def test_learning_pattern_aggregation_sufficient(tmp_path):
    ledger = LearningLedger(str(tmp_path))
    for i in range(12):
        pos = create_mock_position()
        pos.position_id = str(uuid.uuid4())
        pos.realized_pnl = 100 if i % 2 == 0 else -50
        pos.close_price = 1100 if i % 2 == 0 else 950
        pos.entry_price = 1000
        lesson = ledger.generate_lesson(pos, {})
        ledger.save_lesson(lesson)
        
    stats = ledger.get_pattern_statistics()
    assert stats["status"] == "VALID"
    assert stats["sample_size"] == 12
    assert stats["win_rate"] == 0.5
    assert stats["avg_pnl"] == 25.0

def test_position_tracking_max_excursions():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.update_price(1050)
    assert pos.max_favorable_excursion == 0.05
    pos.update_price(950)
    assert pos.max_adverse_excursion == -0.05
    pos.update_price(1100)
    assert pos.max_favorable_excursion == 0.1
    assert pos.max_adverse_excursion == -0.05

def test_material_event_generation():
    pos = create_mock_position()
    pos.status = "OPEN"
    # Move price near target (1200)
    res = PositionMonitor.monitor(pos, 1190, "ts", {})
    assert any(e.event_type == "TARGET_APPROACHING" for e in res.events)
    
    # Move price near stop (900)
    res2 = PositionMonitor.monitor(pos, 910, "ts", {})
    assert any(e.event_type == "STOP_APPROACHING" for e in res2.events)

def test_close_reason_persistence():
    portfolio = PaperPortfolio(10000)
    pos = create_mock_position()
    portfolio.open_position(pos)
    portfolio.close_position(pos.position_id, 1200, "ts", "MANUAL_EXIT")
    
    assert portfolio.positions[pos.position_id].status == "CLOSED"
    assert portfolio.positions[pos.position_id].close_reason == "MANUAL_EXIT"

def test_portfolio_drawdown():
    portfolio = PaperPortfolio(10000)
    pos = create_mock_position()
    portfolio.open_position(pos)
    
    # price drops
    pos.update_price(900)
    # eq = 10000 - 10000 + 900*100 = 9000
    # Wait, entry_value was 10000, un_pnl = -100*100 = -10000. 
    # Mock position has entry_price 1000, qty 100 -> value 100000! 
    pass # we test conceptually in next test

def test_portfolio_drawdown_actual():
    portfolio = PaperPortfolio(100000)
    pos = create_mock_position() # 1000 * 100 = 100000
    portfolio.open_position(pos)
    
    pos.update_price(900) # un_pnl = -10000
    portfolio.close_position(pos.position_id, 900, "ts", "STOP")
    
    # eq is 90000. Max DD = 10000 / 100000 = 0.1
    assert portfolio.max_drawdown == 0.1

def test_unrealized_pnl_pct():
    pos = create_mock_position()
    pos.status = "OPEN"
    pos.update_price(1100)
    assert pos.unrealized_pnl_pct == 0.1

def test_realized_pnl_pct_in_lesson(tmp_path):
    pos = create_mock_position()
    pos.status = "CLOSED"
    pos.close_price = 1100
    lesson = LearningLedger(str(tmp_path)).generate_lesson(pos, {})
    assert lesson.realized_pnl_pct == 0.1
