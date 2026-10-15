"""
Tests for Gate 8 Real-World Scale, Stratification, and Degradation Invariants
============================================================================
Validates cohort manifest generation, scale levels (L0, L1, L2, L3),
adversarial attacks A-Z, ticker concentration, and zero degradation.
"""

import pytest
from core.gate8_scale_coverage_engine import (
    Gate8ScaleCoverageEngine, Gate8CohortManifest, CoverageStatus,
    DomainClass, Gate8SourceClass, TemporalComplexityClass
)
from core.data_platform_schemas import NoveltyClass, EntityType, AccessClass


@pytest.fixture
def gate8_engine():
    engine = Gate8ScaleCoverageEngine(db_path=":memory:")
    engine.load_canonical_scale_dataset(level=2)
    return engine


def test_gate8_cohort_manifest_generation(gate8_engine):
    """Verify Gate 8 Cohort Manifest fields, hashes, and counts."""
    manifest = gate8_engine.generate_manifest()
    assert manifest.cohort_id == "COHORT_GATE8_CANONICAL_V1"
    assert manifest.n_raw_documents == 120
    assert manifest.n_canonical_documents == 120
    assert manifest.n_unique_sources > 5
    assert manifest.n_source_classes == 12
    assert manifest.n_unique_entities > 10
    assert manifest.n_unique_events > 20
    assert manifest.n_revisions > 0
    assert manifest.n_syndications > 0
    assert manifest.n_unknown_timestamps > 0
    assert manifest.dataset_hash is not None
    assert manifest.manifest_hash is not None


def test_gate8_stratification_year_coverage(gate8_engine):
    """Verify year stratification across 2016..2026."""
    year_rows = gate8_engine.evaluate_year_stratification()
    assert len(year_rows) == 11
    for row in year_rows:
        assert row["STATUS"] in [CoverageStatus.READY.value, CoverageStatus.CONDITIONAL.value]
        assert float(row["PIT_SAFE_RATE"].replace("%", "")) == 100.0
        assert float(row["PROVENANCE_COMPLETENESS"].replace("%", "")) == 100.0


def test_gate8_stratification_domain_coverage(gate8_engine):
    """Verify domain stratification across 12 canonical domains."""
    domain_rows = gate8_engine.evaluate_domain_stratification()
    assert len(domain_rows) == 12
    for row in domain_rows:
        assert row["STATUS"] in [CoverageStatus.READY.value, CoverageStatus.CONDITIONAL.value]
        assert float(row["PIT_SAFE_RATE"].replace("%", "")) == 100.0
        assert float(row["EXPOSURE_VALIDITY_RATE"].replace("%", "")) == 100.0


def test_gate8_ticker_concentration(gate8_engine):
    """Verify descriptive ticker concentration metrics without composite scores."""
    conc = gate8_engine.evaluate_ticker_concentration()
    assert conc["unique_tickers"] >= 10
    assert 0.0 < conc["top_1_doc_share"] < 50.0  # No single ticker dominates > 50%
    assert 0.0 < conc["top_5_doc_share"] <= 100.0
    assert len(conc["top_10_tickers_by_documents"]) == 10


def test_gate8_scale_degradation_invariants(gate8_engine):
    """Verify scale degradation across L0 -> L1 -> L2 -> L3 maintains 100% integrity."""
    deg = gate8_engine.evaluate_scale_degradation()
    assert deg["L0_N"] == 6
    assert deg["L1_N"] == 30
    assert deg["L2_N"] == 120
    assert deg["L3_N"] == 600
    assert deg["L0_PIT_RATE"] == 1.0
    assert deg["L1_PIT_RATE"] == 1.0
    assert deg["L2_PIT_RATE"] == 1.0
    assert deg["L3_PIT_RATE"] == 1.0
    assert deg["DEGRADATION_DETECTED"] is False
    assert deg["REPRODUCIBILITY_MATCH"] is True


def test_gate8_adversarial_suite_az(gate8_engine):
    """Verify all 26 adversarial stress attack scenarios (A through Z) pass."""
    adv_results = gate8_engine.evaluate_adversarial_suite()
    assert len(adv_results) == 26
    for res in adv_results:
        assert res["RESULT"] == "PASS"
