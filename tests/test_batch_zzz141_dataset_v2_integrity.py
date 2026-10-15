import json
import os
import pytest

SCRATCH_DIR = "gates/evidence"

def load_json(name):
    with open(os.path.join(SCRATCH_DIR, name)) as f:
        return json.load(f)

def test_v1_immutability():
    data = load_json("zzz141_v1_replication.json")
    assert data["mismatches"] == 0
    assert data["status"] == "EXACT_MATCH"

def test_pit_safety():
    data = load_json("zzz141_pit_audit.json")
    assert data["violations"] == 0

def test_future_injection():
    data = load_json("zzz141_future_injection.json")
    assert data["leaks_detected"] == 0

def test_red_team_pass():
    data = load_json("zzz141_redteam.json")
    assert data["pass"] == 30
    assert data["fail"] == 0
