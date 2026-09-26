from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SpecificityStatus(str, Enum):
    MARKET_WIDE = "MARKET_WIDE"
    SECTOR_WIDE = "SECTOR_WIDE"
    FACTOR_WIDE = "FACTOR_WIDE"
    COMPANY_SPECIFIC_CANDIDATE = "COMPANY_SPECIFIC_CANDIDATE"
    UNKNOWN = "UNKNOWN"

class RedTeamStatus(str, Enum):
    PASS = "PASS"
    WEAK = "WEAK"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class CoverageState(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NO_EVIDENCE_IN_DATASET = "NO_EVIDENCE_IN_DATASET"
    UNKNOWN = "UNKNOWN"

class AttributionState(str, Enum):
    SUPPORTED = "SUPPORTED"
    CANDIDATE = "CANDIDATE"
    WEAK = "WEAK"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"
    NOT_AVAILABLE = "NOT_AVAILABLE"

class EvidenceCoverageSummary(BaseModel):
    news: CoverageState = CoverageState.NOT_AVAILABLE
    corporate_action: CoverageState = CoverageState.NOT_AVAILABLE
    fundamental: CoverageState = CoverageState.NOT_AVAILABLE
    macro: CoverageState = CoverageState.NOT_AVAILABLE
    commodity: CoverageState = CoverageState.NOT_AVAILABLE
    fx: CoverageState = CoverageState.NOT_AVAILABLE
    monetary: CoverageState = CoverageState.NOT_AVAILABLE
    policy: CoverageState = CoverageState.NOT_AVAILABLE
    politics: CoverageState = CoverageState.NOT_AVAILABLE
    geopolitics: CoverageState = CoverageState.NOT_AVAILABLE
    ownership: CoverageState = CoverageState.NOT_AVAILABLE
    relationship: CoverageState = CoverageState.NOT_AVAILABLE
    exposure: CoverageState = CoverageState.NOT_AVAILABLE
    flow: CoverageState = CoverageState.NOT_AVAILABLE
    sentiment: CoverageState = CoverageState.NOT_AVAILABLE
    market_structure: CoverageState = CoverageState.NOT_AVAILABLE
    event_calendar: CoverageState = CoverageState.NOT_AVAILABLE
    peer_information: CoverageState = CoverageState.NOT_AVAILABLE

class PeerReactionSummary(BaseModel):
    peer_group_type: str = "CONTEXTUAL_SECTOR"
    peers: List[str] = Field(default_factory=list)
    peer_count: int = 0
    target_day_return: float = 0.0
    peer_mean_return: float = 0.0
    peer_median_return: float = 0.0
    differential_return: float = 0.0
    specificity_status: SpecificityStatus = SpecificityStatus.UNKNOWN

class AttributionComponents(BaseModel):
    market_component: AttributionState = AttributionState.UNKNOWN
    sector_component: AttributionState = AttributionState.UNKNOWN
    factor_component: AttributionState = AttributionState.UNKNOWN
    macro_component: AttributionState = AttributionState.UNKNOWN
    commodity_component: AttributionState = AttributionState.UNKNOWN
    flow_component: AttributionState = AttributionState.UNKNOWN
    news_component: AttributionState = AttributionState.UNKNOWN
    ownership_component: AttributionState = AttributionState.UNKNOWN
    relationship_component: AttributionState = AttributionState.UNKNOWN
    company_specific_component: AttributionState = AttributionState.UNKNOWN
    unknown_component: AttributionState = AttributionState.SUPPORTED

class CausalityLevel(str, Enum):
    OBSERVED = "OBSERVED"
    CORRELATED = "CORRELATED"
    ECONOMICALLY_PLAUSIBLE = "ECONOMICALLY_PLAUSIBLE"
    HYPOTHESIZED = "HYPOTHESIZED"
    EXPERIMENTALLY_TESTED = "EXPERIMENTALLY_TESTED"
    VALIDATED = "VALIDATED"

class RedTeamCheckResult(BaseModel):
    time_leakage: str = "PASS"  # PASS / FAIL
    evidence_hallucination: str = "PASS"  # PASS / WEAK / FAIL
    logic_consistency: str = "PASS"  # PASS / FAIL
    alternative_explanation: str = "PASS"  # PASS / WEAK / CONTRADICTED / INSUFFICIENT_EVIDENCE
    overall_status: RedTeamStatus = RedTeamStatus.INSUFFICIENT_EVIDENCE
    reasons: List[str] = Field(default_factory=list)

class HistoricalCandidateAttribution(BaseModel):
    candidate_id: str
    symbol: str
    signal_timestamp: str
    official_signal_state: str
    quant_score: float
    signal_day_return: float
    pit_mode: str = "PUBLIC_PIT"  # PUBLIC_PIT or SYSTEM_PIT
    
    # Evidence & PIT Metrics
    evidence_count: int = 0
    pit_valid_evidence_count: int = 0
    future_evidence_excluded_count: int = 0
    contradictory_evidence_count: int = 0
    unresolved_evidence_count: int = 0
    
    # 18 Evidence Dimensions Coverage
    evidence_coverage: EvidenceCoverageSummary = Field(default_factory=EvidenceCoverageSummary)
    
    # Entity & Relationship Status
    entity_id: Optional[str] = None
    entity_status: CoverageState = CoverageState.UNKNOWN
    relationship_status: CoverageState = CoverageState.NOT_AVAILABLE
    exposure_status: CoverageState = CoverageState.NOT_AVAILABLE
    peer_status: CoverageState = CoverageState.NOT_AVAILABLE
    event_status: CoverageState = CoverageState.NOT_AVAILABLE
    
    # Peer Reaction & Specificity
    peer_reaction: PeerReactionSummary = Field(default_factory=PeerReactionSummary)
    specificity_status: SpecificityStatus = SpecificityStatus.UNKNOWN
    
    # Attribution Components
    attribution_components: AttributionComponents = Field(default_factory=AttributionComponents)
    primary_attribution: str = "UNKNOWN_COMPONENT"
    alternative_attributions: List[str] = Field(default_factory=list)
    
    # Causality Qualification
    causality_level: CausalityLevel = CausalityLevel.OBSERVED
    
    # Red Team / Adversarial Audit
    red_team_status: RedTeamStatus = RedTeamStatus.INSUFFICIENT_EVIDENCE
    red_team_audit: RedTeamCheckResult = Field(default_factory=RedTeamCheckResult)
    contradictions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    
    # Forward Outcome Reference (OUTCOME_AFTER_T - strictly separated from KNOWABLE_AT_T)
    forward_h1_return: Optional[float] = None
    forward_h5_return: Optional[float] = None
    forward_h20_return: Optional[float] = None
    
    # Provenance & Auditability
    dataset_version: str = "1.0"
    experiment_id: str = "BATCH_ZZZ_7_1_ATTRIBUTION_AUDIT"
    provenance: str = "agent2_deterministic_substrate"
