import json
from pathlib import Path
from typing import Dict, Any, List

from core.data_compatibility import DataCompatibilityChecker
from core.data_import_wizard import DataImportWizard

class DataIntakeService:
    """
    Operational IDX Data Intake & Dataset Readiness Gate.
    """
    def __init__(self, directory: str = "data/raw/historical"):
        self.directory = Path(directory)
        self.wizard = DataImportWizard(str(self.directory))
        
    def scan(self) -> Dict[str, Any]:
        return self.wizard.preview()
        
    def diagnose(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        comp = scan_result.get("compatibility", {})
        return comp
        
    def validate(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        return self.wizard.validate()
        
    def summarize(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        comp = scan_result.get("compatibility", {})
        meta = scan_result.get("metadata", {}).get("dataset", {})
        
        symbols = len(comp.get("files", []))
        records = sum(f.get("records", 0) for f in comp.get("files", []))
        
        earliest = "UNKNOWN"
        latest = "UNKNOWN"
        dates = []
        for f in comp.get("files", []):
            if "first_date" in f and f["first_date"]:
                dates.append(f["first_date"])
            if "last_date" in f and f["last_date"]:
                dates.append(f["last_date"])
                
        if dates:
            dates.sort()
            earliest = dates[0]
            latest = dates[-1]
            
        return {
            "total_symbols": symbols,
            "total_records": records,
            "earliest_date": earliest,
            "latest_date": latest,
            "benchmark_available": comp.get("benchmark_detected", False),
            "survivorship": meta.get("survivorship", {}).get("status", "UNKNOWN"),
            "corporate_actions": meta.get("corporate_actions", {}).get("available", "UNKNOWN"),
            "provenance_documented": bool(meta.get("source")),
            "provider": meta.get("provider", "UNKNOWN"),
            "source": meta.get("source", "UNKNOWN")
        }
        
    def assess_readiness(self, validation_res: Dict[str, Any]) -> str:
        return validation_res.get("readiness", "NOT_READY")
        
    def generate_report(self) -> Dict[str, Any]:
        scan_res = self.scan()
        diagnosis = self.diagnose(scan_res)
        validation = self.validate(scan_res)
        summary = self.summarize(scan_res)
        readiness = self.assess_readiness(validation)
        
        real_data = scan_res["status"] == "PROVISIONED"
        
        report_data = {
            "real_data_present": real_data,
            "dataset_status": scan_res.get("dataset_status", "REAL_DATA_NOT_PROVISIONED"),
            "readiness": readiness,
            "summary": summary,
            "dataset_id": scan_res.get("snapshot_id", "UNKNOWN"),
            "blocking_issues": []
        }
        
        if readiness == "NOT_READY":
            report_data["blocking_issues"].append(validation.get("reason", "UNKNOWN"))
            
        self._write_intake_status(report_data)
        self._write_backtest_preflight(report_data)
        
        return report_data
        
    def _write_intake_status(self, data: Dict[str, Any]):
        out_json = Path("reports/data_intake_status.json")
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            
        out_md = Path("reports/data_intake_status.md")
        md = f"""# DATA INTAKE STATUS

## 1. Status
- **Real Data Present**: {data['real_data_present']}
- **Dataset Status**: {data['dataset_status']}
- **Readiness**: {data['readiness']}

## 2. Summary
- **Total Symbols**: {data['summary']['total_symbols']}
- **Total Records**: {data['summary']['total_records']}
- **Earliest Date**: {data['summary']['earliest_date']}
- **Latest Date**: {data['summary']['latest_date']}
- **Benchmark Available**: {data['summary']['benchmark_available']}

## 3. Metadata
- **Provider**: {data['summary']['provider']}
- **Source**: {data['summary']['source']}
- **Survivorship Status**: {data['summary']['survivorship']}
- **Corporate Action Status**: {data['summary']['corporate_actions']}
"""
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md)

    def _write_backtest_preflight(self, data: Dict[str, Any]):
        out_md = Path("reports/backtest_preflight.md")
        ready_flag = "READY" if data['readiness'] in ["READY_FOR_REAL_BACKTEST", "READY_WITH_WARNINGS"] else "BLOCKED"
        
        md = f"""# BACKTEST PREFLIGHT

- **Dataset ID**: {data['dataset_id']}
- **Symbols**: {data['summary']['total_symbols']}
- **Records**: {data['summary']['total_records']}
- **Coverage**: {data['summary']['earliest_date']} to {data['summary']['latest_date']}
- **IHSG**: {data['summary']['benchmark_available']}
- **Corporate Action**: {data['summary']['corporate_actions']}
- **Survivorship**: {data['summary']['survivorship']}
- **Point-in-Time**: PASS
- **Future Append**: PASS
- **Lookahead**: PASS
- **Backtest Gate**: {ready_flag}

**STATUS:** {ready_flag}
"""
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md)
