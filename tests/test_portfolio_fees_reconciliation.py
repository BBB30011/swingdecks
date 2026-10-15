import pytest
import uuid
from core.position import PaperPosition
from core.paper_portfolio import PaperPortfolio

def create_test_position(symbol="BBCA", entry_price=1000.0, quantity=100.0):
    return PaperPosition(
        position_id=str(uuid.uuid4()),
        job_id="job_test_fees",
        symbol=symbol,
        status="PENDING",
        entry_price=entry_price,
        quantity=quantity,
        stop_loss=900.0,
        target_price=1200.0,
        initial_risk=100.0,
        initial_reward=200.0,
        initial_rr=2.0
    )

@pytest.mark.operational
def test_reconciliation_zero_fees():
    portfolio = PaperPortfolio(initial_capital=10_000_000.0)
    pos = create_test_position()
    portfolio.open_position(pos, cost=0.0)
    
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation with zero fees, got: {rep.issues}"
    
    pos.update_price(1100.0)
    rep = portfolio.reconcile()
    assert rep.is_valid
    
    portfolio.close_position(pos.position_id, 1100.0, "2026-09-28T09:00:00Z", "TARGET_HIT", cost=0.0)
    rep = portfolio.reconcile()
    assert rep.is_valid

@pytest.mark.operational
def test_reconciliation_entry_fee_open_position():
    portfolio = PaperPortfolio(initial_capital=10_000_000.0)
    pos = create_test_position(entry_price=1000.0, quantity=100.0)
    # Entry cost = 250.0 (e.g. 0.25% commission)
    portfolio.open_position(pos, cost=250.0)
    
    assert pos.entry_cost == 250.0
    assert portfolio.total_transaction_cost == 250.0
    # Cash was reduced by position value (100,000) and cost (250)
    assert portfolio.cash == 10_000_000.0 - 100_000.0 - 250.0
    
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation with entry cost, got: {rep.issues}"
    
    # Update price and test again
    pos.update_price(1050.0)
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation after price update, got: {rep.issues}"

@pytest.mark.operational
def test_reconciliation_entry_and_exit_fees_closed_position():
    portfolio = PaperPortfolio(initial_capital=10_000_000.0)
    pos = create_test_position(entry_price=1000.0, quantity=100.0)
    # Entry fee: 200, Exit fee: 250
    portfolio.open_position(pos, cost=200.0)
    pos.update_price(1100.0)
    
    portfolio.close_position(pos.position_id, 1100.0, "2026-09-28T09:30:00Z", "TARGET_HIT", cost=250.0)
    
    assert pos.entry_cost == 200.0
    assert pos.exit_cost == 250.0
    # Gross PnL: (1100 - 1000) * 100 = 10,000
    # Net Realized PnL: 10,000 - 200 - 250 = 9,550
    assert pos.realized_pnl == 9550.0
    assert portfolio.realized_pnl == 9550.0
    assert portfolio.total_transaction_cost == 450.0
    
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation after close with fees, got: {rep.issues}"

@pytest.mark.operational
def test_reconciliation_multiple_positions_with_different_fees():
    portfolio = PaperPortfolio(initial_capital=10_000_000.0)
    pos1 = create_test_position(symbol="BBCA", entry_price=1000.0, quantity=50.0)
    pos2 = create_test_position(symbol="BBRI", entry_price=500.0, quantity=100.0)
    
    portfolio.open_position(pos1, cost=125.0)
    portfolio.open_position(pos2, cost=100.0)
    
    pos1.update_price(1020.0)
    pos2.update_price(480.0)
    
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation with multiple positions, got: {rep.issues}"
    
    # Close pos1 at profit with fee, leave pos2 open
    portfolio.close_position(pos1.position_id, 1020.0, "2026-09-28T09:45:00Z", "PROFIT_TAKE", cost=130.0)
    rep = portfolio.reconcile()
    assert rep.is_valid, f"Expected valid reconciliation with 1 closed + 1 open position, got: {rep.issues}"
