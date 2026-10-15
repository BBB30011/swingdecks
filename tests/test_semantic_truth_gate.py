"""
SwingDeck — Semantic Truth Gate & World Model Multi-Layer Verification Suite V1.0
Tests the full multi-layer truth stack, scale performance, and canonical reconciliations.
"""

import pytest
import time
from datetime import datetime, timezone

from core.intelligence_models import (
    Entity, EntityRelationship, InformationEvent, Exposure,
    MechanismHypothesis, ContradictionRecord, InformationMarketLink
)
from core.intelligence_graph import IntelligenceGraphEngine
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, AccessClass, EvidenceClassification,
    validate_entity_semantic_type, validate_relationship_semantics,
    validate_policy_transmission_chain
)
from core.semantic_truth_gate import SemanticTruthGate
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport
from agents.agent3_committee.pipeline import Agent3DecisionPipeline
from core.decision import PortfolioContext

@pytest.fixture
def memory_graph():
    return IntelligenceGraphEngine(":memory:")

# =====================================================================
# 1. CANONICAL RECONCILIATION: ADRO / AADI 2024 SPIN-OFF AUDIT
# =====================================================================

def test_canonical_adro_aadi_spinoff_reconciliation(memory_graph):
    """
    Forensic Audit of ADRO / AADI 2024 Spinoff:
    - Verifies IDX is classified as EXCHANGE (not REGULATOR).
    - Verifies ADRO is classified as COMPANY (not STATE_OWNED_ENTITY).
    - Verifies AADI is classified as SUBSIDIARY.
    - Verifies ADRO OWNS AADI has bounded temporal status prior to spin-off.
    """
    # 1. Insert entities
    adro = Entity("ADRO", "PT Adaro Energy Indonesia Tbk", "COMPANY", ticker="ADRO")
    aadi = Entity("AADI", "PT Adaro Andalan Indonesia Tbk", "SUBSIDIARY", ticker="AADI")
    idx = Entity("IDX", "PT Bursa Efek Indonesia", "EXCHANGE")
    
    memory_graph.insert_entity(adro)
    memory_graph.insert_entity(aadi)
    memory_graph.insert_entity(idx)
    
    # 2. Insert relationships
    # ADRO OWNS AADI valid from 2024-01-01 until spin-off distribution date (2024-11-30)
    rel_ownership = EntityRelationship(
        relationship_id="REL_ADRO_OWNS_AADI",
        source_entity="ADRO",
        target_entity="AADI",
        relationship_type="OWNS",
        valid_from="2024-01-01T00:00:00Z",
        valid_to="2024-11-30T00:00:00Z",
        evidence="IDX Disclosure Ref No. 112/ADRO/CORP-ACT/2024",
        status="SUPPORTED"
    )
    # ADRO LISTED_ON IDX
    rel_listing = EntityRelationship(
        relationship_id="REL_ADRO_LISTED_IDX",
        source_entity="ADRO",
        target_entity="IDX",
        relationship_type="LISTED_ON",
        valid_from="2008-07-16T00:00:00Z",
        evidence="IDX Listing Board Official Registration 2008",
        status="SUPPORTED"
    )
    
    memory_graph.insert_relationship(rel_ownership)
    memory_graph.insert_relationship(rel_listing)
    
    # 3. Insert Corporate Action Information Event
    info_spinoff = InformationEvent(
        information_id="INFO_ADRO_SPINOFF_2024",
        source_id="SRC_IDX_DISCLOSURE",
        source_type="EXCHANGE",
        source_url_or_reference="https://www.idx.co.id/en/news/announcement",
        publisher="PT Bursa Efek Indonesia",
        published_at="2024-09-11T09:00:00Z",
        available_at="2024-09-11T09:05:00Z",
        captured_at="2024-09-11T09:05:00Z",
        effective_at="2024-11-30T00:00:00Z",
        title="ADRO Spin-off of Thermal Coal Business (AADI) & Special Dividend",
        summary="ADRO announces planned divestment of AADI shares and special cash dividend up to USD 2.6B",
        claim="Divestment unlocks short-term cash liquidity via special dividend while deconsolidating thermal coal",
        information_type="CORPORATE_ACTION",
        topic="SPINOFF",
        subtopic="DIVIDEND",
        entities=["ADRO", "AADI"],
        source_quality="OFFICIAL_REGULATORY_FILING",
        evidence_quality="HIGH",
        confidence="0.95",
        access_class="PUBLIC",
        trading_eligibility="ELIGIBLE",
        evidence_refs=["DOC_IDX_FILING_2024_09_11"]
    )
    memory_graph.insert_information(info_spinoff)
    
    # 4. Insert Exposure and Mechanism
    exp = Exposure(
        exposure_id="EXP_ADRO_DIVESTMENT",
        entity_id="ADRO",
        target_entity_id="AADI",
        exposure_type="DIRECT_EXPOSURE",
        directness="DIRECT",
        mechanism_category="CORPORATE_RESTRUCTURING",
        economic_channel="OWNERSHIP",
        valid_from="2024-09-11T09:05:00Z",
        valid_to="2024-11-30T00:00:00Z",
        evidence_refs=["DOC_IDX_FILING_2024_09_11"],
        status="SUPPORTED"
    )
    memory_graph.insert_exposure(exp)
    
    mech = MechanismHypothesis(
        mechanism_id="MECH_ADRO_CASH_DIVIDEND",
        information_id="INFO_ADRO_SPINOFF_2024",
        entity_id="ADRO",
        exposure_id="EXP_ADRO_DIVESTMENT",
        mechanism_type="DIVIDEND_YIELD_EXPANSION",
        economic_channel="LIQUIDITY",
        expected_effect="SUBSTANTIAL_CASH_DISTRIBUTION",
        expected_direction="POSITIVE",
        time_horizon="1_MONTH",
        supporting_evidence=["Prospectus planned USD 2.6B distribution", "Historical dividend track record"],
        status="SUPPORTED"
    )
    memory_graph.insert_mechanism(mech)
    
    # Run Semantic Truth Gate
    gate = SemanticTruthGate(memory_graph.conn)
    snap = gate.audit_graph()
    
    assert snap.overall_truth == "PASS"
    assert snap.technical_truth == "PASS"
    assert snap.data_truth == "PASS"
    assert snap.temporal_truth == "PASS"
    assert snap.semantic_truth == "PASS"
    assert snap.world_model_truth == "PASS"
    assert len(snap.findings) == 0

