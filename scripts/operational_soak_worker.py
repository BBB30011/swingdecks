import os
import sys
import json
import time
import shutil
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path("d:/Project/SwingDeck").resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.data_source import MockMarketDataSource, DataUnavailableError, DataValidationError
from core.orchestrator import Orchestrator
from core.pipeline_runner import PipelineRunner
from core.orchestrator_schemas import JobContext, JobState, FailureType
from core.decision import PortfolioContext
from core.paper_portfolio import PaperPortfolio
from core.position import PaperPosition
from core.exit_engine import ExitEngine
from core.recovery import AtomicHelper
from core.replay_firewall import ReplayFirewall
from agents.agent1_quant.pipeline import Agent1QuantPipeline
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline, MockEvidenceCollector
from agents.agent3_committee.pipeline import Agent3DecisionPipeline

WORK_DIR = REPO_ROOT / "runtime" / "watchdog_worker"

def run_e2e_unit(iteration: int) -> Dict[str, Any]:
    orch_dir = WORK_DIR / f"e2e_it_{iteration}"
    orch = Orchestrator(queue_dir=str(orch_dir / "queue"), state_dir=str(orch_dir / "state"))
    portfolio = PortfolioContext(capital=100_000_000.0, available_cash=100_000_000.0, as_of_timestamp="2026-03-20")

    universe = ["BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNVR", "ICBP", "INDF", "KLBF"]
    cycles = 0
    for sym in universe:
        job_id = f"WD_E2E_{iteration}_{sym}"
        payload = {"symbol": sym, "as_of_timestamp": "2026-03-20", "market_regime": "BULL"}
        orch.process_job(job_id, payload, portfolio)
        s3 = orch_dir / "state" / "stages" / f"{job_id}_agent3.json"
        assert s3.exists(), f"Stage 3 missing for {sym}"
        a3_data = AtomicHelper.load_json(s3)
        assert a3_data["decision"]["action"] in ["BUY", "WAIT", "HOLD", "SELL", "AVOID"]
        cycles += 1

    return {"status": "SUCCESS", "unit": "E2E", "cycles": cycles}

def run_queue_unit(iteration: int) -> Dict[str, Any]:
    orch_dir = WORK_DIR / f"queue_it_{iteration}"
    orch = Orchestrator(queue_dir=str(orch_dir / "queue"), state_dir=str(orch_dir / "state"))

    # Malformed
    job1 = f"WD_Q_MAL_{iteration}"
    ctx1 = JobContext(job_id=job1, symbol="ERR1", created_at="2026-03-20", updated_at="2026-03-20", input_hash="h1")
    orch._to_dead_letter(ctx1, {"corrupt": True}, FailureType.VALIDATION, "Malformed payload")

    # Missing
    job2 = f"WD_Q_MISS_{iteration}"
    ctx2 = JobContext(job_id=job2, symbol="ERR2", created_at="2026-03-20", updated_at="2026-03-20", input_hash="h2")
    orch._to_dead_letter(ctx2, {}, FailureType.VALIDATION, "Missing symbol")

    # Retry exhaust
    job3 = f"WD_Q_RET_{iteration}"
    ctx3 = JobContext(job_id=job3, symbol="ERR3", created_at="2026-03-20", updated_at="2026-03-20", input_hash="h3", retry_count=3)
    orch._to_dead_letter(ctx3, {"symbol": "ERR3"}, FailureType.TRANSIENT, "Retries exhausted")

    dl_dir = orch_dir / "queue" / "dead_letter"
    assert (dl_dir / f"{job1}.json").exists()
    assert (dl_dir / f"{job2}.json").exists()
    assert (dl_dir / f"{job3}.json").exists()

    return {"status": "SUCCESS", "unit": "QUEUE", "tests": 3}

def run_position_unit(iteration: int) -> Dict[str, Any]:
    portfolio = PaperPortfolio(100_000_000.0)
    pos_id = f"WD_POS_{iteration}"
    pos = PaperPosition(
        position_id=pos_id, job_id=f"JOB_{pos_id}", symbol="BBCA",
        status="PENDING", entry_timestamp="2026-03-20", entry_price=9000.0,
        quantity=1000.0, lots=10, stop_loss=8500.0, target_price=10000.0,
        initial_risk=500_000.0, initial_reward=1_000_000.0, initial_rr=2.0
    )
    portfolio.open_position(pos, cost=0.0)
    assert pos.status == "OPEN"
    pos.update_price(9400.0)
    portfolio.close_position(pos_id, close_price=9900.0, timestamp="2026-03-22", reason="TARGET_REACHED", cost=0.0)
    assert pos.status == "CLOSED"
    assert portfolio.reconcile().is_valid == True

    # Duplicate check
    pos2 = PaperPosition(position_id=f"WD_POS2_{iteration}", job_id="J2", symbol="BBRI", entry_price=5000.0, quantity=100.0, stop_loss=4800.0, target_price=5400.0, initial_risk=20000.0, initial_reward=40000.0, initial_rr=2.0)
    portfolio.open_position(pos2, cost=0.0)
    dup_blocked = False
    try:
        portfolio.open_position(pos2, cost=0.0)
    except ValueError:
        dup_blocked = True
    assert dup_blocked == True

    return {"status": "SUCCESS", "unit": "POSITION", "tests": 4}

