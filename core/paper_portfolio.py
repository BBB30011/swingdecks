from typing import Dict, List, Any
from core.position import PaperPosition

class PortfolioReconciliationReport:
    def __init__(self):
        self.is_valid = True
        self.issues = []
        
    def add_issue(self, issue: str):
        self.is_valid = False
        self.issues.append(issue)

class PaperPortfolio:
    def __init__(self, initial_capital: float = 100000000.0):
        self.capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, PaperPosition] = {}
        self.realized_pnl = 0.0
        self.total_transaction_cost = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = initial_capital
        
    def get_equity(self) -> float:
        unrealized = sum(p.unrealized_pnl for p in self.positions.values() if p.status == "OPEN")
        principal = sum(p.position_value for p in self.positions.values() if p.status == "OPEN")
        return self.cash + principal + unrealized
        
    def get_total_unrealized_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions.values() if p.status == "OPEN")

    def get_total_exposure(self) -> float:
        return sum(p.position_value for p in self.positions.values() if p.status == "OPEN")
        
    def get_total_risk(self) -> float:
        return sum(p.initial_risk for p in self.positions.values() if p.status == "OPEN")
        
    def can_open_position(self, symbol: str) -> bool:
        for p in self.positions.values():
            if p.symbol == symbol and p.status in ["PENDING", "OPEN"]:
                return False
        return True
        
    def open_position(self, position: PaperPosition, cost: float = 0.0):
        if not self.can_open_position(position.symbol):
            raise ValueError(f"REJECTED_DUPLICATE_POSITION: {position.symbol} is already OPEN or PENDING")
            
        position.status = "OPEN"
        position.position_value = position.entry_price * position.quantity
        position.entry_cost = cost
        self.positions[position.position_id] = position
        
        self.cash -= position.position_value
        self.cash -= cost
        self.total_transaction_cost += cost
        
    def close_position(self, position_id: str, close_price: float, timestamp: str, reason: str, cost: float = 0.0):
        if position_id not in self.positions:
            return
            
        position = self.positions[position_id]
        if position.status != "OPEN":
            return
            
        position.status = "CLOSED"
        position.close_price = close_price
        position.closed_timestamp = timestamp
        position.close_reason = reason
        position.exit_cost = cost
        
        gross_pnl = (close_price - position.entry_price) * position.quantity
        position.realized_pnl = gross_pnl - position.entry_cost - cost
        
        self.realized_pnl += position.realized_pnl
        self.cash += (close_price * position.quantity) - cost
        self.total_transaction_cost += cost
        
        eq = self.get_equity()
        if eq > self.peak_equity:
            self.peak_equity = eq
        else:
            dd = (self.peak_equity - eq) / self.peak_equity
            if dd > self.max_drawdown:
                self.max_drawdown = dd
                
    def reconcile(self) -> PortfolioReconciliationReport:
        report = PortfolioReconciliationReport()
        
        if self.cash < 0:
            report.add_issue(f"Negative cash: {self.cash}")
            
        seen_symbols = set()
        for p in self.positions.values():
            if p.status in ["OPEN", "PENDING"]:
                if p.symbol in seen_symbols:
                    report.add_issue(f"Duplicate active position for {p.symbol}")
                seen_symbols.add(p.symbol)
                
            if p.quantity <= 0:
                report.add_issue(f"Impossible quantity for {p.position_id}: {p.quantity}")
                
        # Validate PnL
        expected_equity = self.capital + self.realized_pnl + sum((p.unrealized_pnl - p.entry_cost) for p in self.positions.values() if p.status == "OPEN")
        actual_equity = self.get_equity()
        if abs(expected_equity - actual_equity) > 0.1: # float tolerance
            report.add_issue(f"Mismatched PnL. Expected: {expected_equity}, Actual: {actual_equity}")
            
        return report