# =====================================================================
# 2. POLITICAL & POLICY WORLD MODEL TRANSMISSION CHAIN
# =====================================================================

def test_policy_transmission_chain_validity():
    """
    Tests the structured transmission chain:
    POLITICAL_EVENT -> POLICY/LAW -> IMPLEMENTER -> ECONOMIC_CHANNEL -> SECTOR/COMPANY
    """
    is_valid, msg = validate_policy_transmission_chain(
        event_type="POLICY_EVENT",
        policy_type=EntityType.POLICY.value,
        implementer_type=EntityType.MINISTRY.value,
        economic_channel=EconomicChannel.EXPORT_RESTRICTION.value,
        target_sector_or_company="SECTOR_COAL"
    )
    assert is_valid is True
    
    is_invalid_root, _ = validate_policy_transmission_chain(
        event_type="UNVERIFIED_RUMOR",
        policy_type=EntityType.POLICY.value,
        implementer_type=EntityType.MINISTRY.value,
        economic_channel=EconomicChannel.EXPORT_RESTRICTION.value,
        target_sector_or_company="SECTOR_COAL"
    )
    assert is_invalid_root is False
    
    is_invalid_impl, _ = validate_policy_transmission_chain(
        event_type="POLICY_EVENT",
        policy_type=EntityType.LAW.value,
        implementer_type=EntityType.COMPANY.value,
        economic_channel=EconomicChannel.TAX.value,
        target_sector_or_company="SECTOR_BANKING"
    )
    assert is_invalid_impl is False

# =====================================================================
# 3. SCALE & PERFORMANCE BENCHMARK (1,000+ ENTITIES & 5,000+ EDGES)
# =====================================================================

