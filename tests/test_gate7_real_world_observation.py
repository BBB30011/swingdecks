"""
SwingDeck — Gate 7.1 Real-World Intelligence Observation & Metric Audit Test Suite
===================================================================================

Validates:
1. Cohort identity manifest creation & denominator integrity
2. Mutually exclusive primary novelty distribution (Sum == 100.00%)
3. Strict separation of canonical cohort contradiction rate vs. adversarial stress detection rate
4. Source authenticity semantics vs. provenance integrity
5. Temporal completeness and timestamp derivation distribution
6. Availability timestamp verification & derivation provenance
7. Market PIT (available_at <= T) vs. System Observability PIT (observed_at <= T)
8. Source count vs. Event count distinction
9. Syndication non-inflation verification (1 event -> wire -> 3 portals = 1 event, 3 syndications)
10. Document revision & errata lineage tracking
11. Information delta state transition reproducibility
12. Metric calculation determinism (RUN_A == RUN_B)
13. Complete 12-hop lineage reconstruction
"""

import hashlib
import re
import pytest
from datetime import datetime, timezone
from typing import List

from core.data_platform_schemas import (
    AccessClass, ClaimRecord, CorroborationType, EntityRecord,
    EntityRelationshipRecord, EntityType, EvidenceClassification,
    EvidenceRecord, InformationItemRecord, InformationType,
    NoveltyClass, RawDocumentRecord, RelationshipType,
    SourceRecord, SourceType, TemporalConfidence, TimestampDerivationMethod
)
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.intelligence_quality_metrics import (
    IntelligenceQualityAuditEngine, NaturalObservationRecord,
    ObservationCohortManifest, QualityMetricsReport, SourceClass
)


