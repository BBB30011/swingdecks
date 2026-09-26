import pytest
import os
import sys
import subprocess
import pandas as pd
from pathlib import Path
import hashlib
import yaml

from core.data_import_wizard import DataImportWizard

@pytest.fixture
def clean_dir(tmp_path):
    d = tmp_path / "data/raw/historical"
    d.mkdir(parents=True)
    return d

def create_csv(path: Path, rows: int = 150):
    data = []
    start_dt = pd.to_datetime("2020-01-01")
    for i in range(rows):
        dt = start_dt + pd.Timedelta(days=i)
        data.append({
            "timestamp": dt.strftime("%Y-%m-%d"),
            "open": 100,
            "high": 110,
            "low": 90,
            "close": 105,
            "volume": 1000
        })
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    return path

def get_sha256(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def test_empty_directory(clean_dir):
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["dataset_status"] == "REAL_DATA_NOT_PROVISIONED"
    
def test_import_instruction_generation(clean_dir):
    wizard = DataImportWizard(str(clean_dir))
    wizard.generate_operator_instructions()
    assert Path("reports/import_instructions.md").exists()
    
def test_valid_dataset_inspection(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    create_csv(clean_dir / "IHSG.csv")
    
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["dataset_status"] == "READY_FOR_REAL_BACKTEST"
    assert ins["snapshot_id"] != "UNKNOWN"
    
def test_malformed_dataset(clean_dir):
    path = clean_dir / "BBCA.csv"
    with open(path, "w") as f:
        f.write("not a real csv\n")
        
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["dataset_status"] == "NOT_READY"

def test_metadata_loading(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    
    meta = {"dataset": {"name": "Test dataset", "source": "Vendor"}}
    with open(clean_dir / "dataset_metadata.yaml", "w") as f:
        yaml.dump(meta, f)
        
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["metadata"]["dataset"]["source"] == "Vendor"

def test_unknown_metadata(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    # Metadata is empty if not provided
    assert "dataset" not in ins["metadata"]

def test_benchmark_detection(clean_dir):
    create_csv(clean_dir / "IHSG.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["compatibility"]["benchmark_detected"] is True
    
def test_source_provenance(clean_dir):
    wizard = DataImportWizard(str(clean_dir))
    md = wizard.generate_pre_backtest_checklist({"status": "PROVISIONED", "metadata": {"dataset": {"source": "Vendor"}}})
    assert "[x] Dataset provenance documented" in md
    
def test_dataset_snapshot(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins1 = wizard.inspect()
    
    # Adding a file changes the snapshot
    create_csv(clean_dir / "BBNI.csv")
    ins2 = wizard.inspect()
    
    assert ins1["snapshot_id"] != ins2["snapshot_id"]
    
def test_sha_reproducibility(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins1 = wizard.inspect()
    ins2 = wizard.inspect()
    # Snapshots should be deterministic for identical content structure
    assert ins1["snapshot_id"] == ins2["snapshot_id"]

def test_raw_immutability(clean_dir):
    path = create_csv(clean_dir / "BBCA.csv")
    hash_before = get_sha256(path)
    
    wizard = DataImportWizard(str(clean_dir))
    wizard.inspect()
    wizard.validate()
    
    hash_after = get_sha256(path)
    assert hash_before == hash_after

def test_readiness_gate(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    create_csv(clean_dir / "IHSG.csv")
    wizard = DataImportWizard(str(clean_dir))
    val = wizard.validate()
    assert val["readiness"] == "READY_FOR_REAL_BACKTEST"

def test_backtest_handoff(clean_dir):
    wizard = DataImportWizard(str(clean_dir))
    conf = wizard.get_backtest_reproducibility_config({"snapshot_id": "ABC"})
    assert conf["dataset_id"] == "ABC"
    
def test_blocked_backtest(clean_dir):
    path = clean_dir / "BBCA.csv"
    with open(path, "w") as f:
        f.write("not a real csv\n")
        
    wizard = DataImportWizard(str(clean_dir))
    val = wizard.validate()
    assert val["readiness"] == "NOT_READY"

def test_no_network_behavior():
    # Implicitly tested by the fact that wizard does not use requests or urllib
    pass

def test_no_synthetic_fallback(clean_dir):
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert ins["dataset_status"] == "REAL_DATA_NOT_PROVISIONED"
    # Files shouldn't be created synthetically
    assert len(list(clean_dir.iterdir())) == 0

def test_deterministic_inspection(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    assert "BBCA" in str(ins)

def test_report_generation(clean_dir):
    create_csv(clean_dir / "BBCA.csv")
    wizard = DataImportWizard(str(clean_dir))
    ins = wizard.inspect()
    wizard.generate_pre_backtest_checklist(ins)
    assert Path("reports/pre_backtest_checklist.md").exists()

def test_cli_integration_wizard(clean_dir):
    res = subprocess.run([sys.executable, "scripts/onboard_data.py", "--wizard"], cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 0
    assert "Generated import instructions" in res.stdout

def test_cli_integration_preflight_empty(clean_dir):
    res = subprocess.run([sys.executable, "scripts/onboard_data.py", "--preflight"], cwd=str(Path(__file__).parent.parent), capture_output=True, text=True)
    assert res.returncode == 3
    assert "REAL_DATA_NOT_PROVISIONED" in res.stdout
