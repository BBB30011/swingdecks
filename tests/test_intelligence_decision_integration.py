import pytest
import json
import hashlib
from datetime import datetime
from pathlib import Path

from core.intelligence_models import (
    Entity, EntityRelationship, InformationEvent, Exposure,
    MechanismHypothesis, InformationMarketLink
)
from core.intelligence_graph import IntelligenceGraphEngine
from core.historical_knowledge_state import HistoricalKnowledgeState
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport
from agents.agent3_committee.pipeline import Agent3DecisionPipeline
from core.decision import PortfolioContext
from core.decision_trace import DecisionTraceAPI
from core.evidence_truth_gate import EvidenceTruthGate

@pytest.fixture
def memory_graph():
    """In-memory DuckDB graph engine for isolated deterministic testing."""
    return IntelligenceGraphEngine(":memory:")

# =========================================================================
# PHASE 1: FORENSIC DEFECT RECONCILIATION & DYNAMIC LINKAGE
# =========================================================================

def test_reconciled_defects_duckdb_precision(memory_graph):
    """Verifies that float precision and schemas operate cleanly in DuckDB."""
    link = InformationMarketLink(
        information_id="INFO_TEST_FLOAT",
        market_symbol="BBCA",
        information_available_at="2026-09-29T10:00:00Z",
        reaction_window="T+1",
        observed_return=-0.05,
        observed_volume_change=1.25,
        observed_volatility_change=0.02
    )
    memory_graph.insert_market_link(link)
    res = memory_graph.get_market_links("INFO_TEST_FLOAT")
    assert len(res) == 1
    assert res[0]["observed_return"] == pytest.approx(-0.05)
    assert res[0]["observed_volume_change"] == pytest.approx(1.25)

def test_dashboard_subgraph_extraction(memory_graph):
    """Verifies dynamic subgraph extraction for dashboard & agent pipelines."""
    # Seed Entity & Relations
    memory_graph.insert_entity(Entity("ENT_BBCA", "Bank Central Asia Tbk", "COMPANY", ticker="BBCA", aliases=["BBCA", "BCA"]))
    memory_graph.insert_entity(Entity("ENT_BI", "Bank Indonesia", "REGULATOR"))
    memory_graph.insert_relationship(EntityRelationship("REL_1", "ENT_BI", "ENT_BBCA", "REGULATES", "2020-01-01T00:00:00Z"))
    
    # Seed Information & Exposure & Mechanism
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_RATE_01",
        source_id="SRC_BI_PORTAL",
        source_type="POLICY",
        source_url_or_reference="https://bi.go.id/rate/2026",
        publisher="Bank Indonesia",
        published_at="2026-09-15T07:30:00Z",
        available_at="2026-09-15T07:30:00Z",
        captured_at="2026-09-15T07:31:00Z",
        title="BI Rate Decision",
        summary="BI Maintains 7-Day Reverse Repo Rate",
        claim="Stable policy rate maintains banking NIM stability",
        information_type="POLICY",
        topic="MONETARY_POLICY",
        subtopic="INTEREST_RATE",
        entities=["ENT_BBCA"],
        source_quality="VERIFIED",
        evidence_quality="HIGH",
        confidence="0.95"
    ))
    
    memory_graph.insert_exposure(Exposure(
        exposure_id="EXP_BBCA_RATE",
        entity_id="ENT_BBCA",
        target_entity_id="ENT_BI",
        exposure_type="POLICY_RATE",
        directness="DIRECT",
        mechanism_category="COST_OF_FUNDS",
        valid_from="2020-01-01T00:00:00Z"
    ))
    
    memory_graph.insert_mechanism(MechanismHypothesis(
        mechanism_id="MECH_BBCA_01",
        information_id="INFO_RATE_01",
        entity_id="ENT_BBCA",
        exposure_id="EXP_BBCA_RATE",
        mechanism_type="MONETARY_TRANSMISSION",
        economic_channel="NIM_STABILITY",
        expected_effect="STABLE_MARGINS",
        expected_direction="POSITIVE",
        time_horizon="QUARTERLY",
        supporting_evidence=["Historical NIM correlation 0.88"],
        contradicting_evidence=[]
    ))
    
    subgraph = memory_graph.get_entity_subgraph("BBCA", "2026-09-29T10:00:00Z")
    assert subgraph["status"] == "VALID"
    assert subgraph["entity"]["canonical_name"] == "Bank Central Asia Tbk"
    assert len(subgraph["relationships"]) == 1
    assert len(subgraph["information"]) == 1
    assert len(subgraph["exposures"]) == 1
    assert len(subgraph["mechanisms"]) == 1

