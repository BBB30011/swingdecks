from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class EvidenceReference(BaseModel):
    event_id: str
    source_id: str
    published_at: str
    description: str

class EconomicTransmission(BaseModel):
    event_impact: Optional[str]
    business_impact: Optional[str]
    financial_impact: Optional[str]
    price_expectation: Optional[Literal["POSITIVE", "NEGATIVE", "MIXED", "UNKNOWN"]]

class DifferentialAssessment(BaseModel):
    target_reaction: Optional[str]
    peer_reaction: Optional[str]
    market_reaction: Optional[str]
    differential_status: Literal[
        "MARKET_WIDE_CANDIDATE", 
        "SECTOR_WIDE_CANDIDATE", 
        "COMPANY_SPECIFIC_CANDIDATE", 
        "ASYMMETRIC_BENEFICIARY_CANDIDATE", 
        "ASYMMETRIC_DETRIMENT_CANDIDATE", 
        "NO_CLEAR_DIFFERENTIAL", 
        "UNKNOWN"
    ]

class RedTeamChallenge(BaseModel):
    supporting_evidence: List[EvidenceReference]
    contradicting_evidence: List[EvidenceReference]
    alternative_explanations: List[str]
    missing_information: List[str]
    invalidation_conditions: List[str]

class Agent2IntelligenceReport(BaseModel):
    analysis_id: str
    decision_timestamp: str
    pit_mode: Literal["PUBLIC_PIT", "SYSTEM_PIT"]
    
    entity: str
    
    evidence: List[EvidenceReference]
    
    information_state: Literal["FACT", "OBSERVATION", "INTERPRETATION", "HYPOTHESIS"]
    information_delta: Literal["NEW", "CHANGED", "REMOVED", "CONTRADICTED", "STALE", "UNCHANGED", "UNKNOWN"]
    
    relationships: List[str]
    exposures: List[str]
    
    economic_transmission: EconomicTransmission
    differential_assessment: DifferentialAssessment
    
    thesis: str
    
    red_team: RedTeamChallenge
    
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    research_status: Literal["OBSERVATION", "HYPOTHESIS", "TESTING", "SUPPORTED", "REJECTED", "UNKNOWN", "UNRESOLVED"]
