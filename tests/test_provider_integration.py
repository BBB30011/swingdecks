import pytest
from core.data_source import DataSourceFactory
from core.data_repository import DataRepository
from core.data_engine import DataEngine
from agents.agent1_quant.pipeline import Agent1QuantPipeline

def test_provider_engine_pipeline_integration(tmp_path):
    # Setup Factory & Mock Provider
    config = {
        "data_source": {
            "provider": "MOCK",
            "freshness": {"max_age_minutes": 60}
        }
    }
    provider = DataSourceFactory.create(config)
    
    # Setup Repository & Engine
    repo = DataRepository(tmp_path)
    engine = DataEngine(provider, repo, config)
    
    symbols = ["TEST1", "TEST2", "TEST3"]
    snapshots = []
    
    for sym in symbols:
        snap = engine.fetch_and_store(sym)
        snapshots.append(snap)
        
    assert len(snapshots) == 3
    assert (tmp_path / "TEST1.json").exists()
    
    # Setup Agent 1 Pipeline
    pipeline = Agent1QuantPipeline()
    res = pipeline.run(snapshots)
    
    # Verify End-to-End integration
    assert res["input_count"] == 3
    assert "run_id" in res
    assert res["rejection_summary"]["INSUFFICIENT_DATA"] > 0
    assert "TEST1" in res["stage_trace"]
