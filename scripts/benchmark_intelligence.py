"""
Benchmark performance script for Gate 3 & Gate 7 metrics.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))
import time
import numpy as np
import duckdb
from datetime import datetime, timezone
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import EntityRecord, EntityType, EntityRelationshipRecord, RelationshipType

def run_benchmarks():
    platform = KnowledgeDataPlatform(":memory:")
    
    # Setup test graph
    platform.register_entity(EntityRecord(entity_id="ENT_ADRO", canonical_name="Adaro Energy", entity_type=EntityType.COMPANY))
    platform.register_entity(EntityRecord(entity_id="ENT_SECTOR", canonical_name="Coal Sector", entity_type=EntityType.SECTOR))
    platform.register_entity(EntityRecord(entity_id="ENT_MEMR", canonical_name="ESDM Ministry", entity_type=EntityType.MINISTRY))
    platform.insert_entity_identifier("ENT_ADRO", "IDX_TICKER", "ADRO")
    platform.insert_entity_alias("ENT_ADRO", "Adaro")
    
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_1", subject_entity_id="ENT_MEMR", relationship_type=RelationshipType.REGULATES,
        object_entity_id="ENT_SECTOR", valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))
    platform.register_relationship(EntityRelationshipRecord(
        relationship_id="REL_2", subject_entity_id="ENT_ADRO", relationship_type=RelationshipType.OPERATES_IN,
        object_entity_id="ENT_SECTOR", valid_from="2020-01-01T00:00:00Z", observed_at="2020-01-01T00:00:00Z"
    ))
    
    retriever = KnowledgeRetrievalEngine(platform)
    N = 100

    benchmarks = {}

    # 1. Entity Lookup
    t_ent = []
    for _ in range(N):
        t0 = time.perf_counter()
        platform.resolve_entity("ADRO", "IDX_TICKER")
        t_ent.append((time.perf_counter() - t0) * 1000)
    benchmarks["Entity Lookup"] = t_ent

    # 2. Information Lookup
    t_info = []
    for _ in range(N):
        t0 = time.perf_counter()
        retriever.search_information(query="ADRO", as_of="2024-01-01T00:00:00Z")
        t_info.append((time.perf_counter() - t0) * 1000)
    benchmarks["Information Lookup"] = t_info

    # 3. PIT Retrieval
    t_pit = []
    for _ in range(N):
        t0 = time.perf_counter()
        retriever.retrieve("ENT_ADRO", as_of="2024-01-01T00:00:00Z")
        t_pit.append((time.perf_counter() - t0) * 1000)
    benchmarks["PIT Retrieval"] = t_pit

    # 4. 3-hop Traversal
    t_hop3 = []
    for _ in range(N):
        t0 = time.perf_counter()
        platform.traverse_multi_hop_exposure("ENT_MEMR", target_entity_id="ENT_ADRO", max_hops=3)
        t_hop3.append((time.perf_counter() - t0) * 1000)
    benchmarks["3-Hop Exposure Traversal"] = t_hop3

    # 5. 5-hop Bounded Traversal
    t_hop5 = []
    for _ in range(N):
        t0 = time.perf_counter()
        platform.traverse_multi_hop_exposure("ENT_MEMR", max_hops=5)
        t_hop5.append((time.perf_counter() - t0) * 1000)
    benchmarks["5-Hop Bounded Traversal"] = t_hop5

    # 6. Agent 2 Context Retrieval (World Snapshot)
    t_a2 = []
    for _ in range(N):
        t0 = time.perf_counter()
        retriever.get_world_snapshot("ENT_ADRO", "2024-01-01T00:00:00Z")
        t_a2.append((time.perf_counter() - t0) * 1000)
    benchmarks["Agent 2 Context Retrieval"] = t_a2

    # 7. ThesisDelta Retrieval
    t_td = []
    for _ in range(N):
        t0 = time.perf_counter()
        retriever.get_information_delta("ENT_ADRO", "2024-01-01T00:00:00Z", "2024-06-01T00:00:00Z")
        t_td.append((time.perf_counter() - t0) * 1000)
    benchmarks["ThesisDelta"] = t_td

    print(f"{'Operation':<32} | {'N':<5} | {'p50 (ms)':<9} | {'p95 (ms)':<9} | {'p99 (ms)':<9} | {'min (ms)':<9} | {'max (ms)':<9}")
    print("-" * 95)
    for name, latencies in benchmarks.items():
        arr = np.array(latencies)
        p50 = np.percentile(arr, 50)
        p95 = np.percentile(arr, 95)
        p99 = np.percentile(arr, 99)
        min_v = np.min(arr)
        max_v = np.max(arr)
        print(f"{name:<32} | {N:<5} | {p50:<9.3f} | {p95:<9.3f} | {p99:<9.3f} | {min_v:<9.3f} | {max_v:<9.3f}")

if __name__ == "__main__":
    run_benchmarks()
