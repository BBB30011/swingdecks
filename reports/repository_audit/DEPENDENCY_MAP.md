# DEPENDENCY MAP

### `agents/agent1_quant/pipeline.py`
- imports `core.schemas`
- imports `core.universe`
- imports `core.liquidity`
- imports `core.market_scanner`
- imports `core.benchmark`
- imports `core.alert_engine`
- imports `core.signal_state_tracker`

### `agents/agent2_intelligence/llm_reasoner.py`
- imports `agents.agent2_intelligence.schemas`

### `agents/agent2_intelligence/pipeline.py`
- imports `core.research`
- imports `core.intelligence_engine`
- imports `agents.agent2_intelligence.llm_reasoner`
- imports `agents.agent2_intelligence.schemas`

### `agents/agent3_committee/committee.py`
- imports `core.decision`
- imports `core.opportunity_ranker`
- imports `core.timing_engine`

### `agents/agent3_committee/pipeline.py`
- imports `core.decision`
- imports `core.risk_engine`
- imports `agents.agent3_committee.committee`

### `core/alert_engine.py`
- imports `core.schemas`

### `core/audit_ledger.py`
- imports `core.orchestrator_schemas`

### `core/benchmark.py`
- imports `core.data_source`
- imports `core.schemas`

### `core/csv_data_source.py`
- imports `core.data_source`
- imports `core.schemas`

### `core/dataset.py`
- imports `core.schemas`

### `core/dataset_audit.py`
- imports `core.schemas`

### `core/data_acquisition.py`
- imports `core.data_source`
- imports `core.snapshot_manager`
- imports `core.schemas`

### `core/data_engine.py`
- imports `core.schemas`
- imports `core.validator`
- imports `core.data_source`
- imports `core.data_repository`

### `core/data_import_wizard.py`
- imports `core.data_compatibility`

### `core/data_intake.py`
- imports `core.data_compatibility`
- imports `core.data_import_wizard`

### `core/data_provisioning.py`
- imports `core.data_import_wizard`

### `core/data_repository.py`
- imports `core.schemas`

### `core/data_source.py`
- imports `core.schemas`
- imports `core.csv_data_source`
- imports `core.providers.yfinance_provider`

### `core/exit_engine.py`
- imports `core.position`

### `core/first_real_backtest.py`
- imports `core.data_import_wizard`

### `core/flow_features.py`
- imports `core.schemas`

### `core/intelligence.py`
- imports `core.research`

### `core/liquidity.py`
- imports `core.schemas`
- imports `core.universe`

### `core/market_scanner.py`
- imports `core.schemas`
- imports `core.quant_features`
- imports `core.market_regime`
- imports `core.flow_features`
- imports `core.evidence`

### `core/opportunity_ranker.py`
- imports `core.timing_engine`

### `core/orchestrator.py`
- imports `core.orchestrator_schemas`
- imports `core.idempotency`
- imports `core.retry`
- imports `core.audit_ledger`
- imports `core.pipeline_metrics`
- imports `core.health`
- imports `core.pipeline_runner`
- imports `core.recovery`
- imports `core.decision`

### `core/paper_portfolio.py`
- imports `core.position`

### `core/paper_session.py`
- imports `core.paper_portfolio`

### `core/pipeline_runner.py`
- imports `core.orchestrator_schemas`
- imports `core.idempotency`
- imports `core.retry`
- imports `core.audit_ledger`
- imports `core.pipeline_metrics`
- imports `core.health`
- imports `core.recovery`
- imports `core.decision`
- imports `agents.agent1_quant.pipeline`
- imports `agents.agent2_intelligence.pipeline`
- imports `agents.agent3_committee.pipeline`
- imports `core.alert_engine`
- imports `core.signal_state_tracker`
- imports `core.decision`

### `core/position_monitor.py`
- imports `core.position`
- imports `core.exit_engine`
- imports `core.materiality`

### `core/quant_features.py`
- imports `core.schemas`

### `core/real_backtest.py`
- imports `core.data_onboarding`

### `core/red_team.py`
- imports `core.research`
- imports `core.research_contradiction`
- imports `core.opportunity_ranker`
- imports `core.timing_engine`

### `core/research_contradiction.py`
- imports `core.research`

### `core/retry.py`
- imports `core.orchestrator_schemas`

