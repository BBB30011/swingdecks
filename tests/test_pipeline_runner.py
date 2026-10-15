import pytest
import shutil
from pathlib import Path
from core.pipeline_runner import PipelineRunner
from core.orchestrator_schemas import JobContext, JobState
from core.decision import PortfolioContext

@pytest.fixture(autouse=True)
def clean_stage_dir():
    test_dir = Path("test_state_runner")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    yield
    if test_dir.exists():
        shutil.rmtree(test_dir)

def test_pipeline_runner_initialization():
    runner = PipelineRunner(base_dir="test_state_runner")
    assert runner.agent1 is not None
    assert runner.agent2 is not None
    assert runner.agent3 is not None
    assert runner.audit is not None
    assert runner.alert_engine is not None
    assert runner.state_tracker is not None

def test_pipeline_runner_full_cycle():
    runner = PipelineRunner(base_dir="test_state_runner")
    job_ctx = JobContext(
        job_id="job_test_001",
        symbol="BBCA",
        created_at="2020-01-02T08:30:00",
        updated_at="2020-01-02T08:30:00",
        input_hash="hash_001"
    )
    payload = {
        "symbol": "BBCA",
        "as_of_timestamp": "2020-01-02",
        "market_regime": "BULL"
    }
    portfolio = PortfolioContext(
        capital=100000000.0,
        available_cash=100000000.0,
        as_of_timestamp="2020-01-02"
    )
    
    result = runner.run_pipeline(job_ctx, payload, portfolio)
    assert result is not None
    assert "decision" in result
    assert result["decision"]["action"] in ["BUY", "ACT", "WATCH", "WAIT", "AVOID", "HOLD", "SELL"]
    assert job_ctx.current_state == JobState.COMPLETED
    
    # Check that stage files were persisted
    stage_dir = Path("test_state_runner/stages")
    assert (stage_dir / "job_test_001_agent1.json").exists()
    assert (stage_dir / "job_test_001_agent2.json").exists()
    assert (stage_dir / "job_test_001_agent3.json").exists()