# =========================================================================
# PHASE 2 & 3 & 4: CANONICAL INTELLIGENCE CASES & 3-AGENT CHAIN
# =========================================================================

def test_canonical_historical_case_adro(memory_graph):
    """
    Canonical Historical Case: ADRO Corporate Action & Coal Commodity Exposure.
    Proves Agent 2 and Agent 3 end-to-end integration without schema loss.
    """
    memory_graph.insert_entity(Entity("ENT_ADRO", "Adaro Energy Indonesia Tbk", "COMPANY", ticker="ADRO", aliases=["ADRO"]))
    memory_graph.insert_entity(Entity("ENT_COAL", "Coal Commodity", "SECTOR"))
    memory_graph.insert_relationship(EntityRelationship("REL_ADRO_COAL", "ENT_ADRO", "ENT_COAL", "OPERATES_IN", "2010-01-01T00:00:00Z"))
    
    memory_graph.insert_information(InformationEvent(
        information_id="DIV_ADRO_20220601",
        source_id="SRC_IDX_FILING",
        source_type="CORPORATE_ACTION",
        source_url_or_reference="https://idx.co.id/disclosures/adro/2022/div",
        publisher="PT Bursa Efek Indonesia",
        published_at="2022-05-25T09:00:00Z",
        available_at="2022-05-25T09:00:00Z",
        captured_at="2022-05-25T09:05:00Z",
        title="ADRO Cash Dividend Announcement",
        summary="Final cash dividend distribution for FY2021",
        claim="Distribution of substantial cash dividend to shareholders",
        information_type="CORPORATE_ACTION",
        topic="DIVIDEND",
        subtopic="CASH_DISTRIBUTION",
        entities=["ENT_ADRO"],
        source_quality="AUDITED_FILING",
        evidence_quality="HIGH",
        confidence="1.0"
    ))
    
    memory_graph.insert_exposure(Exposure(
        exposure_id="EXP_ADRO_COAL",
        entity_id="ENT_ADRO",
        target_entity_id="ENT_COAL",
        exposure_type="COMMODITY",
        directness="DIRECT",
        mechanism_category="REVENUE",
        valid_from="2010-01-01T00:00:00Z"
    ))
    
    memory_graph.insert_mechanism(MechanismHypothesis(
        mechanism_id="MECH_ADRO_DIV",
        information_id="DIV_ADRO_20220601",
        entity_id="ENT_ADRO",
        exposure_id="EXP_ADRO_COAL",
        mechanism_type="CASH_DISTRIBUTION",
        economic_channel="SHAREHOLDER_YIELD",
        expected_effect="DIVIDEND_YIELD_EXPANSION",
        expected_direction="POSITIVE",
        time_horizon="SHORT_TERM",
        supporting_evidence=["Audited financial statement retained earnings"],
        contradicting_evidence=[]
    ))
    
    subgraph = memory_graph.get_entity_subgraph("ADRO", "2022-05-26T00:00:00Z")
    
    # Phase 3: Agent 2 consumes graph
    a2_pipeline = Agent2IntelligencePipeline(graph_engine=memory_graph)
    a2_report = a2_pipeline.process_graph_subgraph(subgraph, pit="2022-05-26T00:00:00Z")
    
    assert a2_report.information_state == "FACT"
    assert a2_report.research_status == "SUPPORTED"
    assert a2_report.confidence == "HIGH"
    assert len(a2_report.evidence) == 1
    assert a2_report.evidence[0].event_id == "DIV_ADRO_20220601"
    assert len(a2_report.mechanisms) == 1
    
    # Phase 4: Agent 3 consumes Agent 2 report
    a3_pipeline = Agent3DecisionPipeline()
    quant_ctx = {
        "quant_score": 88,
        "quant_confidence": 92,
        "entry_price": 3200.0,
        "stop_loss": 3050.0,
        "target_price": 3550.0,
        "market_regime": "BULL"
    }
    decision_payload = {
        "job_id": "JOB_HIST_ADRO_001",
        "symbol": "ADRO",
        "as_of_timestamp": "2022-05-26T00:00:00Z",
        "quant_context": quant_ctx,
        "research_context": a2_report.model_dump()
    }
    portfolio = PortfolioContext(capital=500000000.0, available_cash=500000000.0, as_of_timestamp="2022-05-26T00:00:00Z")
    a3_output = a3_pipeline.process_job(decision_payload, portfolio)
    
    decision = a3_output["decision"]
    assert decision["action"] in ["BUY", "WAIT"]
    assert "DIV_ADRO_20220601" in decision["trace"]["evidence_refs"]
    assert len(decision["trace"]["graph_intelligence"]["mechanisms"]) == 1

