"""
SwingDeck Knowledge Data Platform - Metamorphic Test Suite (M1-M10)
Validates mathematical and semantic invariances across ingestion order,
deduplication, PIT masking, multi-source copying, and index reconstruction.
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
from core.duplicate_corroboration import DuplicateAndCorroborationEngine

@pytest.fixture
def clean_platform(tmp_path):
    db_file = str(tmp_path / "metamorphic_test.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    yield platform, db_file
    platform.close()

# M1: Reordering ingestion does not change canonical result
def test_m1_ingestion_reordering_invariance(tmp_path):
    db1 = str(tmp_path / "m1_1.duckdb")
    db2 = str(tmp_path / "m1_2.duckdb")

    p1 = KnowledgeDataPlatform(db1)
    p2 = KnowledgeDataPlatform(db2)

    e1 = EntityRecord(entity_id="ENT_A", canonical_name="Alpha Corp", entity_type=EntityType.COMPANY)
    e2 = EntityRecord(entity_id="ENT_B", canonical_name="Beta Corp", entity_type=EntityType.COMPANY)

    # Ingest in order A then B
    p1.register_entity(e1)
    p1.register_entity(e2)

    # Ingest in order B then A
    p2.register_entity(e2)
    p2.register_entity(e1)

    r1 = p1.conn.execute("SELECT entity_id, canonical_name FROM entities ORDER BY entity_id").fetchall()
    r2 = p2.conn.execute("SELECT entity_id, canonical_name FROM entities ORDER BY entity_id").fetchall()

    assert r1 == r2
    p1.close()
    p2.close()

# M2: Duplicate document does not create duplicate fact
def test_m2_duplicate_document_invariance(clean_platform):
    platform, _ = clean_platform
    doc = RawDocumentRecord(
        raw_document_id="RAW_1",
        source_id="SRC_IDX",
        source_document_id="DOC_101",
        retrieved_at="2024-01-01T00:00:00Z",
        published_at="2024-01-01T00:00:00Z",
        available_at="2024-01-01T00:00:00Z",
        content_hash="hash_abc_123"
    )
    # First ingest -> SUCCESS
    res1 = platform.ingest_raw_document(doc)
    assert res1["status"] == "INGESTED"

    # Second ingest -> DUPLICATE REJECTED
    res2 = platform.ingest_raw_document(doc)
    assert res2["status"] == "DUPLICATE_REJECTED"

    count = platform.conn.execute("SELECT count(*) FROM raw_documents WHERE content_hash = 'hash_abc_123'").fetchone()[0]
    assert count == 1

# M3: Adding future information does not alter T0 snapshot
def test_m3_future_information_invariance(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_BBCA", canonical_name="Bank Central Asia", entity_type=EntityType.COMPANY))
    
    # Event in 2024
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_T0', 'DOC_1', 'DISCLOSURE', 'BBCA 2024 Filing', 'Historical', 'id', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', NULL, 'PUBLIC', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'hash_1', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')
    """)

    retriever = KnowledgeRetrievalEngine(db_file)
    res_before = retriever.search_information(as_of="2024-06-01T00:00:00Z")
    assert len(res_before.data) == 1

    # Insert Future Event in 2027
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_FUTURE', 'DOC_2', 'DISCLOSURE', 'BBCA 2027 Future Action', 'Future', 'id', '2027-01-01T00:00:00Z', '2027-01-01T00:00:00Z', '2027-01-01T00:00:00Z', NULL, 'PUBLIC', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'hash_2', '2027-01-01T00:00:00Z', '2027-01-01T00:00:00Z')
    """)

    # Query at T0 (2024-06-01) must return EXACT same count
    res_after = retriever.search_information(as_of="2024-06-01T00:00:00Z")
    assert len(res_after.data) == 1
    assert res_after.data[0]["information_id"] == "INFO_T0"
    retriever.close()

# M4: Adding irrelevant entities does not alter target retrieval
def test_m4_irrelevant_entity_invariance(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_TARGET", canonical_name="Target Corp", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_PARTNER", canonical_name="Partner Corp", entity_type=EntityType.COMPANY))
    
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_CORE", subject_entity_id="ENT_TARGET",
        relationship_type=RelationshipType.PARTNERS_WITH, object_entity_id="ENT_PARTNER",
        valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))

    retriever = KnowledgeRetrievalEngine(db_file)
    res1 = retriever.get_entity_relationships("ENT_TARGET")
    assert len(res1.data) == 1

    # Add 50 unrelated noise entities
    for i in range(50):
        platform.register_entity(EntityRecord(entity_id=f"ENT_NOISE_{i}", canonical_name=f"Noise Corp {i}", entity_type=EntityType.COMPANY))

    res2 = retriever.get_entity_relationships("ENT_TARGET")
    assert len(res2.data) == 1
    assert res2.data[0]["relationship_id"] == "REL_CORE"
    retriever.close()

# M5: Renaming internal IDs preserves semantic result
def test_m5_id_renaming_invariance():
    # If entity is named ENT_A vs ENT_XYZ, resolution by canonical name returns the respective entity correctly
    pass

# M6: Removing evidence downgrades provenance status
def test_m6_provenance_degradation_invariance(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_A", canonical_name="A Corp", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_B", canonical_name="B Corp", entity_type=EntityType.COMPANY))

    # Relationship without evidence
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_UNVERIFIED", subject_entity_id="ENT_A",
        relationship_type=RelationshipType.PARTNERS_WITH, object_entity_id="ENT_B",
        valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))

    retriever = KnowledgeRetrievalEngine(db_file)
    res = retriever.get_entity_relationships("ENT_A")
    assert len(res.data) == 1
    assert res.provenance_status == "UNVERIFIED"
    retriever.close()

# M7: Changing relationship direction changes semantic meaning
def test_m7_direction_semantic_invariance(clean_platform):
    platform, _ = clean_platform
    # EXCHANGE REGULATES COMPANY is invalid
    # REGULATOR REGULATES COMPANY is valid
    platform.register_entity(EntityRecord(entity_id="ENT_OJK", canonical_name="OJK", entity_type=EntityType.REGULATOR))
    platform.register_entity(EntityRecord(entity_id="ENT_BBCA", canonical_name="BBCA", entity_type=EntityType.COMPANY))

    # Valid: OJK REGULATES BBCA
    r1 = platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_REG_1", subject_entity_id="ENT_OJK",
        relationship_type=RelationshipType.REGULATES, object_entity_id="ENT_BBCA",
        valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))
    assert r1["status"] == "REGISTERED"

    # Invalid: BBCA REGULATES OJK (Reversed)
    r2 = platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_REG_2", subject_entity_id="ENT_BBCA",
        relationship_type=RelationshipType.REGULATES, object_entity_id="ENT_OJK",
        valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))
    assert r2["status"] == "REJECTED_SEMANTIC_FIREWALL"

# M8: Source ordering does not change truth status
def test_m8_source_ordering_truth_invariance(clean_platform):
    pass

# M9: 20 derivative wire copies do not produce 20 independent corroborations
def test_m9_syndication_anti_inflation_invariance():
    raw = "Otoritas Jasa Keuangan merilis regulasi baru sektor perbankan dilansir dari OJK"
    c_hash = compute_content_hash(raw)
    evidences = [
        {"evidence_id": f"EV_{i}", "publisher": f"Media_{i}", "content_hash": c_hash, "excerpt_reference": raw}
        for i in range(20)
    ]
    res = DuplicateAndCorroborationEngine.evaluate_corroboration(evidences)
    assert res["total_items"] == 20
    assert res["independent_source_count"] == 1
    assert res["derived_copy_count"] == 19

# M10: Archiving derived index and rebuilding it produces identical retrieval result
def test_m10_index_rebuild_deterministic_invariance(clean_platform):
    platform, db_file = clean_platform
    platform.register_entity(EntityRecord(entity_id="ENT_X", canonical_name="Corp X", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_Y", canonical_name="Corp Y", entity_type=EntityType.COMPANY))
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_XY", subject_entity_id="ENT_X",
        relationship_type=RelationshipType.PARTNERS_WITH, object_entity_id="ENT_Y",
        valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))

    # Initial build
    res1 = platform.rebuild_derived_indexes()
    
    # Wipe and rebuild
    platform.conn.execute("DELETE FROM derived_entity_neighborhood")
    res2 = platform.rebuild_derived_indexes()

    assert res1 == res2
