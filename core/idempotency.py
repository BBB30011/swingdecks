from typing import Dict, Optional
from pathlib import Path
import json

class IdempotencyEngine:
    def __init__(self, storage_dir: str = "state/idempotency"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def check_and_record(self, job_id: str, input_hash: str) -> str:
        """
        Returns 'NEW', 'DUPLICATE', or 'CONFLICT'
        """
        # Security/path injection protection
        safe_job_id = "".join(c for c in job_id if c.isalnum() or c in "-_")
        if not safe_job_id or safe_job_id != job_id:
            raise ValueError("Invalid job_id format - potential path traversal")
            
        file_path = self.storage_dir / f"{safe_job_id}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if data.get("input_hash") == input_hash:
                return "DUPLICATE"
            else:
                return "CONFLICT"
                
        # Record new
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"job_id": safe_job_id, "input_hash": input_hash}, f)
            
        return "NEW"
