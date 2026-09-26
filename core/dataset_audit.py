from typing import List, Dict, Any, Tuple
from core.schemas import MarketBar

class DatasetAuditReport:
    def __init__(self):
        self.status = "VALID" # VALID, VALID_WITH_WARNINGS, INVALID
        self.errors = []
        self.warnings = []
        self.infos = []
        self.gap_count = 0
        self.largest_gap = 0
        self.gap_status = "NO_GAP"
        
    def add_error(self, msg: str):
        self.errors.append(msg)
        self.status = "INVALID"
        
    def add_warning(self, msg: str):
        self.warnings.append(msg)
        if self.status == "VALID":
            self.status = "VALID_WITH_WARNINGS"
            
    def add_info(self, msg: str):
        self.infos.append(msg)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
            "gap_count": self.gap_count,
            "largest_gap": self.largest_gap,
            "gap_status": self.gap_status
        }

class DatasetAuditor:
    @staticmethod
    def audit(bars: List[MarketBar], as_of_timestamp: str = None, global_timeline: List[str] = None) -> DatasetAuditReport:
        report = DatasetAuditReport()
        
        if not bars:
            report.add_error("Empty dataset")
            return report
            
        timestamps = []
        seen = set()
        
        for bar in bars:
            # Temporal rules
            if bar.timestamp in seen:
                report.add_error(f"Duplicate timestamp detected: {bar.timestamp}")
            seen.add(bar.timestamp)
            timestamps.append(bar.timestamp)
            
            if as_of_timestamp and bar.timestamp > as_of_timestamp:
                report.add_error(f"Future timestamp detected: {bar.timestamp} > {as_of_timestamp}")
                
            # OHLCV rules (some caught by Pydantic, some here for safety/warning)
            import math
            if math.isnan(bar.open) or math.isnan(bar.close) or math.isnan(bar.high) or math.isnan(bar.low):
                report.add_error(f"NaN detected at {bar.timestamp}")
                
            if bar.volume == 0:
                report.add_warning(f"Zero volume at {bar.timestamp}")
                
            # extreme price movement gap check (e.g., > 50% single day)
            # just structural tracking is fine for now
            
        # Unsorted timestamps
        if timestamps != sorted(timestamps):
            report.add_error("Timestamps are not strictly ascending")
            
        # Gap analysis
        if global_timeline and timestamps:
            try:
                start_idx = global_timeline.index(timestamps[0])
                end_idx = global_timeline.index(timestamps[-1])
                expected_bars = end_idx - start_idx + 1
                actual_bars = len(timestamps)
                gap_count = expected_bars - actual_bars
                
                if gap_count > 0:
                    report.gap_status = "GAP_DETECTED"
                    report.gap_count = gap_count
                    
                largest_gap = 0
                for i in range(1, len(timestamps)):
                    idx1 = global_timeline.index(timestamps[i-1])
                    idx2 = global_timeline.index(timestamps[i])
                    gap = idx2 - idx1 - 1
                    if gap > largest_gap:
                        largest_gap = gap
                        
                report.largest_gap = largest_gap
                
                if largest_gap > 5:
                    report.add_warning(f"Abnormal gap detected: {largest_gap} bars")
                elif gap_count > 0:
                    report.add_info(f"Normal gaps detected: {gap_count} missing bars")
                    
            except ValueError:
                report.gap_status = "INSUFFICIENT_DATA"
                report.add_warning("Timestamps not fully aligned with global timeline")

        return report

import json
from pathlib import Path

class DatasetQualitySummary:
    @staticmethod
    def generate_summary(manifest: Dict[str, Any]) -> str:
        return f"""Dataset:
{manifest.get('dataset_id', 'UNKNOWN')}

Period:
{manifest.get('period', {}).get('start', '')} -> {manifest.get('period', {}).get('end', '')}

Symbols:
{len(manifest.get('symbols', []))}

Records:
{manifest.get('record_count', 0)}

Valid:
{len(manifest.get('valid_symbols', []))}

Valid with warnings:
{len(manifest.get('warning_symbols', []))}

Invalid:
{len(manifest.get('invalid_symbols', []))}

Gap status:
{manifest.get('data_quality_summary', {}).get('overall_gap_status', 'UNKNOWN')}

Corporate Action:
{manifest.get('corporate_action_status', 'UNKNOWN')}

Universe:
{manifest.get('universe_method', 'UNKNOWN')}

Look-ahead:
{manifest.get('data_quality_summary', {}).get('look_ahead', 'FAIL')}

Survivorship:
{manifest.get('data_quality_summary', {}).get('survivorship', 'UNKNOWN')}
"""

