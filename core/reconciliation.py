from pathlib import Path
from typing import Dict, Any

class ReconciliationReport:
    def __init__(self):
        self.healthy = True
        self.warnings = []
        self.errors = []
        self.repaired_items = []

class Reconciler:
    def __init__(self, queue_dir: str = "queue", state_dir: str = "state"):
        self.queue_dir = Path(queue_dir)
        self.state_dir = Path(state_dir)
        
    def reconcile(self) -> ReconciliationReport:
        report = ReconciliationReport()
        
        # Check orphan .tmp files
        for tmp_file in self.queue_dir.rglob("*.tmp"):
            report.healthy = False
            report.warnings.append(f"Orphan tmp file found: {tmp_file}")
            
        # Check corrupt json
        import json
        for json_file in self.queue_dir.rglob("*.json"):
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except Exception as e:
                report.healthy = False
                report.errors.append(f"Corrupt JSON: {json_file}")
                
        return report
