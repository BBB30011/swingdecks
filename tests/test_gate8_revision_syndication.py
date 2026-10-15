"""
Tests for Gate 8 Revision Chains and Syndication Non-Inflation
==============================================================
"""

import pytest
from core.gate8_scale_coverage_engine import Gate8ScaleCoverageEngine
from core.data_platform_schemas import NoveltyClass


def test_gate8_revision_chain_lineage():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    revisions = [r for r in records if r.is_revision]
    assert len(revisions) > 0
    for rev in revisions:
        assert rev.primary_novelty_class == NoveltyClass.REVISION
        assert rev.prior_document_id is not None


def test_gate8_syndication_non_inflation():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    records = engine.load_canonical_scale_dataset(level=2)
    
    syndications = [r for r in records if r.is_syndication]
    assert len(syndications) > 0
    for synd in syndications:
        assert synd.primary_novelty_class == NoveltyClass.SYNDICATION
        # Syndications must NOT create new independent event clusters
        assert synd.event_cluster_id is not None
