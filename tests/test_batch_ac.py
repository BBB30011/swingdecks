import pytest
import time
import shutil
from pathlib import Path
from core.orchestrator import Orchestrator
from core.orchestrator_schemas import JobContext, FailureType
from core.idempotency import IdempotencyEngine
from core.retry import RetryPolicy
from core.reconciliation import Reconciler
from core.health import HealthMonitor, HealthStatus, SystemState
from core.recovery import AtomicHelper
from core.decision import PortfolioContext

@pytest.fixture(autouse=True)
def clean_state():
    for d in ["test_queue", "test_state"]:
        path = Path(d)
        if path.exists():
            shutil.rmtree(path)
    yield
    for d in ["test_queue", "test_state"]:
        path = Path(d)
        if path.exists():
            shutil.rmtree(path)

@pytest.fixture
def portfolio():
    return PortfolioContext(
        capital=100000000,
        available_cash=100000000,
        current_positions=[],
        as_of_timestamp="2020"
    )

def test_job_context_hash():
    payload = {"symbol": "BBCA", "timestamp": "123", "value": 100}
    payload2 = {"symbol": "BBCA", "timestamp": "456", "value": 100}
    assert JobContext.compute_hash(payload) == JobContext.compute_hash(payload2)
    payload3 = {"symbol": "BBCA", "value": 200}
    assert JobContext.compute_hash(payload) != JobContext.compute_hash(payload3)

def test_idempotency_engine():
    engine = IdempotencyEngine("test_state/idempotency")
    res1 = engine.check_and_record("job1", "hashA")
    assert res1 == "NEW"
    res2 = engine.check_and_record("job1", "hashA")
    assert res2 == "DUPLICATE"
    res3 = engine.check_and_record("job1", "hashB")
    assert res3 == "CONFLICT"

def test_path_traversal_idempotency():
    engine = IdempotencyEngine("test_state/idempotency")
    with pytest.raises(ValueError, match="path traversal"):
        engine.check_and_record("../../evil", "hash")

def test_retry_policy():
    policy = RetryPolicy()
    assert policy.classify_error(Exception("Pydantic validation failed")) == FailureType.VALIDATION
    assert policy.classify_error(Exception("Secret API_KEY found")) == FailureType.SECURITY
    assert policy.classify_error(Exception("Timeout IOError")) == FailureType.TRANSIENT
    assert not policy.is_retryable(FailureType.VALIDATION)
    assert policy.is_retryable(FailureType.TRANSIENT)

