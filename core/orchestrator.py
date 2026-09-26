from pathlib import Path
from core.orchestrator_schemas import JobContext, JobState, FailureType
from core.idempotency import IdempotencyEngine
from core.retry import RetryPolicy
from core.audit_ledger import AuditLedger
from core.pipeline_metrics import PipelineMetrics
from core.health import HealthMonitor, HealthStatus
from core.pipeline_runner import PipelineRunner
from core.recovery import AtomicHelper
from core.decision import PortfolioContext
import datetime
import traceback
import json
import os

class Orchestrator:
    def __init__(self, queue_dir: str = "queue", state_dir: str = "state"):
        self.queue_dir = Path(queue_dir)
        self.processing_dir = self.queue_dir / "processing"
        self.completed_dir = self.queue_dir / "completed"
        self.failed_dir = self.queue_dir / "failed"
        self.dead_letter_dir = self.queue_dir / "dead_letter"
        
        for d in [self.queue_dir, self.processing_dir, self.completed_dir, self.failed_dir, self.dead_letter_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.idempotency = IdempotencyEngine(f"{state_dir}/idempotency")
        self.retry_policy = RetryPolicy(max_retries=3)
        self.audit = AuditLedger(f"{state_dir}/audit")
        self.metrics = PipelineMetrics(f"{state_dir}/metrics.json")
        self.health = HealthMonitor(f"{state_dir}/system_state.json")
        self.runner = PipelineRunner(state_dir)
        
    def process_job(self, job_id: str, payload: dict, portfolio: PortfolioContext):
        if self.health.check_health() != HealthStatus.HEALTHY:
            raise RuntimeError("System is not HEALTHY, pipeline paused.")
            
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        input_hash = JobContext.compute_hash(payload)
        
        job_ctx = JobContext(
            job_id=job_id,
            symbol=payload.get("symbol", "UNKNOWN"),
            created_at=now,
            updated_at=now,
            input_hash=input_hash
        )
        
        # Idempotency
        idemp_status = self.idempotency.check_and_record(job_id, input_hash)
        if idemp_status == "DUPLICATE":
            self.audit.log_event(job_id, now, "ORCHESTRATOR", "JOB_DUPLICATE_SKIPPED", "INFO")
            return
        elif idemp_status == "CONFLICT":
            self.audit.log_event(job_id, now, "ORCHESTRATOR", "JOB_IDEMPOTENCY_CONFLICT", "ERROR")
            self._to_dead_letter(job_ctx, payload, FailureType.IDEMPOTENCY, "Idempotency conflict on hash")
            return
            
        self.audit.log_event(job_id, now, "ORCHESTRATOR", "JOB_STARTED", "INFO")
        self.metrics.record_job_start()
        
        try:
            job_ctx.current_state = JobState.PROCESSING
            res = self.runner.run_pipeline(job_ctx, payload, portfolio)
            
            job_ctx.current_state = JobState.COMPLETED
            self.audit.log_event(job_id, datetime.datetime.now(datetime.timezone.utc).isoformat(), "ORCHESTRATOR", "JOB_COMPLETED", "INFO", {"decision": res["decision"]["action"]})
            self.metrics.record_job_completed(res["decision"]["action"])
            
        except Exception as e:
            err_str = str(e)
            failure_type = self.retry_policy.classify_error(e)
            job_ctx.last_error = err_str
            job_ctx.current_state = JobState.FAILED
            
            is_retryable = self.retry_policy.is_retryable(failure_type)
            
            if is_retryable and job_ctx.retry_count < job_ctx.max_retries:
                job_ctx.retry_count += 1
                job_ctx.current_state = JobState.RETRY
                self.audit.log_event(job_id, datetime.datetime.now(datetime.timezone.utc).isoformat(), "ORCHESTRATOR", "JOB_RETRY", "WARN", {"error": err_str})
                self.metrics.record_job_retry()
                # In real scenario, it would go back to queue. For now, we simulate just throwing up the error or dead lettering if exhausted.
                # Just simulating exhausted immediately if we were synchronous, but let's just record it.
                self._to_failed(job_ctx, payload, failure_type, err_str)
            else:
                job_ctx.current_state = JobState.DEAD_LETTER
                self.audit.log_event(job_id, datetime.datetime.now(datetime.timezone.utc).isoformat(), "ORCHESTRATOR", "JOB_DEAD_LETTER", "ERROR", {"error": err_str})
                self.metrics.record_job_failed("ORCHESTRATOR", is_dead_letter=True)
                self._to_dead_letter(job_ctx, payload, failure_type, err_str)
                
    def _to_dead_letter(self, job_ctx: JobContext, payload: dict, f_type: FailureType, err: str):
        dl_payload = {
            "job_context": job_ctx.model_dump(),
            "original_payload": payload,
            "failure_type": f_type.value,
            "error": err,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        AtomicHelper.write_json(self.dead_letter_dir / f"{job_ctx.job_id}.json", dl_payload)

    def _to_failed(self, job_ctx: JobContext, payload: dict, f_type: FailureType, err: str):
        fail_payload = {
            "job_context": job_ctx.model_dump(),
            "original_payload": payload,
            "failure_type": f_type.value,
            "error": err,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        AtomicHelper.write_json(self.failed_dir / f"{job_ctx.job_id}.json", fail_payload)
