"""
Tests for Gate 8 Deterministic Rebuild and Idempotent Execution
===============================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine


def test_gate8_deterministic_replay_and_rebuild():
    engine_a = Gate8ScaleCoverageEngine(db_path=":memory:")
    records_a = engine_a.load_canonical_scale_dataset(level=2)
    manifest_a = engine_a.generate_manifest()
    
    engine_b = Gate8ScaleCoverageEngine(db_path=":memory:")
    records_b = engine_b.load_canonical_scale_dataset(level=2)
    manifest_b = engine_b.generate_manifest()
    
    assert len(records_a) == len(records_b)
    assert manifest_a.dataset_hash == manifest_b.dataset_hash
    assert manifest_a.manifest_hash == manifest_b.manifest_hash
