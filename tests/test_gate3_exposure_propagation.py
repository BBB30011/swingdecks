"""
SwingDeck — Gate 3 Multi-Hop Economic Transmission & Exposure Propagation Test Suite
Validates:
- Golden Cases A through H (Policy, Commodity, Regulatory, Ownership, Supply-chain, Contradictions, Future Injection, Ambiguity)
- Adversarial attack and edge cases (Cycles, Future leaks, MNPI firewall, Explosion prevention, Duplicate collapse, Rebuild determinism)
"""

import pytest
import time
from datetime import datetime, timezone
from pathlib import Path

from core.data_platform_schemas import (
    EntityRecord, EntityRelationshipRecord, EvidenceRecord, SourceRecord,
    PolicyRecord, ExposureRecord, ExposurePath, TransmissionHop,
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    AccessClass, TimestampDerivationMethod, TemporalConfidence
)
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine

@pytest.fixture
def gate3_platform(tmp_path):
    db_file = str(tmp_path / "gate3_test.duckdb")
    platform = KnowledgeDataPlatform(db_file)
    
    # 1. Sources
    platform.conn.execute("""
        INSERT INTO sources VALUES
        ('SRC_GOV', 'Government Gazette', 'Gov of Indonesia', 'GOVERNMENT', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('SRC_IDX', 'IDX Disclosure Feed', 'BEI', 'EXCHANGE', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('SRC_OJK', 'OJK Regulatory Circular', 'OJK', 'REGULATOR', 'ID', '', '', 'OFFICIAL', 'ACTIVE', 'PUBLIC', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z');
    """)

    # 2. Base Entities
    entities = [
        EntityRecord(entity_id="ENT_MEMR", canonical_name="Ministry of Energy and Mineral Resources", entity_type=EntityType.MINISTRY),
        EntityRecord(entity_id="ENT_OJK", canonical_name="Otoritas Jasa Keuangan", entity_type=EntityType.REGULATOR),
        EntityRecord(entity_id="ENT_COAL_COMMODITY", canonical_name="Thermal Coal", entity_type=EntityType.COMMODITY),
        EntityRecord(entity_id="ENT_COAL_SECTOR", canonical_name="Coal Mining Sector", entity_type=EntityType.SECTOR),
        EntityRecord(entity_id="ENT_FINANCIAL_SECTOR", canonical_name="Financial Services Sector", entity_type=EntityType.SECTOR),
        EntityRecord(entity_id="ENT_ENERGY_SECTOR", canonical_name="Energy & Resources Sector", entity_type=EntityType.SECTOR),
        EntityRecord(entity_id="ENT_ADRO", canonical_name="PT Adaro Energy Indonesia Tbk", entity_type=EntityType.COMPANY),
        EntityRecord(entity_id="ENT_AADI", canonical_name="PT Adaro Andalan Indonesia Tbk", entity_type=EntityType.SUBSIDIARY),
        EntityRecord(entity_id="ENT_PTBA", canonical_name="PT Bukit Asam Tbk", entity_type=EntityType.STATE_OWNED_ENTITY),
        EntityRecord(entity_id="ENT_BBCA", canonical_name="PT Bank Central Asia Tbk", entity_type=EntityType.BANK),
        EntityRecord(entity_id="ENT_DJARUM", canonical_name="Djarum Group", entity_type=EntityType.HOLDING_COMPANY),
        EntityRecord(entity_id="ENT_NICKEL_MINER", canonical_name="PT Vale Indonesia Tbk", entity_type=EntityType.COMPANY),
        EntityRecord(entity_id="ENT_SMELTER", canonical_name="PT Huayue Nickel Smelter", entity_type=EntityType.COMPANY),
        EntityRecord(entity_id="ENT_BATTERY_CO", canonical_name="PT Industri Baterai Indonesia", entity_type=EntityType.STATE_OWNED_ENTITY)
    ]
    for e in entities:
        platform.register_entity(e)

    # 3. Base Evidences
    evidences = [
        EvidenceRecord(evidence_id="EV_PP26", information_id="INFO_PP26", source_id="SRC_GOV", document_id="DOC_PP26",
                       content_hash="h1", published_at="2024-01-01T00:00:00Z", available_at="2024-01-01T00:00:00Z",
                       observed_at="2024-01-01T00:00:00Z", access_class=AccessClass.PUBLIC),
        EvidenceRecord(evidence_id="EV_OJK_REG", information_id="INFO_OJK", source_id="SRC_OJK", document_id="DOC_OJK",
                       content_hash="h2", published_at="2024-01-01T00:00:00Z", available_at="2024-01-01T00:00:00Z",
                       observed_at="2024-01-01T00:00:00Z", access_class=AccessClass.PUBLIC),
        EvidenceRecord(evidence_id="EV_DJARUM", information_id="INFO_DJARUM", source_id="SRC_IDX", document_id="DOC_DJARUM",
                       content_hash="h3", published_at="2024-01-01T00:00:00Z", available_at="2024-01-01T00:00:00Z",
                       observed_at="2024-01-01T00:00:00Z", access_class=AccessClass.PUBLIC),
        EvidenceRecord(evidence_id="EV_SUPPLY", information_id="INFO_SUPPLY", source_id="SRC_IDX", document_id="DOC_SUPPLY",
                       content_hash="h4", published_at="2024-01-01T00:00:00Z", available_at="2024-01-01T00:00:00Z",
                       observed_at="2024-01-01T00:00:00Z", access_class=AccessClass.PUBLIC)
    ]
    for ev in evidences:
        platform.insert_evidence(ev)

    # 4. Base Relationships
    rels = [
        # Policy / Regulator to Sector
        EntityRelationshipRecord(relationship_id="REL_MEMR_COAL_SECTOR", subject_entity_id="ENT_MEMR", relationship_type=RelationshipType.REGULATES, object_entity_id="ENT_COAL_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.95),
        EntityRelationshipRecord(relationship_id="REL_OJK_FIN_SECTOR", subject_entity_id="ENT_OJK", relationship_type=RelationshipType.REGULATES, object_entity_id="ENT_FINANCIAL_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.95),
        EntityRelationshipRecord(relationship_id="REL_COAL_COMM_ENERGY", subject_entity_id="ENT_COAL_COMMODITY", relationship_type=RelationshipType.SUPPLIES, object_entity_id="ENT_ENERGY_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.90),
        
        # Sector to Company (Company operates in Sector)
        EntityRelationshipRecord(relationship_id="REL_ADRO_COAL_SECTOR", subject_entity_id="ENT_ADRO", relationship_type=RelationshipType.OPERATES_IN, object_entity_id="ENT_COAL_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.90),
        EntityRelationshipRecord(relationship_id="REL_PTBA_ENERGY_SECTOR", subject_entity_id="ENT_PTBA", relationship_type=RelationshipType.OPERATES_IN, object_entity_id="ENT_ENERGY_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.90),
        EntityRelationshipRecord(relationship_id="REL_BBCA_FIN_SECTOR", subject_entity_id="ENT_BBCA", relationship_type=RelationshipType.OPERATES_IN, object_entity_id="ENT_FINANCIAL_SECTOR", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.95),
        
        # Ownership / Control
        EntityRelationshipRecord(relationship_id="REL_DJARUM_BBCA", subject_entity_id="ENT_DJARUM", relationship_type=RelationshipType.CONTROLS, object_entity_id="ENT_BBCA", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.99),
        EntityRelationshipRecord(relationship_id="REL_ADRO_AADI", subject_entity_id="ENT_ADRO", relationship_type=RelationshipType.OWNS, object_entity_id="ENT_AADI", valid_from="2024-01-01T00:00:00Z", valid_to="2024-11-30T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.99),
        
        # Supply Chain: Nickel Miner -> Smelter -> Battery Co
        EntityRelationshipRecord(relationship_id="REL_NICKEL_SMELTER", subject_entity_id="ENT_NICKEL_MINER", relationship_type=RelationshipType.SUPPLIES, object_entity_id="ENT_SMELTER", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.85),
        EntityRelationshipRecord(relationship_id="REL_SMELTER_BATTERY", subject_entity_id="ENT_SMELTER", relationship_type=RelationshipType.SUPPLIES, object_entity_id="ENT_BATTERY_CO", valid_from="2024-01-01T00:00:00Z", observed_at="2024-01-01T00:00:00Z", confidence=0.80)
    ]
    for r in rels:
        ev_id = "EV_PP26"
        if "OJK" in r.relationship_id: ev_id = "EV_OJK_REG"
        elif "DJARUM" in r.relationship_id: ev_id = "EV_DJARUM"
        elif "SMELTER" in r.relationship_id or "NICKEL" in r.relationship_id: ev_id = "EV_SUPPLY"
        platform.register_relationship(r, evidence_id=ev_id)

    # 5. Base Exposures (Economic Channels)
    platform.conn.execute("""
        INSERT INTO exposures VALUES
        ('EXP_COAL_ROYALTY', 'ENT_COAL_SECTOR', 'INFO_PP26', 'TAX', 'INDIRECT', 'NEGATIVE', 'HIGH', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_FIN_REG', 'ENT_FINANCIAL_SECTOR', 'INFO_OJK', 'REGULATORY_COST', 'DIRECT', 'NEUTRAL', 'MEDIUM', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_COAL_PRICE', 'ENT_ENERGY_SECTOR', 'INFO_PP26', 'COMMODITY_PRICE', 'DIRECT', 'POSITIVE', 'HIGH', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_ADRO', 'ENT_ADRO', 'INFO_PP26', 'REGULATORY_COST', 'DIRECT', 'NEGATIVE', 'HIGH', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_BBCA', 'ENT_BBCA', 'INFO_OJK', 'CREDIT', 'DIRECT', 'POSITIVE', 'MEDIUM', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED'),
        ('EXP_BATTERY', 'ENT_BATTERY_CO', 'INFO_SUPPLY', 'INPUT_COST', 'INDIRECT', 'NEGATIVE', 'HIGH', '2024-01-01T00:00:00Z', NULL, 'SUPPORTED');
    """)

    return platform

# =====================================================================
# 1. GOLDEN CASES (A THROUGH H)
# =====================================================================

def test_golden_case_a_policy_sector_company(gate3_platform):
    """Case A: Policy/Ministry -> Sector -> Company (MEMR -> Coal Sector -> ADRO)."""
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_MEMR",
        target_entity_id="ENT_ADRO",
        as_of="2024-06-01T00:00:00Z",
        max_hops=3
    )
    assert len(paths) == 1
    path = paths[0]
    assert path.hop_count == 2
    assert path.relationship_sequence == ["REGULATES", "OPERATES_IN"]
    assert path.cumulative_confidence == pytest.approx(0.95 * 0.90, rel=1e-3)
    assert "ENT_MEMR" in path.economic_mechanism_description
    assert "ENT_ADRO" in path.economic_mechanism_description

def test_golden_case_b_commodity_sector_company(gate3_platform):
    """Case B: Commodity -> Sector -> Company (Thermal Coal -> Energy Sector -> PTBA)."""
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_COAL_COMMODITY",
        target_entity_id="ENT_PTBA",
        as_of="2024-06-01T00:00:00Z",
        max_hops=3
    )
    assert len(paths) == 1
    path = paths[0]
    assert path.hop_count == 2
    assert path.relationship_sequence == ["SUPPLIES", "OPERATES_IN"]
    assert path.cumulative_confidence == pytest.approx(0.90 * 0.90, rel=1e-3)

def test_golden_case_c_regulatory_sector_company(gate3_platform):
    """Case C: Regulatory Action -> Sector -> Company (OJK -> Financial Sector -> BBCA)."""
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_OJK",
        target_entity_id="ENT_BBCA",
        as_of="2024-06-01T00:00:00Z",
        max_hops=3
    )
    assert len(paths) == 1
    path = paths[0]
    assert path.hop_count == 2
    assert path.relationship_sequence == ["REGULATES", "OPERATES_IN"]
    assert "EV_OJK_REG" in path.evidence_sequence

def test_golden_case_d_ownership_control_relationship(gate3_platform):
    """Case D: Ownership/Control relationship (Djarum -> BBCA, ADRO -> AADI)."""
    # 1-hop Djarum -> BBCA
    p1 = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_DJARUM",
        target_entity_id="ENT_BBCA",
        as_of="2024-06-01T00:00:00Z",
        max_hops=2
    )
    assert len(p1) == 1
    assert p1[0].hop_count == 1
    assert p1[0].relationship_sequence == ["CONTROLS"]

    # 1-hop ADRO -> AADI before spinoff date
    p2 = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_ADRO",
        target_entity_id="ENT_AADI",
        as_of="2024-06-01T00:00:00Z",
        max_hops=2
    )
    assert len(p2) == 1
    assert p2[0].relationship_sequence == ["OWNS"]

    # Post spinoff date ADRO -> AADI must return 0 active paths
    p2_post = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_ADRO",
        target_entity_id="ENT_AADI",
        as_of="2024-12-01T00:00:00Z",
        max_hops=2
    )
    assert len(p2_post) == 0

