from typing import Dict, Any, List
import json
from pathlib import Path

class DatasetReadinessEngine:
    @staticmethod
    def evaluate(manifest: Dict[str, Any], audit_results: List[Any] = None) -> Dict[str, Any]:
        data_origin = manifest.get("data_origin", "UNKNOWN")
        invalid_symbols = manifest.get("invalid_symbols", [])
        warning_symbols = manifest.get("warning_symbols", [])
        valid_symbols = manifest.get("valid_symbols", [])
        gap_summary = manifest.get("gap_summary", "NO_GAP")
        
        warnings = []
        blocking_issues = []
        
        # Base initialization
        status = "REAL_DATA_READY"
        
        if data_origin != "REAL_HISTORICAL" and data_origin != "MIXED":
            status = "REAL_DATA_NOT_PROVISIONED"
            blocking_issues.append("REAL_HISTORICAL_DATASET_NOT_PROVISIONED")
        
        if not manifest.get("benchmark_available", False):
            warnings.append("Benchmark (IHSG) not available. Agent will use graceful degradation.")
            
        if manifest.get("corporate_action_status") == "UNKNOWN":
            warnings.append("CORPORATE_ACTION_STATUS_UNKNOWN")
            
        if manifest.get("universe_method") == "CURRENT_UNIVERSE":
            warnings.append("POSSIBLE_SURVIVORSHIP_BIAS: Current universe used, missing delisted stocks.")
            
        if invalid_symbols:
            warnings.append(f"{len(invalid_symbols)} symbols are structurally invalid.")
            
        if warning_symbols:
            warnings.append(f"{len(warning_symbols)} symbols have data warnings (gaps, zeros).")
            
        has_insufficient = len(manifest.get("insufficient_history_symbols", [])) > 0
            
        if gap_summary == "INSUFFICIENT_DATA" or has_insufficient:
            if status != "REAL_DATA_NOT_PROVISIONED":
                status = "REAL_DATA_PARTIAL"
                
        if len(valid_symbols) == 0 and len(warning_symbols) == 0:
            blocking_issues.append("No valid symbols found in dataset.")
            if status != "REAL_DATA_NOT_PROVISIONED":
                status = "REAL_DATA_INVALID"
                
        if status == "REAL_DATA_READY" and warnings:
            status = "REAL_DATA_READY_WITH_WARNINGS"
            
        return {
            "status": status,
            "warnings": warnings,
            "blocking_issues": blocking_issues,
            "manifest_summary": {
                "dataset_id": manifest.get("dataset_id"),
                "data_origin": data_origin,
                "period": manifest.get("period", {}),
                "symbol_count": manifest.get("symbol_count", 0),
                "record_count": manifest.get("record_count", 0),
                "valid": len(valid_symbols),
                "warnings": len(warning_symbols),
                "invalid": len(invalid_symbols),
                "benchmark_available": manifest.get("benchmark_available", False),
                "corporate_action_status": manifest.get("corporate_action_status", "UNKNOWN"),
                "universe_method": manifest.get("universe_method", "UNKNOWN"),
                "gap_summary": gap_summary,
                "insufficient_history": len(manifest.get("insufficient_history_symbols", []))
            }
        }

    @staticmethod
    def generate_report(readiness_result: Dict[str, Any], output_dir: str = "reports"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        with open(f"{output_dir}/data_readiness_report.json", "w") as f:
            json.dump(readiness_result, f, indent=4)
            
        summary = readiness_result["manifest_summary"]
        
        md = f"""# Data Readiness Report

**Status:** {readiness_result['status']}

## Overview
- **Dataset ID:** {summary['dataset_id']}
- **Origin:** {summary['data_origin']}
- **Period:** {summary['period'].get('start', '')} to {summary['period'].get('end', '')}
- **Total Symbols:** {summary['symbol_count']}
- **Total Records:** {summary['record_count']}

## Quality
- **Valid Symbols:** {summary['valid']}
- **Warning Symbols:** {summary['warnings']}
- **Invalid Symbols:** {summary['invalid']}
- **Insufficient History Symbols:** {summary['insufficient_history']}
- **Gap Status:** {summary['gap_summary']}

## Metadata
- **Benchmark Available:** {summary['benchmark_available']}
- **Corporate Action:** {summary['corporate_action_status']}
- **Universe Method:** {summary['universe_method']}

## Warnings
"""
        for w in readiness_result["warnings"]:
            md += f"- {w}\n"
            
        md += "\n## Blocking Issues\n"
        for b in readiness_result["blocking_issues"]:
            md += f"- {b}\n"
            
        with open(f"{output_dir}/data_readiness_report.md", "w") as f:
            f.write(md)