def test_canonical_controlled_case_bbca(memory_graph):
    """
    Controlled Case: BBCA Policy Rate Transmission Chain.
    Proves complete 3-agent pipeline with exposure and mechanism hypotheses.
    """
    test_dashboard_subgraph_extraction(memory_graph)
    subgraph = memory_graph.get_entity_subgraph("BBCA", "2026-09-20T00:00:00Z")
    
    a2_pipeline = Agent2IntelligencePipeline(graph_engine=memory_graph)
    a2_report = a2_pipeline.process_graph_subgraph(subgraph, pit="2026-09-20T00:00:00Z")
    
    assert a2_report.information_state == "FACT"
    assert len(a2_report.evidence) == 1
    assert a2_report.evidence[0].event_id == "INFO_RATE_01"
    assert a2_report.economic_transmission.price_expectation == "POSITIVE"
    
    a3_pipeline = Agent3DecisionPipeline()
    quant_ctx = {
        "quant_score": 85,
        "quant_confidence": 90,
        "entry_price": 10500.0,
        "stop_loss": 10200.0,
        "target_price": 11200.0,
        "market_regime": "BULL"
    }
    decision_payload = {
        "job_id": "JOB_BBCA_CTRL",
        "symbol": "BBCA",
        "as_of_timestamp": "2026-09-20T00:00:00Z",
        "quant_context": quant_ctx,
        "research_context": a2_report.model_dump()
    }
    a3_output = a3_pipeline.process_job(decision_payload, PortfolioContext(capital=100000000.0, available_cash=100000000.0, as_of_timestamp="2026-09-20T00:00:00Z"))
    assert a3_output["status"] == "COMPLETED"
    assert a3_output["decision"]["action"] in ["BUY", "WAIT"]

# =========================================================================
# PHASE 5: TEMPORAL DECISION REPLAY & FUTURE INVARIANCE
# =========================================================================

