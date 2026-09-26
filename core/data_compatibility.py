import pandas as pd
import csv
from pathlib import Path
from typing import Dict, Any, List

class DataCompatibilityChecker:
    """
    Checks compatibility of real historical IDX datasets.
    Does not modify files. Operates on raw data safely.
    """
    def __init__(self, directory: str = "data/raw/historical"):
        self.directory = Path(directory)
        
    def _detect_delimiter(self, filepath: Path) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                header = f.readline()
                sniffer = csv.Sniffer()
                # Default to comma if sniffer fails
                try:
                    dialect = sniffer.sniff(header, delimiters=[',', ';', '\t', '|'])
                    return dialect.delimiter
                except:
                    return ','
        except:
            return ','
            
    def _detect_columns(self, columns: List[str]) -> Dict[str, str]:
        # Mapping standard required columns to their detected counterparts
        mapping = {
            "timestamp": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": None
        }
        
        col_lower = {c.lower(): c for c in columns}
        
        # Temporal
        for t in ["timestamp", "date", "datetime", "time"]:
            if t in col_lower:
                mapping["timestamp"] = col_lower[t]
                break
                
        # OHLCV
        for c in ["open", "high", "low", "close", "volume"]:
            if c in col_lower:
                mapping[c] = col_lower[c]
                
        return mapping
        
    def _detect_symbol(self, filename: str) -> str:
        stem = Path(filename).stem.upper()
        if "_" in stem or "-" in stem or " " in stem:
            return "AMBIGUOUS_SYMBOL"
        return stem

    def check_file(self, filepath: Path) -> Dict[str, Any]:
        result = {
            "file": filepath.name,
            "status": "COMPATIBLE",
            "symbol": self._detect_symbol(filepath.name),
            "delimiter": self._detect_delimiter(filepath),
            "columns_detected": {},
            "missing_columns": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            df = pd.read_csv(filepath, sep=result["delimiter"], nrows=0) # Only read header
        except Exception as e:
            result["status"] = "INCOMPATIBLE"
            result["errors"].append(f"Failed to read CSV: {str(e)}")
            return result
            
        mapping = self._detect_columns(list(df.columns))
        result["columns_detected"] = mapping
        
        missing = [k for k, v in mapping.items() if v is None]
        if missing:
            result["status"] = "INCOMPATIBLE"
            result["missing_columns"] = missing
            result["errors"].append(f"Missing required columns: {missing}")
            return result
            
        # Try full read for content compatibility
        try:
            df = pd.read_csv(filepath, sep=result["delimiter"])
            ts_col = mapping["timestamp"]
            duplicate_ts = df[ts_col].duplicated().sum()
            if duplicate_ts > 0:
                result["status"] = "INCOMPATIBLE"
                result["errors"].append(f"Duplicate timestamp detected ({duplicate_ts})")
                
            # Date range & records
            result["records"] = len(df)
            if len(df) > 0:
                result["first_date"] = str(df[ts_col].iloc[0])
                result["last_date"] = str(df[ts_col].iloc[-1])
            else:
                result["first_date"] = None
                result["last_date"] = None
                
            if result["records"] < 100:
                result["warnings"].append("Insufficient history (<100 records)")
                
        except Exception as e:
            result["status"] = "INCOMPATIBLE"
            result["errors"].append(f"Content validation failed: {str(e)}")
            
        return result
        
    def check_directory(self) -> Dict[str, Any]:
        if not self.directory.exists() or not any(self.directory.iterdir()):
            return {"status": "REAL_DATA_NOT_PROVISIONED"}
            
        files = list(self.directory.glob("*.csv"))
        if not files:
            return {"status": "REAL_DATA_NOT_PROVISIONED"}
            
        results = []
        symbols_seen = set()
        duplicate_symbols = set()
        
        benchmark_detected = False
        
        for f in files:
            res = self.check_file(f)
            sym = res["symbol"]
            
            if sym == "IHSG" or sym == "^JKSE" or sym == "JKSE":
                benchmark_detected = True
                
            if sym != "AMBIGUOUS_SYMBOL":
                if sym in symbols_seen:
                    duplicate_symbols.add(sym)
                symbols_seen.add(sym)
                
            results.append(res)
            
        for r in results:
            if r["symbol"] in duplicate_symbols:
                r["warnings"].append("DUPLICATE_SYMBOL_SOURCE")
                
        dataset_status = "READY_FOR_REAL_BACKTEST"
        incompatible = [r for r in results if r["status"] == "INCOMPATIBLE"]
        warnings = [r for r in results if len(r["warnings"]) > 0]
        
        if incompatible or duplicate_symbols or not benchmark_detected:
            dataset_status = "NOT_READY"
        elif warnings:
            dataset_status = "READY_WITH_WARNINGS"
            
        report = {
            "status": "PROVISIONED",
            "dataset_status": dataset_status,
            "total_files": len(results),
            "benchmark_detected": benchmark_detected,
            "duplicate_symbols": list(duplicate_symbols),
            "files": results
        }
        self._generate_reports(report)
        return report

    def _generate_reports(self, report: Dict[str, Any]):
        md_path = Path("reports/data_compatibility_report.md")
        md_path.parent.mkdir(parents=True, exist_ok=True)
        
        md = f"""# DATA COMPATIBILITY REPORT

## DATASET STATUS: {report['dataset_status']}
- **Total Files**: {report['total_files']}
- **Benchmark Detected**: {report['benchmark_detected']}
- **Duplicate Symbols**: {report['duplicate_symbols']}

## FILES

"""
        for f in report['files']:
            md += f"### FILE: {f['file']}\n"
            md += f"- **Detected Symbol**: {f['symbol']}\n"
            md += f"- **Delimiter**: `{f['delimiter']}`\n"
            md += f"- **Status**: {f['status']}\n"
            if 'records' in f:
                md += f"- **Records**: {f['records']}\n"
                md += f"- **First Date**: {f['first_date']}\n"
                md += f"- **Last Date**: {f['last_date']}\n"
            if f['columns_detected']:
                md += "- **Mapping**:\n"
                for k, v in f['columns_detected'].items():
                    md += f"  - `{k}` -> `{v}`\n"
            if f['missing_columns']:
                md += f"- **Missing**: {', '.join(f['missing_columns'])}\n"
            if f['warnings']:
                md += f"- **Warnings**: {', '.join(f['warnings'])}\n"
            if f['errors']:
                md += f"- **Errors**: {', '.join(f['errors'])}\n"
            md += "\n"
            
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
            
        # Also generate Checklist
        chk_path = Path("reports/dataset_operator_checklist.md")
        chk = f"""# OPERATOR CHECKLIST

- [{'x' if report['status'] == 'PROVISIONED' else ' '}] Real IDX historical CSV tersedia
- [{'x' if report['benchmark_detected'] else ' '}] IHSG tersedia
- [{'x' if not any(len(f['missing_columns']) > 0 for f in report['files']) else ' '}] OHLCV lengkap
- [{'x' if not any('Duplicate timestamp' in str(f['errors']) for f in report['files']) else ' '}] Timestamp valid
- [{'x' if not report['duplicate_symbols'] else ' '}] Tidak ada duplicate symbol
- [{'x' if report['dataset_status'] in ['READY_FOR_REAL_BACKTEST', 'READY_WITH_WARNINGS'] else ' '}] Dataset accepted
"""
        with open(chk_path, "w", encoding="utf-8") as f:
            f.write(chk)
