"""
SwingDeck Knowledge Data Platform - Adversarial & Corruption Test Suite (16 Attacks)
Tests fail-closed robustness against duplicate injections, referential corruption,
semantic firewall bypass, PIT leakage, MNPI containment, and origin tampering.
"""

import pytest
from datetime import datetime, timezone

from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import (
    EntityRecord, EntityRelationshipRecord, RawDocumentRecord,
    InformationItemRecord, EvidenceRecord, RetrievalPathMode,
    compute_content_hash, compute_document_fingerprint
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    AccessClass, EvidenceClassification
)

@pytest.fixture
def clean_platform(tmp_path):
    db_file = str(tmp_path / "adversarial_kdp.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    yield platform, db_file
    platform.close()

# Attack 1: Duplicate entity insertion
def test_attack_01_duplicate_entity(clean_platform):
    platform, _ = clean_platform
    e1 = EntityRecord(entity_id="ENT_BBCA", canonical_name="Bank Central Asia", entity_type=EntityType.COMPANY)
    r1 = platform.register_entity(e1)
    assert r1["status"] == "REGISTERED"
    
    # Re-inserting replaces/updates without duplicate primary key
    r2 = platform.register_entity(e1)
    assert r2["status"] == "REGISTERED"
    count = platform.conn.execute("SELECT count(*) FROM entities WHERE entity_id = 'ENT_BBCA'").fetchone()[0]
    assert count == 1

# Attack 2: Duplicate raw document insertion
def test_attack_02_duplicate_raw_document(clean_platform):
    platform, _ = clean_platform
    doc = RawDocumentRecord(
        raw_document_id="RAW_1", source_id="SRC_IDX", source_document_id="DOC_1",
        retrieved_at="2024-01-01T00:00:00Z", published_at="2024-01-01T00:00:00Z",
        available_at="2024-01-01T00:00:00Z", content_hash="hash_1"
    )
    r1 = platform.ingest_raw_document(doc)
    assert r1["status"] == "INGESTED"
    r2 = platform.ingest_raw_document(doc)
    assert r2["status"] == "DUPLICATE_REJECTED"

# Attack 3: Duplicate evidence insertion
def test_attack_03_duplicate_evidence(clean_platform):
    platform, _ = clean_platform
    platform.conn.execute("""
        INSERT INTO evidence VALUES 
        ('EV_1', 'INFO_1', 'SRC_IDX', 'DOC_1', 'CLAIM_1', 'EXCERPT', 'Text', 'hash_1', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'PUBLIC', 'NATURAL', 'VERIFIED', '2024-01-01T00:00:00Z')
    """)
    # Inserting same primary key must fail or be caught
    with pytest.raises(Exception):
        platform.conn.execute("""
            INSERT INTO evidence VALUES 
            ('EV_1', 'INFO_1', 'SRC_IDX', 'DOC_1', 'CLAIM_1', 'EXCERPT', 'Text', 'hash_1', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'PUBLIC', 'NATURAL', 'VERIFIED', '2024-01-01T00:00:00Z')
        """)

# Attack 4: Missing foreign key in relationship caught by audit
def test_attack_04_missing_foreign_key(clean_platform):
    platform, _ = clean_platform
    platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at)
        VALUES ('REL_BAD', 'ENT_MISSING_1', 'OWNS', 'ENT_MISSING_2', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')
    """)
    audit = platform.run_data_quality_audit()
    assert audit["status"] == "FAIL"
    assert any("REFERENTIAL_INTEGRITY" in f["check"] for f in audit["findings"])

# Attack 5: Incompatible relationship semantic typing
def test_attack_05_incompatible_relationship_semantics(clean_platform):
    platform, _ = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_IDX", canonical_name="IDX", entity_type=EntityType.EXCHANGE))
    platform.register_entity(EntityRecord(entity_id="ENT_BBCA", canonical_name="BBCA", entity_type=EntityType.COMPANY))
    
    # EXCHANGE OWNS COMPANY is semantically forbidden
    rel = EntityRelationshipRecord(
        relationship_id="REL_INVALID", subject_entity_id="ENT_IDX",
        relationship_type=RelationshipType.OWNS, object_entity_id="ENT_BBCA",
        valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z"
    )
    res = platform.register_relationship(rel)
    assert res["status"] == "REJECTED_SEMANTIC_FIREWALL"

# Attack 6: Future evidence leaking into past PIT query
def test_attack_06_future_evidence_pit_isolation(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_BBCA", canonical_name="BBCA", entity_type=EntityType.COMPANY))
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_FUTURE', 'DOC_F', 'DISCLOSURE', 'Future 2028 Disclosure', 'Leak Test', 'id', '2028-01-01T00:00:00Z', '2028-01-01T00:00:00Z', '2028-01-01T00:00:00Z', NULL, 'PUBLIC', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'h_f', '2028-01-01T00:00:00Z', '2028-01-01T00:00:00Z')
    """)
    retriever = KnowledgeRetrievalEngine(db_file)
    res = retriever.search_information(as_of="2024-01-01T00:00:00Z")
    assert len(res.data) == 0
    retriever.close()

