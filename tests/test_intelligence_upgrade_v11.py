"""
Tests for SwingDeck Intelligence Capability Upgrade V1.1+
Covers:
- Gate 1: Temporal Truth Hardening & Timezone Normalization (WIB, WITA, WIT, UTC, PIT Safety)
- Gate 2: Information Novelty Engine, Event Clustering, Syndication Non-Inflation & Information Delta
- Gate 3: Multi-Hop Exposure Propagation & Explainability
- Gate 4: Agent 1 <-> Agent 2 Reverse Investigation
- Gate 5: Why-Now Engine & Market Snapshot at Availability
- Gate 6: Dynamic Thesis Delta & Proactive Exit Intelligence
"""

import os
import tempfile
import pytest
from datetime import datetime, timezone

from core.source_authenticity import (
    SourceAuthenticityEvaluator, normalize_timestamp_to_utc,
    AuthenticityStatus, OriginClass, AccessClass
)
from core.data_platform_schemas import (
    TimestampDerivationMethod, TemporalConfidence, NoveltyClass, CorroborationType,
    ThesisState, InvestigationTriggerType, RawDocumentRecord, SourceRecord,
    EntityRecord, InformationItemRecord, ClaimRecord, EvidenceRecord,
    EntityRelationshipRecord, PolicyRecord, ExposureRecord, MechanismRecord,
    ContradictionDataRecord, EventClusterRecord, InformationDeltaRecord,
    MarketSnapshotAtAvailability, PropagatedExposureResult, TransmissionHop,
    InvestigationRequest, InvestigationReport, ThesisDelta, SourceType,
    InformationType, EvidenceRole
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, EvidenceClassification
)
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.natural_information_pipeline import NaturalInformationPipeline
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.exit_engine import ExitEngine
from core.position import PaperPosition
from agents.agent1_quant.pipeline import Agent1QuantPipeline
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
from agents.agent3_committee.committee import InvestmentCommittee


@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_intel_v11.duckdb")
    platform = KnowledgeDataPlatform(db_path)
    
    # Register core entities
    platform.insert_entity(EntityRecord(
        entity_id="ENT_ADRO",
        canonical_name="PT Adaro Energy Indonesia Tbk",
        entity_type=EntityType.COMPANY,
        jurisdiction="ID"
    ))
    platform.insert_entity_identifier("ENT_ADRO", "IDX_TICKER", "ADRO")
    
    platform.insert_entity(EntityRecord(
        entity_id="ENT_AADI",
        canonical_name="PT Adaro Andalan Indonesia Tbk",
        entity_type=EntityType.COMPANY,
        jurisdiction="ID"
    ))
    platform.insert_entity_identifier("ENT_AADI", "IDX_TICKER", "AADI")

    platform.insert_entity(EntityRecord(
        entity_id="ENT_BBCA",
        canonical_name="PT Bank Central Asia Tbk",
        entity_type=EntityType.COMPANY,
        jurisdiction="ID"
    ))
    platform.insert_entity_identifier("ENT_BBCA", "IDX_TICKER", "BBCA")

    platform.insert_entity(EntityRecord(
        entity_id="ENT_SECTOR_COAL",
        canonical_name="Coal Mining Sector",
        entity_type=EntityType.SECTOR,
        jurisdiction="ID"
    ))

    platform.insert_entity(EntityRecord(
        entity_id="ENT_GOV_ID",
        canonical_name="Government of Indonesia",
        entity_type=EntityType.REGULATOR,
        jurisdiction="ID"
    ))

    # Link ADRO to Coal Sector
    platform.insert_relationship(EntityRelationshipRecord(
        relationship_id="REL_ADRO_SECTOR_COAL",
        subject_entity_id="ENT_ADRO",
        relationship_type=RelationshipType.OPERATES_IN,
        object_entity_id="ENT_SECTOR_COAL",
        valid_from="2020-01-01T00:00:00Z",
        observed_at="2020-01-01T00:00:00Z"
    ))



    # Register Coal Sector exposure to EXPORT_RESTRICTION
    platform.insert_exposure(ExposureRecord(
        exposure_id="EXP_SECTOR_COAL_DMO",
        entity_id="ENT_SECTOR_COAL",
        economic_channel=EconomicChannel.EXPORT_RESTRICTION,
        exposure_type=ExposureType.INDIRECT_EXPOSURE,
        direction="NEGATIVE",
        magnitude_class="HIGH",
        valid_from="2020-01-01T00:00:00Z"
    ))

    # Rebuild derived indexes
    platform.rebuild_derived_indexes()

    yield db_path, platform
    platform.close()