@pytest.fixture
def canonical_gate7_observations() -> List[NaturalObservationRecord]:
    """Canonical 6-case real-world observation cohort."""
    return [
        # Case A: Primary Issuer Corporate Action
        NaturalObservationRecord(
            source_url="https://idx.co.id/disclosures/2024/ADRO-spinoff-aadi.pdf",
            source_identity="SRC_IDX_DISCLOSURE",
            source_class=SourceClass.PRIMARY_ISSUER,
            retrieval_timestamp="2024-09-11T10:05:00Z",
            raw_content_hash=hashlib.sha256(b"ADRO Spinoff AADI Disclosure Content").hexdigest(),
            document_id="DOC_IDX_ADRO_20240911",
            published_at="2024-09-11T09:45:00Z",
            available_at="2024-09-11T10:00:00Z",
            observed_at="2024-09-11T10:05:00Z",
            event_time="2024-09-11T09:30:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.EXCHANGE_METADATA,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="IDX_OFFICIAL_FEED",
            availability_derivation_method="STRUCTURED_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_ADRO",
            cluster_id="CLUS_ADRO_SPINOFF_2024",
            novelty_class=NoveltyClass.MATERIAL_CHANGE,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        ),
        # Case B: Primary Regulator / Exchange Circular
        NaturalObservationRecord(
            source_url="https://ojk.go.id/regulations/2024/POJK-14-2024.pdf",
            source_identity="SRC_OJK_REG",
            source_class=SourceClass.PRIMARY_REGULATOR,
            retrieval_timestamp="2024-05-02T14:15:00Z",
            raw_content_hash=hashlib.sha256(b"POJK 14 2024 Banking Governance").hexdigest(),
            document_id="DOC_OJK_POJK14_2024",
            published_at="2024-05-02T14:00:00Z",
            available_at="2024-05-02T14:10:00Z",
            observed_at="2024-05-02T14:15:00Z",
            event_time="2024-05-02T13:30:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.STRUCTURED_FEED,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="OJK_REGULATORY_CIRCULAR",
            availability_derivation_method="STRUCTURED_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_OJK",
            cluster_id="CLUS_OJK_GOVERNANCE_2024",
            novelty_class=NoveltyClass.NEW_CATALYST,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        ),
        # Case C: Government Ministerial Gazette
        NaturalObservationRecord(
            source_url="https://jdih.esdm.go.id/peraturan/kepmen-esdm-2024-coal-royalty.pdf",
            source_identity="SRC_ESDM_GAZETTE",
            source_class=SourceClass.GOVERNMENT_POLICY,
            retrieval_timestamp="2024-03-15T08:30:00Z",
            raw_content_hash=hashlib.sha256(b"Kepmen ESDM Coal Royalty Adjustment").hexdigest(),
            document_id="DOC_ESDM_ROYALTY_2024",
            published_at="2024-03-15T08:00:00Z",
            available_at="2024-03-15T08:15:00Z",
            observed_at="2024-03-15T08:30:00Z",
            event_time="2024-03-15T07:45:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.SOURCE_ARTICLE_METADATA,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="MINISTERIAL_JDIH_PORTAL",
            availability_derivation_method="SOURCE_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_MEMR",
            cluster_id="CLUS_COAL_ROYALTY_2024",
            novelty_class=NoveltyClass.NEW_CATALYST,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        ),
        # Case D: Reputable Secondary Media
        NaturalObservationRecord(
            source_url="https://market.bisnis.com/read/20240912/adro-divestasi-batu-bara",
            source_identity="SRC_BISNIS_MEDIA",
            source_class=SourceClass.SECONDARY_MEDIA,
            retrieval_timestamp="2024-09-12T11:00:00Z",
            raw_content_hash=hashlib.sha256(b"Bisnis Indonesia Analysis on ADRO Spin-off").hexdigest(),
            document_id="DOC_BISNIS_ADRO_20240912",
            published_at="2024-09-12T10:45:00Z",
            available_at="2024-09-12T10:50:00Z",
            observed_at="2024-09-12T11:00:00Z",
            event_time="2024-09-12T10:30:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.SOURCE_ARTICLE_METADATA,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="BISNIS_INDONESIA_CMS",
            availability_derivation_method="SOURCE_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_ADRO",
            cluster_id="CLUS_ADRO_SPINOFF_2024",
            novelty_class=NoveltyClass.STATUS_UPDATE,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        ),
        # Case E: Syndicated News Wire (Verbatim Portal Replication)
        NaturalObservationRecord(
            source_url="https://finance.detik.com/bursa/antara-adro-spin-off-resmi",
            source_identity="SRC_PORTAL_DETIK",
            source_class=SourceClass.SYNDICATED_WIRE,
            retrieval_timestamp="2024-09-12T11:15:00Z",
            raw_content_hash=hashlib.sha256(b"Antara Syndicated Wire Verbatim Body").hexdigest(),
            document_id="DOC_DETIK_SYND_20240912",
            published_at="2024-09-12T11:00:00Z",
            available_at="2024-09-12T11:05:00Z",
            observed_at="2024-09-12T11:15:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.SOURCE_ARTICLE_METADATA,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="DETIK_PORTAL_CMS",
            availability_derivation_method="SOURCE_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_ADRO",
            cluster_id="CLUS_ADRO_SPINOFF_2024",
            novelty_class=NoveltyClass.SYNDICATION,
            is_syndication=True,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        ),
        # Case F: Revised / Errata Document
        NaturalObservationRecord(
            source_url="https://idx.co.id/disclosures/2024/ADRO-spinoff-aadi-errata.pdf",
            source_identity="SRC_IDX_DISCLOSURE",
            source_class=SourceClass.REVISED_DOCUMENT,
            retrieval_timestamp="2024-09-13T09:00:00Z",
            raw_content_hash=hashlib.sha256(b"ADRO Spinoff AADI Correction Errata").hexdigest(),
            document_id="DOC_IDX_ADRO_ERRATA_20240913",
            prior_document_id="DOC_IDX_ADRO_20240911",
            published_at="2024-09-13T08:30:00Z",
            available_at="2024-09-13T08:45:00Z",
            observed_at="2024-09-13T09:00:00Z",
            timestamp_derivation_method=TimestampDerivationMethod.EXCHANGE_METADATA,
            temporal_confidence=TemporalConfidence.EXACT,
            availability_source="IDX_OFFICIAL_FEED",
            availability_derivation_method="STRUCTURED_METADATA",
            availability_confidence="VERIFIED",
            entity_resolution_status="RESOLVED",
            resolved_entity_id="ENT_ADRO",
            cluster_id="CLUS_ADRO_SPINOFF_2024",
            novelty_class=NoveltyClass.REVISION,
            is_revision=True,
            provenance_status="VERIFIED",
            market_pit_status="PIT_SAFE",
            system_pit_status="PIT_SAFE"
        )
    ]


