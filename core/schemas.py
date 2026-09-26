from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Dict, Any

class JobRequest(BaseModel):
    job_id: str
    symbol: str
    created_at: str
    status: str = "CREATED"

class QuantResult(BaseModel):
    job_id: str
    symbol: str
    quant_score: float = Field(..., ge=0, le=100)
    market_regime: str
    data_quality: str
    status: str = "READY_FOR_RESEARCH"

class ResearchResult(BaseModel):
    job_id: str
    symbol: str
    fundamental_summary: str
    macro_summary: str
    policy_summary: str
    sentiment_summary: str
    risk_flags: List[str]
    status: str = "READY_FOR_REVIEW"

class RedTeamResult(BaseModel):
    job_id: str
    symbol: str
    bull_case: str
    bear_case: str
    contradictions: List[str]
    unknowns: List[str]
    decision: Literal["PASS", "REWORK", "BLOCK"]

class DecisionResult(BaseModel):
    job_id: str
    symbol: str
    action: Literal["BUY", "WAIT", "HOLD", "SELL", "AVOID"]
    risk_state: Literal["GREEN", "YELLOW", "RED"]
    confidence: float = Field(..., ge=0, le=100)
    reason: str

class JobEnvelope(BaseModel):
    job_id: str = Field(..., min_length=1)
    job_type: str = Field(..., min_length=1)
    created_at: str
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    payload: Dict[str, Any]
    schema_version: str = "1.0"

class MarketBar(BaseModel):
    symbol: str = Field(..., min_length=1)
    timestamp: str
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float = Field(..., ge=0)

    @model_validator(mode='after')
    def check_ohlc(self) -> 'MarketBar':
        if self.high < self.low:
            raise ValueError("high tidak boleh lebih kecil dari low")
        if self.high < self.open:
            raise ValueError("high tidak boleh lebih kecil dari open")
        if self.high < self.close:
            raise ValueError("high tidak boleh lebih kecil dari close")
        if self.low > self.open:
            raise ValueError("low tidak boleh lebih besar dari open")
        if self.low > self.close:
            raise ValueError("low tidak boleh lebih besar dari close")
        return self

class DatasetMetadata(BaseModel):
    dataset_id: str = "UNKNOWN"
    data_origin: str = "UNKNOWN"
    market: str = "IDX"
    start_timestamp: str = ""
    end_timestamp: str = ""
    bar_frequency: str = "1D"
    record_count: int = 0
    universe_method: str = "CURRENT_UNIVERSE"
    corporate_action_status: str = "UNKNOWN"
    benchmark_available: bool = False
    audit_status: str = "VALID"
    gap_status: str = "NO_GAP"
    warnings: List[str] = []
    errors: List[str] = []

class MarketSnapshot(BaseModel):
    symbol: str = Field(..., min_length=1)
    timestamp: str
    bars: List[MarketBar] = Field(..., min_length=1)
    data_source: str = Field(..., min_length=1)
    data_quality: Literal["FRESH", "STALE", "INVALID"]
    metadata: DatasetMetadata = Field(default_factory=DatasetMetadata)

class BrokerFlowSnapshot(BaseModel):
    timestamp: str
    symbol: str
    foreign_net: float | None = None
    domestic_net: float | None = None
    broker_buy: float | None = None
    broker_sell: float | None = None
    source: str | None = None

class WalkForwardSplit(BaseModel):
    train_start: str
    train_end: str
    validation_start: str
    validation_end: str
    test_start: str
    test_end: str

    @model_validator(mode='after')
    def validate_split(self) -> 'WalkForwardSplit':
        if not (self.train_start < self.train_end):
            raise ValueError("train_start must be < train_end")
        if not (self.validation_start < self.validation_end):
            raise ValueError("validation_start must be < validation_end")
        if not (self.test_start < self.test_end):
            raise ValueError("test_start must be < test_end")
        if not (self.train_end < self.validation_start):
            raise ValueError("train period must not overlap validation period")
        if not (self.validation_end < self.test_start):
            raise ValueError("validation period must not overlap test period")
        return self

