from typing import Dict, Any
from pathlib import Path
import json
import hashlib
from core.orchestrator_schemas import AuditEvent

class AuditLedger:
    def __init__(self, log_dir: str = "state/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "ledger.jsonl"
        self.seen_events = set()
        
        # Load seen events for idempotency on restart
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            ev = json.loads(line)
                            self.seen_events.add(ev["event_id"])
                        except json.JSONDecodeError:
                            pass

    def log_event(self, job_id: str, timestamp: str, stage: str, event_type: str, status: str, metadata: Dict[str, Any] = None):
        # Deterministic Event ID
        event_key = f"{job_id}_{stage}_{event_type}_{status}"
        event_id = hashlib.md5(event_key.encode('utf-8')).hexdigest()
        
        if event_id in self.seen_events:
            return # Idempotent: don't log duplicate
            
        clean_metadata = {k: v for k, v in (metadata or {}).items() if "secret" not in k.lower() and "key" not in k.lower()}
        
        event = AuditEvent(
            event_id=event_id,
            job_id=job_id,
            timestamp=timestamp,
            stage=stage,
            event_type=event_type,
            status=status,
            metadata=clean_metadata
        )
        
        # Append-only
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
            
        self.seen_events.add(event_id)