def test_golden_case_e_supply_chain_exposure(gate3_platform):
    """Case E: Supply-chain multi-hop (Nickel Miner -> Smelter -> Battery Co)."""
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_NICKEL_MINER",
        target_entity_id="ENT_BATTERY_CO",
        as_of="2024-06-01T00:00:00Z",
        max_hops=3
    )
    assert len(paths) == 1
    path = paths[0]
    assert path.hop_count == 2
    assert path.relationship_sequence == ["SUPPLIES", "SUPPLIES"]
    assert path.cumulative_confidence == pytest.approx(0.85 * 0.80, rel=1e-3)

def test_golden_case_f_contradictory_exposure_evidence(gate3_platform):
    """Case F: Injected contradictory edge does not crash traversal; returns valid supported path."""
    gate3_platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_BAD_CONTRADICT', 'ENT_MEMR', 'SUPPLIES', 'ENT_ADRO', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'INACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 0.1);
    """)
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_MEMR",
        target_entity_id="ENT_ADRO",
        as_of="2024-06-01T00:00:00Z"
    )
    assert len(paths) == 1
    assert paths[0].relationship_sequence == ["REGULATES", "OPERATES_IN"]

def test_golden_case_g_future_information_injection(gate3_platform):
    """Case G: Future relationship injected at T+30d is invisible at decision time T."""
    gate3_platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_FUTURE_MERGER', 'ENT_ADRO', 'ACQUIRES', 'ENT_PTBA', '2024-12-01T00:00:00Z', NULL, '2024-12-01T00:00:00Z', 'ACTIVE', 1, '2024-12-01T00:00:00Z', '2024-12-01T00:00:00Z', 0.99);
    """)
    # Query at T = 2024-06-01
    paths_early = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_ADRO",
        target_entity_id="ENT_PTBA",
        as_of="2024-06-01T00:00:00Z"
    )
    assert len(paths_early) == 0

    # Query at T = 2024-12-15 (future)
    paths_future = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_ADRO",
        target_entity_id="ENT_PTBA",
        as_of="2024-12-15T00:00:00Z"
    )
    assert len(paths_future) == 1
    assert paths_future[0].relationship_sequence == ["ACQUIRES"]

