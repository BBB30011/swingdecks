from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from enum import Enum

class FactorState(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN"

class FactorImpact(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ContradictionSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class EvidenceContradiction(BaseModel):
    topic: str
    description: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM

class EvidenceFactor(BaseModel):
    factor_name: str
    state: FactorState = FactorState.UNKNOWN
    impact: FactorImpact = FactorImpact.LOW
    freshness: str = "UNKNOWN"
    reason: str = ""

class EvidenceMatrix(BaseModel):
    factors: Dict[str, EvidenceFactor] = Field(default_factory=dict)
    convergence_summary: str = "UNKNOWN"
    contradictions: List[EvidenceContradiction] = []

class InvestmentThesis(BaseModel):
    bull_thesis: str = "UNKNOWN"
    bear_thesis: str = "UNKNOWN"
    thesis_deteriorating: bool = False
    key_catalysts: List[str] = []
    key_risks: List[str] = []
    macro_factors: List[str] = []
    policy_factors: List[str] = []
    global_factors: List[str] = []
    unknowns: List[str] = []
    contradictions: List[EvidenceContradiction] = []
    invalidating_conditions: List[str] = []

class DecisionTrace(BaseModel):
    passed_gates: List[str] = []
    failed_gates: List[str] = []
    warnings: List[str] = []
    blockers: List[str] = []
    risk_checks: Dict[str, Any] = {}
    evidence_checks: Dict[str, Any] = {}
    sizing_checks: Dict[str, Any] = {}
    final_override: Optional[str] = None

class TriggerInfo(BaseModel):
    trigger_type: str = "UNKNOWN" # e.g., BREAKOUT, PULLBACK_BOUNCE
    trigger_price: Optional[float] = None
    trigger_condition: str = "UNKNOWN"
    timestamp: str = "UNKNOWN"

    @property
    def is_valid(self) -> bool:
        return self.trigger_price is not None and self.trigger_price > 0

class OpportunityAssessment(BaseModel):
    symbol: str
    setup_state: str = "UNKNOWN"
    opportunity_score: float = 0.0
    technical_state: str = "UNKNOWN"
    flow_state: str = "UNKNOWN"
    sector_state: str = "UNKNOWN"
    market_state: str = "UNKNOWN"
    catalyst_state: str = "UNKNOWN"
    fundamental_state: str = "UNKNOWN"
    risk_state: str = "UNKNOWN"
    evidence_quality: str = "UNKNOWN"
    contradiction_level: str = "UNKNOWN"
    entry_readiness: str = "UNKNOWN"
    opportunity_class: str = "UNCLASSIFIED"
    why_now: str = "NONE"
    signal_tier: str = "UNKNOWN"
    # Batch AR additions
    timing_quality: str = "UNKNOWN"        # EARLY/FORMING/READY/LATE/EXTENDED/INVALID/UNKNOWN
    trigger_proximity: str = "UNKNOWN"     # TOO_FAR/NEAR_TRIGGER/AT_TRIGGER/TRIGGERED/INVALID/UNKNOWN
    entry_window_status: str = "UNKNOWN"   # EARLY/OPEN/NARROW/MISSED/CLOSED/UNKNOWN
    priced_in_status: str = "UNKNOWN"      # NOT_PRICED_IN/PARTIALLY_PRICED/LIKELY_PRICED_IN/OVEREXTENDED/UNKNOWN
    alert_urgency: str = "MEDIUM"          # LOW/MEDIUM/HIGH/VERY_HIGH/CRITICAL
    signal_strength: str = "UNKNOWN"       # LOW/MEDIUM/HIGH/VERY_HIGH
    invalidation_conditions: List[str] = []
    distance_to_trigger_pct: Optional[float] = None

class DecisionResult(BaseModel):
    job_id: str
    symbol: str
    as_of_timestamp: str
    
    action: str  # BUY, WAIT, HOLD, SELL, AVOID
    risk_state: str  # GREEN, YELLOW, RED
    confidence: float
    opportunity_score: float = 0.0
    
    thesis: InvestmentThesis
    evidence_matrix: EvidenceMatrix = Field(default_factory=EvidenceMatrix)
    reason: str
    blockers: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    
    current_price: float = 0.0
    entry_price: float = 0.0
    trigger_price: float = 0.0 # Legacy fallback
    trigger: Optional[TriggerInfo] = None
    stop_loss: float = 0.0
    target_price: float = 0.0
    
    risk_per_share: float = 0.0
    reward_per_share: float = 0.0
    risk_reward_ratio: float = 0.0
    
    position_size: int = 0  # number of shares
    position_lots: int = 0
    position_value: float = 0.0
    
    portfolio_risk: float = 0.0
    
    evidence_state: str = "UNKNOWN"
    red_team_status: str = "UNKNOWN"
    
    decision_timestamp: str
    decision_source: str = "AGENT3"
    
    trace: DecisionTrace = Field(default_factory=DecisionTrace)
    opportunity_assessment: Optional[OpportunityAssessment] = None

    @model_validator(mode='after')
    def validate_finite_numerics(self) -> 'DecisionResult':
        import math
        numeric_fields = [
            'confidence', 'opportunity_score', 'entry_price', 'stop_loss', 'target_price', 
            'risk_per_share', 'reward_per_share', 'risk_reward_ratio', 
            'position_size', 'position_lots', 'position_value', 'portfolio_risk'
        ]
        for field in numeric_fields:
            val = getattr(self, field)
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"{field} must be finite")
                
        if self.action == "BUY" and self.stop_loss <= 0.0:
            raise ValueError("stop_loss must be > 0.0 for BUY action")
            
        return self

class PortfolioContext(BaseModel):
    capital: float
    available_cash: float
    current_positions: List[str] = []
    total_exposure: float = 0.0
    total_risk: float = 0.0
    number_of_positions: int = 0
    as_of_timestamp: str