# ==============================================================================
# GATE 1: TEMPORAL TRUTH HARDENING & TIMEZONE NORMALIZATION
# ==============================================================================
class TestGate1TemporalTruthHardening:
    def test_wib_timezone_normalization(self):
        # 2026-09-30 14:00:00 WIB -> 2026-09-30 07:00:00 UTC
        raw_ts = "2026-09-30 14:00:00 WIB"
        utc_ts, orig_ts, orig_tz, deriv, conf = normalize_timestamp_to_utc(raw_ts)
        assert orig_tz == "WIB"
        assert deriv == TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
        assert conf == TemporalConfidence.EXACT
        assert "2026-09-30T07:00:00" in utc_ts

    def test_wita_timezone_normalization(self):
        # 2026-09-30 15:00:00 WITA -> 2026-09-30 07:00:00 UTC
        raw_ts = "2026-09-30 15:00:00 WITA"
        utc_ts, orig_ts, orig_tz, deriv, conf = normalize_timestamp_to_utc(raw_ts)
        assert orig_tz == "WITA"
        assert "2026-09-30T07:00:00" in utc_ts

    def test_wit_timezone_normalization(self):
        # 2026-09-30 16:00:00 WIT -> 2026-09-30 07:00:00 UTC
        raw_ts = "2026-09-30 16:00:00 WIT"
        utc_ts, orig_ts, orig_tz, deriv, conf = normalize_timestamp_to_utc(raw_ts)
        assert orig_tz == "WIT"
        assert "2026-09-30T07:00:00" in utc_ts

    def test_missing_timestamp_fallback(self):
        utc_ts, orig_ts, orig_tz, deriv, conf = normalize_timestamp_to_utc(
            None, default_utc="2026-09-30T08:00:00Z"
        )
        assert orig_tz == "UNKNOWN"
        assert deriv == TimestampDerivationMethod.RETRIEVAL_CLOCK_FALLBACK
        assert conf == TemporalConfidence.FALLBACK
        assert utc_ts == "2026-09-30T08:00:00Z"

    def test_pit_safety_future_document_rejected(self):
        # A document publication time in the future relative to retrieval time must be rejected
        auth = SourceAuthenticityEvaluator.evaluate(
            url="https://www.idx.co.id/news/disclosure_future.html",
            content="<html><body>Future disclosure</body></html>",
            pub_time="2026-10-05T10:00:00Z",
            retrieval_time="2026-09-30T10:00:00Z"
        )
        assert auth.authenticity_status == AuthenticityStatus.REJECTED
        assert "Impossible timestamp" in auth.authenticity_reason


# ==============================================================================
# GATE 2: INFORMATION NOVELTY ENGINE, DELTA & EVENT CLUSTERING
# ==============================================================================
class TestGate2NoveltyAndClustering:
    def test_novelty_classification_and_delta(self, temp_db):
        db_path, platform = temp_db
        pipeline = NaturalInformationPipeline(db_path=db_path)

        # 1. Ingest initial announcement
        res1 = pipeline.ingest_natural_information(
            url="https://www.idx.co.id/news/adro_aadi_plan.html",
            content="PT Adaro Energy Indonesia Tbk (ADRO) mengumumkan rencana spinoff dan divestasi saham AADI.",
            title="ADRO Mengumumkan Rencana Divestasi Saham AADI",
            pub_time="2026-09-20T08:00:00Z"
        )
        assert res1.canonical_persisted is True
        assert res1.novelty_class == NoveltyClass.NEW_CATALYST
        assert res1.event_cluster is not None

        # 2. Ingest status update (RUPS Approval)
        res2 = pipeline.ingest_natural_information(
            url="https://www.idx.co.id/news/adro_aadi_approved.html",
            content="RUPS PT Adaro Energy Indonesia Tbk (ADRO) resmi menyetujui divestasi saham AADI secara tuntas.",
            title="RUPS ADRO Resmi Menyetujui Divestasi AADI",
            pub_time="2026-09-25T08:00:00Z"
        )
        assert res2.canonical_persisted is True
        assert res2.novelty_class == NoveltyClass.STATUS_UPDATE
        assert len(res2.information_deltas) > 0
        delta = res2.information_deltas[0]
        assert delta.previous_state == "ANNOUNCED"
        assert delta.new_state == "APPROVED"

        pipeline.close()

    def test_syndication_non_inflation(self, temp_db):
        db_path, platform = temp_db
        pipeline = NaturalInformationPipeline(db_path=db_path)

        # 1. Ingest primary article
        res1 = pipeline.ingest_natural_information(
            url="https://www.bisnis.com/market/read/20260920/adro_dividend.html",
            content="ADRO membagikan dividen interim jumbo tahun 2026.",
            title="ADRO Bagikan Dividen Interim 2026",
            pub_time="2026-09-20T08:00:00Z"
        )
        assert res1.canonical_persisted is True
        initial_cluster_id = res1.event_cluster.cluster_id

        # 2. Ingest syndicated copy from portal 2 marked with syndication url
        res2 = pipeline.ingest_natural_information(
            url="https://portal-agregator.com/berita/adro_dividend_copy.html",
            content="ADRO membagikan dividen interim jumbo tahun 2026.",
            title="ADRO Bagikan Dividen Interim 2026",
            pub_time="2026-09-20T08:30:00Z",
            syndication_original_url="https://www.bisnis.com/market/read/20260920/adro_dividend.html"
        )
        assert res2.novelty_class == NoveltyClass.SYNDICATION
        
        # Verify cluster independent count is NOT inflated
        cluster_row = platform.conn.execute("""
            SELECT independent_sources_count, syndicated_copies_count
            FROM event_clusters WHERE cluster_id = ?
        """, (initial_cluster_id,)).fetchone()
        assert cluster_row[0] == 1  # independent sources remains 1
        assert cluster_row[1] >= 1  # syndicated copies incremented

        pipeline.close()