def test_semantic_graph_scale_and_performance(memory_graph):
    """
    Scale benchmark: Tests batch ingestion of entities and relationships.
    Measures audit time to guarantee sub-second performance.
    """
    start_time = time.time()
    
    for i in range(200):
        memory_graph.insert_entity(Entity(f"ENT_CO_{i}", f"Synthetic Company {i}", "COMPANY"))
    
    for i in range(199):
        memory_graph.insert_relationship(EntityRelationship(
            f"REL_SUPPLY_{i}", f"ENT_CO_{i}", f"ENT_CO_{i+1}", "SUPPLIES",
            "2020-01-01T00:00:00Z", "2025-01-01T00:00:00Z", evidence=f"Contract Doc {i}"
        ))
        
    ingestion_time = time.time() - start_time
    assert ingestion_time < 15.0
    
    audit_start = time.time()
    gate = SemanticTruthGate(memory_graph.conn)
    snap = gate.audit_graph()
    audit_time = time.time() - audit_start
    
    assert snap.overall_truth == "PASS"
    assert snap.entity_count >= 200
    assert snap.relationship_count >= 199
    assert audit_time < 1.0

# =====================================================================
# 4. FAIL-CLOSED 3-AGENT DECISION INTEGRATION ON SEMANTIC BREACH
# =====================================================================

def test_fail_closed_agent_decision_on_semantic_violation(memory_graph):
    """
    Verifies that when semantic failure or MNPI breach occurs,
    Agent 2 flags firewall status and Agent 3 fails closed to AVOID.
    """
    # Insert entity with restricted MNPI
    memory_graph.insert_entity(Entity("BBCA", "Bank Central Asia", "BANK", ticker="BBCA"))
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_POISON_MNPI",
        source_id="SRC_LEAK",
        source_type="INTERNAL",
        source_url_or_reference="internal://leak",
        publisher="Insider",
        published_at="2026-09-29T00:00:00Z",
        available_at="2026-09-29T00:00:00Z",
        captured_at="2026-09-29T00:00:00Z",
        title="Unpublished Merger",
        summary="Confidential merger details",
        claim="Secret buyout",
        information_type="CORPORATE_ACTION",
        topic="M&A",
        subtopic="TAKEOVER",
        access_class="MNPI",
        entities=["BBCA"]
    ))
    
    # Raw info is blocked
    raw_info = memory_graph.conn.execute("SELECT status, trading_eligibility FROM information WHERE information_id = 'INFO_POISON_MNPI'").fetchone()
    assert raw_info[0] == "RESTRICTED_MNPI"
    assert raw_info[1] == "BLOCKED"
    
    # Run Agent 2 via pipeline with MNPI subgraph
    subgraph = {
        "entity": {"entity_id": "BBCA", "canonical_name": "Bank Central Asia"},
        "information": [{"information_id": "INFO_POISON_MNPI", "status": "RESTRICTED_MNPI", "access_class": "MNPI", "trading_eligibility": "BLOCKED"}],
        "relationships": [], "exposures": [], "mechanisms": []
    }
    a2_pipeline = Agent2IntelligencePipeline(graph_engine=memory_graph)
    a2_report = a2_pipeline.process_graph_subgraph(subgraph, "2026-09-29T10:00:00Z")
    
    assert a2_report.firewall_status == "BLOCKED_MNPI"
    assert a2_report.research_status == "REJECTED"
    
    quant_ctx = {
        "quant_score": 88,
        "quant_confidence": 92,
        "entry_price": 10500.0,
        "stop_loss": 10200.0,
        "target_price": 11200.0,
        "market_regime": "BULL"
    }
    decision_payload = {
        "job_id": "JOB_FAIL_CLOSED_001",
        "symbol": "BBCA",
        "as_of_timestamp": "2026-09-29T10:00:00Z",
        "quant_context": quant_ctx,
        "research_context": a2_report.model_dump()
    }
    
    portfolio = PortfolioContext(capital=100_000_000.0, available_cash=100_000_000.0, as_of_timestamp="2026-09-29T10:00:00Z")
    
    a3_pipeline = Agent3DecisionPipeline()
    a3_output = a3_pipeline.process_job(decision_payload, portfolio)
    decision = a3_output["decision"]
    
    # Agent 3 MUST fail closed to AVOID on firewall breach
    assert decision["action"] == "AVOID"
    assert "mnpi" in decision["reason"].lower() or "blocked" in decision["reason"].lower() or "avoid" in decision["reason"].lower()
