import pytest
from core.intelligence_models import Entity, EntityRelationship
from core.intelligence_graph import IntelligenceGraphEngine

@pytest.fixture
def graph():
    return IntelligenceGraphEngine(":memory:")

def test_no_unsupported_relationship(graph):
    rel = EntityRelationship(
        relationship_id="REL_001",
        source_entity="A",
        target_entity="B",
        relationship_type="OWNS",
        valid_from="2026-01-01T00:00:00Z",
        status="UNSUPPORTED",
        evidence=""
    )
    graph.insert_relationship(rel)
    count = graph.conn.execute("SELECT COUNT(*) FROM relationships WHERE relationship_id='REL_001'").fetchone()[0]
    assert count == 0  # Should not insert unsupported relationships

def test_pit_relationship_resolution(graph):
    rel1 = EntityRelationship(
        relationship_id="REL_002",
        source_entity="ENT_A",
        target_entity="ENT_B",
        relationship_type="SUPPLIER_OF",
        valid_from="2025-01-01T00:00:00Z",
        valid_to="2026-06-01T00:00:00Z",
        status="SUPPORTED"
    )
    rel2 = EntityRelationship(
        relationship_id="REL_003",
        source_entity="ENT_A",
        target_entity="ENT_C",
        relationship_type="SUPPLIER_OF",
        valid_from="2026-06-01T00:00:00Z",
        valid_to=None,
        status="SUPPORTED"
    )
    graph.insert_relationship(rel1)
    graph.insert_relationship(rel2)

    # At 2026-05-01, ENT_A is supplier of ENT_B
    rels_may = graph.get_related_entities("ENT_A", "2026-05-01T00:00:00Z")
    assert len(rels_may) == 1
    assert rels_may[0]['entity'] == "ENT_B"

    # At 2026-07-01, ENT_A is supplier of ENT_C
    rels_jul = graph.get_related_entities("ENT_A", "2026-07-01T00:00:00Z")
    assert len(rels_jul) == 1
    assert rels_jul[0]['entity'] == "ENT_C"

def test_entity_resolution_alias(graph):
    ent = Entity(
        entity_id="ENT_COMP",
        canonical_name="PT Example Tbk",
        entity_type="COMPANY",
        aliases=["Example", "IDX:EXAMPLE"]
    )
    graph.insert_entity(ent)
    
    match1 = graph.resolve_entity("PT Example Tbk")
    assert match1['entity_id'] == "ENT_COMP"
    assert match1['match_type'] == "MATCH_EXACT"
    
    match2 = graph.resolve_entity("IDX:EXAMPLE")
    assert match2['entity_id'] == "ENT_COMP"
    assert match2['match_type'] == "MATCH_ALIAS"
    
    match3 = graph.resolve_entity("Unknown")
    assert match3 is None
