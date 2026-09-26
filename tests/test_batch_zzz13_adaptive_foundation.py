"""
Test Suite for Batch ZZZ.13 — Adaptive Historical Data & Research Foundation
"""

import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.adaptive_historical_foundation import (
    AdaptiveHistoricalFoundationEngine,
    GovernanceLayer,
    CriterionType,
    CompatibilityStatus,
    PromotionStatus,
    CriterionProposal,
    FieldLineage,
    TaxonomyExtension,
    TemporalRelationship,
    ResearchBranch
)


@pytest.fixture
def adaptive_engine():
    base_dir = Path(__file__).resolve().parents[1]
    return AdaptiveHistoricalFoundationEngine(base_dir=base_dir)


# Test 1: Four-Layer Governance Isolation
def test_01_four_layer_governance_isolation(adaptive_engine):
    layers = [l.value for l in GovernanceLayer]
    assert len(layers) == 4
    assert "LAYER_1_FROZEN_BASELINE" in layers
    assert "LAYER_2_EXTENSION" in layers
    assert "LAYER_3_EXPERIMENT" in layers
    assert "LAYER_4_PROMOTION" in layers


# Test 2: Six-Type Criteria Intake Classification
def test_02_six_type_criteria_intake_classification(adaptive_engine):
    prop_a = CriterionProposal(
        criterion_id="T-A", date_discovered="2026-09-15",
        description="Multi-year historical OHLCV data addition", source="IDX",
        reason="Expansion", domain="MARKET_DATA", affected_component="dataset_time_series",
        expected_value="More data", possible_risk="None", relationship_to_existing_methodology="Additive",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_a) == CriterionType.TYPE_A_DATA_EXTENSION

    prop_b = CriterionProposal(
        criterion_id="T-B", date_discovered="2026-09-15",
        description="Timestamp refinement and duplicate deduplication", source="IDX",
        reason="Quality fix", domain="DATA_QUALITY", affected_component="fact_event.timestamp",
        expected_value="Clean data", possible_risk="None", relationship_to_existing_methodology="Correction",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_b) == CriterionType.TYPE_B_DATA_QUALITY

    prop_c = CriterionProposal(
        criterion_id="T-C", date_discovered="2026-09-15",
        description="Supply chain supplier relationship and political link", source="Report",
        reason="Intelligence", domain="SUPPLY_CHAIN", affected_component="fact_relationship",
        expected_value="Transmission", possible_risk="None", relationship_to_existing_methodology="Relational",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_c) == CriterionType.TYPE_C_INFORMATION_EXTENSION

    prop_d = CriterionProposal(
        criterion_id="T-D", date_discovered="2026-09-15",
        description="Fixed effects econometric statistical test control variable", source="Academic",
        reason="Econometrics", domain="STATISTICAL", affected_component="estimation_pipeline",
        expected_value="Robustness", possible_risk="None", relationship_to_existing_methodology="Experiment",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_d) == CriterionType.TYPE_D_ANALYTICAL_EXTENSION

    prop_e = CriterionProposal(
        criterion_id="T-E", date_discovered="2026-09-15",
        description="Change primary endpoint to cumulative abnormal return", source="Academic",
        reason="Methodology", domain="METHODOLOGY", affected_component="primary_endpoint",
        expected_value="New interpretation", possible_risk="Incomparability", relationship_to_existing_methodology="V2",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_e) == CriterionType.TYPE_E_METHODOLOGY_CHANGE

    prop_f = CriterionProposal(
        criterion_id="T-F", date_discovered="2026-09-15",
        description="Modify breakout entry threshold and position size", source="Trading",
        reason="Strategy tuning", domain="STRATEGY", affected_component="layer_e_threshold",
        expected_value="Optimized returns", possible_risk="Overfitting", relationship_to_existing_methodology="Execution",
        PIT_requirement="Standard", testability="High"
    )
    assert adaptive_engine.classify_criterion(prop_f) == CriterionType.TYPE_F_STRATEGY_CHANGE


