import os
import json
from pathlib import Path
from pydantic import BaseModel

class FileQueue:
    def __init__(self, queue_directory):
        self.queue_dir = Path(queue_directory)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        # Base dir untuk meresolve completed & failed
        self.base_dir = self.queue_dir.parent
        self.completed_dir = self.base_dir / "completed"
        self.failed_dir = self.base_dir / "failed"
        
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)

    def enqueue(self, job_id: str, payload):
        if not isinstance(job_id, str):
            raise TypeError("job_id wajib string")
            
        # Dukungan Pydantic payload langsung didecode menjadi dictionary
        if isinstance(payload, BaseModel):
            payload = payload.model_dump()
            
        if not isinstance(payload, dict):
            raise TypeError("payload wajib dictionary atau Pydantic Model")
            
        target_file = self.queue_dir / f"{job_id}.json"
        tmp_file = self.queue_dir / f"{job_id}.json.tmp"
        
        if target_file.exists():
            raise FileExistsError(f"Job dengan ID {job_id} sudah ada dalam queue.")
            
        data = {
            "job_id": job_id,
            "payload": payload
        }
        
        # Atomic Write
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())  
            
        os.replace(tmp_file, target_file)

    def dequeue(self):
        json_files = sorted(self.queue_dir.glob("*.json"))
        
        for target_file in json_files:
            processing_file = self.queue_dir / f"{target_file.name}.processing"
            
            try:
                # Atomic rename resolves race condition
                os.rename(target_file, processing_file)
            except FileNotFoundError:
                # Another worker picked this up before we could rename
                continue
            except FileExistsError:
                # Processing file already exists
                continue
                
            try:
                with open(processing_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                # Rename back or fail it
                os.rename(processing_file, self.failed_dir / target_file.name)
                raise ValueError(f"File JSON corrupt: {target_file.name}. Error: {e}")
                
        return None

    def complete(self, job_id: str):
        src = self.queue_dir / f"{job_id}.json.processing"
        dst = self.completed_dir / f"{job_id}.json"
        if src.exists():
            os.replace(src, dst)
        else:
            raise FileNotFoundError(f"Job file tidak ditemukan untuk diselesaikan: {src}")

    def fail(self, job_id: str):
        src = self.queue_dir / f"{job_id}.json.processing"
        dst = self.failed_dir / f"{job_id}.json"
        if src.exists():
            os.replace(src, dst)
        else:
            raise FileNotFoundError(f"Job file tidak ditemukan untuk ditandai gagal: {src}")
            
    def requeue(self, job_id: str):
        src = self.queue_dir / f"{job_id}.json.processing"
        dst = self.queue_dir / f"{job_id}.json"
        if src.exists():
            os.replace(src, dst)
        else:
            raise FileNotFoundError(f"Job file tidak ditemukan untuk direqueue: {src}")