def test_golden_case_h_ambiguous_relationship(gate3_platform):
    """Case H: Ambiguous or unknown relationship preserved without speculative fabrication."""
    gate3_platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_UNKNOWN_EDGE', 'ENT_DJARUM', 'RELATED_TO', 'ENT_ADRO', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 0.50);
    """)
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_DJARUM",
        target_entity_id="ENT_ADRO",
        as_of="2024-06-01T00:00:00Z",
        allowed_relationship_types=["OWNS", "CONTROLS", "SUPPLIES"]
    )
    # Allowed edge whitelist excludes RELATED_TO
    assert len(paths) == 0

# =====================================================================
# 2. ADVERSARIAL & INVARIANT TESTS
# =====================================================================

def test_adversarial_cyclic_graph_termination(gate3_platform):
    """Attack: Cyclic relationships A -> B -> C -> A must terminate without hanging."""
    gate3_platform.conn.execute("""
        INSERT INTO entities VALUES
        ('ENT_CYCLE_A', 'Cycle A', 'COMPANY', 'ID', 'ACTIVE', '1970-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('ENT_CYCLE_B', 'Cycle B', 'COMPANY', 'ID', 'ACTIVE', '1970-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
        ('ENT_CYCLE_C', 'Cycle C', 'COMPANY', 'ID', 'ACTIVE', '1970-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z');
        
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_C_1', 'ENT_CYCLE_A', 'SUPPLIES', 'ENT_CYCLE_B', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 1.0),
        ('REL_C_2', 'ENT_CYCLE_B', 'SUPPLIES', 'ENT_CYCLE_C', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 1.0),
        ('REL_C_3', 'ENT_CYCLE_C', 'SUPPLIES', 'ENT_CYCLE_A', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 1.0);
    """)
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_CYCLE_A",
        max_hops=5
    )
    # Must terminate cleanly and return acyclic paths
    assert len(paths) == 2
    for p in paths:
        assert p.origin_entity != p.target_entity

def test_adversarial_restricted_mnpi_firewall(gate3_platform):
    """Attack: Restricted MNPI edge must be blocked from exposure traversal."""
    gate3_platform.conn.execute("""
        INSERT INTO evidence VALUES
        ('EV_MNPI_SECRET', 'INFO_M', 'SRC_GOV', 'DOC_M', 'CLAIM_M', 'EXCERPT', 'Secret Merger', 'hash_m', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 'EXCHANGE_METADATA', 'SOURCE_ARTICLE_METADATA', 'EXACT', 'RESTRICTED', 'NATURAL', 'VERIFIED', '2024-01-01T00:00:00Z');
        
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_SECRET_MERGER', 'ENT_BBCA', 'ACQUIRES', 'ENT_PTBA', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 0.99);
        
        INSERT INTO relationship_evidence (relationship_evidence_id, relationship_id, evidence_id, evidence_role, support_status, created_at) VALUES
        ('RELEV_MNPI', 'REL_SECRET_MERGER', 'EV_MNPI_SECRET', 'PRIMARY', 'SUPPORTED', '2024-01-01T00:00:00Z');
    """)
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_BBCA",
        target_entity_id="ENT_PTBA",
        as_of="2024-06-01T00:00:00Z"
    )
    # Restricted evidence causes fail-closed exclusion
    assert len(paths) == 0

def test_adversarial_duplicate_path_collapse(gate3_platform):
    """Attack: Duplicate parallel paths collapse to highest confidence path."""
    gate3_platform.conn.execute("""
        INSERT INTO entity_relationships (relationship_id, subject_entity_id, relationship_type, object_entity_id, valid_from, valid_to, observed_at, status, source_priority, created_at, updated_at, confidence) VALUES
        ('REL_DUP_LOW', 'ENT_MEMR', 'REGULATES', 'ENT_COAL_SECTOR', '2024-01-01T00:00:00Z', NULL, '2024-01-01T00:00:00Z', 'ACTIVE', 1, '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z', 0.60);
    """)
    paths = gate3_platform.traverse_multi_hop_exposure(
        origin_entity_id="ENT_MEMR",
        target_entity_id="ENT_ADRO",
        as_of="2024-06-01T00:00:00Z"
    )
    assert len(paths) == 1
    # Retains the 0.95 * 0.90 = 0.855 path rather than 0.60 * 0.90 = 0.54
    assert paths[0].cumulative_confidence == pytest.approx(0.855, rel=1e-3)

def test_adversarial_rebuild_determinism(gate3_platform):
    """Verifies that rebuilding derived indexes is fully deterministic."""
    r1 = gate3_platform.rebuild_derived_indexes()
    r2 = gate3_platform.rebuild_derived_indexes()
    assert r1 == r2
    assert r1["neighborhood_records"] > 0
    assert r1["exposure_index_records"] > 0