# Test 3: Five-Tier Backward Compatibility Assessment
def test_03_five_tier_backward_compatibility(adaptive_engine):
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_A_DATA_EXTENSION) == CompatibilityStatus.COMPATIBLE
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_B_DATA_QUALITY) == CompatibilityStatus.EXTENSION_ONLY
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_C_INFORMATION_EXTENSION) == CompatibilityStatus.EXTENSION_ONLY
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_D_ANALYTICAL_EXTENSION) == CompatibilityStatus.EXPERIMENTAL
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_E_METHODOLOGY_CHANGE) == CompatibilityStatus.METHODOLOGY_CHANGING
    assert adaptive_engine.assess_compatibility(CriterionType.TYPE_F_STRATEGY_CHANGE) == CompatibilityStatus.STRATEGY_CHANGING


# Test 4: Schema Evolution & Additive Field Lineage
def test_04_schema_evolution_additive_field_lineage(adaptive_engine):
    initial_count = len(adaptive_engine.schema_fields)
    new_field = FieldLineage(
        field_name="test_novelty_metric",
        schema_version="SCHEMA_V2_TEST",
        introduced_at_batch="BATCH-ZZZ.13",
        data_type="DOUBLE",
        description="Test metric",
        is_nullable=True,
        fallback_value=0.0
    )
    res = adaptive_engine.evolve_schema(new_field)
    assert res["status"] == "REGISTERED_BACKWARD_COMPATIBLE"
    assert len(adaptive_engine.schema_fields) == initial_count + 1
    assert "symbol" in adaptive_engine.schema_fields  # V1 field remains untouched


# Test 5: Taxonomy Domain Expansion
def test_05_taxonomy_domain_expansion(adaptive_engine):
    initial_domains = len(adaptive_engine.taxonomy_extensions)
    new_tax = TaxonomyExtension(
        domain_name="TECHNOLOGY_EXPOSURE",
        introduced_at_batch="BATCH-ZZZ.13",
        parent_domain=None,
        description="Technology adoption and infrastructure exposure",
        allowed_values=["AI_ADOPTER", "CLOUD_PROVIDER", "HARDWARE_SUPPLIER"]
    )
    res = adaptive_engine.evolve_taxonomy(new_tax)
    assert res["status"] == "TAXONOMY_EXTENSION_REGISTERED"
    assert len(adaptive_engine.taxonomy_extensions) == initial_domains + 1
    assert "COMMODITY" in adaptive_engine.taxonomy_extensions  # Baseline taxonomy untouched


# Test 6: Temporal Relationship Tracking & PIT Bounds
def test_06_temporal_relationship_tracking_and_bounds(adaptive_engine):
    valid_rel = TemporalRelationship(
        entity_id="UNTR",
        related_entity_id="PTBA",
        relationship_type="MINING_CONTRACTOR",
        valid_from="2024-01-01",
        valid_to="2026-12-31",
        observed_at="2024-03-25T10:00:00Z",
        source="Annual Report",
        confidence=0.95,
        PIT_status="VERIFIED_PIT",
        provenance_hash="abc123hash"
    )
    res = adaptive_engine.record_temporal_relationship(valid_rel)
    assert res["status"] == "TEMPORAL_RELATIONSHIP_RECORDED"

    # Test invalid temporal bounds (valid_from > valid_to) must raise error
    invalid_rel = TemporalRelationship(
        entity_id="UNTR",
        related_entity_id="PTBA",
        relationship_type="MINING_CONTRACTOR",
        valid_from="2026-12-31",
        valid_to="2024-01-01",
        observed_at="2024-03-25T10:00:00Z",
        source="Annual Report",
        confidence=0.95,
        PIT_status="VERIFIED_PIT",
        provenance_hash="abc123hash"
    )
    with pytest.raises(ValueError, match="Invalid temporal bounds"):
        adaptive_engine.record_temporal_relationship(invalid_rel)


# Test 7: Research Branching Structure
def test_07_research_branching_structure(adaptive_engine):
    branch = ResearchBranch(
        branch_id="BRANCH_EXPERIMENT_MFE",
        parent_version="METHODOLOGY_V1_FROZEN_20260915",
        branch_type="METHODOLOGY_EXPERIMENT",
        created_at="2026-09-15T10:00:00Z",
        hypothesis="Evaluating MFE path metrics alongside H5"
    )
    res = adaptive_engine.create_branch(branch)
    assert res["status"] == "BRANCH_CREATED"
    assert adaptive_engine.research_branches["BRANCH_EXPERIMENT_MFE"].parent_version == "METHODOLOGY_V1_FROZEN_20260915"


