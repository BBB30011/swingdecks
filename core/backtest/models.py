from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class BacktestIntegrityError(Exception):
    pass

class BacktestConfig(BaseModel):
    initial_capital: float = 100000000.0
    holding_period_bars: int = 5
    entry_mode: str = "NEXT_BAR_OPEN"
    exit_mode: str = "FIXED_HOLD"
    commission_rate: float = 0.001
    slippage_rate: float = 0.0005
    max_positions: int = 5
    risk_per_trade: float = 0.005
    minimum_bars: int = 200
    lot_size: int = 100
    
    # Batch AX Parameters
    atr_stop_multiplier: Optional[float] = None
    atr_trailing_multiplier: Optional[float] = None
    block_bear_regime: bool = False
    
class BacktestSignal(BaseModel):
    timestamp: str
    symbol: str
    quant_score: float
    quant_confidence: float
    candidate_quality: str
    research_priority: str = "UNKNOWN"
    stock_regime: str
    market_regime: str
    regime_alignment: str = "UNKNOWN"
    flow_state: str = "UNKNOWN"
    action: str
    features: dict

from core.decision import DecisionResult

class BacktestTrade(BaseModel):
    position_id: str
    symbol: str
    signal_timestamp: str
    entry_timestamp: str
    exit_timestamp: Optional[str] = None
    entry_price: float
    stop_loss: float
    target_price: float
    exit_price: Optional[float] = None
    shares: float
    quantity: float
    gross_pnl: Optional[float] = None
    net_pnl: Optional[float] = None
    return_pct: Optional[float] = None
    cost: Optional[float] = None
    holding_bars: Optional[int] = None
    status: str = "PENDING"
    signal: Any

class BacktestResult(BaseModel):
    initial_capital: float
    final_capital: float
    total_return: float
    max_drawdown: float
    
    signals_generated: int = 0
    trades_opened: int = 0
    trades_closed: int = 0
    trades_skipped: int = 0
    open_positions_at_end: int = 0
    
    trades_history: List[BacktestTrade] = []
    
    number_of_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Optional[float]
    profit_factor: Optional[float]
    expectancy: Optional[float]
    average_win: Optional[float]
    average_loss: Optional[float]
    average_hold: Optional[float]
    sharpe: Optional[float] = None
    sortino: Optional[float] = None
    turnover: Optional[float]
    total_cost: float
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    score_buckets: Dict[str, dict]
    confidence_buckets: Dict[str, dict]
    regime_breakdown: Dict[str, dict]
    
    timing_buckets: Dict[str, dict] = {}
    tier_buckets: Dict[str, dict] = {}
    urgency_buckets: Dict[str, dict] = {}
    relative_strength_buckets: Dict[str, dict] = {}
    flow_buckets: Dict[str, dict] = {}
    
    data_gap_flags: Dict[str, Any] = {}
    corporate_action_status: str = "UNKNOWN"
    universe_method: str = "CURRENT_UNIVERSE"
    
    data_bias_flags: Dict[str, str] = {
        "lookahead_bias": "TESTED",
        "survivorship_bias": "POSSIBLE",
        "selection_bias": "POSSIBLE"
    }
    oos_validation: str = "NOT_CONFIGURED"
    integrity_warnings: List[str] = []
    warnings: List[str] = [
        "POSSIBLE_SURVIVORSHIP_BIAS",
        "POSSIBLE_SELECTION_BIAS",
        "NO_OOS_SPLIT",
        "NO_REAL_BROKER_FLOW",
        "NO_MARKET_IMPACT_MODEL"
    ]
    market_impact_model: str = "NOT_IMPLEMENTED"