# ==============================================================================
# GATE 3: MULTI-HOP EXPOSURE PROPAGATION & EXPLAINABILITY
# ==============================================================================
class TestGate3MultiHopExposurePropagation:
    def test_policy_to_company_propagation(self, temp_db):
        db_path, platform = temp_db

        # 1. Register a new Coal DMO Policy enacted by Government
        platform.insert_policy(PolicyRecord(
            policy_id="POL_DMO_COAL_2026",
            title="Penyesuaian Tarif Royalti dan DMO Batubara 2026",
            policy_type="REGULATION",
            issuing_institution_id="ENT_GOV_ID",
            economic_channel=EconomicChannel.EXPORT_RESTRICTION,
            effective_from="2026-09-01T00:00:00Z"
        ))

        # 2. Run propagation
        results = platform.propagate_macro_policy_exposure("POL_DMO_COAL_2026", as_of="2026-09-30T00:00:00Z")
        assert len(results) > 0

        adro_exposure = next((r for r in results if r.target_entity_id == "ENT_ADRO"), None)
        assert adro_exposure is not None
        assert adro_exposure.exposure_type == ExposureType.INDIRECT_EXPOSURE
        assert len(adro_exposure.transmission_path) == 3
        
        # Hop 1: Gov -> Channel
        assert adro_exposure.transmission_path[0].source_node == "ENT_GOV_ID"
        assert adro_exposure.transmission_path[0].relationship_type == "REGULATES"
        # Hop 2: Channel -> Sector
        assert adro_exposure.transmission_path[1].target_node == "ENT_SECTOR_COAL"
        # Hop 3: Sector -> Company ADRO
        assert adro_exposure.transmission_path[2].target_node == "ENT_ADRO"


# ==============================================================================
# GATE 4: AGENT 1 <-> AGENT 2 REVERSE INVESTIGATION
# ==============================================================================
class TestGate4ReverseInvestigation:
    def test_agent1_requests_investigation_and_agent2_resolves(self, temp_db):
        db_path, platform = temp_db
        retriever = KnowledgeRetrievalEngine(db_path)
        pipeline_nat = NaturalInformationPipeline(db_path=db_path)

        # Ingest catalyst 1 day prior
        pipeline_nat.ingest_natural_information(
            url="https://www.idx.co.id/news/bbca_expansion.html",
            content="PT Bank Central Asia Tbk (BBCA) mengumumkan pertumbuhan laba bersih 15% YoY.",
            title="Laba Bersih BBCA Tumbuh 15% YoY",
            pub_time="2026-09-29T10:00:00Z"
        )

        # Agent 1 identifies unusual volume / breakout and creates request
        agent1 = Agent1QuantPipeline()
        cand = {
            "symbol": "BBCA",
            "quant_score": 88,
            "features": {
                "volume": {"relative_volume": 3.2},
                "price_action": {"breakout_20d": True},
                "relative_strength": {"relative_return_20d": 0.08}
            }
        }
        inv_requests = agent1.build_investigation_requests([cand], as_of="2026-09-30T10:00:00Z")
        assert len(inv_requests) == 1
        req = inv_requests[0]
        assert req.symbol == "BBCA"
        assert req.trigger_type == InvestigationTriggerType.MOMENTUM_BREAKOUT

        # Agent 2 processes reverse investigation
        agent2 = Agent2IntelligencePipeline()
        report = agent2.investigate_candidate(req, retrieval_engine=retriever)
        assert report.investigation_status == "COMPLETED"
        assert report.has_matching_catalyst is True
        assert "Laba Bersih BBCA" in report.why_now_assessment

        retriever.close()
        pipeline_nat.close()