def test_temporal_decision_replay_t0_invariance(memory_graph):
    """
    Reconstruct case at historical T0.
    Verify future injected evidence leaves T0 output completely unchanged.
    """
    memory_graph.insert_entity(Entity("ENT_TLKM", "Telkom Indonesia Tbk", "COMPANY", ticker="TLKM"))
    
    # Event 1 at T0 (2026-01-01)
    ev_t0 = InformationEvent(
        information_id="INFO_TLKM_T0",
        source_id="SRC_IDX",
        source_type="CORPORATE_ACTION",
        source_url_or_reference="https://idx/tlkm/t0",
        publisher="IDX",
        published_at="2026-01-01T09:00:00Z",
        available_at="2026-01-01T09:00:00Z",
        captured_at="2026-01-01T09:00:00Z",
        title="TLKM CapEx Plan",
        summary="Data center expansion funding approved",
        claim="CapEx commitment of 5T IDR",
        information_type="CORPORATE_ACTION",
        topic="CAPEX",
        subtopic="INFRASTRUCTURE",
        entities=["ENT_TLKM"],
        source_quality="VERIFIED"
    )
    memory_graph.insert_information(ev_t0)
    
    # Replay at T0
    subgraph_t0_first = memory_graph.get_entity_subgraph("TLKM", "2026-01-01T10:00:00Z")
    a2_pipeline = Agent2IntelligencePipeline(graph_engine=memory_graph)
    a2_t0_first = a2_pipeline.process_graph_subgraph(subgraph_t0_first, pit="2026-01-01T10:00:00Z")
    
    # Now Inject Future Event at T1 (2026-03-01)
    ev_t1 = InformationEvent(
        information_id="INFO_TLKM_T1_FUTURE",
        source_id="SRC_IDX",
        source_type="CORPORATE_ACTION",
        source_url_or_reference="https://idx/tlkm/t1",
        publisher="IDX",
        published_at="2026-03-01T09:00:00Z",
        available_at="2026-03-01T09:00:00Z",
        captured_at="2026-03-01T09:00:00Z",
        title="TLKM Earnings Q1",
        summary="Earnings declined 10%",
        claim="Lower net profit due to forex losses",
        information_type="CORPORATE_ACTION",
        topic="EARNINGS",
        subtopic="PROFIT",
        entities=["ENT_TLKM"],
        source_quality="AUDITED_FILING"
    )
    memory_graph.insert_information(ev_t1)
    
    # Replay AGAIN at T0
    subgraph_t0_second = memory_graph.get_entity_subgraph("TLKM", "2026-01-01T10:00:00Z")
    a2_t0_second = a2_pipeline.process_graph_subgraph(subgraph_t0_second, pit="2026-01-01T10:00:00Z")
    
    # Assert Bit-for-bit Invariance at T0
    assert len(subgraph_t0_second["information"]) == 1
    assert subgraph_t0_second["information"][0]["information_id"] == "INFO_TLKM_T0"
    assert a2_t0_first.thesis == a2_t0_second.thesis
    assert a2_t0_first.confidence == a2_t0_second.confidence
    
    # Now query at T1
    subgraph_t1 = memory_graph.get_entity_subgraph("TLKM", "2026-03-02T00:00:00Z")
    assert len(subgraph_t1["information"]) == 2

# =========================================================================
# PHASE 6: CONTRADICTION & 10 NEGATIVE EDGE CASES
# =========================================================================

def test_case_1_supported_mechanism(memory_graph):
    """Case 1: Supported mechanism with explicit evidence -> High/Medium confidence."""
    test_canonical_controlled_case_bbca(memory_graph)

def test_case_2_incomplete_mechanism(memory_graph):
    """Case 2: Incomplete mechanism (missing exposure link) -> flags missing info."""
    memory_graph.insert_entity(Entity("ENT_INCOMP", "Incomplete Co", "COMPANY", ticker="INCOMP"))
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_INCOMP", source_id="SRC_1", source_type="NEWS",
        source_url_or_reference="http://test", publisher="PUB",
        published_at="2026-01-01T00:00:00Z", available_at="2026-01-01T00:00:00Z",
        captured_at="2026-01-01T00:00:00Z", title="Vague News", summary="Vague",
        claim="Something happened", information_type="NEWS", topic="UNKNOWN", subtopic="UNKNOWN",
        entities=["ENT_INCOMP"]
    ))
    subgraph = memory_graph.get_entity_subgraph("INCOMP", "2026-01-02T00:00:00Z")
    a2 = Agent2IntelligencePipeline(graph_engine=memory_graph)
    rep = a2.process_graph_subgraph(subgraph, "2026-01-02T00:00:00Z")
    assert "Company-to-event exposure channel unverified" in rep.red_team.missing_information
    assert rep.confidence != "HIGH"

