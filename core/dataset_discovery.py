import json
from pathlib import Path
import hashlib
import pandas as pd
from typing import Dict, Any

class DatasetDiscovery:
    def __init__(self, directory: str = "data/raw/historical"):
        self.directory = Path(directory)
        
    def run_discovery(self, output_file: str = "reports/dataset_inventory.json") -> Dict[str, Any]:
        inventory = {
            "status": "UNKNOWN",
            "files": [],
            "total_symbols": 0,
            "readiness": "REAL_DATA_NOT_PROVISIONED"
        }
        
        if not self.directory.exists() or not any(self.directory.iterdir()):
            inventory["status"] = "REAL_DATA_NOT_PROVISIONED"
            inventory["readiness"] = "REAL_DATA_NOT_PROVISIONED"
            self._save(inventory, output_file)
            return inventory
            
        inventory["status"] = "PROVISIONED"
        
        for file_path in self.directory.glob("*.csv"):
            symbol = file_path.stem
            try:
                df = pd.read_csv(file_path)
                with open(file_path, "rb") as f:
                    checksum = hashlib.sha256(f.read()).hexdigest()
                    
                first_ts = df['timestamp'].iloc[0] if 'timestamp' in df.columns and not df.empty else "UNKNOWN"
                last_ts = df['timestamp'].iloc[-1] if 'timestamp' in df.columns and not df.empty else "UNKNOWN"
                
                inventory["files"].append({
                    "symbol": symbol,
                    "file": file_path.name,
                    "record_count": len(df),
                    "first_timestamp": str(first_ts),
                    "last_timestamp": str(last_ts),
                    "timezone": "Asia/Jakarta",
                    "corporate_action_status": "UNKNOWN",
                    "universe_status": "UNKNOWN",
                    "source": "UNKNOWN",
                    "checksum": checksum,
                    "readiness": "VALID" if len(df) >= 200 else "PARTIAL"
                })
            except Exception as e:
                inventory["files"].append({
                    "symbol": symbol,
                    "file": file_path.name,
                    "error": str(e),
                    "readiness": "INVALID"
                })
                
        inventory["total_symbols"] = len(inventory["files"])
        if inventory["total_symbols"] > 0:
            inventory["readiness"] = "REAL_DATA_READY"
            
        self._save(inventory, output_file)
        return inventory
        
    def _save(self, data: Dict[str, Any], output_file: str):
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
