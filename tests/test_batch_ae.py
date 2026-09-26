import pytest
from core.dataset_discovery import DatasetDiscovery
from pathlib import Path
import json

def test_dataset_discovery_empty():
    discovery = DatasetDiscovery("non_existent_dir_123")
    res = discovery.run_discovery("reports/test_inventory.json")
    assert res["status"] == "REAL_DATA_NOT_PROVISIONED"
    assert res["readiness"] == "REAL_DATA_NOT_PROVISIONED"
    
def test_dataset_discovery_with_files():
    # Use the synthetic fixtures from Batch AD
    discovery = DatasetDiscovery("tests/fixtures/historical")
    res = discovery.run_discovery("reports/test_inventory_2.json")
    assert res["status"] == "PROVISIONED"
    assert res["readiness"] == "REAL_DATA_READY"
    assert res["total_symbols"] > 0
    assert "checksum" in res["files"][0]