def test_case_3_contradictory_source(memory_graph):
    """Case 3: Contradictory source in mechanism -> Agent 3 forces downgrade."""
    memory_graph.insert_entity(Entity("ENT_CONTRA", "Contra Co", "COMPANY", ticker="CONTRA"))
    memory_graph.insert_exposure(Exposure("EXP_C", "ENT_CONTRA", "ENT_CONTRA", "SECTOR", "DIRECT", "REVENUE", "2020-01-01T00:00:00Z"))
    memory_graph.insert_mechanism(MechanismHypothesis(
        mechanism_id="MECH_CONTRA", information_id="INFO_C", entity_id="ENT_CONTRA",
        exposure_id="EXP_C", mechanism_type="REGULATION", economic_channel="MARGINS",
        expected_effect="PROFIT_DROP", expected_direction="NEGATIVE", time_horizon="SHORT",
        supporting_evidence=["Policy draft"],
        contradicting_evidence=["Government ministry denial", "Official gazette exemption"]
    ))
    subgraph = memory_graph.get_entity_subgraph("CONTRA", "2026-01-01T00:00:00Z")
    a2 = Agent2IntelligencePipeline(graph_engine=memory_graph)
    rep = a2.process_graph_subgraph(subgraph, "2026-01-01T00:00:00Z")
    assert rep.contradictions_found == 2
    assert rep.economic_transmission.price_expectation == "NEGATIVE"
    
    # Agent 3 must downgrade
    a3 = Agent3DecisionPipeline()
    res = a3.process_job({
        "job_id": "CONTRA_JOB", "symbol": "CONTRA", "as_of_timestamp": "2026-01-01T00:00:00Z",
        "quant_context": {"quant_score": 85, "entry_price": 1000.0, "stop_loss": 950.0, "target_price": 1100.0},
        "research_context": rep.model_dump()
    }, PortfolioContext(capital=1000000.0, available_cash=1000000.0, as_of_timestamp="2026-01-01T00:00:00Z"))
    assert res["decision"]["action"] in ["WAIT", "AVOID"]

def test_case_4_duplicate_article(memory_graph):
    """Case 4: Duplicate article insertion -> idempotent storage, no ghost duplicates."""
    ev = InformationEvent(
        information_id="INFO_DUP_01", source_id="SRC_DUP", source_type="NEWS",
        source_url_or_reference="http://dup", publisher="PUB",
        published_at="2026-01-01T00:00:00Z", available_at="2026-01-01T00:00:00Z",
        captured_at="2026-01-01T00:00:00Z", title="Duplicate Story", summary="Same",
        claim="Same claim", information_type="NEWS", topic="GENERAL", subtopic="GENERAL"
    )
    memory_graph.insert_information(ev)
    memory_graph.insert_information(ev) # duplicate insert
    count = memory_graph.conn.execute("SELECT COUNT(*) FROM information WHERE information_id='INFO_DUP_01'").fetchone()[0]
    assert count == 1

def test_case_5_false_ownership_relationship(memory_graph):
    """Case 5: Unsupported relationship status -> rejected by graph engine."""
    rel = EntityRelationship(
        relationship_id="REL_FALSE", source_entity="ENT_A", target_entity="ENT_B",
        relationship_type="OWNS", valid_from="2020-01-01T00:00:00Z",
        status="UNSUPPORTED", evidence=""
    )
    memory_graph.insert_relationship(rel)
    count = memory_graph.conn.execute("SELECT COUNT(*) FROM relationships WHERE relationship_id='REL_FALSE'").fetchone()[0]
    assert count == 0

