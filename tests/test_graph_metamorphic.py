import pytest
from datetime import datetime
from core.intelligence_models import (
    Entity, EntityRelationship, InformationEvent, Exposure, MechanismHypothesis
)
from core.intelligence_graph import IntelligenceGraphEngine

@pytest.fixture
def graph():
    return IntelligenceGraphEngine(":memory:")

def test_duplicate_source(graph):
    # Adding duplicate article must not create independent catalyst
    info = InformationEvent(
        information_id="INFO_01",
        source_id="SRC_01",
        source_type="NEWS",
        source_url_or_reference="http://a",
        publisher="PUB",
        published_at="2026-01-01T00:00:00Z",
        available_at="2026-01-01T00:00:00Z",
        captured_at="2026-01-01T00:00:00Z",
        title="Title", summary="Sum", claim="Claim", information_type="CORP",
        topic="TOPIC", subtopic="SUB"
    )
    graph.insert_information(info)
    graph.insert_information(info)
    res = graph.conn.execute("SELECT COUNT(*) FROM information WHERE information_id='INFO_01'").fetchone()[0]
    assert res == 1

def test_alias_addition(graph):
    # Adding valid alias must not create duplicate entity
    ent = Entity(
        entity_id="E1",
        canonical_name="BBCA",
        entity_type="COMPANY",
        aliases=["BCA"]
    )
    graph.insert_entity(ent)
    
    ent.aliases.append("Bank Central Asia")
    graph.insert_entity(ent)
    
    res = graph.conn.execute("SELECT COUNT(*) FROM entities WHERE entity_id='E1'").fetchone()[0]
    assert res == 1
    
    match = graph.resolve_entity("Bank Central Asia")
    assert match['entity_id'] == "E1"
    assert match['match_type'] == "MATCH_ALIAS"

def test_future_event_replay(graph):
    # Adding future information must not change historical replay
    rel1 = EntityRelationship(
        relationship_id="R1", source_entity="A", target_entity="B",
        relationship_type="OWNS", valid_from="2025-01-01T00:00:00Z",
        valid_to="2025-12-31T23:59:59Z"
    )
    rel2 = EntityRelationship(
        relationship_id="R2", source_entity="A", target_entity="C",
        relationship_type="OWNS", valid_from="2026-01-01T00:00:00Z",
        valid_to=None
    )
    graph.insert_relationship(rel1)
    graph.insert_relationship(rel2)
    
    # Replay at T_decision = 2025-06-01
    rels = graph.get_related_entities("A", "2025-06-01T00:00:00Z")
    assert len(rels) == 1
    assert rels[0]['entity'] == "B"

def test_relationship_versioning(graph):
    # Adding valid new relationship version must change only applicable temporal windows
    rel = EntityRelationship(
        relationship_id="R1", source_entity="X", target_entity="Y",
        relationship_type="SUPPLIER_OF", valid_from="2020-01-01T00:00:00Z",
        valid_to="2022-01-01T00:00:00Z"
    )
    graph.insert_relationship(rel)
    
    rel_new = EntityRelationship(
        relationship_id="R2", source_entity="X", target_entity="Z",
        relationship_type="SUPPLIER_OF", valid_from="2022-01-01T00:00:01Z",
        valid_to=None
    )
    graph.insert_relationship(rel_new)
    
    assert graph.get_related_entities("X", "2021-01-01T00:00:00Z")[0]['entity'] == "Y"
    assert graph.get_related_entities("X", "2023-01-01T00:00:00Z")[0]['entity'] == "Z"

def test_multi_hop_traversal(graph):
    # A -> B -> C -> D
    graph.insert_relationship(EntityRelationship("R1", "A", "B", "OWNS", "2020-01-01T00:00:00Z"))
    graph.insert_relationship(EntityRelationship("R2", "B", "C", "OWNS", "2020-01-01T00:00:00Z"))
    graph.insert_relationship(EntityRelationship("R3", "C", "D", "SUPPLIES", "2020-01-01T00:00:00Z"))
    
    path = graph.find_shortest_evidence_path("A", "D", "2021-01-01T00:00:00Z")
    assert path == ["A", "B", "C", "D"]
