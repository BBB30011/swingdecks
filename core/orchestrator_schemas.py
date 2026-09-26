from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import json

class FailureType(str, Enum):
    TRANSIENT = "TRANSIENT"
    VALIDATION = "VALIDATION"
    DATA = "DATA"
    SECURITY = "SECURITY"
    BUSINESS_RULE = "BUSINESS_RULE"
    IDEMPOTENCY = "IDEMPOTENCY"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"

class JobState(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    QUANT_READY = "QUANT_READY"
    RESEARCH_READY = "RESEARCH_READY"
    RED_TEAM_READY = "RED_TEAM_READY"
    COMMITTEE_REVIEW = "COMMITTEE_REVIEW"
    RISK_CHECK = "RISK_CHECK"
    DECISION_READY = "DECISION_READY"
    COMPLETED = "COMPLETED"
    RETRY = "RETRY"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"

class JobContext(BaseModel):
    job_id: str
    symbol: str
    created_at: str
    current_state: JobState = JobState.CREATED
    retry_count: int = 0
    max_retries: int = 3
    last_error: str = ""
    updated_at: str
    input_hash: str
    pipeline_version: str = "1.0.0"
    
    @staticmethod
    def compute_hash(payload: Dict[str, Any]) -> str:
        # Exclude dynamic timestamps from hash
        clean_payload = {k: v for k, v in payload.items() if k not in ["timestamp", "created_at", "updated_at"]}
        sorted_json = json.dumps(clean_payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(sorted_json.encode('utf-8')).hexdigest()

class AuditEvent(BaseModel):
    event_id: str
    job_id: str
    timestamp: str
    stage: str
    event_type: str
    status: str
    metadata: Dict[str, Any] = {}
