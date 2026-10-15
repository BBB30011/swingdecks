"""
Tests for Gate 8 Event Clustering, Source vs Event Discrepancy, and Lineage
===========================================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine


def test_gate8_event_clustering_and_lineage():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    unique_docs = len(set(r.document_id for r in records))
    unique_events = len(set(r.event_id for r in records))
    unique_lineages = len(set(r.lineage_id for r in records))
    unique_sources = len(set(r.source_id for r in records))
    
    assert unique_docs == 120
    # Multiple documents map to single real-world event cluster
    assert unique_events < unique_docs
    assert unique_lineages <= unique_events
    # Documents != Events invariant
    assert unique_docs != unique_events
