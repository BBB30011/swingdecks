"""
Tests for Gate 8 UNKNOWN and Missingness Integrity
==================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine


def test_gate8_unknown_preservation():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    # Check that missing event times remain explicitly None rather than fabricated
    unk_times = [r for r in records if r.event_time is None]
    assert len(unk_times) > 0
    for r in unk_times:
        assert r.event_time is None
        # Must not fabricate a timestamp
        assert r.published_at is not None