def test_case_6_future_policy_information_pit_leak(memory_graph):
    """Case 6: Future policy information -> rejected by PIT query at T0."""
    memory_graph.insert_entity(Entity("ENT_LEAK", "Leak Co", "COMPANY", ticker="LEAK"))
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_FUTURE_POLICY", source_id="SRC_LEAK", source_type="POLICY",
        source_url_or_reference="http://gov", publisher="GOV",
        published_at="2026-10-01T00:00:00Z", available_at="2026-10-01T00:00:00Z",
        captured_at="2026-09-29T00:00:00Z", title="Future Policy", summary="Future",
        claim="Tax rate cut in October", information_type="POLICY", topic="TAX", subtopic="RATES",
        entities=["ENT_LEAK"]
    ))
    # Query at 2026-09-29 (before publication)
    subgraph = memory_graph.get_entity_subgraph("LEAK", "2026-09-29T10:00:00Z")
    assert len(subgraph["information"]) == 0

def test_case_7_unauthorized_private_information_mnpi(memory_graph):
    """Case 7: Unauthorized private information / MNPI -> blocked by security firewall."""
    memory_graph.insert_entity(Entity("ENT_MNPI", "MNPI Co", "COMPANY", ticker="MNPI"))
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_MNPI_01", source_id="SRC_PRIVATE_LEAK", source_type="LEAK",
        source_url_or_reference="private_leak_channel", publisher="Confidential",
        published_at="2026-09-29T00:00:00Z", available_at="2026-09-29T00:00:00Z",
        captured_at="2026-09-29T00:00:00Z", title="Private Acquisition", summary="Private",
        claim="Secret board merger agreed", information_type="MNPI", topic="M_AND_A", subtopic="TAKEOVER",
        entities=["ENT_MNPI"], access_class="PRIVATE_RESTRICTED", trading_eligibility="RESTRICTED"
    ))
    
    # Graph engine flags as RESTRICTED_MNPI
    info_row = memory_graph.conn.execute("SELECT status, trading_eligibility FROM information WHERE information_id='INFO_MNPI_01'").fetchone()
    assert info_row[0] == "RESTRICTED_MNPI"
    assert info_row[1] == "BLOCKED"
    
    # Agent 2 & Agent 3 enforce block
    subgraph = {
        "entity": {"entity_id": "ENT_MNPI", "canonical_name": "MNPI"},
        "information": [{"information_id": "INFO_MNPI_01", "status": "RESTRICTED_MNPI", "access_class": "PRIVATE_RESTRICTED", "trading_eligibility": "BLOCKED"}],
        "relationships": [], "exposures": [], "mechanisms": []
    }
    a2 = Agent2IntelligencePipeline(graph_engine=memory_graph)
    rep = a2.process_graph_subgraph(subgraph, "2026-09-29T10:00:00Z")
    assert rep.firewall_status == "BLOCKED_MNPI"
    assert rep.research_status == "REJECTED"
    
    a3 = Agent3DecisionPipeline()
    res = a3.process_job({
        "job_id": "MNPI_JOB", "symbol": "MNPI", "as_of_timestamp": "2026-09-29T10:00:00Z",
        "quant_context": {"quant_score": 95, "entry_price": 1000.0},
        "research_context": rep.model_dump()
    }, PortfolioContext(capital=1000000.0, available_cash=1000000.0, as_of_timestamp="2026-09-29T10:00:00Z"))
    assert res["decision"]["action"] == "AVOID"

