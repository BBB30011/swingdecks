import json
from pathlib import Path
from typing import Dict, Any

from core.data_import_wizard import DataImportWizard

class DataProvisioningReporter:
    def __init__(self, raw_data_dir: str = "data/raw/historical"):
        self.wizard = DataImportWizard(raw_data_dir)
        
    def generate_status(self) -> Dict[str, Any]:
        inspection = self.wizard.inspect()
        validation = self.wizard.validate()
        
        status_data = {
            "real_data_present": inspection["status"] == "PROVISIONED",
            "dataset_status": inspection.get("dataset_status", "REAL_DATA_NOT_PROVISIONED"),
            "symbol_count": 0,
            "record_count": 0,
            "benchmark_available": False,
            "dataset_ready": validation["readiness"] in ["READY_FOR_REAL_BACKTEST", "READY_WITH_WARNINGS"],
            "real_backtest_allowed": validation["readiness"] in ["READY_FOR_REAL_BACKTEST", "READY_WITH_WARNINGS"],
            "predictive_value_evaluated": False,
            "blocking_issues": []
        }
        
        comp = inspection.get("compatibility", {})
        if status_data["real_data_present"]:
            status_data["symbol_count"] = len(comp.get("files", []))
            status_data["record_count"] = sum([f.get("records", 0) for f in comp.get("files", [])])
            status_data["benchmark_available"] = comp.get("benchmark_detected", False)
            
        if validation["readiness"] == "NOT_READY":
            status_data["blocking_issues"].append(validation.get("reason", "UNKNOWN"))
            
        self._write_reports(status_data, inspection)
        return status_data
        
    def _write_reports(self, status: Dict[str, Any], inspection: Dict[str, Any]):
        out_json = Path("reports/data_provisioning_status.json")
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=4)
            
        out_md = Path("reports/data_provisioning_status.md")
        
        meta = inspection.get("metadata", {}).get("dataset", {})
        surv_req = "Unknown (WARNING: Possible Survivorship Bias)" if meta.get("survivorship", {}).get("status") in [None, "UNKNOWN"] else "Known"
        corp_req = "Unknown (WARNING)" if meta.get("corporate_actions", {}).get("available") is False else "Known"
        prov_req = "Unknown (WARNING)" if not meta.get("source") else "Documented"
        
        next_action = "Dataset accepted and ready for backtest." if status['dataset_ready'] else "Provision compliant real IDX historical CSV files into `data/raw/historical/`\nThen rerun the onboarding/preflight process."
        
        md = f"""# DATA PROVISIONING STATUS

## 1. Current Status
- **Dataset Status**: {status['dataset_status']}
- **Ready for Backtest**: {status['dataset_ready']}

## 2. Data Availability
- **Real Data Present**: {status['real_data_present']}

## 3. Required Dataset
- Daily OHLCV IDX data

## 4. Recommended Coverage
- Minimum 3-5 years historical coverage per symbol.

## 5. Symbol Coverage
- Symbols Found: {status['symbol_count']}
- Total Records: {status['record_count']}

## 6. IHSG Requirement
- **Benchmark Available**: {status['benchmark_available']}

## 7. Corporate Action Requirement
- {corp_req}

## 8. Survivorship Requirement
- {surv_req}

## 9. Provenance Requirement
- {prov_req}

## 10. Acceptance Gate
- **Status**: {status['dataset_status']}

## 11. Next Operator Action
**NEXT ACTION:**
{next_action}
"""
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md)