### `core/risk_engine.py`
- imports `core.decision`

### `core/signal_state_tracker.py`
- imports `core.schemas`

### `core/backtest/dataset_splitter.py`
- imports `core.schemas`
- imports `core.dataset`

### `core/backtest/engine.py`
- imports `core.backtest.models`
- imports `core.backtest.replay`
- imports `core.backtest.costs`
- imports `core.backtest.metrics`
- imports `core.backtest.calendar`
- imports `core.market_scanner`
- imports `core.schemas`
- imports `core.backtest.models`
- imports `core.backtest.replay`
- imports `core.backtest.costs`
- imports `core.backtest.metrics`
- imports `core.backtest.calendar`
- imports `core.market_scanner`
- imports `core.schemas`
- imports `core.decision`
- imports `core.risk_engine`
- imports `agents.agent3_committee.committee`

### `core/backtest/metrics.py`
- imports `core.backtest.models`

### `core/backtest/models.py`
- imports `core.decision`

### `core/backtest/performance_attribution.py`
- imports `core.backtest.models`
- imports `core.schemas`

### `core/backtest/replay.py`
- imports `core.schemas`

### `core/backtest/robustness.py`
- imports `core.backtest.engine`
- imports `core.backtest.models`
- imports `core.schemas`

### `core/backtest/score_analysis.py`
- imports `core.schemas`

### `core/backtest/walk_forward.py`
- imports `core.dataset`
- imports `core.schemas`

### `core/providers/yfinance_provider.py`
- imports `core.data_source`
- imports `core.schemas`

### `reports/archive/scratch_historical/perf_test.py`
- imports `core.market_scanner`

### `scripts/acquire_data.py`
- imports `core.data_acquisition`

### `scripts/onboard_data.py`
- imports `core.data_onboarding`
- imports `core.data_compatibility`
- imports `core.data_import_wizard`
- imports `core.data_provisioning`

### `scripts/real_backtest.py`
- imports `core.real_backtest`

### `scripts/run_backtest.py`
- imports `core.backtest.models`
- imports `core.backtest.engine`
- imports `core.backtest.dataset_splitter`
- imports `core.backtest.walk_forward`
- imports `core.schemas`
- imports `core.dataset`
- imports `core.backtest.performance_attribution`
- imports `core.backtest.metrics`

### `scripts/run_experiments_ax.py`
- imports `core.backtest.models`
- imports `core.backtest.engine`
- imports `core.backtest.dataset_splitter`
- imports `core.backtest.walk_forward`
- imports `core.schemas`
- imports `core.dataset`
- imports `core.backtest.metrics`

### `scripts/run_forensics_aw.py`
- imports `core.backtest.models`
- imports `core.backtest.engine`
- imports `core.backtest.dataset_splitter`
- imports `core.backtest.walk_forward`
- imports `core.schemas`
- imports `core.dataset`
- imports `core.backtest.metrics`

### `scripts/run_research_ay.py`
- imports `core.backtest.replay`
- imports `core.market_scanner`
- imports `core.schemas`

### `scripts/run_research_ay1.py`
- imports `core.backtest.replay`
- imports `core.market_scanner`
- imports `core.schemas`

### `scripts/run_research_ay2.py`
- imports `core.backtest.replay`
- imports `core.market_scanner`
- imports `core.schemas`

### `tests/test_agent1_end_to_end.py`
- imports `core.data_source`
- imports `core.data_repository`
- imports `core.data_engine`
- imports `agents.agent1_quant.pipeline`

### `tests/test_agent1_pipeline.py`
- imports `core.schemas`
- imports `agents.agent1_quant.pipeline`

### `tests/test_agent2_pipeline.py`
- imports `agents.agent2_intelligence.pipeline`
- imports `core.research`
- imports `core.research_contradiction`
- imports `core.research`

### `tests/test_alert_engine.py`
- imports `core.alert_engine`
- imports `core.signal_state_tracker`
- imports `core.schemas`
- imports `core.decision`

### `tests/test_batch_ab.py`
- imports `agents.agent3_committee.pipeline`
- imports `core.decision`

### `tests/test_batch_ab_scenarios.py`
- imports `agents.agent3_committee.pipeline`
- imports `core.decision`

