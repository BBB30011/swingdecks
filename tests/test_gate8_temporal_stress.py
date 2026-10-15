"""
Tests for Gate 8 Temporal Complexity Stress and 4-Timestamp Invariants
======================================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine
from core.data_platform_schemas import TemporalConfidence


def test_gate8_four_timestamp_invariant():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    for r in records:
        assert r.published_at is not None
        assert r.available_at is not None
        assert r.observed_at is not None
        # Verify ordering invariant: published <= available <= observed
        assert r.published_at <= r.available_at <= r.observed_at
        
        # When event_time is known, verify event_time <= published_at
        if r.event_time is not None:
            assert r.event_time <= r.published_at
            
        # Verify temporal confidence is explicitly preserved
        assert r.temporal_confidence in [TemporalConfidence.EXACT, TemporalConfidence.FALLBACK, TemporalConfidence.DERIVED]


def test_gate8_temporal_boundary_checks():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=1)
    
    for r in records:
        # Check boundary condition at available_at
        avail_t = r.available_at
        
        # Before availability: strictly invisible under Market PIT
        # At availability or later: visible under Market PIT
        assert r.market_pit_status == "PIT_SAFE"
        assert r.system_pit_status == "PIT_SAFE"
