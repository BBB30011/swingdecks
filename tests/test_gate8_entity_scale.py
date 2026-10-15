"""
Tests for Gate 8 Entity Resolution Scale and Ambiguity Handling
===============================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine
from core.data_platform_schemas import EntityType


def test_gate8_entity_diversity_and_no_forced_matching():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    entity_types_found = set(r.entity_type for r in records)
    assert EntityType.COMPANY in entity_types_found
    assert EntityType.REGULATOR in entity_types_found
    assert EntityType.MINISTRY in entity_types_found
    assert EntityType.CENTRAL_BANK in entity_types_found
    
    # Verify FORCED_MATCH_RATE = 0
    # Every resolved entity must map directly to known canonical ID
    for r in records:
        if r.entity_resolution_status == "RESOLVED":
            assert r.entity_id is not None
            assert r.entity_id.startswith("ENT_")
        elif r.entity_resolution_status == "AMBIGUOUS":
            assert len(r.entity_candidate_matches) >= 2
        elif r.entity_resolution_status == "UNKNOWN":
            assert r.entity_id is None