# Test 8: Ten-Point Promotion Gate Pass
def test_08_ten_point_promotion_gate_pass(adaptive_engine):
    prop = CriterionProposal(
        criterion_id="CRIT-PROMO-TEST",
        date_discovered="2026-09-15",
        description="Multi-year historical OHLCV data addition",
        source="IDX",
        reason="Expansion",
        domain="MARKET_DATA",
        affected_component="dataset_time_series",
        expected_value="Power",
        possible_risk="None",
        relationship_to_existing_methodology="Additive",
        PIT_requirement="publication_time <= AS_OF",
        testability="High"
    )
    adaptive_engine.register_criterion(prop)
    
    eval_pass = {
        "clear_definition": True,
        "verifiable_source": True,
        "pit_compliance": True,
        "provenance_complete": True,
        "entity_resolution_adequate": True,
        "zero_lookahead_leakage": True,
        "non_redundant": True,
        "clear_use_case": True,
        "appropriately_tested": True,
        "red_team_pass": True
    }
    promo = adaptive_engine.evaluate_promotion_gate("CRIT-PROMO-TEST", eval_pass)
    assert promo["promoted"] is True
    assert promo["passed_points"] == 10
    assert promo["governance_verdict"] == "PROMOTION_APPROVED"


# Test 9: Incomplete Promotion Gate Rejection
def test_09_incomplete_promotion_gate_rejection(adaptive_engine):
    prop = CriterionProposal(
        criterion_id="CRIT-FAIL-TEST",
        date_discovered="2026-09-15",
        description="Unverified rumor signal",
        source="Social media",
        reason="Test",
        domain="RUMOR",
        affected_component="fact_event",
        expected_value="None",
        possible_risk="High",
        relationship_to_existing_methodology="None",
        PIT_requirement="None",
        testability="Low"
    )
    adaptive_engine.register_criterion(prop)
    
    eval_fail = {
        "clear_definition": True,
        "verifiable_source": False,  # Missing verifiable source
        "pit_compliance": False,     # Missing PIT compliance
        "provenance_complete": False,
        "entity_resolution_adequate": True,
        "zero_lookahead_leakage": True,
        "non_redundant": True,
        "clear_use_case": True,
        "appropriately_tested": False,
        "red_team_pass": False
    }
    promo = adaptive_engine.evaluate_promotion_gate("CRIT-FAIL-TEST", eval_fail)
    assert promo["promoted"] is False
    assert promo["passed_points"] == 5
    assert promo["governance_verdict"] == "PROMOTION_CONDITIONAL_OR_REJECTED"


# Test 10: Twenty-Dimension Red Team Adaptive Battery Pass
def test_10_red_team_20_adaptive_battery_pass(adaptive_engine):
    rt_res = adaptive_engine.evaluate_redteam_20_adaptive_battery()
    assert rt_res["overall_status"] == "PASS"
    assert rt_res["passed_checks"] == 20
    assert rt_res["failed_checks"] == 0
    assert rt_res["verdict"] == "ADAPTIVE_FOUNDATION_GOVERNANCE_CERTIFIED"


# Test 11: All Required Artifacts Exist and Non-Empty
def test_11_all_artifacts_exist_and_non_empty(adaptive_engine):
    base_dir = adaptive_engine.base_dir
    required_files = [
        base_dir / "reports" / "zzz13_adaptive_historical_data_foundation.md",
        base_dir / "scratch" / "zzz13_criteria_registry.json",
        base_dir / "scratch" / "zzz13_schema_lineage.json",
        base_dir / "scratch" / "zzz13_branch_manifest.json",
        base_dir / "scratch" / "zzz13_redteam.json",
        base_dir / "docs" / "ADAPTIVE_HISTORICAL_DATA_FOUNDATION_ZZZ13.md"
    ]
    for rf in required_files:
        assert rf.exists(), f"File missing: {rf}"
        assert rf.stat().st_size > 0, f"File empty: {rf}"