### `tests/test_batch_ac.py`
- imports `core.orchestrator`
- imports `core.orchestrator_schemas`
- imports `core.idempotency`
- imports `core.retry`
- imports `core.reconciliation`
- imports `core.health`
- imports `core.recovery`
- imports `core.decision`
- imports `core.pipeline_metrics`
- imports `core.audit_ledger`
- imports `core.audit_ledger`

### `tests/test_batch_ad.py`
- imports `core.csv_data_source`
- imports `core.dataset_readiness`
- imports `core.dataset_audit`
- imports `core.data_source`
- imports `agents.agent1_quant.pipeline`

### `tests/test_batch_ae.py`
- imports `core.dataset_discovery`

### `tests/test_batch_af.py`
- imports `core.position`
- imports `core.position_monitor`
- imports `core.exit_engine`
- imports `core.paper_portfolio`
- imports `core.materiality`
- imports `core.learning`
- imports `core.paper_session`

### `tests/test_batch_ag.py`
- imports `core.data_onboarding`

### `tests/test_batch_ah.py`
- imports `core.real_backtest`
- imports `core.data_onboarding`

### `tests/test_batch_ai.py`
- imports `core.data_compatibility`

### `tests/test_batch_aj.py`
- imports `core.data_import_wizard`

### `tests/test_batch_ak.py`
- imports `core.first_real_backtest`

### `tests/test_batch_al.py`
- imports `core.data_provisioning`

### `tests/test_batch_am.py`
- imports `core.data_intake`

### `tests/test_batch_ao.py`
- imports `core.alert_engine`
- imports `core.schemas`
- imports `core.decision`
- imports `agents.agent3_committee.committee`

### `tests/test_batch_ap.py`
- imports `core.alert_engine`
- imports `core.schemas`
- imports `core.decision`
- imports `agents.agent3_committee.committee`

### `tests/test_batch_aq.py`
- imports `core.intelligence`
- imports `core.research`
- imports `core.red_team`
- imports `core.decision`

### `tests/test_batch_ar.py`
- imports `core.timing_engine`
- imports `core.opportunity_ranker`
- imports `core.exit_engine`
- imports `core.position`
- imports `core.decision`
- imports `core.decision`

### `tests/test_batch_as.py`
- imports `core.schemas`
- imports `core.decision`
- imports `core.signal_state_tracker`
- imports `core.alert_engine`

### `tests/test_batch_at.py`
- imports `core.providers.yfinance_provider`
- imports `core.snapshot_manager`
- imports `core.schemas`
- imports `core.data_source`

### `tests/test_batch_av.py`
- imports `core.learning`

### `tests/test_batch_ax.py`
- imports `core.backtest.models`
- imports `core.backtest.engine`

### `tests/test_batch_q.py`
- imports `core.data_source`
- imports `core.quant_features`
- imports `core.market_scanner`
- imports `agents.agent1_quant.pipeline`

### `tests/test_batch_r.py`
- imports `core.data_source`
- imports `core.quant_features`
- imports `core.market_scanner`
- imports `core.benchmark`
- imports `core.market_regime`
- imports `agents.agent1_quant.pipeline`

### `tests/test_batch_s.py`
- imports `core.schemas`
- imports `core.flow_features`
- imports `core.market_scanner`
- imports `agents.agent1_quant.pipeline`
- imports `core.data_source`

### `tests/test_batch_t.py`
- imports `core.evidence`
- imports `core.market_scanner`

### `tests/test_batch_u.py`
- imports `core.schemas`
- imports `core.backtest.models`
- imports `core.backtest.replay`
- imports `core.backtest.costs`
- imports `core.backtest.metrics`
- imports `core.backtest.engine`
- imports `core.market_scanner`
- imports `core.backtest.models`
- imports `core.decision`

### `tests/test_batch_v.py`
- imports `core.backtest.models`
- imports `core.backtest.engine`
- imports `core.backtest.calendar`
- imports `core.schemas`

### `tests/test_batch_w.py`
- imports `core.schemas`
- imports `core.dataset_audit`
- imports `core.dataset`
- imports `core.universe`
- imports `agents.agent1_quant.pipeline`

### `tests/test_batch_xxx2.py`
- imports `core.intelligence_engine`

### `tests/test_batch_xxx3_pit.py`
- imports `core.intelligence_engine`