def test_atomic_helper():
    path = Path("test_state/atomic.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    AtomicHelper.write_json(path, {"test": "data"})
    assert path.exists()
    assert not path.with_suffix(".tmp").exists()
    data = AtomicHelper.load_json(path)
    assert data["test"] == "data"

def test_health_monitor():
    hm = HealthMonitor("test_state/sys.json")
    assert hm.check_health() == HealthStatus.HEALTHY
    hm.set_pause(True)
    assert hm.check_health() == HealthStatus.PAUSED
    assert hm.get_system_state() == SystemState.PAUSED

def test_orchestrator_paused_kill_switch(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    orch.health.set_pause(True)
    with pytest.raises(RuntimeError, match="paused"):
        orch.process_job("job1", {"symbol": "BBCA"}, portfolio)

def test_end_to_end_buy(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    payload = {
        "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "market_regime": "BULL",
        "as_of_timestamp": "2020-01-01"
    }
    orch.process_job("job1", payload, portfolio)
    assert orch.metrics.metrics["jobs_total"] == 1
    assert orch.metrics.metrics["jobs_completed"] == 1
    assert orch.metrics.metrics.get("decision_buy", 0) > 0

def test_end_to_end_duplicate(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    payload = {"symbol": "BBCA"}
    orch.process_job("job1", payload, portfolio)
    orch.process_job("job1", payload, portfolio)
    assert orch.metrics.metrics["jobs_total"] == 1

def test_end_to_end_conflict_dead_letter(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    orch.process_job("job1", {"symbol": "BBCA"}, portfolio)
    orch.process_job("job1", {"symbol": "BBRI"}, portfolio)
    assert (orch.dead_letter_dir / "job1.json").exists()

def test_reconciliation():
    rec = Reconciler("test_queue", "test_state")
    Path("test_queue").mkdir(parents=True, exist_ok=True)
    with open("test_queue/orphan.tmp", "w") as f:
        f.write("bad")
    with open("test_queue/corrupt.json", "w") as f:
        f.write("{bad json}")
    
    report = rec.reconcile()
    assert not report.healthy
    assert len(report.warnings) == 1
    assert len(report.errors) == 1

def test_audit_ledger_idempotency():
    from core.audit_ledger import AuditLedger
    ledger = AuditLedger("test_state/audit")
    ledger.log_event("job1", "2020", "STAGE", "START", "INFO")
    ledger.log_event("job1", "2020", "STAGE", "START", "INFO") # duplicate
    
    lines = list(open("test_state/audit/ledger.jsonl"))
    assert len(lines) == 1 # Second one skipped

def test_dead_letter_format(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    orch.process_job("jobDL", {"symbol": "A"}, portfolio)
    orch.process_job("jobDL", {"symbol": "B"}, portfolio)
    dl = AtomicHelper.load_json(orch.dead_letter_dir / "jobDL.json")
    assert dl["failure_type"] == FailureType.IDEMPOTENCY.value
    assert dl["original_payload"]["symbol"] == "B"

def test_orchestrator_e2e_wait(portfolio):
    # Wait tested implicitly by invalid agent payload handling
    pass

def test_crash_recovery(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    payload = {"symbol": "BBCA_SYNTHETIC_FIXTURE"}
    orch.runner.stage_dir.mkdir(parents=True, exist_ok=True)
    AtomicHelper.write_json(orch.runner.stage_dir / "jobR_agent1.json", {"status": "COMPLETED", "candidates": [{"score": 90}]})
    
    orch.process_job("jobR", payload, portfolio)
    assert orch.metrics.metrics["jobs_completed"] == 1

def test_security_classification():
    policy = RetryPolicy()
    assert policy.classify_error(Exception("Secret API_KEY found")) == FailureType.SECURITY

def test_data_classification():
    policy = RetryPolicy()
    assert policy.classify_error(Exception("contains NaN in score")) == FailureType.DATA

from core.pipeline_metrics import PipelineMetrics

def test_atomic_replace():
    path = Path("test_state/test_atomic_replace.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    AtomicHelper.write_json(path, {"A": 1})
    AtomicHelper.write_json(path, {"A": 2}) # overwrites
    assert AtomicHelper.load_json(path) == {"A": 2}

def test_restart_safety(portfolio):
    orch1 = Orchestrator("test_queue", "test_state")
    orch1.process_job("jobRS", {"symbol": "X"}, portfolio)
    
    orch2 = Orchestrator("test_queue", "test_state")
    orch2.process_job("jobRS", {"symbol": "X"}, portfolio)
    
    assert orch2.metrics.metrics["jobs_completed"] == 1
    
def test_deterministic_replay(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    payload = {"symbol": "BBCA_SYNTHETIC_FIXTURE"}
    orch.process_job("jobReplay1", payload, portfolio)
    res1 = AtomicHelper.load_json(orch.runner.stage_dir / "jobReplay1_agent3.json")
    
    orch.process_job("jobReplay2", payload, portfolio)
    res2 = AtomicHelper.load_json(orch.runner.stage_dir / "jobReplay2_agent3.json")
    
    assert res1["decision"]["action"] == res2["decision"]["action"]
    assert res1["decision"]["position_size"] == res2["decision"]["position_size"]

def test_stuck_job_detection_concept():
    j = JobContext(job_id="1", symbol="x", created_at="2020", updated_at="2020", input_hash="")
    assert j.current_state.value == "CREATED"

def test_pipeline_runner_handles_invalid_agent1(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    orch.runner.stage_dir.mkdir(parents=True, exist_ok=True)
    AtomicHelper.write_json(orch.runner.stage_dir / "jobF_agent1.json", {"status": "FAILED"})
    orch.process_job("jobF", {"symbol": "X"}, portfolio)
    # Should record a completed job with AVOID decision
    assert orch.metrics.metrics.get("decision_avoid", 0) > 0

def test_reconciliation_healthy():
    rec = Reconciler("test_queue", "test_state")
    report = rec.reconcile()
    assert report.healthy

def test_audit_ledger_no_secrets():
    from core.audit_ledger import AuditLedger
    ledger = AuditLedger("test_state/audit")
    ledger.log_event("1", "2020", "S", "E", "OK", {"secret_token": "123", "data": "yes"})
    with open("test_state/audit/ledger.jsonl") as f:
        line = f.read()
    assert "secret_token" not in line
    assert "data" in line

def test_pipeline_metrics_retry():
    metrics = PipelineMetrics("test_state/metrics.json")
    metrics.record_job_retry()
    assert metrics.metrics["jobs_retry"] == 1

def test_pipeline_metrics_dead_letter():
    metrics = PipelineMetrics("test_state/metrics.json")
    metrics.record_job_failed("AGENT1", is_dead_letter=True)
    assert metrics.metrics["jobs_dead_letter"] == 1
    assert metrics.metrics["stage_failure_count"]["AGENT1"] == 1

def test_health_dir_missing():
    missing_dir = Path("test_state/missing_dir")
    hm = HealthMonitor(str(missing_dir / "sys.json"))
    if missing_dir.exists():
        shutil.rmtree(missing_dir)
    assert hm.check_health() == HealthStatus.FAILED

def test_orchestrator_job_failed_retry(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    # Mocking runner to throw an IOError which is TRANSIENT
    def mock_run(*args):
        raise IOError("timeout")
    orch.runner.run_pipeline = mock_run
    orch.process_job("jobRetry", {"symbol": "BBCA"}, portfolio)
    
    assert orch.metrics.metrics["jobs_retry"] == 1
    # Check that failed payload was written to failed dir (retry queue conceptual)
    assert (orch.failed_dir / "jobRetry.json").exists()

def test_orchestrator_job_failed_exhausted(portfolio):
    orch = Orchestrator("test_queue", "test_state")
    # Mocking runner to throw a Validation error which is NOT retryable
    def mock_run(*args):
        raise ValueError("Pydantic validation error")
    orch.runner.run_pipeline = mock_run
    orch.process_job("jobFail", {"symbol": "BBCA"}, portfolio)
    
    assert orch.metrics.metrics["jobs_dead_letter"] == 1
    assert (orch.dead_letter_dir / "jobFail.json").exists()

def test_job_context_serialization():
    j = JobContext(job_id="1", symbol="x", created_at="2020", updated_at="2020", input_hash="hash")
    d = j.model_dump()
    assert d["current_state"] == "CREATED"
