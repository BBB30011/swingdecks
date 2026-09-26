"""
Test Suite for Batch ZZZ.12 — Research Methodology Lock & Historical Expansion Gate
"""

import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.research_methodology_lock import (
    ResearchMethodologyLockEngine,
    ChangeClass,
    ChangeProposal,
    EvidenceTaxonomyState,
    CausalityLevel,
    AttributionComponent,
    CounterfactualTier
)


@pytest.fixture
def lock_engine():
    base_dir = Path(__file__).resolve().parents[1]
    return ResearchMethodologyLockEngine(base_dir=base_dir)


# Test 1: Exactly 3 Agents
def test_01_exactly_three_agents(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["governance_invariants"]["max_agents"] == 3


# Test 2: Agent 4 Absent
def test_02_agent_4_absent(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["governance_invariants"]["agent_4_allowed"] is False


# Test 3: Canonical Universe Lock
def test_03_canonical_universe_lock(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    expected = ["ADRO", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "INCO", "ITMG", "PTBA", "TLKM", "UNTR"]
    assert sorted(manifest["canonical_universe"]) == sorted(expected)
    assert manifest["universe_size"] == 12


# Test 4: Primary Endpoint Lock
def test_04_primary_endpoint_lock(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["primary_endpoint"] == "H5_PEER_EXCESS_DIFFERENTIAL"


# Test 5: Frozen Evidence States (NO_EVIDENCE != NO_EVENT)
def test_05_frozen_evidence_states(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    states = manifest["evidence_states"]
    assert "EVIDENCE_PRESENT" in states
    assert "NO_EVIDENCE_IN_DATASET" in states
    assert "VERIFIED_NO_EVENT" in states
    assert manifest["governance_invariants"]["missing_equals_no_event"] is False


# Test 6: PIT Rules Enforced
def test_06_pit_rules_enforced(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["governance_invariants"]["lookahead_allowed"] is False


# Test 7: Peer Exclusion & Absence of Self-Inclusion
def test_07_peer_exclusion_absence_of_self_inclusion(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["governance_invariants"]["self_inclusion_allowed"] is False


# Test 8: Counterfactual Hierarchy Tiers (C0 to C5)
def test_08_counterfactual_hierarchy_tiers(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    tiers = manifest["counterfactual_hierarchy"]
    assert len(tiers) == 6
    assert "C0_Canonical" in tiers
    assert "C5_Fully_Purified" in tiers


# Test 9: Dataset Snapshot Hash Integrity
def test_09_dataset_snapshot_hash_integrity(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["snapshot_id"] == "SNAPSHOT_ZZZ117_687970d0e904"


# Test 10: Sample Hash Integrity
def test_10_sample_hash_integrity(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["sample_hash"] == "SAMPLE_ZZZ117_HASH_f03310068fd3"


# Test 11: Immutable V1 Baseline Verification
def test_11_immutable_v1_baseline(lock_engine):
    v1_verif = lock_engine.verify_v1_baseline()
    assert v1_verif["verified"] is True
    assert v1_verif["sample_n"] == 73
    assert abs(v1_verif["c0_differential_pp"] - 3.1037) < 0.01
    assert abs(v1_verif["c5_differential_pp"] - 2.9779) < 0.01


# Test 12: Methodology Versioning
def test_12_methodology_versioning(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["methodology_version"] == "METHODOLOGY_V1_FROZEN_20260915"


# Test 13: Change Ledger & Class A-D Validation
def test_13_change_ledger_class_ad_validation(lock_engine):
    # Class D (Strategy Change) must be rejected during expansion
    prop_d = ChangeProposal(
        change_id="CHG-001",
        date="2026-09-15",
        component="layer_e_threshold",
        change_class=ChangeClass.CLASS_D,
        old_state="80",
        new_state="85",
        reason="Optimize win rate",
        evidence="Backtest",
        impact="High",
        validation="None",
        rollback="Revert"
    )
    res_d = lock_engine.validate_change_proposal(prop_d)
    assert res_d["allowed"] is False
    assert res_d["status"] == "REJECTED_CLASS_D_PROHIBITED"

    # Class A (Data Addition) must be approved with replication requirement
    prop_a = ChangeProposal(
        change_id="CHG-002",
        date="2026-09-15",
        component="historical_years",
        change_class=ChangeClass.CLASS_A,
        old_state="2024-2026",
        new_state="2016-2026",
        reason="Dataset V2 Expansion",
        evidence="Ingestion pipeline",
        impact="Expanded coverage",
        validation="Replication-First test",
        rollback="Drop V2"
    )
    res_a = lock_engine.validate_change_proposal(prop_a)
    assert res_a["allowed"] is True
    assert res_a["status"] == "APPROVED_CLASS_A_DATA_EXPANSION"


# Test 14: Replication Protocol Validation
def test_14_replication_protocol_validation(lock_engine):
    valid_v2_manifest = {
        "dataset_version": "DATASET_V2_EXPANDED",
        "snapshot_id": "SNAPSHOT_V2_TEST",
        "source_manifest_hash": "abc123hash",
        "row_count": 2500,
        "ticker_set": ["ADRO", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "INCO", "ITMG", "PTBA", "TLKM", "UNTR"],
        "v1_subset_hash": "SAMPLE_ZZZ117_HASH_f03310068fd3",
        "primary_endpoint": "H5_PEER_EXCESS_DIFFERENTIAL"
    }
    rep_res = lock_engine.verify_replication_protocol(valid_v2_manifest)
    assert rep_res["replication_passed"] is True
    assert rep_res["status"] == "REPLICATION_PROTOCOL_CERTIFIED"


# Test 15: No Automatic Dataset Mutation
def test_15_no_automatic_dataset_mutation(lock_engine):
    manifest = lock_engine.get_locked_methodology_manifest()
    assert manifest["governance_invariants"]["replication_first_mandate"] is True


# Test 16: Red Team 20-Dimension Battery Pass
def test_16_red_team_20_battery_pass(lock_engine):
    rt_res = lock_engine.evaluate_redteam_20_battery()
    assert rt_res["overall_status"] == "PASS"
    assert rt_res["passed_checks"] == 20
    assert rt_res["failed_checks"] == 0


# Test 17: Historical Expansion Gate Decision
def test_17_gate_decision(lock_engine):
    gate = lock_engine.evaluate_gate_decision()
    assert gate["methodology_lock"] is True
    assert gate["historical_expansion_gate"] == "OPEN"
    assert gate["gate_status"] == "METHODOLOGY_LOCKED"