def run_restart_unit(iteration: int) -> Dict[str, Any]:
    runner_dir = WORK_DIR / f"restart_it_{iteration}"
    stage_dir = runner_dir / "stages"
    stage_dir.mkdir(parents=True, exist_ok=True)

    job_id = f"WD_REC_{iteration}"
    ctx = JobContext(job_id=job_id, symbol="TLKM", created_at="2026-03-20", updated_at="2026-03-20", input_hash=f"h_{job_id}")
    AtomicHelper.write_json(stage_dir / f"{job_id}_agent1.json", {
        "status": "COMPLETED",
        "candidates": [{"symbol": "TLKM", "quant_score": 85.0, "market_regime": "BULL", "entry_price": 3200.0, "stop_loss": 3050.0, "target_price": 3500.0}]
    })
    AtomicHelper.write_json(stage_dir / f"{job_id}_agent2.json", {
        "status": "COMPLETED",
        "report": {"symbol": "TLKM", "evidence_state": "GOOD", "flow_state": "POSITIVE", "contradictions": [], "catalysts": []}
    })

    resumed_runner = PipelineRunner(base_dir=str(runner_dir))
    portfolio = PortfolioContext(capital=100_000_000.0, available_cash=100_000_000.0, as_of_timestamp="2026-03-20")
    out = resumed_runner.run_pipeline(ctx, {"symbol": "TLKM"}, portfolio)
    assert (stage_dir / f"{job_id}_agent3.json").exists()
    assert out["decision"]["action"] in ["BUY", "WAIT", "HOLD", "SELL", "AVOID"]

    return {"status": "SUCCESS", "unit": "RESTART", "tests": 2}

def run_pit_unit(iteration: int) -> Dict[str, Any]:
    cutoff = "2026-03-20T00:00:00"
    assert ReplayFirewall.prevent_future_leak({"published_at": "2026-03-20T00:00:00"}, cutoff) == True
    assert ReplayFirewall.prevent_future_leak({"published_at": "2026-03-19T23:59:59"}, cutoff) == True
    assert ReplayFirewall.prevent_future_leak({"published_at": "2026-03-20T00:00:01"}, cutoff) == False
    assert ReplayFirewall.prevent_future_leak({"published_at": "2026-03-25T00:00:00"}, cutoff) == False
    return {"status": "SUCCESS", "unit": "PIT", "tests": 4}

def run_data_unit(iteration: int) -> Dict[str, Any]:
    ds = MockMarketDataSource()
    assert ds.get_snapshot("BBCA").data_quality == "FRESH"
    assert ds.get_snapshot("STALE").data_quality == "STALE"
    unavail = False
    try:
        ds.get_snapshot("UNAVAILABLE")
    except DataUnavailableError:
        unavail = True
    assert unavail == True

    corrupt = False
    try:
        ds.get_snapshot("CORRUPT")
    except DataValidationError:
        corrupt = True
    assert corrupt == True
    return {"status": "SUCCESS", "unit": "DATA_QUALITY", "tests": 4}

def run_agent_unit(iteration: int) -> Dict[str, Any]:
    a1 = Agent1QuantPipeline()
    assert "execute_trade" not in dir(a1)
    a2 = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    assert "place_order" not in dir(a2)
    a3 = Agent3DecisionPipeline()
    assert hasattr(a3, "process_job")
    return {"status": "SUCCESS", "unit": "AGENT_BOUNDARY", "tests": 3}

def run_integrity_unit() -> Dict[str, Any]:
    coba_19 = list(REPO_ROOT.glob("**/COBA_019*"))
    assert len(coba_19) == 0
    coba_exp_dir = REPO_ROOT / "research" / "experiments"
    if coba_exp_dir.exists():
        dirs = [d.name for d in coba_exp_dir.iterdir() if d.is_dir() and d.name.startswith("COBA_")]
        assert len(dirs) >= 18
    return {"status": "SUCCESS", "unit": "INTEGRITY", "tests": 2}

def main():
    parser = argparse.ArgumentParser(description="Operational Soak Worker Unit")
    parser.add_argument("--unit", type=str, required=True, help="Work unit to execute")
    parser.add_argument("--iteration", type=int, default=1, help="Iteration number")
    args = parser.parse_args()

    unit = args.unit.upper()
    it = args.iteration

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    if unit == "E2E":
        res = run_e2e_unit(it)
    elif unit == "QUEUE":
        res = run_queue_unit(it)
    elif unit == "POSITION":
        res = run_position_unit(it)
    elif unit == "RESTART":
        res = run_restart_unit(it)
    elif unit == "PIT":
        res = run_pit_unit(it)
    elif unit == "DATA":
        res = run_data_unit(it)
    elif unit == "AGENT":
        res = run_agent_unit(it)
    elif unit == "INTEGRITY":
        res = run_integrity_unit()
    else:
        print(json.dumps({"status": "ERROR", "message": f"Unknown unit {unit}"}))
        sys.exit(1)

    print(json.dumps(res))
    sys.exit(0)

if __name__ == "__main__":
    main()
