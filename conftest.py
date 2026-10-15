import sys
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OPERATIONAL_FILE_STEMS = {
    'test_00_architecture_enforcement',
    'test_agent1_pipeline',
    'test_agent1_end_to_end',
    'test_csv_agent1_end_to_end',
    'test_agent2_pipeline',
    'test_agent2_semi_manual_news',
    'test_red_team',
    'test_pipeline_runner',
    'test_batch_ac',
    'test_queue',
    'test_queue_watcher',
    'test_csv_data_source',
    'test_dataset_readiness',
    'test_replay_firewall',
    'test_batch_xxx3_pit',
    'test_performance_attribution',
    'test_config',
    'test_alert_engine',
    'test_main',
    'test_indicators',
    'test_market_scanner',
    'test_quant_features',
    'test_schemas',
    'test_state_machine',
    'test_universe',
    'test_logger',
    'test_data_source_factory',
    'test_data_source_errors',
    'test_data_source',
    'test_data_repository',
    'test_data_engine',
    'test_market_data_schema',
    'test_job_envelope',
    'test_liquidity',
    'test_event_mapping',
    'test_provider_integration',
    'test_daily_cycle'
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        rel_path = str(Path(item.fspath).relative_to(ROOT))
        stem = Path(item.fspath).stem
        
        if stem in OPERATIONAL_FILE_STEMS:
            item.add_marker(pytest.mark.operational)
        else:
            item.add_marker(pytest.mark.historical)