# ==============================================================================
# GATE 5: WHY-NOW ENGINE & MARKET SNAPSHOT AT AVAILABILITY
# ==============================================================================
class TestGate5MarketSnapshotAtAvailability:
    def test_market_snapshot_captured_at_availability(self, temp_db):
        db_path, platform = temp_db
        pipeline = NaturalInformationPipeline(db_path=db_path)

        res = pipeline.ingest_natural_information(
            url="https://www.idx.co.id/news/adro_dividend_report.html",
            content="PT Adaro Energy Indonesia Tbk (ADRO) dividen interim 2026 disetujui.",
            title="ADRO Dividen Interim Disetujui",
            pub_time="2026-09-28T09:00:00Z"
        )
        assert res.market_snapshot is not None
        assert res.market_snapshot.symbol == "ADRO"
        assert "2026-09-28T09:00:00" in res.market_snapshot.availability_timestamp
        assert res.market_snapshot.stock_price > 0

        # Retrieve from platform
        snap = platform.get_market_snapshot_at_availability(res.extracted_claims[0].information_id)
        assert snap is not None
        assert snap["symbol"] == "ADRO"

        pipeline.close()


# ==============================================================================
# GATE 6: DYNAMIC THESIS DELTA & EXIT INTELLIGENCE
# ==============================================================================
class TestGate6DynamicThesisDeltaAndExit:
    def test_thesis_invalidation_triggers_exit_in_engine_and_committee(self, temp_db):
        db_path, platform = temp_db
        retriever = KnowledgeRetrievalEngine(db_path)
        pipeline = NaturalInformationPipeline(db_path=db_path)

        # Position entered at 2026-09-20
        entry_time = "2026-09-20T00:00:00Z"
        position = PaperPosition(
            position_id="POS_ADRO_001",
            job_id="JOB_TEST",
            symbol="ADRO",
            entry_price=3500.0,
            stop_loss=3300.0,
            target_price=4200.0,
            current_price=3600.0,
            entry_time=entry_time,
            shares=10000,
            holding_bars=3,
            initial_risk=200.0,
            initial_reward=700.0,
            initial_rr=3.5
        )

        # 1. Before bad news -> Thesis is Neutral
        delta_pre = retriever.get_thesis_delta("ADRO", position.position_id, entry_time, as_of="2026-09-21T00:00:00Z")
        assert delta_pre.thesis_state == ThesisState.NEUTRAL

        # 2. Ingest catastrophic cancellation/lawsuit after entry at 2026-09-25
        pipeline.ingest_natural_information(
            url="https://www.idx.co.id/news/adro_divestment_cancelled.html",
            content="Divestasi AADI oleh PT Adaro Energy Indonesia Tbk (ADRO) resmi dibatalkan akibat tuntutan hukum.",
            title="Divestasi AADI Resmi Dibatalkan",
            pub_time="2026-09-25T08:00:00Z"
        )

        # 3. Post-entry retrieval yields ThesisState.INVALIDATED
        delta_post = retriever.get_thesis_delta("ADRO", position.position_id, entry_time, as_of="2026-09-26T00:00:00Z")
        assert delta_post.thesis_state == ThesisState.INVALIDATED
        assert delta_post.recommended_action == "EXIT"

        # 4. ExitEngine evaluates position with thesis_delta
        exit_eval = ExitEngine.evaluate(position, {"thesis_delta": delta_post})
        assert exit_eval["action"] == "EXIT"
        assert exit_eval["reason"] == "THESIS_INVALIDATED"

        # 5. InvestmentCommittee receives thesis_delta and downgrades action to AVOID/SELL
        committee = InvestmentCommittee()
        decision = committee.synthesize(
            job_id="JOB_TEST_THESIS",
            symbol="ADRO",
            as_of_timestamp="2026-09-26T00:00:00Z",
            quant_data={"quant_score": 85, "entry_price": 3500.0},
            research_data={"thesis_delta": delta_post, "evidence_state": "GOOD"},
            risk_evaluation={"action": "BUY", "risk_state": "GREEN", "risk_per_share": 100.0, "reward_per_share": 300.0, "risk_reward_ratio": 3.0, "position_size": 10000, "position_lots": 100, "position_value": 35000000.0, "portfolio_risk": 0.01}
        )
        assert decision.action in ["AVOID", "SELL"]
        assert any("THESIS_INVALIDATED" in b for b in decision.blockers)

        retriever.close()
        pipeline.close()