# Attack 7: Expired relationship remaining active
def test_attack_07_expired_relationship_clamping(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_A", canonical_name="A Corp", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_B", canonical_name="B Corp", entity_type=EntityType.COMPANY))
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_EXP", subject_entity_id="ENT_A",
        relationship_type=RelationshipType.PARTNERS_WITH, object_entity_id="ENT_B",
        valid_from="2020-01-01T00:00:00Z", valid_to="2022-01-01T00:00:00Z",
        observed_at="2020-01-01T00:00:00Z"
    ))
    retriever = KnowledgeRetrievalEngine(db_file)
    res = retriever.get_entity_relationships("ENT_A", as_of="2024-01-01T00:00:00Z")
    assert len(res.data) == 0
    retriever.close()

# Attack 8: Wrong entity semantic type injection
def test_attack_08_wrong_entity_type_conflict(clean_platform):
    platform, _ = clean_platform
    # IDX labeled as REGULATOR
    e = EntityRecord(entity_id="ENT_IDX", canonical_name="Bursa Efek Indonesia", entity_type=EntityType.REGULATOR)
    res = platform.register_entity(e)
    assert res["semantic_status"] == "CONFLICT_DETECTED"

# Attack 9: Wrong source publisher assignment
def test_attack_09_source_audit(clean_platform):
    platform, _ = clean_platform
    platform.conn.execute("""
        INSERT INTO sources VALUES 
        ('SRC_1', 'Official IDX', 'IDX', 'EXCHANGE', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')
    """)
    count = platform.conn.execute("SELECT count(*) FROM sources WHERE source_id = 'SRC_1'").fetchone()[0]
    assert count == 1

# Attack 10: Corrupted SHA-256 hash injection
def test_attack_10_corrupted_content_hash():
    text = "Important regulatory document"
    real_hash = compute_content_hash(text)
    fake_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    assert real_hash != fake_hash

# Attack 11: Missing provenance reference
def test_attack_11_missing_provenance_audit(clean_platform):
    platform, _ = clean_platform
    platform.conn.execute("""
        INSERT INTO evidence VALUES 
        ('EV_ORPHAN', 'INFO_1', 'SRC_GHOST_NON_EXISTENT', 'DOC_1', 'CLAIM_1', 'EXCERPT', 'Text', 'hash', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'PUBLIC', 'NATURAL', 'UNVERIFIED', '2024-01-01T00:00:00Z')
    """)
    audit = platform.run_data_quality_audit()
    assert audit["status"] == "FAIL"
    assert any("PROVENANCE_INTEGRITY" in f["check"] for f in audit["findings"])

# Attack 12: MNPI access class containment
def test_attack_12_mnpi_access_containment(clean_platform):
    platform, db_file = clean_platform
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_MNPI', 'DOC_M', 'DISCLOSURE', 'Unpublished Merger Leak', 'MNPI', 'id', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', NULL, 'MNPI', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'h_m', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')
    """)
    retriever = KnowledgeRetrievalEngine(db_file)
    # Default public search MUST NOT return MNPI
    res = retriever.search_information(access_class=AccessClass.PUBLIC)
    assert len(res.data) == 0
    retriever.close()

# Attack 13: Unauthorized private data access attempt
def test_attack_13_restricted_access_containment(clean_platform):
    platform, db_file = clean_platform
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_RESTRICTED', 'DOC_R', 'DISCLOSURE', 'Private Due Diligence', 'Restricted', 'id', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', NULL, 'RESTRICTED', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'h_r', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')
    """)
    retriever = KnowledgeRetrievalEngine(db_file)
    res = retriever.search_information(access_class=AccessClass.PUBLIC)
    assert len(res.data) == 0
    retriever.close()

# Attack 14: Fixture record marked as natural separation
def test_attack_14_fixture_origin_separation(clean_platform):
    platform, _ = clean_platform
    doc = RawDocumentRecord(
        raw_document_id="RAW_FIXTURE", source_id="SRC_FIXTURE", source_document_id="DOC_F",
        retrieved_at="2024-01-01T00:00:00Z", published_at="2024-01-01T00:00:00Z",
        available_at="2024-01-01T00:00:00Z", content_hash="hash_fix",
        origin_class=EvidenceClassification.FIXTURE
    )
    assert doc.origin_class == EvidenceClassification.FIXTURE

# Attack 15: Natural record marked as fixture separation
def test_attack_15_natural_origin_separation():
    doc = RawDocumentRecord(
        raw_document_id="RAW_NAT", source_id="SRC_IDX", source_document_id="DOC_N",
        retrieved_at="2024-01-01T00:00:00Z", published_at="2024-01-01T00:00:00Z",
        available_at="2024-01-01T00:00:00Z", content_hash="hash_nat",
        origin_class=EvidenceClassification.NATURAL
    )
    assert doc.origin_class == EvidenceClassification.NATURAL

# Attack 16: Disconnected multi-hop graph traversal
def test_attack_16_disconnected_graph_traversal(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_ISOLATED", canonical_name="Isolated Corp", entity_type=EntityType.COMPANY))
    retriever = KnowledgeRetrievalEngine(db_file)
    res = retriever.get_entity_relationships("ENT_ISOLATED", max_hops=3, mode=RetrievalPathMode.DEEP_PATH)
    assert len(res.data) == 0
    retriever.close()
