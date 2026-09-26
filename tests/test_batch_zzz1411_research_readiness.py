import json
import os
import pytest

SCRATCH_DIR = "d:/Project/SwingDeck/gates/evidence"

def load_json(name):
    with open(os.path.join(SCRATCH_DIR, name)) as f:
        return json.load(f)

def test_v1_observation_replication():
    data = load_json("zzz1411_v1_observation_replication.json")
    assert data["observation_level_match"] is True
    assert data["delta"] == 0

def test_pit_semantic_safety():
    data = load_json("zzz1411_pit_semantic_audit.json")
    assert data["four_timestamp_model_verified"] is True
    assert data["semantics_verified"] is True

def test_future_injection_leaks():
    data = load_json("zzz1411_future_injection.json")
    assert data["leaks"] == 0

def test_missingness_honesty():
    data = load_json("zzz1411_missingness.json")
    assert data["no_evidence_invariant_verified"] is True

def test_final_gate_conditional():
    data = load_json("zzz1411_final_gate.json")
    assert "CONDITIONAL" in data["status"]
