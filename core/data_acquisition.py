import time
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

from core.data_source import DataSourceFactory, MarketDataSource, DataUnavailableError, DataValidationError
from core.snapshot_manager import SnapshotManager
from core.schemas import MarketSnapshot

import yfinance # For getting version

class DataAcquisitionEngine:
    def __init__(self, config: dict = None):
        self.config = config or {}
        # Make sure provider is YFINANCE for acquisition unless specified
        if "provider" not in self.config.get("data_source", {}):
            if "data_source" not in self.config:
                self.config["data_source"] = {}
            self.config["data_source"]["provider"] = "YFINANCE"
            
        self.provider = DataSourceFactory.create(self.config)
        self.snapshot_manager = SnapshotManager(data_dir=self.config.get("data_dir", "data"))
        self.manifest: Dict[str, Any] = {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "symbols": {},
            "benchmark": {},
            "readiness": "NOT_READY",
            "warnings": [],
            "provider_info": {
                "name": self.config["data_source"]["provider"],
                "yfinance_version": yfinance.__version__,
                "source": "Yahoo Finance via yfinance"
            }
        }
        
    def acquire_symbols(self, symbols: List[str]) -> None:
        for sym in symbols:
            try:
                # Add a small rate limit sleep
                time.sleep(0.5)
                
                print(f"[ACQUIRE] Fetching {sym}...")
                snapshot = self.provider.get_snapshot(sym)
                
                # Check Data Gaps & Quality
                if not snapshot.bars:
                    raise DataValidationError("Empty bars returned.")
                    
                first_date = snapshot.bars[0].timestamp
                last_date = snapshot.bars[-1].timestamp
                record_count = len(snapshot.bars)
                
                # We expect at least ~700 bars for 3 years
                quality = "GOOD"
                if record_count < 250:
                    quality = "INSUFFICIENT"
                elif record_count < 700:
                    quality = "PARTIAL"
                    
                # Save Raw JSON
                # Convert bars back to dict for raw storage to mimic API response caching
                raw_data = json.dumps([b.model_dump() for b in snapshot.bars])
                metadata = {
                    "symbol": sym,
                    "source": "Yahoo Finance",
                    "provider": self.config["data_source"]["provider"],
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "record_count": record_count,
                    "first_date": first_date,
                    "last_date": last_date,
                    "quality": quality,
                    "adjustment_status": "UNADJUSTED", # default yfinance auto_adjust=False
                    "corporate_action_status": "PARTIAL" # yf handles basic splits/divs on the backend, but we requested unadjusted
                }
                
                filepath = self.snapshot_manager.save_raw_data(sym, raw_data, metadata)
                
                self.manifest["symbols"][sym] = {
                    "filepath": str(filepath),
                    "checksum_sha256": metadata["checksum_sha256"],
                    "record_count": record_count,
                    "first_date": first_date,
                    "last_date": last_date,
                    "quality": quality
                }
                
            except Exception as e:
                print(f"[ERROR] Failed to acquire {sym}: {e}")
                self.manifest["warnings"].append(f"Failed to acquire {sym}: {str(e)}")
                
    def acquire_benchmark(self, benchmark_symbol: str = "IHSG") -> None:
        try:
            print(f"[ACQUIRE] Fetching Benchmark {benchmark_symbol}...")
            snapshot = self.provider.get_snapshot(benchmark_symbol)
            
            raw_data = json.dumps([b.model_dump() for b in snapshot.bars])
            metadata = {
                "symbol": benchmark_symbol,
                "source": "Yahoo Finance",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "record_count": len(snapshot.bars)
            }
            filepath = self.snapshot_manager.save_raw_data(benchmark_symbol, raw_data, metadata)
            
            self.manifest["benchmark"] = {
                "symbol": benchmark_symbol,
                "filepath": str(filepath),
                "checksum_sha256": metadata["checksum_sha256"],
                "record_count": len(snapshot.bars)
            }
        except Exception as e:
            print(f"[ERROR] Failed to acquire Benchmark {benchmark_symbol}: {e}")
            self.manifest["warnings"].append(f"Failed to acquire Benchmark {benchmark_symbol}: {str(e)}")

    def determine_readiness(self) -> str:
        # Rules for RESEARCH_READY:
        # - Benchmark must exist
        # - Most symbols must be GOOD or PARTIAL
        
        if not self.manifest.get("benchmark"):
            self.manifest["warnings"].append("Missing Benchmark.")
            return "NOT_READY"
            
        if not self.manifest["symbols"]:
            self.manifest["warnings"].append("No symbols acquired.")
            return "NOT_READY"
            
        insufficient_count = sum(1 for s in self.manifest["symbols"].values() if s["quality"] == "INSUFFICIENT")
        total_symbols = len(self.manifest["symbols"])
        
        if insufficient_count > total_symbols * 0.5:
            self.manifest["warnings"].append(f"More than 50% of symbols have INSUFFICIENT history.")
            return "NOT_READY"
            
        if self.manifest["warnings"]:
            return "READY_WITH_WARNINGS"
            
        return "RESEARCH_READY"
        
    def finalize_snapshot(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        self.manifest["readiness"] = self.determine_readiness()
        # Log survivorship bias since we use current lists
        self.manifest["survivorship_risk"] = "HIGH" 
        self.manifest["historical_universe"] = "NOT_AVAILABLE"
        
        snapshot_id = self.snapshot_manager.create_snapshot(date_str, self.manifest)
        print(f"\n[SNAPSHOT] Created {snapshot_id} | Status: {self.manifest['readiness']}")
        return snapshot_id
