"""
SwingDeck Knowledge Data Platform - Unified Schema & Data Contracts V1
Provides complete typed models for all 9 platform layers:
RAW, CORE, MARKET, INFORMATION, RELATIONSHIPS, POLICY, INTELLIGENCE, DECISION, AUDIT, DERIVED
"""

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field, field_validator

from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, AccessClass, EvidenceClassification
)

class SourceType(str, Enum):
    REGULATOR = "REGULATOR"
    EXCHANGE = "EXCHANGE"
    GOVERNMENT = "GOVERNMENT"
    MINISTRY = "MINISTRY"
    CENTRAL_BANK = "CENTRAL_BANK"
    COMPANY = "COMPANY"
    CORPORATE_FILING = "CORPORATE_FILING"
    NEWS = "NEWS"
    RESEARCH = "RESEARCH"
    BROKER = "BROKER"
    MARKET_DATA = "MARKET_DATA"
    SOCIAL = "SOCIAL"
    OTHER = "OTHER"

class InformationType(str, Enum):
    NEWS = "NEWS"
    DISCLOSURE = "DISCLOSURE"
    CORPORATE_ACTION = "CORPORATE_ACTION"
    POLICY = "POLICY"
    LAW = "LAW"
    REGULATION = "REGULATION"
    EARNINGS = "EARNINGS"
    MACRO_EVENT = "MACRO_EVENT"
    POLITICAL_EVENT = "POLITICAL_EVENT"
    OWNERSHIP_EVENT = "OWNERSHIP_EVENT"
    MANAGEMENT_EVENT = "MANAGEMENT_EVENT"
    COMMODITY_EVENT = "COMMODITY_EVENT"
    MARKET_EVENT = "MARKET_EVENT"
    SOCIAL_EVENT = "SOCIAL_EVENT"
    OTHER = "OTHER"

class CorporateActionType(str, Enum):
    IPO = "IPO"
    SPINOFF = "SPINOFF"
    RIGHTS_ISSUE = "RIGHTS_ISSUE"
    DIVIDEND = "DIVIDEND"
    BONUS = "BONUS"
    STOCK_SPLIT = "STOCK_SPLIT"
    MERGER = "MERGER"
    ACQUISITION = "ACQUISITION"
    DISPOSAL = "DISPOSAL"
    BUYBACK = "BUYBACK"
    DELISTING = "DELISTING"
    LISTING = "LISTING"
    PUPS = "PUPS"
    OTHER = "OTHER"

