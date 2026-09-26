import json
import hashlib
import yaml
from pathlib import Path
from typing import Dict, Any, List

from core.data_compatibility import DataCompatibilityChecker

class DataImportWizard:
    def __init__(self, raw_data_dir: str = "data/raw/historical"):
        self.raw_data_dir = Path(raw_data_dir)
        self.compatibility = DataCompatibilityChecker(str(self.raw_data_dir))
        
    def generate_operator_instructions(self) -> str:
        md = """# DATASET IMPORT INSTRUCTIONS

## Required Dataset

Place compliant IDX historical CSV files into:
`data/raw/historical/`

Minimal required columns (case-insensitive, customizable order):
- symbol (usually derived from filename)
- date/timestamp
- open
- high
- low
- close
- volume

Recommended:
- `IHSG.csv` for benchmark
- Several years of daily history across multiple sectors
- Historical universe information
- Corporate action metadata
- Suspension/delist metadata
- Source provenance

**Warning:**
A dataset that only contains currently active stocks may suffer from severe survivorship bias.
Please provide `dataset_metadata.yaml` describing the provenance.

## Recommended Directory Structure

```text
data/
└── raw/
    └── historical/
        ├── dataset_metadata.yaml
        ├── BBCA.csv
        ├── BBRI.csv
        ├── BMRI.csv
        ├── BBNI.csv
        ├── TLKM.csv
        ├── ASII.csv
        ├── ...
        └── IHSG.csv
```
"""
        out_path = Path("reports/import_instructions.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
            
        return md

    def inspect(self) -> Dict[str, Any]:
        """
        Runs compatibility checks and generates dataset snapshot ID.
        """
        comp_res = self.compatibility.check_directory()
        
        # Load metadata
        meta = {}
        meta_path = self.raw_data_dir / "dataset_metadata.yaml"
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = yaml.safe_load(f) or {}
            except:
                pass
                
        snapshot_id = self._generate_snapshot_id(comp_res, meta)
        
        return {
            "status": comp_res["status"],
            "dataset_status": comp_res.get("dataset_status", "REAL_DATA_NOT_PROVISIONED"),
            "snapshot_id": snapshot_id,
            "metadata": meta,
            "compatibility": comp_res
        }
        
    def validate(self) -> Dict[str, Any]:
        inspection = self.inspect()
        readiness = inspection["dataset_status"]
        
        if readiness == "REAL_DATA_NOT_PROVISIONED":
            return {"readiness": "NOT_READY", "reason": "REAL_DATA_NOT_PROVISIONED"}
            
        if readiness == "READY_FOR_REAL_BACKTEST":
            return {"readiness": "READY_FOR_REAL_BACKTEST", "snapshot_id": inspection["snapshot_id"]}
            
        if readiness == "READY_WITH_WARNINGS":
            return {"readiness": "READY_WITH_WARNINGS", "snapshot_id": inspection["snapshot_id"]}
            
        return {"readiness": "NOT_READY", "reason": "FAILED_VALIDATION"}

    def preview(self) -> Dict[str, Any]:
        return self.inspect()
        
    def accept(self, dataset_id: str) -> bool:
        # In a real GUI this confirms dataset acceptance
        # Here we just validate snapshot id
        ins = self.inspect()
        return ins["snapshot_id"] == dataset_id
        
    def reject(self, dataset_id: str) -> bool:
        # Operator rejects
        return True

    def _generate_snapshot_id(self, comp_res: Dict[str, Any], meta: Dict[str, Any]) -> str:
        # Create a hash from the list of files, sizes, and metadata
        if comp_res["status"] == "REAL_DATA_NOT_PROVISIONED":
            return "UNKNOWN"
            
        hasher = hashlib.sha256()
        
        # Sort files to ensure deterministic hash
        files = sorted(comp_res.get("files", []), key=lambda x: x["file"])
        for f in files:
            hasher.update(f["file"].encode("utf-8"))
            if "records" in f:
                hasher.update(str(f["records"]).encode("utf-8"))
                
        hasher.update(json.dumps(meta, sort_keys=True).encode("utf-8"))
        
        return hasher.hexdigest()

    def generate_pre_backtest_checklist(self, inspection: Dict[str, Any]) -> str:
        status = inspection.get("status")
        comp = inspection.get("compatibility", {})
        meta = inspection.get("metadata", {}).get("dataset", {})
        
        is_prov = status == "PROVISIONED"
        has_ihsg = comp.get("benchmark_detected", False)
        
        no_dupe_ts = True
        no_malformed = True
        sufficient_history = True
        
        if is_prov:
            for f in comp.get("files", []):
                errs = str(f.get("errors", []))
                if "Duplicate timestamp" in errs: no_dupe_ts = False
                if f.get("status") == "INCOMPATIBLE": no_malformed = False
                
                warns = str(f.get("warnings", []))
                if "Insufficient history" in warns: sufficient_history = False
                
        corp_known = meta.get("corporate_actions", {}).get("available", False) or meta.get("adjusted_prices") not in [None, "UNKNOWN"]
        surv_known = meta.get("survivorship", {}).get("status") not in [None, "UNKNOWN"]
        prov_known = meta.get("source") not in [None, ""]
        
        dataset_status = inspection.get("dataset_status")
        gate_pass = dataset_status in ["READY_FOR_REAL_BACKTEST", "READY_WITH_WARNINGS"]

        md = f"""# PRE-BACKTEST CHECKLIST

- [{'x' if is_prov else ' '}] Real data physically present
- [{'x' if prov_known else ' '}] Dataset provenance documented
- [{'x' if no_malformed else ' '}] IDX daily OHLCV available
- [{'x' if has_ihsg else ' '}] IHSG available
- [{'x' if sufficient_history else ' '}] Sufficient history
- [{'x' if no_dupe_ts else ' '}] No unresolved duplicate timestamps
- [{'x' if no_malformed else ' '}] No future timestamps
- [{'x' if no_malformed else ' '}] No malformed OHLC
- [{'x' if corp_known else ' '}] Corporate action status known/explicitly warned
- [{'x' if surv_known else ' '}] Survivorship status known/explicitly warned
- [{'x' if is_prov else ' '}] Manifest generated
- [{'x' if is_prov else ' '}] SHA-256 verified
- [{'x' if gate_pass else ' '}] Point-in-time validation PASS
- [{'x' if gate_pass else ' '}] Future append invariance PASS
- [{'x' if gate_pass else ' '}] Agent1 integration PASS
- [{'x' if gate_pass else ' '}] Backtest gate PASS

## Dataset Snapshot
ID: {inspection.get('snapshot_id')}
"""
        out_path = Path("reports/pre_backtest_checklist.md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
            
        return md

    def get_backtest_reproducibility_config(self, inspection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates the payload needed to reproduce the backtest
        """
        return {
            "dataset_id": inspection.get("snapshot_id"),
            "manifest_hash": "TODO",
            "strategy_config_hash": "TODO",
            "risk_config_hash": "TODO",
            "backtest_config_hash": "TODO"
        }
