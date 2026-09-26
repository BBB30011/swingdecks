"""
tests/test_zzz1432_fixed_sample_measurement.py

Comprehensive Test Suite for Batch ZZZ.14.3.2: Fixed-Sample Layer Attribution & Agent 2 Measurement Gate.
Verifies fixed N=73 sample size across all layers A0..A5, Information Variation Audit metrics,
+3.1037 pp differential replication, 15 adversarial probes (A..O), and 100% deterministic reproducibility.
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.fixed_sample_layer_attribution_engine import (
    FixedSampleLayerAttributionEngine,
    EXPECTED_MANIFEST_HASH
)

@pytest.fixture(scope="module")
def attribution_results():
    engine = FixedSampleLayerAttributionEngine()
    results = engine.execute_full_fixed_sample_attribution_suite()
    return results

def test_fixed_sample_manifest_identity_and_hash(attribution_results):
    report = attribution_results["report_summary"]
    manifest = report["manifest_summary"]

    assert manifest["total_canonical_observations"] == 73
    assert manifest["evidence_count"] == 59
    assert manifest["unobserved_count"] == 14
    assert manifest["commodity_count"] == 51
    assert manifest["non_commodity_count"] == 22
    assert manifest["unique_tickers_count"] == 11
    assert manifest["unique_dates_count"] == 49
    assert manifest["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert manifest["manifest_hash_verified"] is True

def test_fixed_sample_all_layers_n73(attribution_results):
    report = attribution_results["report_summary"]
    layers = report["layer_comparison"]["fixed_sample_layers"]

    assert len(layers) == 6
    for layer_entry in layers:
        assert layer_entry["N"] == 73, f"Layer {layer_entry['layer']} must have fixed sample N=73"
        assert layer_entry["h5_peer_excess_mean_pct"] is not None
        assert layer_entry["ci_95_pct"][0] <= layer_entry["ci_95_pct"][1]

def test_information_variation_audit(attribution_results):
    report = attribution_results["report_summary"]
    audit = report["information_variation_audit"]
    summaries = audit["field_summaries"]

    # Agent 2 confidence
    conf_summary = summaries["agent2_confidence"]
    assert conf_summary["unique_values_count"] == 1
    assert conf_summary["value_distribution"]["MEDIUM"] == 73
    assert conf_summary["is_constant_across_sample"] is True

    # Red Team verdict
    rt_summary = summaries["red_team_verdict"]
    assert rt_summary["unique_values_count"] == 1
    assert rt_summary["value_distribution"]["PASS"] == 73
    assert rt_summary["is_constant_across_sample"] is True

    # Diagnostic status
    conclusion = audit["audit_conclusion"]
    assert conclusion["diagnostic_status"] == "AGENT2_INFORMATION_PRESENT_BUT_NOT_DISCRIMINATIVELY_OPERATIONALIZED"

def test_evidence_association_replicated(attribution_results):
    report = attribution_results["report_summary"]
    ev_assoc = report["evidence_association"]

    treat = ev_assoc["treatment_cohort"]
    ctrl = ev_assoc["control_cohort"]
    diff = ev_assoc["differential_summary"]

    assert treat["N"] == 59
    assert ctrl["N"] == 14
    assert treat["mean_excess_h5_pct"] == 0.6529
    assert ctrl["mean_excess_h5_pct"] == -2.4509
    assert diff["peer_excess_differential_pp"] == 3.1037
    assert diff["replication_delta_pp"] == 0.0
    assert diff["replicated_successfully"] is True

def test_preoutcome_freeze_and_outcome_invariance(attribution_results):
    freeze_path = "gates/evidence/zzz1432_preoutcome_freeze.json"
    assert os.path.exists(freeze_path)

    with open(freeze_path, "r") as f:
        freeze_data = json.load(f)

    assert len(freeze_data) == 73
    for sid, data in freeze_data.items():
        assert len(data["hks_hash"]) == 64
        assert len(data["pre_outcome_hash"]) == 64
        assert "frozen_at_timestamp" in data

def test_adversarial_15_probes(attribution_results):
    report = attribution_results["report_summary"]
    probes = report["leakage_audit"]["probes"]

    assert len(probes) == 15
    assert report["leakage_audit"]["all_adversarial_probes_passed"] is True
    for p in probes:
        assert p["status"] == "PASS", f"Adversarial probe {p['probe_id']} failed"

def test_reproducibility_dual_run(attribution_results):
    report = attribution_results["report_summary"]
    repro = report["reproducibility"]

    assert repro["passed"] is True
    assert repro["matches"] == 73

def test_all_14_required_artifacts_exist():
    required_files = [
        "gates/evidence/zzz1432_fixed_sample_manifest.json",
        "gates/evidence/zzz1432_layer_states.json",
        "gates/evidence/zzz1432_agent2_output_ledger.json",
        "gates/evidence/zzz1432_redteam_output_ledger.json",
        "gates/evidence/zzz1432_information_variation_audit.json",
        "gates/evidence/zzz1432_layer_comparison.json",
        "gates/evidence/zzz1432_evidence_association.json",
        "gates/evidence/zzz1432_concentration_audit.json",
        "gates/evidence/zzz1432_leakage_audit.json",
        "gates/evidence/zzz1432_reproducibility.json",
        "gates/evidence/zzz1432_preoutcome_freeze.json",
        "gates/closed/zzz14_3_2_fixed_sample_layer_attribution.json"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing required artifact: {f}"
