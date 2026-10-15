import pytest
import shutil
import hashlib
import json
from pathlib import Path
from core.audit_ledger import AuditLedger
from core.health import HealthMonitor, HealthStatus
from core.paper_portfolio import PaperPortfolio
from core.position import PaperPosition
from core.trading_desk_simulation import TradingDeskSimulator
from core.paper_execution import PaperExecutionSimulator, PaperOrder

def test_health_monitor_does_not_delete_state():
    """Verify health monitor failure check does not wipe runtime state directory."""
    state_dir = Path("state/audit")
    assert state_dir.exists(), "Runtime state/audit must exist"
    
    # Test checking a missing path inside test_state
    dummy_dir = Path("test_state/sub_missing")
    hm = HealthMonitor(str(dummy_dir / "sys.json"))
    if dummy_dir.exists():
        shutil.rmtree(dummy_dir)
    assert hm.check_health() == HealthStatus.FAILED
    assert state_dir.exists(), "HealthMonitor must never delete production state directory"
    if Path("test_state").exists():
        shutil.rmtree("test_state")

def test_audit_ledger_throughput_and_flushing(tmp_path):
    """Verify AuditLedger handles high-frequency logging with immediate flush and persistence."""
    audit_dir = tmp_path / "audit"
    ledger = AuditLedger(log_dir=str(audit_dir))
    
    # Log 100 events rapidly
    for i in range(100):
        ledger.log_event(
            job_id="TEST_THROUGHPUT",
            timestamp=f"2026-03-20T09:{i:02d}:00Z",
            stage="TEST_STAGE",
            event_type="TEST_EVENT",
            status="INFO",
            metadata={"iteration": i}
        )
        
    log_file = audit_dir / "ledger.jsonl"
    assert log_file.exists()
    lines = [line.strip() for line in open(log_file, "r", encoding="utf-8") if line.strip()]
    assert len(lines) == 100, f"Expected 100 events, found {len(lines)}"
    
    ledger.close()

def test_trade_level_vs_portfolio_accounting_exactness():
    """Verify that trade-level gross, fees, and realized P&L sum exactly to portfolio metrics."""
    portfolio = PaperPortfolio(initial_capital=100_000_000.0)
    
    # Simulate Trade 1: Winning trade
    pos1 = PaperPosition(
        position_id="POS_TEST_001",
        job_id="JOB_001",
        symbol="BBCA",
        status="PENDING",
        entry_timestamp="2026-03-20",
        entry_price=1000.0,
        quantity=5000.0,
        lots=50,
        stop_loss=950.0,
        target_price=1100.0,
        initial_risk=250000.0,
        initial_reward=500000.0,
        initial_rr=2.0
    )
    portfolio.open_position(pos1, cost=7500.0) # 0.15% of 5,000,000
    portfolio.close_position("POS_TEST_001", close_price=1100.0, timestamp="2026-03-25", reason="TARGET_REACHED", cost=13750.0)
    
    # Simulate Trade 2: Losing trade
    pos2 = PaperPosition(
        position_id="POS_TEST_002",
        job_id="JOB_002",
        symbol="BBRI",
        status="PENDING",
        entry_timestamp="2026-03-26",
        entry_price=500.0,
        quantity=10000.0,
        lots=100,
        stop_loss=470.0,
        target_price=560.0,
        initial_risk=300000.0,
        initial_reward=600000.0,
        initial_rr=2.0
    )
    portfolio.open_position(pos2, cost=7500.0)
    portfolio.close_position("POS_TEST_002", close_price=470.0, timestamp="2026-03-30", reason="STOP_LOSS", cost=11750.0)
    
    # Simulate Trade 3: Open position
    pos3 = PaperPosition(
        position_id="POS_TEST_003",
        job_id="JOB_003",
        symbol="BMRI",
        status="PENDING",
        entry_timestamp="2026-04-01",
        entry_price=600.0,
        quantity=8000.0,
        lots=80,
        stop_loss=570.0,
        target_price=660.0,
        initial_risk=240000.0,
        initial_reward=480000.0,
        initial_rr=2.0
    )
    portfolio.open_position(pos3, cost=7200.0)
    pos3.update_price(620.0) # Current price higher than entry
    
    # Reconcile Path A (Trade-level recomputation)
    closed = [p for p in portfolio.positions.values() if p.status == "CLOSED"]
    trade_gross_sum = sum((p.close_price - p.entry_price) * p.quantity for p in closed)
    trade_fees_sum = sum(p.entry_cost + p.exit_cost for p in closed)
    trade_net_sum = sum(p.realized_pnl for p in closed)
    
    # Reconcile Path B (Portfolio state)
    assert abs(trade_gross_sum - trade_fees_sum - trade_net_sum) < 1e-6, "Trade level Gross - Fees != Net PnL"
    assert abs(trade_net_sum - portfolio.realized_pnl) < 1e-6, "Trade net PnL sum != portfolio.realized_pnl"
    
    # Equity identity: Cash + Open Market Value == Equity
    open_positions = [p for p in portfolio.positions.values() if p.status == "OPEN"]
    open_mv = sum(p.quantity * p.current_price for p in open_positions)
    assert abs(portfolio.cash + open_mv - portfolio.get_equity()) < 1e-6, "Cash + MV != Equity"
    
    # Cash flow identity: Initial Cash + Realized PnL - Open Cost - Open Entry Fee == Cash
    open_cost = sum(p.quantity * p.entry_price for p in open_positions)
    open_fee = sum(p.entry_cost for p in open_positions)
    expected_cash = 100_000_000.0 + portfolio.realized_pnl - open_cost - open_fee
    assert abs(expected_cash - portfolio.cash) < 1e-6, "Cash flow conservation mismatch"

def test_deterministic_id_generation(tmp_path):
    """Verify that deterministic hashing produces identical IDs across distinct runs with identical inputs."""
    desk1 = TradingDeskSimulator(run_id="RUN_1", state_dir=str(tmp_path / "s1"), audit_dir=str(tmp_path / "a1"))
    desk2 = TradingDeskSimulator(run_id="RUN_2", state_dir=str(tmp_path / "s2"), audit_dir=str(tmp_path / "a2"))
    
    quant_out = {
        "status": "CANDIDATE_FOUND",
        "quant_score": 85.0,
        "quant_confidence": 90.0,
        "close_price": 1010.0,
        "stop_loss": 950.0,
        "target_price": 1150.0
    }
    intel_out = {
        "thesis": "Strong growth",
        "catalysts": ["Earnings beat"],
        "contradictions": [],
        "red_team_decision": "PASS"
    }
    
    desk1.simulated_timestamp = "2026-03-20T09:00:00Z"
    desk2.simulated_timestamp = "2026-03-20T09:00:00Z"
    
    dec1 = desk1.run_agent3_committee("BBCA", quant_out, intel_out)
    dec2 = desk2.run_agent3_committee("BBCA", quant_out, intel_out)
    
    assert dec1.job_id == dec2.job_id, f"Decision job_id mismatch: {dec1.job_id} != {dec2.job_id}"
    assert dec1.action == dec2.action
    assert dec1.position_size == dec2.position_size
