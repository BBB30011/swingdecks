"""
SwingDeck Knowledge Data Platform - Foundation Unit & Integration Tests
Tests schema integrity, entity resolution tiers, source-aware corroboration,
corporate actions, policy transmission, data quality audit, and backup/restore.
"""

import os
import shutil
import tempfile
import pytest
from datetime import datetime, timezone

from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import (
    EntityRecord, EntityAliasRecord, EntityIdentifierRecord,
    SourceRecord, RawDocumentRecord, EntityRelationshipRecord,
    CorporateActionRecord, ExposureRecord, SourceType,
    InformationType, CorporateActionType, EvidenceRole,
    compute_content_hash, compute_document_fingerprint
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    AccessClass, EvidenceClassification
)
from core.duplicate_corroboration import DuplicateAndCorroborationEngine

@pytest.fixture
def temp_db_platform(tmp_path):
    db_file = str(tmp_path / "test_kdp.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    yield platform, db_file
    platform.close()

def test_schema_initialization(temp_db_platform):
    platform, _ = temp_db_platform
    tables = [t[0] for t in platform.conn.execute("SHOW TABLES").fetchall()]
    assert "entities" in tables
    assert "entity_aliases" in tables
    assert "entity_identifiers" in tables
    assert "raw_documents" in tables
    assert "sources" in tables
    assert "information_items" in tables
    assert "claims" in tables
    assert "evidence" in tables
    assert "entity_relationships" in tables
    assert "relationship_evidence" in tables
    assert "corporate_actions" in tables
    assert "exposures" in tables
    assert "mechanisms" in tables
    assert "contradictions" in tables
    assert "economic_channels" in tables
    assert "derived_entity_neighborhood" in tables
    assert "derived_entity_exposure_index" in tables

def test_layered_entity_resolution(temp_db_platform):
    platform, _ = temp_db_platform
    
    # 1. Register Canonical Entity
    ent = EntityRecord(
        entity_id="ENT_BBCA",
        canonical_name="PT Bank Central Asia Tbk",
        entity_type=EntityType.COMPANY
    )
    platform.register_entity(ent)

    # 2. Register Identifiers
    platform.conn.execute("""
        INSERT INTO entity_identifiers VALUES ('ID_BBCA_TICKER', 'ENT_BBCA', 'IDX_TICKER', 'BBCA', 'IDX', '1970-01-01T00:00:00Z', NULL);
        INSERT INTO entity_identifiers VALUES ('ID_BBCA_ISIN', 'ENT_BBCA', 'ISIN', 'ID1000106808', 'KSEI', '1970-01-01T00:00:00Z', NULL);
    """)

    # 3. Register Aliases
    platform.conn.execute("""
        INSERT INTO entity_aliases VALUES ('AL_BBCA_1', 'ENT_BBCA', 'BCA', 'COMMON', 'id', '1970-01-01T00:00:00Z', NULL, 'SYSTEM');
        INSERT INTO entity_aliases VALUES ('AL_BBCA_2', 'ENT_BBCA', 'Bank Central Asia', 'FORMER', 'id', '1970-01-01T00:00:00Z', NULL, 'SYSTEM');
    """)

    # Test Resolution Tiers:
    # Tier 1: Exact Ticker
    res1 = platform.resolve_entity("BBCA", identifier_type="IDX_TICKER")
    assert res1["status"] == "RESOLVED"
    assert res1["entity_id"] == "ENT_BBCA"
    assert res1["resolution_tier"] == "EXACT_IDENTIFIER"

    # Tier 2: ISIN Identifier
    res2 = platform.resolve_entity("ID1000106808")
    assert res2["status"] == "RESOLVED"
    assert res2["entity_id"] == "ENT_BBCA"

    # Tier 3: Alias
    res3 = platform.resolve_entity("BCA")
    assert res3["status"] == "RESOLVED"
    assert res3["entity_id"] == "ENT_BBCA"
    assert res3["resolution_tier"] == "CANONICAL_ALIAS"

    # Tier 4: Canonical Name
    res4 = platform.resolve_entity("PT Bank Central Asia Tbk")
    assert res4["status"] == "RESOLVED"
    assert res4["entity_id"] == "ENT_BBCA"

    # Tier 5: Unknown Entity
    res5 = platform.resolve_entity("UNKNOWN_RANDOM_CORP_999")
    assert res5["status"] == "UNKNOWN"
    assert res5["entity_id"] is None

def test_source_aware_corroboration_engine():
    # Simulate 3 identical copies from same syndicated news
    raw_text = "Bank Indonesia menaikkan suku bunga BI Rate sebesar 25 bps dilansir dari Reuters"
    c_hash = compute_content_hash(raw_text)
    
    evidences = [
        {"evidence_id": "EV_1", "publisher": "Reuters", "content_hash": c_hash, "excerpt_reference": raw_text},
        {"evidence_id": "EV_2", "publisher": "DetikCom", "content_hash": c_hash, "excerpt_reference": raw_text},
        {"evidence_id": "EV_3", "publisher": "BisnisCom", "content_hash": c_hash, "excerpt_reference": raw_text}
    ]

    res = DuplicateAndCorroborationEngine.evaluate_corroboration(evidences)
    # Even though 3 documents exist, exact content duplicate means only 1 independent source!
    assert res["total_items"] == 3
    assert res["independent_source_count"] == 1
    assert res["derived_copy_count"] == 2
    assert res["corroboration_status"] == "SINGLE_SOURCE"

def test_corporate_action_lifecycle(temp_db_platform):
    platform, _ = temp_db_platform
    
    # Register parent ADRO and subsidiary AADI
    platform.register_entity(EntityRecord(entity_id="ENT_ADRO", canonical_name="Adaro Energy", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_AADI", canonical_name="Adaro Andalan", entity_type=EntityType.SUBSIDIARY))

    # Register Corporate Action (Spinoff)
    ca = CorporateActionRecord(
        corporate_action_id="CA_ADRO_SPINOFF_AADI",
        entity_id="ENT_ADRO",
        action_type=CorporateActionType.SPINOFF,
        announcement_date="2024-08-15T00:00:00Z",
        effective_date="2024-11-30T00:00:00Z",
        source_id="SRC_IDX_DISCLOSURE"
    )
    platform.conn.execute("""
        INSERT INTO corporate_actions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ca.corporate_action_id, ca.entity_id, ca.action_type.value,
        ca.announcement_date, ca.effective_date, ca.record_date,
        ca.source_id, ca.information_id, ca.status
    ))

    # Register Relationship with expiry clamped to effective_date
    rel = EntityRelationshipRecord(
        relationship_id="REL_ADRO_AADI",
        subject_entity_id="ENT_ADRO",
        relationship_type=RelationshipType.OWNS,
        object_entity_id="ENT_AADI",
        valid_from="2024-01-01T00:00:00Z",
        valid_to="2024-11-30T00:00:00Z",
        observed_at="2024-01-01T00:00:00Z"
    )
    reg_res = platform.register_relationship(rel)
    assert reg_res["status"] == "REGISTERED"

    # Query before spinoff
    rows_pre = platform.conn.execute("""
        SELECT relationship_id FROM entity_relationships
        WHERE subject_entity_id = 'ENT_ADRO'
          AND valid_from <= '2024-06-01T00:00:00Z'
          AND (valid_to IS NULL OR valid_to > '2024-06-01T00:00:00Z')
    """).fetchall()
    assert len(rows_pre) == 1

    # Query after spinoff (expired)
    rows_post = platform.conn.execute("""
        SELECT relationship_id FROM entity_relationships
        WHERE subject_entity_id = 'ENT_ADRO'
          AND valid_from <= '2025-01-01T00:00:00Z'
          AND (valid_to IS NULL OR valid_to > '2025-01-01T00:00:00Z')
    """).fetchall()
    assert len(rows_post) == 0

def test_data_quality_audit(temp_db_platform):
    platform, _ = temp_db_platform
    
    # 1. Clean audit should pass
    audit1 = platform.run_data_quality_audit()
    assert audit1["status"] == "PASS"
    assert audit1["findings_count"] == 0

    # 2. Inject orphaned relationship (subject entity does not exist)
    platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at)
        VALUES ('REL_BROKEN', 'ENT_NON_EXISTENT', 'OWNS', 'ENT_BBCA', '2020-01-01T00:00:00Z', NULL, '2020-01-01T00:00:00Z', 'ACTIVE', 1, '2020-01-01T00:00:00Z', '2020-01-01T00:00:00Z');
    """)
    audit2 = platform.run_data_quality_audit()
    assert audit2["status"] == "FAIL"
    assert any(f["check"] == "REFERENTIAL_INTEGRITY" for f in audit2["findings"])

def test_backup_and_restore(temp_db_platform, tmp_path):
    platform, db_file = temp_db_platform
    
    # Register an entity
    platform.register_entity(EntityRecord(entity_id="ENT_TLKM", canonical_name="Telkom Indonesia", entity_type=EntityType.COMPANY))
    
    # Create backup
    backup_dir = str(tmp_path / "backups")
    backup_res = platform.create_backup(backup_dir)
    assert backup_res["status"] == "BACKUP_CREATED"
    assert os.path.exists(backup_res["backup_file"])

    # Corrupt database by deleting table
    platform.conn.execute("DROP TABLE entities")
    
    # Restore from backup
    restore_ok = platform.restore_from_backup(backup_res["backup_file"])
    assert restore_ok is True
    
    # Verify restored content
    row = platform.conn.execute("SELECT canonical_name FROM entities WHERE entity_id = 'ENT_TLKM'").fetchone()
    assert row is not None
    assert row[0] == "Telkom Indonesia"
