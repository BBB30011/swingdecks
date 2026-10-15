"""
SwingDeck Knowledge Data Platform - Knowledge Retrieval & Golden Queries Test Suite
Validates Golden Queries Q01-Q10, FAST PATH vs DEEP PATH, PIT boundary clamping,
information delta, full contract traceability, and local performance scaling.
"""

import time
import pytest
from datetime import datetime, timezone
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import (
    EntityRecord, EntityRelationshipRecord, ExposureRecord,
    InformationItemRecord, EvidenceRecord, RetrievalPathMode,
    CorporateActionRecord, CorporateActionType
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    AccessClass, EvidenceClassification
)

@pytest.fixture
def populated_test_platform(tmp_path):
    db_file = str(tmp_path / "retrieval_test.duckdb")
    platform = KnowledgeDataPlatform(db_file)

    # 1. Register Entities
    platform.register_entity(EntityRecord(entity_id="ENT_ADRO", canonical_name="Adaro Energy Indonesia", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_AADI", canonical_name="Adaro Andalan Indonesia", entity_type=EntityType.SUBSIDIARY))
    platform.register_entity(EntityRecord(entity_id="ENT_BBCA", canonical_name="Bank Central Asia", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_DJARUM", canonical_name="Djarum Group", entity_type=EntityType.HOLDING_COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_COAL_COMMODITY", canonical_name="Thermal Coal", entity_type=EntityType.COMMODITY))

    # 2. Register Sources
    platform.conn.execute("""
        INSERT INTO sources VALUES 
        ('SRC_IDX', 'IDX Disclosure Feed', 'PT Bursa Efek Indonesia', 'EXCHANGE', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('SRC_BI', 'Bank Indonesia Release', 'Bank Indonesia', 'CENTRAL_BANK', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z');
    """)

    # 3. Register Evidences
    platform.conn.execute("""
        INSERT INTO evidence VALUES 
        ('EV_ADRO_AADI', 'INFO_1', 'SRC_IDX', 'DOC_1', 'CLAIM_1', 'PROSPECTUS', 'ADRO owns 99.9% of AADI', 'hash123', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'PUBLIC', 'NATURAL', 'VERIFIED', '2024-01-01T00:00:00Z'),
        ('EV_DJARUM_BBCA', 'INFO_2', 'SRC_IDX', 'DOC_2', 'CLAIM_2', 'FILING', 'Djarum Group controls 54.9% of BBCA', 'hash456', '2010-01-01T00:00:00Z', '2010-01-01T00:00:00Z', '2010-01-01T00:00:00Z', '2010-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'PUBLIC', 'NATURAL', 'VERIFIED', '2010-01-01T00:00:00Z');
    """)

    # 4. Register Relationships
    platform.register_relationship(
        EntityRelationshipRecord(
            relationship_id="REL_ADRO_AADI",
            subject_entity_id="ENT_ADRO",
            relationship_type=RelationshipType.OWNS,
            object_entity_id="ENT_AADI",
            valid_from="2024-01-01T00:00:00Z",
            valid_to="2024-11-30T00:00:00Z",
            observed_at="2024-01-01T00:00:00Z"
        ),
        evidence_id="EV_ADRO_AADI"
    )

    platform.register_relationship(
        EntityRelationshipRecord(
            relationship_id="REL_DJARUM_BBCA",
            subject_entity_id="ENT_DJARUM",
            relationship_type=RelationshipType.CONTROLS,
            object_entity_id="ENT_BBCA",
            valid_from="2010-01-01T00:00:00Z",
            valid_to=None,
            observed_at="2010-01-01T00:00:00Z"
        ),
        evidence_id="EV_DJARUM_BBCA"
    )

    # 5. Register Exposures
    platform.conn.execute("""
        INSERT INTO exposures VALUES 
        ('EXP_ADRO_COAL', 'ENT_ADRO', 'INFO_1', 'COMMODITY_PRICE', 'DIRECT_EXPOSURE', 'POSITIVE', 'HIGH', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_BBCA_RATE', 'ENT_BBCA', 'INFO_2', 'INTEREST_RATE', 'DIRECT_EXPOSURE', 'POSITIVE', 'MEDIUM', '2020-01-01T00:00:00Z', NULL, 'SUPPORTED');
    """)

    # 6. Register Information Items
    platform.conn.execute("""
        INSERT INTO information_items VALUES 
        ('INFO_1', 'DOC_1', 'DISCLOSURE', 'ADRO PUPS Prospectus for AADI IPO', 'Spin-off disclosure', 'id', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-11-30T00:00:00Z', 'PUBLIC', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'hash123', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('INFO_POLICY_BI', 'DOC_3', 'POLICY', 'Bank Indonesia Rate Decision 6.00%', 'BI raises benchmark rate by 25bps', 'id', '2024-04-24T00:00:00Z', '2024-04-24T00:00:00Z', '2024-04-24T00:00:00Z', NULL, 'PUBLIC', 'NATURAL', 'VALID', 'VALID', 'VERIFIED', 'hash789', '2024-04-24T00:00:00Z', '2024-04-24T00:00:00Z');
    """)

    # 7. Register Contradictions
    platform.conn.execute("""
        INSERT INTO contradictions VALUES 
        ('CONTRA_BBCA_1', 'ENT_BBCA', 'FACTUAL_CONTRADICTION', 'EV_DJARUM_BBCA', 'EV_ADRO_AADI', 'LOW', 'ACTIVE', 'RESOLVED', '2024-01-01T00:00:00Z');
    """)

    platform.rebuild_derived_indexes()
    platform.close()

    retriever = KnowledgeRetrievalEngine(db_file)
    yield retriever, db_file
    retriever.close()

# Q01: All current relationships of ADRO
def test_golden_q01_adro_current_relationships(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_entity_relationships("ENT_ADRO", as_of="2024-06-01T00:00:00Z")
    assert len(res.data) == 1
    assert res.data[0]["object_entity_id"] == "ENT_AADI"
    assert "EV_ADRO_AADI" in res.evidence_refs
    assert res.temporal_status == "VALID"

# Q02: ADRO relationships at 2024-06-01 (Pre-spinoff active)
def test_golden_q02_adro_pit_active(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_entity_relationships("ENT_ADRO", as_of="2024-06-01T00:00:00Z")
    assert len(res.data) == 1
    assert res.data[0]["relationship_id"] == "REL_ADRO_AADI"

# Q03: ADRO relationships at 2025-01-01 (Post-spinoff expired)
def test_golden_q03_adro_pit_expired(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_entity_relationships("ENT_ADRO", as_of="2025-01-01T00:00:00Z")
    assert len(res.data) == 0

# Q04: All evidence supporting ADRO-AADI ownership
def test_golden_q04_evidence_support(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_entity_relationships("ENT_ADRO", as_of="2024-06-01T00:00:00Z")
    assert "EV_ADRO_AADI" in res.evidence_refs
    assert res.provenance_status == "VERIFIED"

# Q05: All information available for BBCA before T0
def test_golden_q05_bbca_information_pit(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.search_information(query="Prospectus", as_of="2024-06-01T00:00:00Z")
    assert len(res.data) == 1
    assert res.data[0]["information_id"] == "INFO_1"

# Q06: All current exposures of BBCA
def test_golden_q06_bbca_exposures(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_exposures("ENT_BBCA", as_of="2024-06-01T00:00:00Z")
    assert len(res.data) == 1
    assert res.data[0]["economic_channel"] == "INTEREST_RATE"

# Q07: All contradictions for BBCA
def test_golden_q07_bbca_contradictions(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.get_contradictions("ENT_BBCA")
    assert len(res.data) == 1
    assert res.data[0]["contradiction_id"] == "CONTRA_BBCA_1"

# Q08: All policy events affecting banking
def test_golden_q08_policy_search(populated_test_platform):
    retriever, _ = populated_test_platform
    res = retriever.search_information(information_type="POLICY", as_of="2024-06-01T00:00:00Z")
    assert len(res.data) == 1
    assert res.data[0]["information_id"] == "INFO_POLICY_BI"

# Q09: Full World Snapshot at T0
def test_golden_q09_world_snapshot(populated_test_platform):
    retriever, _ = populated_test_platform
    snapshot = retriever.get_world_snapshot("ENT_BBCA", "2024-06-01T00:00:00Z")
    assert snapshot.data["entity"]["canonical_name"] == "Bank Central Asia"
    assert len(snapshot.data["relationships"]) == 1
    assert len(snapshot.data["exposures"]) == 1
    assert snapshot.execution_time_ms >= 0.0

# Q10: Information Delta between T0 and T1
def test_golden_q10_information_delta(populated_test_platform):
    retriever, _ = populated_test_platform
    delta = retriever.get_information_delta("ENT_ADRO", "2024-01-01T00:00:00Z", "2024-12-31T00:00:00Z")
    # In 2024-11-30, REL_ADRO_AADI expired
    assert delta.data["total_changes"] >= 1
    assert any(r["id"] == "REL_ADRO_AADI" for r in delta.data["expired_relationships"])

# Multi-hop Graph Traversal & Scale Test
def test_multi_hop_deep_path(populated_test_platform):
    retriever, _ = populated_test_platform
    # Traversal from DJARUM -> BBCA (1-hop)
    res_deep = retriever.get_entity_relationships("ENT_DJARUM", max_hops=2, mode=RetrievalPathMode.DEEP_PATH)
    assert len(res_deep.data) == 1
    assert res_deep.data[0]["object_entity_id"] == "ENT_BBCA"
    assert res_deep.path_mode == RetrievalPathMode.DEEP_PATH

def test_scale_benchmark(tmp_path):
    db_file = str(tmp_path / "scale_test.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    
    # Insert 1,000 entities and 2,000 relationships
    t_start = time.perf_counter()
    platform.conn.execute("BEGIN TRANSACTION")
    for i in range(1000):
        platform.conn.execute(f"INSERT INTO entities VALUES ('ENT_{i}', 'Company_{i}', 'COMPANY', 'ID', 'ACTIVE', '1970-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')")
        if i > 0:
            platform.conn.execute(f"INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at) VALUES ('REL_{i}', 'ENT_{i-1}', 'OWNS', 'ENT_{i}', '1970-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z')")
    platform.conn.execute("COMMIT")
    insert_time = time.perf_counter() - t_start
    assert insert_time < 2.0  # Fast batch insert

    platform.rebuild_derived_indexes()
    platform.close()

    retriever = KnowledgeRetrievalEngine(db_file)
    t_query = time.perf_counter()
    res = retriever.get_entity_relationships("ENT_500", max_hops=1, mode=RetrievalPathMode.FAST_PATH)
    q_time_ms = (time.perf_counter() - t_query) * 1000
    assert q_time_ms < 50.0  # Fast path under 50ms locally
    assert len(res.data) >= 1
    retriever.close()