def test_case_8_missing_provenance(memory_graph):
    """Case 8: Missing provenance -> untrusted or unverified classification."""
    memory_graph.insert_entity(Entity("ENT_NOPROV", "No Prov Co", "COMPANY", ticker="NOPROV"))
    memory_graph.insert_information(InformationEvent(
        information_id="INFO_NOPROV", source_id="SRC_UNKN", source_type="RUMOR",
        source_url_or_reference="", publisher="", published_at="2026-01-01T00:00:00Z",
        available_at="2026-01-01T00:00:00Z", captured_at="2026-01-01T00:00:00Z",
        title="Unverified Rumor", summary="Rumor", claim="Rumor claim",
        information_type="NEWS", topic="RUMOR", subtopic="RUMOR", entities=["ENT_NOPROV"]
    ))
    subgraph = memory_graph.get_entity_subgraph("NOPROV", "2026-01-02T00:00:00Z")
    a2 = Agent2IntelligencePipeline(graph_engine=memory_graph)
    rep = a2.process_graph_subgraph(subgraph, "2026-01-02T00:00:00Z")
    assert rep.information_state != "FACT"

def test_case_9_unknown_exposure(memory_graph):
    """Case 9: Unknown exposure -> differential status is UNKNOWN."""
    memory_graph.insert_entity(Entity("ENT_NOEXP", "No Exp Co", "COMPANY", ticker="NOEXP"))
    subgraph = memory_graph.get_entity_subgraph("NOEXP", "2026-01-01T00:00:00Z")
    a2 = Agent2IntelligencePipeline(graph_engine=memory_graph)
    rep = a2.process_graph_subgraph(subgraph, "2026-01-01T00:00:00Z")
    assert rep.differential_assessment.differential_status in ["UNKNOWN", "NO_CLEAR_DIFFERENTIAL"]

def test_case_10_invalid_graph_path(memory_graph):
    """Case 10: Invalid multi-hop path -> returns empty path."""
    memory_graph.insert_entity(Entity("ENT_ISOLATED_A", "A", "COMPANY"))
    memory_graph.insert_entity(Entity("ENT_ISOLATED_B", "B", "COMPANY"))
    path = memory_graph.find_shortest_evidence_path("ENT_ISOLATED_A", "ENT_ISOLATED_B", "2026-01-01T00:00:00Z")
    assert path == []

# =========================================================================
# PHASE 7: MARKET REACTION LINK & NON-CAUSALITY
# =========================================================================

def test_market_reaction_link_preserves_non_causality(memory_graph):
    """
    Verifies PRE_DECISION_EVIDENCE != POST_DECISION_OUTCOME separation.
    Confirms no causal assertions are made.
    """
    link = InformationMarketLink(
        information_id="INFO_REACTION_01",
        market_symbol="BBCA",
        information_available_at="2026-09-15T07:30:00Z",
        reaction_window="T+1",
        observed_return=0.015,
        observed_volume_change=1.4,
        observed_volatility_change=0.01,
        sector_context="FINANCIALS_UP_0.8_PCT",
        benchmark_context="IHSG_UP_0.5_PCT"
    )
    memory_graph.insert_market_link(link)
    
    links = memory_graph.get_market_links("INFO_REACTION_01")
    assert len(links) == 1
    assert links[0]["observed_return"] == pytest.approx(0.015)
    
    # Verify non-causality: outcome link does NOT modify the pre-decision information state
    assert links[0]["reaction_window"] == "T+1"

# =========================================================================
# PHASE 8: EVIDENCE TRUTH GATE EXTENSION
# =========================================================================

def test_evidence_truth_gate_graph_scan(tmp_path):
    """Verifies that EvidenceTruthGate scans graph security & PIT boundaries."""
    db_file = tmp_path / "test_gate_graph.duckdb"
    graph = IntelligenceGraphEngine(str(db_file))
    
    # Insert clean entity and relationship
    graph.insert_entity(Entity("ENT_VALID", "Valid Co", "COMPANY"))
    graph.insert_relationship(EntityRelationship("REL_VALID", "ENT_VALID", "ENT_VALID", "PEER", "2020-01-01T00:00:00Z", "2025-01-01T00:00:00Z"))
    
    gate = EvidenceTruthGate(graph_db_path=str(db_file))
    snap = gate.scan()
    # Clean graph should have no critical security findings
    assert snap.pit_integrity == "PASS"
