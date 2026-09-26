import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import hashlib

class ExperimentRegistry:
    def __init__(self, registry_file: str = "reports/experiment_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_file.exists():
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump({"experiments": []}, f)
                
    def _hash_config(self, config: Dict[str, Any]) -> str:
        s = json.dumps(config, sort_keys=True)
        return hashlib.sha256(s.encode('utf-8')).hexdigest()[:12]

    def log_experiment(self, 
                       dataset_snapshot: str, 
                       config: Dict[str, Any], 
                       metrics: Dict[str, Any],
                       hypothesis: str = "General backtest"):
                       
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        exp_id = f"EXP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        config_hash = self._hash_config(config)
        
        record = {
            "experiment_id": exp_id,
            "timestamp": datetime.now().isoformat(),
            "hypothesis": hypothesis,
            "dataset_snapshot": dataset_snapshot,
            "config_hash": config_hash,
            "config": config,
            "metrics": metrics
        }
        
        data["experiments"].append(record)
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        return exp_id
