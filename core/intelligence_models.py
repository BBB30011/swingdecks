import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

@dataclass
class Entity:
    entity_id: str
    canonical_name: str
    entity_type: str
    jurisdiction: str = "ID"
    aliases: List[str] = field(default_factory=list)
    former_names: List[str] = field(default_factory=list)
    ticker: Optional[str] = None
    status: str = "ACTIVE"
    source_refs: List[str] = field(default_factory=list)
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    semantic_status: str = "VALIDATED"
    evidence_classification: str = "CONTROLLED"

@dataclass
class EntityRelationship:
    relationship_id: str
    source_entity: str
    target_entity: str
    relationship_type: str
    valid_from: str
    valid_to: Optional[str] = None
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_refs: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"
    status: str = "SUPPORTED"
    pit_status: str = "AVAILABLE"
    evidence: str = ""
    semantic_status: str = "VALIDATED"
    temporal_status: str = "BOUNDED"
    access_class: str = "PUBLIC"
    evidence_classification: str = "CONTROLLED"

@dataclass
class InformationEvent:
    information_id: str
    source_id: str
    source_type: str
    source_url_or_reference: str
    publisher: str
    published_at: str
    available_at: str
    captured_at: str
    
    title: str
    summary: str
    claim: str
    
    information_type: str
    topic: str
    subtopic: str
    
    entities: List[str] = field(default_factory=list)
    sectors: List[str] = field(default_factory=list)
    geographies: List[str] = field(default_factory=list)
    
    source_quality: str = "UNVERIFIED"
    evidence_quality: str = "UNKNOWN"
    confidence: str = "UNKNOWN"
    
    access_class: str = "PUBLIC"
    trading_eligibility: str = "ELIGIBLE"
    
    pit_status: str = "AVAILABLE"
    status: str = "NEW"
    semantic_status: str = "VALIDATED"
    evidence_classification: str = "CONTROLLED"
    
    event_cluster_id: Optional[str] = None
    effective_at: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)

@dataclass
class Exposure:
    exposure_id: str
    entity_id: str
    target_entity_id: str
    exposure_type: str
    directness: str
    mechanism_category: str
    valid_from: str
    economic_channel: str = "UNKNOWN"
    valid_to: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"
    pit_status: str = "AVAILABLE"
    status: str = "SUPPORTED"
    semantic_status: str = "VALIDATED"
    evidence_classification: str = "CONTROLLED"

@dataclass
class MechanismHypothesis:
    mechanism_id: str
    information_id: str
    entity_id: str
    exposure_id: str
    mechanism_type: str
    economic_channel: str
    expected_effect: str
    expected_direction: str
    time_horizon: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    invalidation_condition: str = "UNKNOWN"
    confidence: str = "UNKNOWN"
    pit_status: str = "AVAILABLE"
    status: str = "SUPPORTED"
    semantic_status: str = "VALIDATED"
    evidence_classification: str = "CONTROLLED"

@dataclass
class ContradictionRecord:
    contradiction_id: str
    contradiction_type: str
    source_a_id: str
    source_b_id: str
    claim_a: str
    claim_b: str
    entity_id: Optional[str] = None
    severity: str = "HIGH"
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolution_status: str = "OPEN"
    evidence_classification: str = "CONTROLLED"

@dataclass
class InformationMarketLink:
    information_id: str
    market_symbol: str
    information_available_at: str
    reaction_window: str
    observed_return: Optional[float] = None
    observed_volume_change: Optional[float] = None
    observed_volatility_change: Optional[float] = None
    sector_context: str = "UNKNOWN"
    benchmark_context: str = "UNKNOWN"
    pit_status: str = "AVAILABLE"
    evidence_classification: str = "CONTROLLED"
    non_causality_disclaimer: str = "PRE_DECISION_EVIDENCE != POST_DECISION_OUTCOME. Observational correlation does not prove causation."
