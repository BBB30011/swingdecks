from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional, Any
from enum import Enum

class ResearchEvidence(BaseModel):
    evidence_id: str
    symbol: str
    category: str  # FUNDAMENTAL, CORPORATE_EVENT, MACRO, POLICY, SECTOR, NEWS, SENTIMENT, CATALYST, RISK
    claim: str
    claim_class: str  # FACT, INFERENCE, SPECULATION, UNKNOWN
    source: str = "UNKNOWN"
    source_title: str = "UNKNOWN"
    published_at: str = "UNKNOWN"
    retrieved_at: str = "UNKNOWN"
    relevance: str = "UNKNOWN"  # HIGH, MEDIUM, LOW, UNKNOWN
    credibility: str = "UNKNOWN"  # HIGH, MEDIUM, LOW, UNKNOWN
    as_of_timestamp: str

    @model_validator(mode='after')
    def validate_claim(self) -> 'ResearchEvidence':
        if self.claim_class == "FACT" and self.source == "UNKNOWN":
            raise ValueError("FACT evidence must have a verifiable source.")
        if self.claim_class == "INFERENCE" and not getattr(self, 'supporting_evidence_provided', True):
            # Base validation: inference should conceptually have support (mocked as true for schema if not explicit)
            pass
        if self.claim_class == "UNKNOWN":
            # Just allowed but flagged downstream
            pass
        return self

class MacroEvidence(ResearchEvidence):
    indicator: str
    value: float
    unit: str
    timestamp: str
    direction: str  # POSITIVE, NEGATIVE, NEUTRAL, MIXED, UNKNOWN
    interpretation: str
    affected_sectors: List[str] = []
    affected_symbols: List[str] = []

class FundamentalEvidence(ResearchEvidence):
    metric: str
    value: float | None = None
    unit: str = ""
    period: str = "UNKNOWN"
    comparison: str = ""
    direction: str = "UNKNOWN"

class CorporateEvent(ResearchEvidence):
    event_type: str  # EARNINGS, DIVIDEND, RIGHTS_ISSUE, etc.
    event_date: str
    announcement_date: str
    description: str
    materiality: str = "UNKNOWN" # HIGH, MEDIUM, LOW, UNKNOWN
    status: str = "UNKNOWN"

class SentimentEvidence(ResearchEvidence):
    timestamp: str
    sentiment: str  # POSITIVE, NEGATIVE, NEUTRAL, MIXED, UNKNOWN
    confidence: float
    sample_size: int = 0

class CatalystEvidence(ResearchEvidence):
    event_type: str  # EARNINGS, M&A, DIVIDEND, COMMODITY, POLICY, MACRO, GLOBAL, TECHNICAL
    materiality: str = "UNKNOWN" # LOW, MEDIUM, HIGH, CRITICAL
    direction: str = "UNKNOWN" # POSITIVE, NEGATIVE, NEUTRAL, UNKNOWN
    decay_state: str = "UNKNOWN" # ACTIVE, EXPIRED, UNKNOWN
    affected_sectors: List[str] = []
    affected_symbols: List[str] = []

class NewsEvidence(ResearchEvidence):
    headline: str
    direction: str = "UNKNOWN"
    materiality: str = "UNKNOWN"
    affected_sectors: List[str] = []
    affected_symbols: List[str] = []

class ResearchPacket(BaseModel):
    job_id: str
    symbol: str
    as_of_timestamp: str
    
    quant_context: Dict[str, Any]
    
    fundamental: List[FundamentalEvidence] = []
    corporate_events: List[CorporateEvent] = []
    macro: List[MacroEvidence] = []
    policy: List[ResearchEvidence] = []
    sector: List[ResearchEvidence] = []
    news: List[NewsEvidence] = []
    sentiment: List[SentimentEvidence] = []
    catalysts: List[CatalystEvidence] = []
    risks: List[ResearchEvidence] = []
    
    contradictions: List[Dict[str, Any]] = []
    unknowns: List[Dict[str, Any]] = []
    
    def filter_by_timestamp(self, as_of: str):
        """
        Point-in-Time filtering: reject anything published after as_of.
        """
        def _filter(ev_list):
            return [ev for ev in ev_list if ev.published_at <= as_of or ev.published_at == "UNKNOWN"]
            
        self.fundamental = _filter(self.fundamental)
        self.corporate_events = _filter(self.corporate_events)
        self.macro = _filter(self.macro)
        self.policy = _filter(self.policy)
        self.sector = _filter(self.sector)
        self.news = _filter(self.news)
        self.sentiment = _filter(self.sentiment)
        self.catalysts = _filter(self.catalysts)
        self.risks = _filter(self.risks)

class ResearchCompletenessEngine:
    @staticmethod
    def evaluate(packet: ResearchPacket) -> str:
        # A simple check: how many categories have at least some non-UNKNOWN evidence
        categories = [
            packet.fundamental, packet.corporate_events, packet.macro,
            packet.policy, packet.sector, packet.news, packet.sentiment
        ]
        available = sum(1 for c in categories if len(c) > 0)
        expected = len(categories)
        
        ratio = available / expected if expected > 0 else 0
        
        if ratio == 1.0: return "COMPLETE"
        if ratio >= 0.7: return "GOOD"
        if ratio >= 0.4: return "PARTIAL"
        if ratio > 0.0: return "WEAK"
        return "INSUFFICIENT"
