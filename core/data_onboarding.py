import json
import yaml
from pathlib import Path
import hashlib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime

class DataOnboardingService:
    def __init__(self, directory: str = "data/raw/historical"):
        self.directory = Path(directory)
        self.supported_extensions = [".csv"]
        
    def _sanitize_symbol(self, filename: str) -> str:
        # Check path traversal and invalid chars
        if ".." in filename or "/" in filename or "\\" in filename or "\0" in filename:
            raise ValueError("SECURITY_VIOLATION: Invalid filename")
        
        if filename.startswith('.'):
            raise ValueError("INVALID_SYMBOL: Hidden file or just extension")
            
        stem = Path(filename).stem
        if not stem or stem.isspace():
            raise ValueError("INVALID_SYMBOL: Empty or whitespace")
        if len(stem) > 20:
            raise ValueError("INVALID_SYMBOL: Too long")
        return stem.upper()
        
    def _read_metadata(self) -> Dict[str, Any]:
        meta_path = self.directory / "dataset_metadata.yaml"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}
        
    def discover(self) -> Dict[str, Any]:
        if not self.directory.exists() or not self.directory.is_dir():
            return {"status": "REAL_DATA_NOT_PROVISIONED", "files": []}
            
        files_found = list(self.directory.iterdir())
        if not files_found:
            return {"status": "REAL_DATA_NOT_PROVISIONED", "files": []}
            
        supported_files = []
        ignored_files = []
        errors = []
        
        for f in files_found:
            if f.is_dir():
                continue
            if f.name == "dataset_metadata.yaml":
                continue
                
            if f.suffix.lower() in self.supported_extensions:
                try:
                    symbol = self._sanitize_symbol(f.name)
                    supported_files.append({"file": f.name, "symbol": symbol, "path": str(f)})
                except Exception as e:
                    errors.append({"file": f.name, "error": str(e)})
            else:
                ignored_files.append(f.name)
                
        return {
            "status": "PROVISIONED" if supported_files else "REAL_DATA_NOT_PROVISIONED",
            "supported_files": supported_files,
            "ignored_files": ignored_files,
            "errors": errors
        }

    def profile_and_validate(self, file_info: Dict[str, str]) -> Dict[str, Any]:
        file_path = Path(file_info["path"])
        symbol = file_info["symbol"]
        
        with open(file_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
            
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return {"symbol": symbol, "validity": "REJECTED", "errors": [f"CSV Read Error: {e}"]}
            
        size_bytes = file_path.stat().st_size
        row_count = len(df)
        columns = list(df.columns)
        
        # Standardize columns to lowercase for check
        df.columns = [str(c).lower() for c in columns]
        
        req_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        missing = [c for c in req_cols if c not in df.columns]
        if missing:
            return {"symbol": symbol, "validity": "REJECTED", "errors": [f"Missing columns: {missing}"]}
            
        # Check nulls/NaNs
        null_count = int(df[req_cols].isnull().sum().sum())
        if null_count > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": [f"Contains {null_count} nulls/NaNs"]}
            
        # Check types
        for c in ["open", "high", "low", "close", "volume"]:
            if not pd.api.types.is_numeric_dtype(df[c]):
                return {"symbol": symbol, "validity": "REJECTED", "errors": [f"Column {c} is not numeric"]}
                
        # Data logic validation
        invalid_prices = df[(df["open"] <= 0) | (df["high"] <= 0) | (df["low"] <= 0) | (df["close"] <= 0)]
        if len(invalid_prices) > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": ["Zero or negative prices detected"]}
            
        invalid_volume = df[df["volume"] < 0]
        if len(invalid_volume) > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": ["Negative volume detected"]}
            
        # OHLC logic
        invalid_high = df[(df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["high"] < df["low"])]
        if len(invalid_high) > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": ["High is less than Open/Close/Low"]}
            
        invalid_low = df[(df["low"] > df["open"]) | (df["low"] > df["close"]) | (df["low"] > df["high"])]
        if len(invalid_low) > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": ["Low is greater than Open/Close/High"]}
            
        # Temporal logic
        duplicate_ts = df["timestamp"].duplicated().sum()
        if duplicate_ts > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": [f"Found {duplicate_ts} duplicate timestamps"]}
            
        # Exact duplicate row
        duplicate_rows = df.duplicated().sum()
        if duplicate_rows > 0:
            return {"symbol": symbol, "validity": "REJECTED", "errors": [f"Found {duplicate_rows} exact duplicate rows"]}
            
        # History Sufficiency
        if row_count >= 200:
            history_status = "FULL"
        elif row_count >= 100:
            history_status = "PARTIAL"
        else:
            history_status = "INSUFFICIENT"
            
        first_ts = str(df["timestamp"].iloc[0])
        last_ts = str(df["timestamp"].iloc[-1])
        
        validity = "ACCEPTED" if history_status == "FULL" else "ACCEPTED_WITH_WARNINGS"
        warnings = [f"History is {history_status} ({row_count} bars)"] if history_status != "FULL" else []
        
        return {
            "symbol": symbol,
            "filename": file_info["file"],
            "size_bytes": size_bytes,
            "columns": columns, # original
            "row_count": row_count,
            "first_timestamp": first_ts,
            "last_timestamp": last_ts,
            "duplicate_count": int(duplicate_rows),
            "null_count": null_count,
            "checksum": checksum,
            "validity": validity,
            "warnings": warnings,
            "errors": []
        }

    def onboard(self) -> Dict[str, Any]:
        discovery = self.discover()
        if discovery["status"] == "REAL_DATA_NOT_PROVISIONED":
            return {"readiness": "REAL_DATA_NOT_PROVISIONED", "report_markdown": self._generate_markdown_report({}, "REAL_DATA_NOT_PROVISIONED"), "dataset_acceptance": "REAL_DATA_NOT_PROVISIONED"}
            
        metadata = self._read_metadata()
        
        results = []
        for f in discovery["supported_files"]:
            results.append(self.profile_and_validate(f))
            
        # Determine overall readiness
        accepted = [r for r in results if r.get("validity") in ["ACCEPTED", "ACCEPTED_WITH_WARNINGS"]]
        rejected = [r for r in results if r.get("validity") == "REJECTED"]
        
        dataset_warnings = []
        dataset_blockers = []
        
        has_benchmark = any(r["symbol"] == "IHSG" for r in accepted)
        if not has_benchmark:
            dataset_warnings.append("BENCHMARK_NOT_AVAILABLE: IHSG missing or invalid")
            
        corp_action = metadata.get("corporate_action_status", "UNKNOWN")
        if corp_action == "UNKNOWN":
            dataset_warnings.append("CORPORATE_ACTION_UNKNOWN")
            
        universe = metadata.get("universe_status", "UNKNOWN")
        if universe == "UNKNOWN":
            dataset_warnings.append("UNIVERSE_UNKNOWN")
        elif universe == "CURRENT_UNIVERSE":
            dataset_warnings.append("POSSIBLE_SURVIVORSHIP_BIAS")
            
        source_prov = metadata.get("source_type", "UNKNOWN")
        
        acceptance_status = "REJECTED"
        readiness = "REAL_DATA_INVALID"
        if len(accepted) > 0:
            if len(rejected) > 0 or len(dataset_warnings) > 0:
                acceptance_status = "ACCEPTED_WITH_WARNINGS"
                readiness = "REAL_DATA_READY_WITH_WARNINGS"
            else:
                acceptance_status = "ACCEPTED"
                readiness = "REAL_DATA_READY"
                
        dataset_summary = {
            "symbol_count": len(results),
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "benchmark_available": has_benchmark,
            "corporate_action_status": corp_action,
            "universe_status": universe,
            "source_type": source_prov,
            "acceptance_status": acceptance_status,
            "readiness": readiness,
            "warnings": dataset_warnings,
            "blockers": dataset_blockers,
            "files": results
        }
        
        self._write_manifest(dataset_summary)
        markdown_report = self._generate_markdown_report(dataset_summary, readiness)
        self._write_machine_report(dataset_summary)
        
        dataset_summary["report_markdown"] = markdown_report
        dataset_summary["dataset_acceptance"] = acceptance_status
        return dataset_summary

    def _write_manifest(self, summary: Dict[str, Any]):
        manifest_path = Path("data/processed/manifest.json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
            
    def _write_machine_report(self, summary: Dict[str, Any]):
        report_path = Path("reports/data_onboarding_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
            
    def _generate_markdown_report(self, summary: Dict[str, Any], readiness: str) -> str:
        report_path = Path("reports/data_onboarding_report.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        if readiness == "REAL_DATA_NOT_PROVISIONED":
            md = "# DATA ONBOARDING REPORT\n\nSTATUS: REAL_DATA_NOT_PROVISIONED\n\nNo valid CSV data found in `data/raw/historical`."
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(md)
            return md
            
        md = f"""# DATA ONBOARDING REPORT

## DATASET SUMMARY
- **Status**: {summary['acceptance_status']}
- **Readiness**: {summary['readiness']}
- **Total Files Evaluated**: {summary['symbol_count']}
- **Accepted**: {summary['accepted_count']}
- **Rejected**: {summary['rejected_count']}

## BENCHMARK
- **IHSG Available**: {summary['benchmark_available']}

## METADATA
- **Corporate Action**: {summary['corporate_action_status']}
- **Survivorship (Universe)**: {summary['universe_status']}
- **Source Type**: {summary['source_type']}

## WARNINGS
"""
        for w in summary["warnings"]:
            md += f"- {w}\n"
            
        md += "\n## ACCEPTED SYMBOLS\n"
        for f in summary["files"]:
            if f["validity"] in ["ACCEPTED", "ACCEPTED_WITH_WARNINGS"]:
                warns = ", ".join(f.get("warnings", []))
                md += f"- **{f['symbol']}** ({f['row_count']} rows, checksum: {f['checksum']}) - {warns}\n"
                
        md += "\n## REJECTED SYMBOLS\n"
        for f in summary["files"]:
            if f["validity"] == "REJECTED":
                errs = ", ".join(f.get("errors", []))
                md += f"- **{f['symbol']}** - {errs}\n"
                
        md += "\n## NEXT ACTION\n"
        if summary['acceptance_status'] == "REJECTED":
            md += "Resolve blockers and re-run onboarding."
        elif summary['acceptance_status'] == "ACCEPTED_WITH_WARNINGS":
            md += "Review warnings. Data is usable but may affect backtest quality."
        else:
            md += "Data is ready for real market backtesting."
            
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(md)
            
        return md
