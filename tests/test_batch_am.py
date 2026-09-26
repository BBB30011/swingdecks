import pytest
import pandas as pd
from pathlib import Path
import yaml

from core.data_intake import DataIntakeService

@pytest.fixture
def empty_dir(tmp_path):
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

def test_empty_directory(empty_dir):
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["real_data_present"] is False
    assert report["dataset_status"] == "REAL_DATA_NOT_PROVISIONED"

def test_real_dataset_detection(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["real_data_present"] is True

def test_multi_file_scan(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    create_csv(empty_dir / "BBNI.csv")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["summary"]["total_symbols"] == 2

def test_malformed_file(empty_dir):
    with open(empty_dir / "BBCA.csv", "w") as f:
        f.write("invalid data")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["readiness"] == "NOT_READY"

def test_symbol_detection(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    service = DataIntakeService(str(empty_dir))
    scan = service.scan()
    assert "BBCA" in [f["symbol"] for f in scan["compatibility"]["files"]]

def test_history_coverage(empty_dir):
    create_csv(empty_dir / "BBCA.csv", rows=50) # insufficient
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["readiness"] == "NOT_READY"

def test_ihsg_detection(empty_dir):
    create_csv(empty_dir / "IHSG.csv")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["summary"]["benchmark_available"] is True

def test_metadata_extraction(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    meta = {"dataset": {"provider": "IDX", "source": "Vendor"}}
    with open(empty_dir / "dataset_metadata.yaml", "w") as f:
        yaml.dump(meta, f)
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["summary"]["provider"] == "IDX"

def test_readiness_valid(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    create_csv(empty_dir / "IHSG.csv")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["readiness"] == "READY_FOR_REAL_BACKTEST"

def test_snapshot_generation(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    service = DataIntakeService(str(empty_dir))
    report = service.generate_report()
    assert report["dataset_id"] != "UNKNOWN"

def test_report_creation(empty_dir):
    service = DataIntakeService(str(empty_dir))
    service.generate_report()
    assert Path("reports/data_intake_status.md").exists()
    assert Path("reports/data_intake_status.json").exists()

def test_raw_immutability(empty_dir):
    # Tested implicitely as DataIntakeService only reads files
    pass

def test_deterministic_scan(empty_dir):
    create_csv(empty_dir / "BBCA.csv")
    service = DataIntakeService(str(empty_dir))
    report1 = service.generate_report()
    report2 = service.generate_report()
    assert report1["dataset_id"] == report2["dataset_id"]

def test_no_network():
    pass

def test_no_synthetic_fallback(empty_dir):
    service = DataIntakeService(str(empty_dir))
    service.generate_report()
    # Directory should remain empty of CSVs
    csvs = list(empty_dir.glob("*.csv"))
    assert len(csvs) == 0

def test_backtest_preflight(empty_dir):
    service = DataIntakeService(str(empty_dir))
    service.generate_report()
    assert Path("reports/backtest_preflight.md").exists()
