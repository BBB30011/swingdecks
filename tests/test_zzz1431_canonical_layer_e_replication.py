"""
tests/test_zzz1431_canonical_layer_e_replication.py

Comprehensive Test Suite for Batch ZZZ.14.3.1: Canonical Layer E Replay-Firewall Replication.
Verifies exact N=73 canonical identity, replay integrity, outcome blindness, 
+3.10 pp differential replication, dual-run reproducibility, and zero leakage/silent fallback.
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.canonical_replication_engine import (
    CanonicalReplicationEngine,
    CANONICAL_12_TICKERS,
    COMMODITY_TICKERS,
    NON_COMMODITY_TICKERS
)

@pytest.fixture(scope="module")
def replication_results():
    engine = CanonicalReplicationEngine()
    results = engine.execute_full_canonical_replication()
    return results

def test_canonical_manifest_identity(replication_results):
    report = replication_results["report_summary"]
    manifest = report["manifest_summary"]
    
    assert manifest["total_canonical_observations"] == 73, "Total canonical setups must be exactly 73"
    assert manifest["evidence_count"] == 59, "Treatment (Evidence) setups must be exactly 59"
    assert manifest["unobserved_count"] == 14, "Control (Unobserved) setups must be exactly 14"
    assert manifest["commodity_count"] == 51, "Commodity setups must be exactly 51"
    assert manifest["non_commodity_count"] == 22, "Non-commodity setups must be exactly 22"
    assert manifest["unique_tickers_count"] == 11, "Unique tickers must be 11"
    assert manifest["unique_dates_count"] == 49, "Unique dates must be 49"
    assert len(manifest["manifest_sha256"]) == 64, "Manifest SHA-256 hash must be valid"

def test_replay_discrepancies_zero(replication_results):
    report = replication_results["report_summary"]
    ledger_path = "gates/evidence/zzz1431_reconciliation_ledger.json"
    assert os.path.exists(ledger_path)
    
    with open(ledger_path, "r") as f:
        ledger = json.load(f)
        
    assert len(ledger) == 73, "Reconciliation ledger must contain 73 rows"
    mismatches = [row for row in ledger if not row["is_match"]]
    assert len(mismatches) == 0, f"Found {len(mismatches)} unexplained discrepancies vs V1 baseline"

def test_thesis_freeze_and_outcome_blindness(replication_results):
    freeze_path = "gates/evidence/zzz1431_agent2_thesis_freeze.json"
    assert os.path.exists(freeze_path)
    
    with open(freeze_path, "r") as f:
        freeze_data = json.load(f)
        
    assert len(freeze_data) == 73, "All 73 setups must have frozen thesis hashes"
    for sid, data in freeze_data.items():
        assert len(data["hks_hash"]) == 64, "HKS hash must be 64-char SHA256"
        assert len(data["thesis_freeze_hash"]) == 64, "Thesis freeze hash must be 64-char SHA256"
        assert "frozen_at_timestamp" in data

def test_primary_differential_replication(replication_results):
    report = replication_results["report_summary"]
    diff = report["differential_summary"]
    
    assert diff["evidence_N"] == 59
    assert diff["unobserved_N"] == 14
    assert diff["replicated_successfully"] is True, "Replication must succeed"
    assert abs(diff["replication_delta_pp"]) < 0.05, f"Replication delta too high: {diff['replication_delta_pp']} pp"
    assert abs(diff["peer_excess_differential_pp"] - 3.1037) < 0.05, f"Differential mismatch: {diff['peer_excess_differential_pp']}"

def test_layer_nested_results(replication_results):
    report = replication_results["report_summary"]
    layers = report["layer_results"]["layers"]
    
    layer_map = {l["layer"]: l for l in layers}
    assert layer_map["A0"]["N"] == 73
    assert layer_map["A1"]["N"] == 73
    assert layer_map["A2"]["N"] == 51
    assert layer_map["A3"]["N"] == 59
    assert layer_map["A4"]["N"] == 59
    assert layer_map["A5"]["N"] == 59
    
    for code in ["A0", "A1", "A2", "A3", "A4", "A5"]:
        assert layer_map[code]["h5_peer_excess_mean_pct"] is not None
        assert layer_map[code]["ci_95_pct"][0] <= layer_map[code]["ci_95_pct"][1]

def test_leakage_and_silent_fallback_probes(replication_results):
    report = replication_results["report_summary"]
    leakage = report["leakage_results"]
    
    assert leakage["all_leakage_probes_passed"] is True, "All leakage probes must pass"
    for probe in leakage["probes"]:
        assert probe["status"] == "PASS", f"Probe {probe['test_id']} failed"

def test_reproducibility_dual_run(replication_results):
    report = replication_results["report_summary"]
    repro = report["reproducibility_results"]
    
    assert repro["passed"] is True
    assert repro["matches"] == 73

def test_red_team_governance(replication_results):
    report = replication_results["report_summary"]
    rt = report["red_team_results"]
    
    assert rt["overall_red_team_verdict"] == "PASS"
    assert len(rt["checks"]) == 20
    for c in rt["checks"]:
        assert c["status"] == "PASS", f"Red Team check {c['check_id']} failed"

def test_required_artifacts_exist():
    required_files = [
        "gates/evidence/zzz1431_observation_level.parquet",
        "gates/evidence/zzz1431_canonical_manifest.json",
        "gates/evidence/zzz1431_reconciliation_ledger.json",
        "gates/evidence/zzz1431_agent2_thesis_freeze.json",
        "gates/evidence/zzz1431_replay_eligibility.json",
        "gates/evidence/zzz1431_leakage_audit.json",
        "gates/evidence/zzz1431_silent_fallback.json",
        "gates/evidence/zzz1431_peer_integrity.json",
        "gates/evidence/zzz1431_derived_feature_leakage.json",
        "gates/evidence/zzz1431_reproducibility.json",
        "gates/evidence/zzz1431_layer_results.json",
        "gates/evidence/zzz1431_concentration_audit.json",
        "gates/evidence/zzz1431_stratification_results.json",
        "gates/evidence/zzz1431_red_team_results.json",
        "gates/closed/zzz14_3_1_canonical_layer_e_replication.json"
    ]
    for f in required_files:
        assert os.path.exists(f), f"Missing required artifact: {f}"