### `tests/test_batch_xxx4_llm_pilot.py`
- imports `core.intelligence_engine`
- imports `agents.agent2_intelligence.pipeline`
- imports `agents.agent2_intelligence.llm_reasoner`
- imports `agents.agent2_intelligence.schemas`

### `tests/test_batch_y.py`
- imports `core.backtest.performance_attribution`
- imports `core.backtest.score_analysis`
- imports `core.backtest.robustness`
- imports `core.backtest.engine`
- imports `core.backtest.models`
- imports `core.decision`
- imports `core.backtest.models`
- imports `core.schemas`
- imports `core.backtest.walk_forward`
- imports `core.backtest.dataset_splitter`
- imports `core.backtest.performance_validator`
- imports `core.schemas`

### `tests/test_batch_yyy2_historical.py`
- imports `core.intelligence_engine`
- imports `agents.agent2_intelligence.pipeline`
- imports `agents.agent2_intelligence.llm_reasoner`

### `tests/test_config.py`
- imports `core.config`

### `tests/test_csv_agent1_end_to_end.py`
- imports `core.data_source`
- imports `core.data_repository`
- imports `core.data_engine`
- imports `agents.agent1_quant.pipeline`
- imports `core.quant_features`
- imports `core.market_scanner`

### `tests/test_csv_data_source.py`
- imports `core.data_source`
- imports `core.csv_data_source`

### `tests/test_dataset_readiness.py`
- imports `core.schemas`
- imports `core.dataset_readiness`
- imports `core.dataset_audit`
- imports `core.csv_data_source`
- imports `core.data_source`
- imports `agents.agent1_quant.pipeline`

### `tests/test_data_engine.py`
- imports `core.schemas`
- imports `core.data_source`
- imports `core.data_repository`
- imports `core.data_engine`

### `tests/test_data_repository.py`
- imports `core.schemas`
- imports `core.data_repository`

### `tests/test_data_source.py`
- imports `core.schemas`
- imports `core.data_source`

### `tests/test_data_source_errors.py`
- imports `core.data_source`
- imports `core.schemas`

### `tests/test_data_source_factory.py`
- imports `core.data_source`

### `tests/test_event_mapping.py`
- imports `core.event_mapping`

### `tests/test_indicators.py`
- imports `core.schemas`
- imports `core.quant_features`

### `tests/test_job_envelope.py`
- imports `core.schemas`

### `tests/test_liquidity.py`
- imports `core.schemas`
- imports `core.universe`
- imports `core.liquidity`

### `tests/test_logger.py`
- imports `core.logger`

### `tests/test_market_data_schema.py`
- imports `core.schemas`

### `tests/test_market_scanner.py`
- imports `core.schemas`
- imports `core.market_scanner`

### `tests/test_mock_historical_data.py`
- imports `core.data_source`
- imports `core.schemas`

### `tests/test_performance_attribution.py`
- imports `core.backtest.performance_attribution`
- imports `core.backtest.score_analysis`
- imports `core.backtest.robustness`
- imports `core.backtest.models`
- imports `core.decision`
- imports `core.backtest.models`
- imports `core.schemas`

### `tests/test_performance_batch_ab.py`
- imports `agents.agent3_committee.pipeline`
- imports `core.decision`

### `tests/test_provider_integration.py`
- imports `core.data_source`
- imports `core.data_repository`
- imports `core.data_engine`
- imports `agents.agent1_quant.pipeline`

### `tests/test_quant_features.py`
- imports `core.schemas`
- imports `core.quant_features`

### `tests/test_queue.py`
- imports `core.queue`

### `tests/test_queue_watcher.py`
- imports `core.queue_watcher`

### `tests/test_red_team.py`
- imports `core.red_team`
- imports `core.research`
- imports `agents.agent2_intelligence.pipeline`

### `tests/test_research_schema.py`
- imports `core.research`

### `tests/test_research_validation.py`
- imports `core.source_quality`

### `tests/test_schemas.py`
- imports `core.schemas`
- imports `core.validator`

### `tests/test_state_machine.py`
- imports `core.state_machine`

### `tests/test_universe.py`
- imports `core.universe`

### `tests/test_walk_forward.py`
- imports `core.schemas`
- imports `core.backtest.dataset_splitter`
- imports `core.backtest.performance_validator`
- imports `core.backtest.walk_forward`
- imports `core.backtest.engine`
- imports `core.backtest.models`
- imports `core.dataset`