class AttributionGroup(BaseModel):
    signals: int = 0
    trades_opened: int = 0
    trades_closed: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float | None = None
    gross_pnl: float = 0.0
    net_pnl: float = 0.0
    expectancy: float | None = None
    profit_factor: float | None = None
    average_win: float | None = None
    average_loss: float | None = None
    max_drawdown: float | None = None
    total_cost: float = 0.0
    average_holding_period: float | None = None
    return_contribution: float | None = None
    status: str = "VALID"

class PerformanceAttribution(BaseModel):
    dataset_id: str = "UNKNOWN"
    overall: AttributionGroup
    by_score: Dict[str, AttributionGroup]
    by_confidence: Dict[str, AttributionGroup]
    by_quality: Dict[str, AttributionGroup]
    by_priority: Dict[str, AttributionGroup]
    by_market_regime: Dict[str, AttributionGroup]
    by_stock_regime: Dict[str, AttributionGroup]
    by_regime_alignment: Dict[str, AttributionGroup]
    by_flow: Dict[str, AttributionGroup]
    oos: Dict[str, Any] = {}
    robustness: Dict[str, Any] = {}
    warnings: List[str] = []

class RobustnessResult(BaseModel):
    baseline_return: float
    stress_return: float
    baseline_dd: float
    stress_dd: float
    baseline_win_rate: float | None
    stress_win_rate: float | None
    status: str

from enum import Enum

class SignalState(str, Enum):
    EARLY_WATCH = "EARLY_WATCH"
    WATCH = "WATCH"
    SETUP_FORMING = "SETUP_FORMING"
    TRIGGER_NEAR = "TRIGGER_NEAR"
    ENTRY_READY = "ENTRY_READY"
    ENTRY_CONFIRMED = "ENTRY_CONFIRMED"
    HOLD = "HOLD"
    EXIT_WARNING = "EXIT_WARNING"
    EXIT_NOW = "EXIT_NOW"
    INVALIDATED = "INVALIDATED"

class AlertPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AlertMessage(BaseModel):
    alert_id: str
    timestamp: str
    symbol: str
    alert_type: str  # FAST_ALERT, DEEP_ALERT, SYSTEM_ALERT
    priority: AlertPriority
    state: SignalState
    
    # Actionable details
    entry_zone: str = "N/A"
    trigger: str = "N/A"
    stop_loss: float = 0.0
    target_price: float = 0.0
    rr_ratio: float = 0.0
    
    # Intelligence context
    opportunity_score: float = 0.0
    evidence_quality: str = "UNKNOWN"
    bull_case: str = ""
    bear_case: str = ""
    catalysts: List[str] = []
    risks: List[str] = []
    reason: str = ""
    
    expires_at: str = ""

class EventType(str, Enum):
    CORPORATE = "CORPORATE"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    OWNERSHIP = "OWNERSHIP"
    GOVERNMENT_POLICY = "GOVERNMENT_POLICY"
    MACRO = "MACRO"
    COMMODITY = "COMMODITY"
    FX_MONETARY = "FX_MONETARY"
    GEOPOLITICS_GLOBAL = "GEOPOLITICS_GLOBAL"
    MARKET_STRUCTURE = "MARKET_STRUCTURE"
    NEWS_INFORMATION = "NEWS_INFORMATION"

class InformationState(str, Enum):
    DETECTED = "DETECTED"
    VALIDATING = "VALIDATING"
    CONFIRMED = "CONFIRMED"
    CONTRADICTED = "CONTRADICTED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"

class InformationDelta(str, Enum):
    NEW = "NEW"
    CHANGED = "CHANGED"
    REMOVED = "REMOVED"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"
    UNCHANGED = "UNCHANGED"
    UNKNOWN = "UNKNOWN"
