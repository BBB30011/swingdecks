from typing import Dict, Any
from pathlib import Path
import json

class PipelineMetrics:
    def __init__(self, metrics_file: str = "state/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = {
            "jobs_total": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "jobs_retry": 0,
            "jobs_dead_letter": 0,
            "stage_failure_count": {},
            "decision_buy": 0,
            "decision_wait": 0,
            "decision_hold": 0,
            "decision_sell": 0,
            "decision_avoid": 0,
            "total_processing_time_ms": 0.0
        }
        self.load()

    def load(self):
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    self.metrics.update(data)
            except Exception:
                pass

    def save(self):
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f)

    def record_job_start(self):
        self.metrics["jobs_total"] += 1
        self.save()
        
    def record_job_completed(self, decision_action: str = None, processing_time_ms: float = 0):
        self.metrics["jobs_completed"] += 1
        self.metrics["total_processing_time_ms"] += processing_time_ms
        if decision_action:
            key = f"decision_{decision_action.lower()}"
            if key in self.metrics:
                self.metrics[key] += 1
        self.save()

    def record_job_failed(self, stage: str, is_dead_letter: bool = False):
        self.metrics["jobs_failed"] += 1
        if is_dead_letter:
            self.metrics["jobs_dead_letter"] += 1
            
        self.metrics["stage_failure_count"][stage] = self.metrics["stage_failure_count"].get(stage, 0) + 1
        self.save()

    def record_job_retry(self):
        self.metrics["jobs_retry"] += 1
        self.save()
