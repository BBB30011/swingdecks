"""
Tests for Gate 8 Dual Point-In-Time (PIT) Forensic Precision
============================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.knowledge_data_platform import KnowledgeDataPlatform


def test_gate8_market_vs_system_pit_boundaries():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=1)
    
    for r in records:
        # Verify Market PIT: available_at <= T_decision
        # System PIT: observed_at <= T_decision
        assert r.market_pit_status == "PIT_SAFE"
        assert r.system_pit_status == "PIT_SAFE"
        assert r.published_at <= r.available_at <= r.observed_at
