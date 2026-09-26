import pytest
import os
import shutil
import pandas as pd
from pathlib import Path
from core.data_onboarding import DataOnboardingService
import subprocess

@pytest.fixture
def clean_onboarding_dir(tmp_path):
    raw_dir = tmp_path / "data/raw/historical"
    raw_dir.mkdir(parents=True)
    return raw_dir

def create_valid_csv(path: Path, rows: int = 250):
    data = []
    for i in range(rows):
        data.append({
            "timestamp": f"2020-01-{i%30+1:02d}",
            "open": 1000.0,
            "high": 1100.0,
            "low": 900.0,
            "close": 1050.0,
            "volume": 10000
        })
    df = pd.DataFrame(data)
    # Ensure unique timestamps if rows <= 30, otherwise just mock
    if rows > 28:
        # Better timestamp generation
        df["timestamp"] = pd.date_range(start="2020-01-01", periods=rows, freq="D").strftime("%Y-%m-%d")
    df.to_csv(path, index=False)

def test_discovery_empty(clean_onboarding_dir):
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.discover()
    assert res["status"] == "REAL_DATA_NOT_PROVISIONED"

def test_discovery_valid(clean_onboarding_dir):
    (clean_onboarding_dir / "BBCA.csv").touch()
    (clean_onboarding_dir / "IHSG.csv").touch()
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.discover()
    assert res["status"] == "PROVISIONED"
    assert len(res["supported_files"]) == 2

def test_symbol_sanitization():
    service = DataOnboardingService("dummy")
    assert service._sanitize_symbol("BBCA.csv") == "BBCA"
    assert service._sanitize_symbol("bmri.csv") == "BMRI"
    
    with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
        service._sanitize_symbol("../BBCA.csv")
        
    with pytest.raises(ValueError, match="INVALID_SYMBOL"):
        service._sanitize_symbol(".csv")

def test_profile_valid_full(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 250)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "ACCEPTED"
    assert res["row_count"] == 250
    assert "checksum" in res

def test_profile_valid_partial(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 150)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "ACCEPTED_WITH_WARNINGS"
    assert any("PARTIAL" in w for w in res["warnings"])

def test_profile_insufficient(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 50)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "ACCEPTED_WITH_WARNINGS"
    assert any("INSUFFICIENT" in w for w in res["warnings"])

def test_profile_missing_columns(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    df = pd.DataFrame({"timestamp": ["2020"], "open": [100]})
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("Missing columns" in e for e in res["errors"])

def test_profile_nulls(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[0, "close"] = pd.NA
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("nulls/NaNs" in e for e in res["errors"])

def test_profile_ohlc_consistency(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[0, "high"] = 500 # High is lower than open(1000)
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("High is less than" in e for e in res["errors"])

def test_profile_duplicate_timestamps(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[1, "timestamp"] = df.loc[0, "timestamp"]
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("duplicate timestamps" in e for e in res["errors"])

def test_onboard_full(clean_onboarding_dir):
    create_valid_csv(clean_onboarding_dir / "BBCA.csv", 250)
    create_valid_csv(clean_onboarding_dir / "IHSG.csv", 250)
    
    # Write metadata
    meta = "corporate_action_status: ADJUSTED\nuniverse_status: HISTORICAL_UNIVERSE\nsource_type: OFFICIAL\n"
    (clean_onboarding_dir / "dataset_metadata.yaml").write_text(meta)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.onboard()
    
    assert res["acceptance_status"] == "ACCEPTED"
    assert res["readiness"] == "REAL_DATA_READY"
    assert res["benchmark_available"] is True
    assert len(res["warnings"]) == 0
    assert Path("reports/data_onboarding_report.md").exists()
    assert Path("data/processed/manifest.json").exists()

def test_onboard_with_warnings(clean_onboarding_dir):
    create_valid_csv(clean_onboarding_dir / "BBCA.csv", 250)
    # No IHSG, no metadata
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.onboard()
    
    assert res["acceptance_status"] == "ACCEPTED_WITH_WARNINGS"
    assert res["readiness"] == "REAL_DATA_READY_WITH_WARNINGS"
    assert res["benchmark_available"] is False
    assert any("BENCHMARK_NOT_AVAILABLE" in w for w in res["warnings"])
    assert any("CORPORATE_ACTION_UNKNOWN" in w for w in res["warnings"])

def test_onboard_rejected(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    df = pd.DataFrame({"timestamp": ["2020"], "open": [100]})
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.onboard()
    
    assert res["acceptance_status"] == "REJECTED"
    assert res["readiness"] == "REAL_DATA_INVALID"
    assert res["accepted_count"] == 0
    assert res["rejected_count"] == 1

def test_onboard_partial_acceptance(clean_onboarding_dir):
    create_valid_csv(clean_onboarding_dir / "BBCA.csv", 250)
    # create invalid file
    file_path = clean_onboarding_dir / "INVALID.csv"
    df = pd.DataFrame({"timestamp": ["2020"], "open": [100]})
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.onboard()
    
    # At least one valid, so it's accepted with warnings
    assert res["acceptance_status"] == "ACCEPTED_WITH_WARNINGS"
    assert res["accepted_count"] == 1
    assert res["rejected_count"] == 1

def test_cli_empty_directory():
    # Calling the CLI script when data/raw/historical is empty
    import sys
    result = subprocess.run([sys.executable, "scripts/onboard_data.py"], capture_output=True, text=True)
    assert result.returncode == 3
    assert "REAL_DATA_NOT_PROVISIONED" in result.stdout

def test_future_append_invariance(clean_onboarding_dir):
    # Just to signify we test point in time logic.
    # The onboarding layer doesn't alter timestamps.
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 250)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res1 = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    
    # Append
    with open(file_path, "a") as f:
        f.write("2021-01-01,1000,1100,900,1050,10000\n")
        
    res2 = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    
    assert res1["first_timestamp"] == res2["first_timestamp"]
    assert res1["checksum"] != res2["checksum"]
    assert res2["row_count"] == 251

def test_negative_prices_rejected(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[0, "close"] = -100
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("negative prices" in e for e in res["errors"])

def test_zero_volume_allowed(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[0, "volume"] = 0 # 0 volume is usually a halt, should be allowed
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "ACCEPTED_WITH_WARNINGS" # partial history since rows=10
    assert "errors" not in res or len(res["errors"]) == 0

def test_negative_volume_rejected(clean_onboarding_dir):
    file_path = clean_onboarding_dir / "BBCA.csv"
    create_valid_csv(file_path, 10)
    df = pd.read_csv(file_path)
    df.loc[0, "volume"] = -100
    df.to_csv(file_path, index=False)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.profile_and_validate({"file": "BBCA.csv", "symbol": "BBCA", "path": str(file_path)})
    assert res["validity"] == "REJECTED"
    assert any("Negative volume" in e for e in res["errors"])

def test_metadata_universe_bias(clean_onboarding_dir):
    create_valid_csv(clean_onboarding_dir / "BBCA.csv", 250)
    meta = "universe_status: CURRENT_UNIVERSE\n"
    (clean_onboarding_dir / "dataset_metadata.yaml").write_text(meta)
    
    service = DataOnboardingService(str(clean_onboarding_dir))
    res = service.onboard()
    
    assert any("POSSIBLE_SURVIVORSHIP_BIAS" in w for w in res["warnings"])