class DatasetManifest:
    @staticmethod
    def create(dataset_id: str, snapshots: List[Any], corporate_action_status="UNKNOWN", universe_method="CURRENT_UNIVERSE") -> Dict[str, Any]:
        valid = []
        warning = []
        invalid = []
        insufficient_history_symbols = []
        record_count = 0
        min_ts = "9999-99-99"
        max_ts = "0000-00-00"
        
        has_gaps = False
        insufficient = False
        
        data_origins = set()
        benchmark_available = False
        
        for snap in snapshots:
            if getattr(snap, 'symbol', '') == 'IHSG':
                benchmark_available = True
                
            meta = getattr(snap, 'metadata', None)
            if meta:
                record_count += meta.record_count
                
                origin = getattr(meta, 'data_origin', 'UNKNOWN')
                data_origins.add(origin)
                
                if getattr(meta, 'benchmark_available', False):
                    benchmark_available = True
                    
                if meta.start_timestamp and meta.start_timestamp < min_ts:
                    min_ts = meta.start_timestamp
                if meta.end_timestamp and meta.end_timestamp > max_ts:
                    max_ts = meta.end_timestamp
                    
                if meta.audit_status == "VALID":
                    valid.append(snap.symbol)
                elif meta.audit_status == "VALID_WITH_WARNINGS":
                    warning.append(snap.symbol)
                else:
                    invalid.append(snap.symbol)
                    
                if meta.gap_status == "GAP_DETECTED":
                    has_gaps = True
                elif meta.gap_status == "INSUFFICIENT_DATA":
                    insufficient = True
                    insufficient_history_symbols.append(snap.symbol)
            else:
                valid.append(snap.symbol)
                record_count += len(snap.bars)
                data_origins.add("UNKNOWN")
                if snap.bars:
                    if snap.bars[0].timestamp < min_ts: min_ts = snap.bars[0].timestamp
                    if snap.bars[-1].timestamp > max_ts: max_ts = snap.bars[-1].timestamp
        
        overall_gap = "NO_GAP"
        if insufficient:
            overall_gap = "INSUFFICIENT_DATA"
        elif has_gaps:
            overall_gap = "GAP_DETECTED"
            
        final_origin = "UNKNOWN"
        if len(data_origins) == 1:
            final_origin = list(data_origins)[0]
        elif "REAL_HISTORICAL" in data_origins and "SYNTHETIC" in data_origins:
            final_origin = "MIXED"
        elif "REAL_HISTORICAL" in data_origins:
            final_origin = "REAL_HISTORICAL"
        elif "SYNTHETIC" in data_origins:
            final_origin = "SYNTHETIC"
            
        manifest = {
            "dataset_id": dataset_id,
            "data_origin": final_origin,
            "market": "IDX",
            "symbols": valid + warning + invalid,
            "symbol_count": len(valid) + len(warning) + len(invalid),
            "record_count": record_count,
            "period": {
                "start": min_ts if min_ts != "9999-99-99" else "",
                "end": max_ts if max_ts != "0000-00-00" else ""
            },
            "frequency": "1D",
            "valid_symbols": valid,
            "warning_symbols": warning,
            "invalid_symbols": invalid,
            "insufficient_history_symbols": insufficient_history_symbols,
            "gap_summary": overall_gap,
            "corporate_action_status": corporate_action_status,
            "universe_method": universe_method,
            "benchmark_available": benchmark_available,
            "generated_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            "checksum": "NOT_CALCULATED"
        }
        return manifest
        
    @staticmethod
    def save(manifest: Dict[str, Any], path: str = "data/processed/manifest.json"):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