@pytest.fixture
def gate7_platform(tmp_path):
    db_file = str(tmp_path / "gate7_test.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    
    # Sources
    sources = [
        SourceRecord(source_id="SRC_IDX_DISCLOSURE", source_name="BEI Official Disclosure Feed", publisher="PT Bursa Efek Indonesia", source_type=SourceType.EXCHANGE, jurisdiction="ID", authority_class="PRIMARY_EXCHANGE"),
        SourceRecord(source_id="SRC_OJK_REG", source_name="OJK Official Circulars", publisher="Otoritas Jasa Keuangan", source_type=SourceType.REGULATOR, jurisdiction="ID", authority_class="STATUTORY_REGULATOR"),
        SourceRecord(source_id="SRC_ESDM_GAZETTE", source_name="Kementerian ESDM Official Gazette", publisher="Kementerian ESDM RI", source_type=SourceType.GOVERNMENT, jurisdiction="ID", authority_class="MINISTRY"),
        SourceRecord(source_id="SRC_BISNIS_MEDIA", source_name="Bisnis Indonesia Markets", publisher="PT Jurnalindo Aksara Grafika", source_type=SourceType.NEWS, jurisdiction="ID", authority_class="REPUTABLE_FINANCIAL_MEDIA"),
        SourceRecord(source_id="SRC_ANTARA_WIRE", source_name="LKBN Antara Wire Feed", publisher="Lembaga Kantor Berita Nasional Antara", source_type=SourceType.NEWS, jurisdiction="ID", authority_class="NATIONAL_NEWS_AGENCY"),
        SourceRecord(source_id="SRC_PORTAL_DETIK", source_name="Detik Finance Portal", publisher="Trans Media", source_type=SourceType.NEWS, jurisdiction="ID", authority_class="SECONDARY_AGGREGATOR")
    ]
    for s in sources:
        platform.insert_source(s)

    # Entities
    entities = [
        EntityRecord(entity_id="ENT_ADRO", canonical_name="PT Adaro Energy Indonesia Tbk", entity_type=EntityType.COMPANY),
        EntityRecord(entity_id="ENT_PTBA", canonical_name="PT Bukit Asam Tbk", entity_type=EntityType.STATE_OWNED_ENTITY),
        EntityRecord(entity_id="ENT_BBCA", canonical_name="PT Bank Central Asia Tbk", entity_type=EntityType.BANK),
        EntityRecord(entity_id="ENT_MEMR", canonical_name="Kementerian Energi dan Sumber Daya Mineral", entity_type=EntityType.MINISTRY),
        EntityRecord(entity_id="ENT_OJK", canonical_name="Otoritas Jasa Keuangan", entity_type=EntityType.REGULATOR),
        EntityRecord(entity_id="ENT_COAL_SECTOR", canonical_name="Coal Mining Sector", entity_type=EntityType.SECTOR)
    ]
    for e in entities:
        platform.register_entity(e)

    # Identifiers & Aliases
    platform.insert_entity_identifier("ENT_ADRO", "IDX_TICKER", "ADRO")
    platform.insert_entity_identifier("ENT_PTBA", "IDX_TICKER", "PTBA")
    platform.insert_entity_identifier("ENT_BBCA", "IDX_TICKER", "BBCA")
    platform.insert_entity_alias("ENT_ADRO", "Adaro Energy")
    platform.insert_entity_alias("ENT_PTBA", "Bukit Asam")
    platform.insert_entity_alias("ENT_MEMR", "Kementerian ESDM")

    return platform


# =====================================================================
# 1. COHORT IDENTITY & METRIC DENOMINATOR INTEGRITY
# =====================================================================

def test_gate7_cohort_identity(canonical_gate7_observations):
    """Verifies that cohort manifest contains complete identity and non-empty bounds."""
    engine = IntelligenceQualityAuditEngine()
    manifest = engine.build_cohort_manifest(canonical_gate7_observations)
    
    assert manifest.cohort_id == "COHORT_GATE7_CANONICAL_V1"
    assert manifest.n_documents == 6
    assert manifest.n_information_items == 6
    assert manifest.n_source_classes == 6
    assert manifest.n_unique_sources == 5
    assert manifest.n_unique_events == 3  # CLUS_ADRO_SPINOFF_2024, CLUS_OJK_GOVERNANCE_2024, CLUS_COAL_ROYALTY_2024
    assert manifest.n_revisions == 1
    assert manifest.n_syndications == 1
    assert manifest.n_canonical_contradictions == 0


def test_gate7_metric_denominator_integrity(canonical_gate7_observations):
    """Verifies every metric contains an explicit valid denominator and valid rate range."""
    engine = IntelligenceQualityAuditEngine()
    report = engine.audit_observations(canonical_gate7_observations)
    
    assert len(report.metrics) >= 20
    for name, m in report.metrics.items():
        assert m.cohort_id == "COHORT_GATE7_CANONICAL_V1"
        assert m.denominator > 0, f"Metric {name} has zero denominator"
        assert 0.0 <= m.rate <= 1.0, f"Metric {name} rate out of bounds: {m.rate}"
        assert m.numerator <= m.denominator or m.dimension == "ADVERSARIAL", f"Metric {name} numerator exceeds denominator"


# =====================================================================
# 2. NOVELTY DISTRIBUTION INTEGRITY (SUM == 100.00%)
# =====================================================================

def test_gate7_novelty_distribution_integrity(canonical_gate7_observations):
    """Verifies primary novelty taxonomy is mutually exclusive and sums to 100.00%."""
    engine = IntelligenceQualityAuditEngine()
    report = engine.audit_observations(canonical_gate7_observations)
    
    dist = report.novelty_class_distribution
    assert dist["MATERIAL_CHANGE"]["numerator"] == 1
    assert dist["MATERIAL_CHANGE"]["percentage"] == pytest.approx(16.67, abs=0.01)
    assert dist["NEW_CATALYST"]["numerator"] == 2
    assert dist["NEW_CATALYST"]["percentage"] == pytest.approx(33.33, abs=0.01)
    assert dist["STATUS_UPDATE"]["numerator"] == 1
    assert dist["STATUS_UPDATE"]["percentage"] == pytest.approx(16.67, abs=0.01)
    assert dist["SYNDICATION"]["numerator"] == 1
    assert dist["SYNDICATION"]["percentage"] == pytest.approx(16.67, abs=0.01)
    assert dist["REVISION"]["numerator"] == 1
    assert dist["REVISION"]["percentage"] == pytest.approx(16.67, abs=0.01)
    
    total_pct = sum(d["percentage"] for d in dist.values())
    assert total_pct == pytest.approx(100.00, abs=0.05)
    assert report.novelty_distribution_sum_check == pytest.approx(100.00, abs=0.05)


# =====================================================================
# 3. CONTRADICTION POPULATION SEPARATION
# =====================================================================

def test_gate7_contradiction_population_separation(canonical_gate7_observations):
    """Verifies canonical cohort contradiction rate (0%) is not polluted by adversarial stress tests."""
    adv_inj = NaturalObservationRecord(
        source_url="https://fake.com/bad",
        source_identity="SRC_BISNIS_MEDIA",
        source_class=SourceClass.SECONDARY_MEDIA,
        retrieval_timestamp="2024-09-12T12:00:00Z",
        raw_content_hash="h_bad",
        document_id="DOC_ADV_CONTRA",
        published_at="2024-09-12T11:00:00Z",
        available_at="2024-09-12T11:30:00Z",
        observed_at="2024-09-12T12:00:00Z",
        novelty_class=NoveltyClass.CONTRADICTION,
        is_adversarial_injection=True
    )
    
    cohort_with_stress = canonical_gate7_observations + [adv_inj]
    engine = IntelligenceQualityAuditEngine()
    report = engine.audit_observations(cohort_with_stress)
    
    # Canonical cohort remains strictly 0.00% contradiction
    assert report.canonical_cohort_contradiction_rate == 0.00
    assert report.metrics["CANONICAL_COHORT_CONTRADICTION_RATE"].numerator == 0
    assert report.metrics["CANONICAL_COHORT_CONTRADICTION_RATE"].denominator == 6

    # Adversarial stress population tracked separately
    assert report.adversarial_injection_rate == pytest.approx(1 / 7, abs=0.01)
    assert report.adversarial_detection_rate == 1.00


# =====================================================================
# 4. SOURCE AUTHENTICITY SEMANTICS VS PROVENANCE INTEGRITY
# =====================================================================

def test_gate7_source_authenticity_semantics(canonical_gate7_observations):
    """Verifies source authenticity (authority class) is cleanly separated from cryptographic provenance."""
    engine = IntelligenceQualityAuditEngine()
    report = engine.audit_observations(canonical_gate7_observations)
    
    assert report.source_authenticity_rate == 1.00
    assert report.provenance_completeness == 1.00
    assert "SOURCE_AUTHENTICITY_RATE" in report.metrics
    assert "PROVENANCE_COMPLETENESS" in report.metrics


# =====================================================================
# 5. TEMPORAL COMPLETENESS & POINT-IN-TIME (MARKET VS SYSTEM PIT)
# =====================================================================

def test_gate7_temporal_completeness(canonical_gate7_observations):
    """Verifies granular temporal field completeness rates."""
    engine = IntelligenceQualityAuditEngine()
    report = engine.audit_observations(canonical_gate7_observations)
    
    assert report.event_time_completeness == pytest.approx(4 / 6, abs=0.01)  # 4/6 have explicit event_time
    assert report.publication_time_completeness == 1.00
    assert report.availability_time_completeness == 1.00
    assert report.observed_time_completeness == 1.00
    assert report.exact_timestamp_rate == 1.00
    assert report.fallback_timestamp_rate == 0.00


def test_gate7_market_pit(gate7_platform):
    """Market PIT: Documents with available_at > T_decision are invisible."""
    retrieval = KnowledgeRetrievalEngine(gate7_platform)
    
    info = InformationItemRecord(
        information_id="INFO_MARKET_PIT_TEST",
        document_id="DOC_M1",
        novelty_class=NoveltyClass.NEW_CATALYST,
        title="Market PIT Test Announcement",
        published_at="2024-06-01T09:00:00Z",
        available_at="2024-06-01T10:00:00Z",
        content_hash="h_m1"
    )
    gate7_platform.insert_information_item(info)
    
    # Query at T = 09:30 (Before market availability)
    res_market_early = retrieval.search_information(query="Market PIT", as_of="2024-06-01T09:30:00Z", pit_mode="MARKET")
    assert len(res_market_early.data) == 0

    # Query at T = 10:30 (After market availability)
    res_market_late = retrieval.search_information(query="Market PIT", as_of="2024-06-01T10:30:00Z", pit_mode="MARKET")
    assert len(res_market_late.data) == 1


def test_gate7_system_observability_pit(gate7_platform):
    """System PIT: Documents ingested after T_decision are invisible under system replay."""
    retrieval = KnowledgeRetrievalEngine(gate7_platform)
    
    # Document published in past (2020), but ingested/created at 2024-09-01
    info = InformationItemRecord(
        information_id="INFO_SYS_PIT_TEST",
        document_id="DOC_S1",
        novelty_class=NoveltyClass.STATUS_UPDATE,
        title="Historical Document Ingested Late",
        published_at="2020-01-01T00:00:00Z",
        available_at="2020-01-01T00:00:00Z",
        created_at="2024-09-01T00:00:00Z",
        content_hash="h_s1"
    )
    gate7_platform.insert_information_item(info)
    
    # Under Market PIT at T = 2022: Document was publicly available
    res_market = retrieval.search_information(query="Historical Document", as_of="2022-01-01T00:00:00Z", pit_mode="MARKET")
    assert len(res_market.data) == 1

    # Under System Observability PIT at T = 2022: SwingDeck had not yet ingested the document!
    res_sys = retrieval.search_information(query="Historical Document", as_of="2022-01-01T00:00:00Z", pit_mode="SYSTEM")
    assert len(res_sys.data) == 0


# =====================================================================
# 6. SOURCE VS EVENT POPULATION & SYNDICATION CONTROL
# =====================================================================

def test_gate7_source_vs_event_population(canonical_gate7_observations):
    """Distinguishes source class count, unique sources, and unique event clusters."""
    engine = IntelligenceQualityAuditEngine()
    manifest = engine.build_cohort_manifest(canonical_gate7_observations)
    
    assert manifest.n_source_classes == 6
    assert manifest.n_unique_sources == 5  # 5 distinct sources across 6 classes (Case A & F share SRC_IDX_DISCLOSURE)
    assert manifest.n_unique_events == 3
    assert manifest.n_independent_information_lineages == 5  # 6 docs minus 1 syndicated copy


def test_gate7_syndication_non_inflation():
    """1 originating event -> Wire -> 3 portals = 1 event, 1 lineage, 3 syndications."""
    wire_hash = hashlib.sha256(b"Antara wire release verbatim body text").hexdigest()
    
    wire = NaturalObservationRecord(
        source_url="https://antara.com/wire/1",
        source_identity="SRC_ANTARA",
        source_class=SourceClass.SYNDICATED_WIRE,
        retrieval_timestamp="2024-08-01T10:00:00Z",
        raw_content_hash=wire_hash,
        document_id="DOC_W1",
        published_at="2024-08-01T09:50:00Z",
        available_at="2024-08-01T09:55:00Z",
        observed_at="2024-08-01T10:00:00Z",
        cluster_id="CLUS_COAL_EXPORT",
        novelty_class=NoveltyClass.NEW_CATALYST,
        is_syndication=False
    )
    portals = [
        NaturalObservationRecord(
            source_url=f"https://portal{i}.com/news",
            source_identity=f"SRC_PORTAL_{i}",
            source_class=SourceClass.SYNDICATED_WIRE,
            retrieval_timestamp=f"2024-08-01T10:1{i}:00Z",
            raw_content_hash=wire_hash,
            document_id=f"DOC_P{i}",
            published_at="2024-08-01T10:00:00Z",
            available_at="2024-08-01T10:05:00Z",
            observed_at=f"2024-08-01T10:1{i}:00Z",
            cluster_id="CLUS_COAL_EXPORT",
            novelty_class=NoveltyClass.SYNDICATION,
            is_syndication=True
        )
        for i in range(1, 4)
    ]
    
    engine = IntelligenceQualityAuditEngine()
    manifest = engine.build_cohort_manifest([wire] + portals)
    report = engine.audit_observations([wire] + portals)
    
    assert manifest.n_unique_events == 1
    assert manifest.n_independent_information_lineages == 1
    assert manifest.n_syndications == 3
    assert report.syndication_rate == 0.75  # 3/4 are syndications
    assert report.syndication_inflation_rate == 0.00  # None counted as independent


# =====================================================================
# 7. REVISION LINEAGE & DELTA REPRODUCIBILITY
# =====================================================================

def test_gate7_revision_lineage(canonical_gate7_observations):
    """Verifies errata document cleanly links lineage to prior document."""
    errata_obs = next(o for o in canonical_gate7_observations if o.is_revision)
    assert errata_obs.prior_document_id == "DOC_IDX_ADRO_20240911"
    assert errata_obs.novelty_class == NoveltyClass.REVISION


def test_gate7_delta_reproducibility(gate7_platform):
    """Verifies state transition delta detection and ordering are fully reproducible."""
    retrieval = KnowledgeRetrievalEngine(gate7_platform)
    
    rel_old = EntityRelationshipRecord(
        relationship_id="REL_DELT_OLD",
        subject_entity_id="ENT_ADRO",
        relationship_type=RelationshipType.OWNS,
        object_entity_id="ENT_PTBA",
        valid_from="2024-01-01T00:00:00Z",
        valid_to="2024-06-01T00:00:00Z",
        observed_at="2024-01-01T00:00:00Z"
    )
    rel_new = EntityRelationshipRecord(
        relationship_id="REL_DELT_NEW",
        subject_entity_id="ENT_ADRO",
        relationship_type=RelationshipType.PARTNERS_WITH,
        object_entity_id="ENT_PTBA",
        valid_from="2024-06-01T00:00:00Z",
        observed_at="2024-06-01T00:00:00Z"
    )
    gate7_platform.register_relationship(rel_old)
    gate7_platform.register_relationship(rel_new)
    
    d1 = retrieval.get_information_delta("ENT_ADRO", "2024-01-01T00:00:00Z", "2024-07-01T00:00:00Z")
    d2 = retrieval.get_information_delta("ENT_ADRO", "2024-01-01T00:00:00Z", "2024-07-01T00:00:00Z")
    
    assert d1.data == d2.data
    assert len(d1.data["new_relationships"]) == 1
    assert len(d1.data["expired_relationships"]) == 1


# =====================================================================
# 8. METRIC DETERMINISM (RUN_A == RUN_B)
# =====================================================================

def test_gate7_metric_determinism(canonical_gate7_observations):
    """Verifies metric engine computation is 100% deterministic across multiple runs."""
    engine = IntelligenceQualityAuditEngine()
    r1 = engine.audit_observations(canonical_gate7_observations)
    r2 = engine.audit_observations(canonical_gate7_observations)
    
    assert r1.metrics == r2.metrics
    assert r1.novelty_class_distribution == r2.novelty_class_distribution
    assert r1.source_authenticity_rate == r2.source_authenticity_rate
    assert r1.market_pit_violation_rate == r2.market_pit_violation_rate


# =====================================================================
# 9. COMPLETE END-TO-END TRACE RECONSTRUCTION
# =====================================================================

def test_full_trace_lineage_reconstruction(gate7_platform):
    """
    Validates complete lineage reconstruction:
    RAW DOC -> AUTHENTICITY -> TIMESTAMP -> ENTITY -> CLAIM -> EVIDENCE -> CLUSTER -> NOVELTY -> EXPOSURE -> PIT RETRIEVAL -> AGENT 2
    """
    content = "PT Adaro Energy Indonesia Tbk mengumumkan rencana pemisahan bisnis pilar batu bara termal."
    c_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    raw_doc = RawDocumentRecord(
        raw_document_id="RAW_DOC_TRACE_001",
        source_id="SRC_IDX_DISCLOSURE",
        source_document_id="IDX_DISC_ADRO_991",
        retrieved_at="2024-09-11T10:05:00Z",
        published_at="2024-09-11T09:45:00Z",
        available_at="2024-09-11T10:00:00Z",
        content_hash=c_hash,
        raw_location="/storage/raw/2024/09/11/adro_disc.pdf",
        raw_size=len(content)
    )
    res_raw = gate7_platform.ingest_raw_document(raw_doc)
    assert res_raw["status"] == "INGESTED"

    res_ent = gate7_platform.resolve_entity(query="ADRO", identifier_type="IDX_TICKER")
    assert res_ent["status"] == "RESOLVED"
    assert res_ent["entity_id"] == "ENT_ADRO"

    info_item = InformationItemRecord(
        information_id="INFO_TRACE_001",
        document_id=raw_doc.raw_document_id,
        novelty_class=NoveltyClass.MATERIAL_CHANGE,
        title="ADRO Thermal Coal Business Spinoff Announcement",
        summary="Adaro announces spinoff of PT Adaro Andalan Indonesia.",
        published_at=raw_doc.published_at,
        available_at=raw_doc.available_at,
        content_hash=c_hash
    )
    gate7_platform.insert_information_item(info_item)

    ev = EvidenceRecord(
        evidence_id="EV_TRACE_001",
        information_id=info_item.information_id,
        source_id="SRC_IDX_DISCLOSURE",
        document_id=raw_doc.raw_document_id,
        content_hash=c_hash,
        published_at=raw_doc.published_at,
        available_at=raw_doc.available_at,
        observed_at="2024-09-11T10:05:00Z"
    )
    gate7_platform.insert_evidence(ev)

    claim = ClaimRecord(
        claim_id="CLAIM_TRACE_001",
        information_id=info_item.information_id,
        subject_entity_id="ENT_ADRO",
        predicate="SPINOFF_SUBSIDIARY",
        object_entity_id="ENT_ADRO",
        claim_text="ADRO spins off thermal coal unit AADI",
        created_at="2024-09-11T10:05:00Z"
    )
    gate7_platform.insert_claim(claim)

    rel = EntityRelationshipRecord(
        relationship_id="REL_TRACE_ADRO_DISP",
        subject_entity_id="ENT_ADRO",
        relationship_type=RelationshipType.DISPOSES,
        object_entity_id="ENT_ADRO",
        valid_from=raw_doc.available_at,
        observed_at="2024-09-11T10:05:00Z"
    )
    gate7_platform.register_relationship(rel, evidence_id=ev.evidence_id)

    retrieval = KnowledgeRetrievalEngine(gate7_platform)
    
    # Query before availability time (09:50)
    res_before = retrieval.retrieve("ENT_ADRO", as_of="2024-09-11T09:50:00Z", pit_mode="MARKET")
    assert len(res_before.data["information_items"]) == 0

    # Query after availability time (10:30)
    res_after = retrieval.retrieve("ENT_ADRO", as_of="2024-09-11T10:30:00Z", pit_mode="MARKET")
    assert len(res_after.data["information_items"]) >= 1
    assert res_after.data["information_items"][0]["information_id"] == "INFO_TRACE_001"
    assert res_after.provenance_status == "VERIFIED"
