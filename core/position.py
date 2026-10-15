from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

class PaperPosition(BaseModel):
    position_id: str
    job_id: str
    symbol: str
    status: Literal["PENDING", "OPEN", "CLOSED", "CANCELLED"] = "PENDING"
    
    # Entry
    entry_timestamp: Optional[str] = None
    entry_price: Optional[float] = None
    quantity: float = 0.0
    lots: int = 0
    
    # Risk parameters
    stop_loss: float
    target_price: float
    initial_risk: float
    initial_reward: float
    initial_rr: float
    position_value: float = 0.0
    entry_cost: float = 0.0
    exit_cost: float = 0.0
    
    # Current state
    current_price: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    max_favorable_excursion: float = 0.0
    max_adverse_excursion: float = 0.0
    highest_price: Optional[float] = None
    lowest_price: Optional[float] = None
    
    # Thesis and Monitoring
    thesis: str = ""
    invalidation_conditions: List[str] = Field(default_factory=list)
    opened_by_decision_id: str = ""
    holding_bars: int = 0
    
    # Exit
    closed_timestamp: Optional[str] = None
    close_price: Optional[float] = None
    close_reason: Optional[str] = None

    def update_price(self, price: float):
        if self.status != "OPEN":
            return
            
        self.current_price = price
        if self.entry_price and self.entry_price > 0:
            self.unrealized_pnl = (self.current_price - self.entry_price) * self.quantity
            self.unrealized_pnl_pct = (self.current_price - self.entry_price) / self.entry_price
            
            # Update MFE/MAE
            if self.highest_price is None or price > self.highest_price:
                self.highest_price = price
            if self.lowest_price is None or price < self.lowest_price:
                self.lowest_price = price
                
            mfe = (self.highest_price - self.entry_price) / self.entry_price
            mae = (self.lowest_price - self.entry_price) / self.entry_price
            
            self.max_favorable_excursion = max(self.max_favorable_excursion, mfe)
            # MAE is typically tracked as a negative number or absolute distance
            # we'll track it as a negative percentage
            if mae < self.max_adverse_excursion:
                self.max_adverse_excursion = mae

class PositionMonitorEvent(BaseModel):
    event_id: str
    position_id: str
    symbol: str
    timestamp: str
    event_type: Literal[
        "PRICE_UPDATE", 
        "STOP_APPROACHING", 
        "TARGET_APPROACHING", 
        "STOP_TRIGGERED", 
        "TARGET_TRIGGERED", 
        "THESIS_INVALIDATED", 
        "RISK_CHANGED", 
        "DATA_QUALITY_CHANGED", 
        "REGIME_CHANGED", 
        "TIME_EXIT"
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    previous_value: Optional[Any] = None
    current_value: Optional[Any] = None
    reason: str