class EvidenceRole(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    CORROBORATING = "CORROBORATING"
    CONTRADICTING = "CONTRADICTING"

class SourceLineageType(str, Enum):
    INDEPENDENT_SOURCE = "INDEPENDENT_SOURCE"
    DERIVED_COPY = "DERIVED_COPY"
    SYNDICATED = "SYNDICATED"
    UNKNOWN = "UNKNOWN"

class RetrievalPathMode(str, Enum):
    FAST_PATH = "FAST_PATH"
    DEEP_PATH = "DEEP_PATH"

class TimestampDerivationMethod(str, Enum):
    EXCHANGE_METADATA = "EXCHANGE_METADATA"
    ISSUER_METADATA = "ISSUER_METADATA"
    SOURCE_ARTICLE_METADATA = "SOURCE_ARTICLE_METADATA"
    HTTP_HEADER = "HTTP_HEADER"
    RSS_METADATA = "RSS_METADATA"
    ARTICLE_BODY_PARSE = "ARTICLE_BODY_PARSE"
    STRUCTURED_FEED = "STRUCTURED_FEED"
    RETRIEVAL_CLOCK_FALLBACK = "RETRIEVAL_CLOCK_FALLBACK"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"

class TemporalConfidence(str, Enum):
    EXACT = "EXACT"
    DERIVED = "DERIVED"
    ESTIMATED = "ESTIMATED"
    FALLBACK = "FALLBACK"
    UNKNOWN = "UNKNOWN"

class NoveltyClass(str, Enum):
    NEW_CATALYST = "NEW_CATALYST"
    STATUS_UPDATE = "STATUS_UPDATE"
    MATERIAL_CHANGE = "MATERIAL_CHANGE"
    NEW_IMPLICATION = "NEW_IMPLICATION"
    CONFIRMATION = "CONFIRMATION"
    REPETITION = "REPETITION"
    SYNDICATION = "SYNDICATION"
    REVISION = "REVISION"
    CONTRADICTION = "CONTRADICTION"
    UNKNOWN = "UNKNOWN"

class CorroborationType(str, Enum):
    INDEPENDENT_CORROBORATION = "INDEPENDENT_CORROBORATION"
    SYNDICATED_REPETITION = "SYNDICATED_REPETITION"
    DERIVED_REPORT = "DERIVED_REPORT"
    REVISION = "REVISION"
    CONTRADICTION = "CONTRADICTION"
    UNCONFIRMED = "UNCONFIRMED"

class ThesisState(str, Enum):
    SUPPORTING = "SUPPORTING"
    NEUTRAL = "NEUTRAL"
    WEAKENING = "WEAKENING"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"

class InvestigationTriggerType(str, Enum):
    UNUSUAL_VOLUME = "UNUSUAL_VOLUME"
    MOMENTUM_BREAKOUT = "MOMENTUM_BREAKOUT"
    ABNORMAL_RETURN = "ABNORMAL_RETURN"
    RELATIVE_STRENGTH = "RELATIVE_STRENGTH"
    SECTOR_ANOMALY = "SECTOR_ANOMALY"

def compute_content_hash(content: str) -> str:
    """Computes deterministic SHA-256 hash of text content."""
    if not content:
        return ""
    return hashlib.sha256(content.strip().encode('utf-8')).hexdigest()

def compute_document_fingerprint(source_id: str, source_doc_id: str, content_hash: str, pub_time: str) -> str:
    """Computes canonical document fingerprint."""
    raw = f"{source_id}|{source_doc_id}|{content_hash}|{pub_time}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

# --- RAW LAYER ---
class RawDocumentRecord(BaseModel):
    raw_document_id: str
    source_id: str
    source_document_id: str
    retrieved_at: str
    published_at: str
    available_at: str
    event_time: Optional[str] = None
    content_hash: str
    content_type: str = "text/plain"
    mime_type: str = "text/plain"
    language: str = "id"
    raw_location: str = ""
    raw_size: int = 0
    access_class: AccessClass = AccessClass.PUBLIC
    ingestion_run_id: str = "DEFAULT"
    origin_class: EvidenceClassification = EvidenceClassification.NATURAL
    timestamp_source: str = "SOURCE_METADATA"
    derivation_method: TimestampDerivationMethod = TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
    timezone: str = "UTC"
    original_timezone: str = "UTC"
    original_timestamp: Optional[str] = None
    temporal_confidence: TemporalConfidence = TemporalConfidence.EXACT
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- SOURCE REGISTRY ---
class SourceRecord(BaseModel):
    source_id: str
    source_name: str
    publisher: str
    source_type: SourceType = SourceType.NEWS
    jurisdiction: str = "ID"
    domain: str = ""
    canonical_url: str = ""
    authority_class: str = "STANDARD"
    source_status: str = "ACTIVE"
    access_class: AccessClass = AccessClass.PUBLIC
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- CORE LAYER ---
class EntityRecord(BaseModel):
    entity_id: str
    canonical_name: str
    entity_type: EntityType = EntityType.COMPANY
    jurisdiction: str = "ID"
    status: str = "ACTIVE"
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EntityAliasRecord(BaseModel):
    alias_id: str
    entity_id: str
    alias: str
    alias_type: str = "COMMON_NAME"
    language: str = "id"
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None
    source_id: str = "SYSTEM"

class EntityIdentifierRecord(BaseModel):
    identifier_id: str
    entity_id: str
    identifier_type: str  # IDX_TICKER, ISIN, LEI, COMPANY_REGISTRATION
    identifier_value: str
    issuer: str = "IDX"
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None

# --- INFORMATION LAYER ---
# --- INFORMATION LAYER ---
class InformationItemRecord(BaseModel):
    information_id: str
    document_id: str
    information_type: InformationType = InformationType.NEWS
    novelty_class: NoveltyClass = NoveltyClass.NEW_CATALYST
    title: str
    summary: str = ""
    language: str = "id"
    event_time: Optional[str] = None
    published_at: str
    available_at: str
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    access_class: AccessClass = AccessClass.PUBLIC
    origin_class: EvidenceClassification = EvidenceClassification.NATURAL
    timestamp_source: str = "SOURCE_METADATA"
    derivation_method: TimestampDerivationMethod = TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
    timezone: str = "UTC"
    original_timezone: str = "UTC"
    original_timestamp: Optional[str] = None
    temporal_confidence: TemporalConfidence = TemporalConfidence.EXACT
    cluster_id: Optional[str] = None
    semantic_status: str = "VALID"
    temporal_status: str = "VALID"
    provenance_status: str = "VERIFIED"
    content_hash: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ClaimRecord(BaseModel):
    claim_id: str
    information_id: str
    subject_entity_id: str
    predicate: str
    object_entity_id: Optional[str] = None
    claim_type: str = "FACTUAL"
    claim_text: str
    temporal_scope: str = "ACTIVE"
    novelty_class: NoveltyClass = NoveltyClass.NEW_CATALYST
    evidence_status: str = "SUPPORTED"
    semantic_status: str = "VALID"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EvidenceRecord(BaseModel):
    evidence_id: str
    information_id: str
    source_id: str
    document_id: str
    claim_id: Optional[str] = None
    evidence_type: str = "DOCUMENT_EXCERPT"
    excerpt_reference: str = ""
    content_hash: str
    event_time: Optional[str] = None
    published_at: str
    available_at: str
    observed_at: str
    timestamp_source: str = "SOURCE_METADATA"
    derivation_method: TimestampDerivationMethod = TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
    temporal_confidence: TemporalConfidence = TemporalConfidence.EXACT
    access_class: AccessClass = AccessClass.PUBLIC
    origin_class: EvidenceClassification = EvidenceClassification.NATURAL
    provenance_status: str = "VERIFIED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- EVENT CLUSTER & INFORMATION DELTA LAYER (GATE 2) ---
class EventClusterRecord(BaseModel):
    cluster_id: str
    canonical_event_name: str
    primary_entity_id: str
    event_type: str
    first_observed_at: str
    latest_update_at: str
    independent_sources_count: int = 1
    syndicated_copies_count: int = 0
    corroboration_status: CorroborationType = CorroborationType.UNCONFIRMED
    primary_information_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class InformationDeltaRecord(BaseModel):
    delta_id: str
    entity_id: str
    information_id: str
    cluster_id: Optional[str] = None
    attribute_name: str
    previous_state: str
    new_state: str
    novelty_class: NoveltyClass = NoveltyClass.STATUS_UPDATE
    change_time: str
    available_at: str
    supporting_evidence_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- RELATIONSHIPS LAYER ---
class EntityRelationshipRecord(BaseModel):
    relationship_id: str
    subject_entity_id: str
    relationship_type: RelationshipType
    object_entity_id: str
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None
    observed_at: str
    status: str = "ACTIVE"
    source_priority: int = 1
    confidence: float = 1.0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class RelationshipEvidenceRecord(BaseModel):
    relationship_evidence_id: str
    relationship_id: str
    evidence_id: str
    evidence_role: EvidenceRole = EvidenceRole.PRIMARY
    support_status: str = "SUPPORTED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- MARKET & CORPORATE ACTION LAYER ---
class CorporateActionRecord(BaseModel):
    corporate_action_id: str
    entity_id: str
    action_type: CorporateActionType = CorporateActionType.OTHER
    announcement_date: str
    effective_date: str
    record_date: Optional[str] = None
    source_id: str
    information_id: Optional[str] = None
    status: str = "ANNOUNCED"

class MarketReactionRecord(BaseModel):
    reaction_id: str
    information_id: str
    security_id: str
    reaction_start: str
    reaction_end: str
    horizon: str = "1D"
    return_pct: float = 0.0
    relative_return: float = 0.0
    volume_change: float = 0.0
    volatility_change: float = 0.0
    regime: str = "NORMAL"
    observation_status: str = "OBSERVED"

# --- MARKET SNAPSHOT AT INFORMATION AVAILABILITY (GATE 5) ---
class MarketSnapshotAtAvailability(BaseModel):
    snapshot_id: str
    information_id: str
    symbol: str
    availability_timestamp: str
    stock_price: float
    stock_volume: float
    ihsg_price: float = 0.0
    sector_name: str = "UNKNOWN"
    sector_performance_1d: float = 0.0
    relative_strength_vs_ihsg: float = 0.0
    market_regime: str = "UNKNOWN"
    liquidity_status: str = "LIQUID"
    as_of_market_time: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- POLICY & ECONOMIC CHANNEL LAYER ---
class PolicyRecord(BaseModel):
    policy_id: str
    political_event_id: Optional[str] = None
    title: str
    policy_type: str = "REGULATION"
    issuing_institution_id: str
    economic_channel: EconomicChannel
    effective_from: str
    effective_to: Optional[str] = None
    status: str = "ACTIVE"

# --- MULTI-HOP EXPOSURE PROPAGATION LAYER (GATE 3) ---
class TransmissionHop(BaseModel):
    source_node: str
    relationship_type: str
    target_node: str
    economic_channel: Optional[str] = None
    hop_distance: int = 1
    evidence_id: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float = 1.0

class ExposurePath(BaseModel):
    path_id: str
    origin_entity: str
    target_entity: str
    hop_count: int
    economic_channel: EconomicChannel
    relationship_sequence: List[str] = Field(default_factory=list)
    evidence_sequence: List[str] = Field(default_factory=list)
    source_sequence: List[str] = Field(default_factory=list)
    available_at_constraints: List[str] = Field(default_factory=list)
    confidence_by_hop: List[float] = Field(default_factory=list)
    cumulative_confidence: float = 1.0
    overall_path_status: str = "VALID"
    temporal_validity_from: str = "1970-01-01T00:00:00Z"
    temporal_validity_to: Optional[str] = None
    economic_mechanism_description: str = ""

class PropagatedExposureResult(BaseModel):
    propagation_id: str
    origin_entity_id: str
    policy_or_event_id: str
    target_entity_id: str
    economic_channel: EconomicChannel
    exposure_type: ExposureType
    transmission_path: List[TransmissionHop] = Field(default_factory=list)
    direction: str = "POSITIVE"
    magnitude_class: str = "MEDIUM"
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    explanation: Optional[ExposurePath] = None


# --- INTELLIGENCE LAYER ---
class ExposureRecord(BaseModel):
    exposure_id: str
    entity_id: str
    information_id: Optional[str] = None
    economic_channel: EconomicChannel
    exposure_type: ExposureType = ExposureType.DIRECT_EXPOSURE
    direction: str = "POSITIVE"
    magnitude_class: str = "MEDIUM"
    valid_from: str = "1970-01-01T00:00:00Z"
    valid_to: Optional[str] = None
    evidence_status: str = "SUPPORTED"

class MechanismRecord(BaseModel):
    mechanism_id: str
    exposure_id: str
    mechanism_type: str
    economic_channel: EconomicChannel
    description: str
    expected_direction: str = "POSITIVE"
    evidence_status: str = "SUPPORTED"
    temporal_status: str = "ACTIVE"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContradictionDataRecord(BaseModel):
    contradiction_id: str
    subject_id: str
    contradiction_type: ContradictionType = ContradictionType.FACTUAL_CONTRADICTION
    evidence_a_id: str
    evidence_b_id: str
    severity: str = "MEDIUM"
    temporal_scope: str = "ACTIVE"
    resolution_status: str = "UNRESOLVED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# --- REVERSE INVESTIGATION LAYER (GATE 4: AGENT 1 <-> AGENT 2) ---
class InvestigationRequest(BaseModel):
    request_id: str
    symbol: str
    entity_id: str
    trigger_type: InvestigationTriggerType
    as_of_timestamp: str
    lookback_hours: int = 48
    trigger_context: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class InvestigationReport(BaseModel):
    request_id: str
    symbol: str
    entity_id: str
    has_matching_catalyst: bool = False
    novelty_summary: str = "NONE"
    information_deltas: List[InformationDeltaRecord] = Field(default_factory=list)
    recent_information: List[Dict[str, Any]] = Field(default_factory=list)
    active_mechanisms: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions_found: List[Dict[str, Any]] = Field(default_factory=list)
    why_now_assessment: str = "NONE"
    investigation_status: str = "COMPLETED"
    as_of: str = ""

# --- THESIS DELTA & EXIT INTELLIGENCE LAYER (GATE 6) ---
class ThesisDelta(BaseModel):
    delta_id: str
    symbol: str
    position_id: str
    as_of_timestamp: str
    thesis_state: ThesisState = ThesisState.NEUTRAL
    reason: str
    new_evidence_ids: List[str] = Field(default_factory=list)
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_action: str = "HOLD"

# --- RETRIEVAL RESULT CONTRACT ---
class RetrievalResultContract(BaseModel):
    query_id: str
    as_of: str
    data: Any
    source_refs: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    entity_refs: List[str] = Field(default_factory=list)
    relationship_refs: List[str] = Field(default_factory=list)
    temporal_status: str = "VALID"
    temporal_confidence: TemporalConfidence = TemporalConfidence.EXACT
    provenance_status: str = "VERIFIED"
    access_status: str = "AUTHORIZED"
    origin_class: str = "NATURAL"
    semantic_status: str = "VALID"
    path_mode: RetrievalPathMode = RetrievalPathMode.FAST_PATH
    novelty_summary: Optional[str] = None
    propagation_paths: List[PropagatedExposureResult] = Field(default_factory=list)
    investigation_report: Optional[InvestigationReport] = None
    thesis_delta: Optional[ThesisDelta] = None
    execution_time_ms: float = 0.0
