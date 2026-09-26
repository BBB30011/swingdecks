# FULL REPOSITORY TREE

```text
./
├── .gitignore
├── AGENTS.md
├── audit_v2.py
├── baseline_audit.py
├── GOVERNANCE.md
├── KNOWLEDGE_INDEX.md
├── main.py
├── MIGRATION_EXECUTION_REPORT.md
├── patch_obsolete_tests.py
├── PROJECT_CONTEXT.md
├── README.md
├── RESEARCH_STATUS.md
├── scratch_inventory.json
├── .pytest_cache/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   ├── v/
│   │   ├── cache/
│   │   │   ├── lastfailed
│   │   │   ├── nodeids
├── agents/
│   ├── agent1_quant/
│   │   ├── .gitkeep
│   │   ├── pipeline.py
│   │   ├── README.md
│   │   ├── __init__.py
│   ├── agent2_intelligence/
│   │   ├── .gitkeep
│   │   ├── llm_reasoner.py
│   │   ├── pipeline.py
│   │   ├── README.md
│   │   ├── schemas.py
│   │   ├── __init__.py
│   ├── agent3_committee/
│   │   ├── .gitkeep
│   │   ├── committee.py
│   │   ├── pipeline.py
│   │   ├── README.md
│   │   ├── __init__.py
├── archive/
│   ├── duplicates/
│   │   ├── BBCA_duplicate.csv
│   │   ├── BBCA_DUP_ROW.csv
│   ├── legacy/
│   │   ├── fix_all_tests.py
│   │   ├── fix_stop_loss.py
│   │   ├── fix_tests.py
│   │   ├── fix_test_imports.py
│   │   ├── fix_test_imports_2.py
│   │   ├── perf_test.cpython-312-pytest-9.1.1.pyc
│   │   ├── perf_test.py
│   │   ├── rewrite_attr.py
│   ├── superseded/
│   ├── temporary/
├── backtest/
│   ├── .gitkeep
├── config/
│   ├── .gitkeep
├── configs/
│   ├── backtest.yaml
│   ├── data_source.yaml
│   ├── models.yaml
│   ├── risk.yaml
│   ├── scanner.yaml
│   ├── settings.yaml
│   ├── universe.yaml
├── core/
│   ├── .gitkeep
│   ├── ablation_engine.py
│   ├── adaptive_historical_foundation.py
│   ├── alert_engine.py
│   ├── attribution_schemas.py
│   ├── audit_ledger.py
│   ├── benchmark.py
│   ├── candidate_attribution_engine.py
│   ├── canonical_replication_engine.py
│   ├── common_support_inference_engine.py
│   ├── company_specific_discrimination_engine.py
│   ├── config.py
│   ├── counterfactual_integrity_engine.py
│   ├── counterfactual_purification_engine.py
│   ├── coverage_aware_discrimination_engine.py
│   ├── csv_data_source.py
│   ├── daily_cycle.py
│   ├── dataset.py
│   ├── dataset_audit.py
│   ├── dataset_discovery.py
│   ├── dataset_readiness.py
│   ├── data_acquisition.py
│   ├── data_compatibility.py
│   ├── data_engine.py
│   ├── data_import_wizard.py
│   ├── data_intake.py
│   ├── data_onboarding.py
│   ├── data_provisioning.py
│   ├── data_repository.py
│   ├── data_source.py
│   ├── db_init.py
│   ├── decision.py
│   ├── event_mapping.py
│   ├── evidence.py
│   ├── evidence_deconfounding_engine.py
│   ├── exit_engine.py
│   ├── first_real_backtest.py
│   ├── fixed_sample_layer_attribution_engine.py
│   ├── flow_features.py
│   ├── health.py
│   ├── historical_disclosure_completeness_audit.py
│   ├── historical_disclosure_coverage_engine.py
│   ├── historical_disclosure_ingestion_engine.py
│   ├── historical_discrimination_engine.py
│   ├── historical_knowledge_state.py
│   ├── historical_replay.py
│   ├── historical_replay_engine.py
│   ├── idempotency.py
│   ├── identification_audit_engine.py
│   ├── identification_stress_test_engine.py
│   ├── information_coverage_engine.py
│   ├── intelligence.py
│   ├── intelligence_engine.py
│   ├── joint_identification_engine.py
│   ├── learning.py
│   ├── liquidity.py
│   ├── logger.py
│   ├── market_regime.py
│   ├── market_scanner.py
│   ├── matched_event_cluster_engine.py
│   ├── materiality.py
│   ├── multi_agent_experiment_engine.py
│   ├── oos_validation_engine.py
│   ├── opportunity_ranker.py
│   ├── orchestrator.py
│   ├── orchestrator_schemas.py
│   ├── paper_portfolio.py
│   ├── paper_session.py
│   ├── pipeline_metrics.py
│   ├── pipeline_runner.py
│   ├── position.py
│   ├── position_monitor.py
│   ├── pretrend_adjusted_information_engine.py
│   ├── quant_features.py
│   ├── queue.py
│   ├── queue_watcher.py
│   ├── README_CSV.md
│   ├── README_DATA_ONBOARDING.md
│   ├── README_DATA_PIPELINE.md
│   ├── README_ORCHESTRATION.md
│   ├── README_PAPER_MONITORING.md
│   ├── README_Quant.md
│   ├── real_backtest.py
│   ├── reconciliation.py
│   ├── recovery.py
│   ├── red_team.py
│   ├── replay_firewall.py
│   ├── research.py
│   ├── research_alpha_validation.py
│   ├── research_contradiction.py
│   ├── research_methodology_lock.py
│   ├── research_oos.py
│   ├── retry.py
│   ├── risk_engine.py
│   ├── schemas.py
│   ├── semantic_ablation_engine.py
│   ├── semantic_attribution_engine.py
│   ├── semantic_substrate_engine.py
│   ├── signal_state_tracker.py
│   ├── snapshot_manager.py
│   ├── source_governance_engine.py
│   ├── source_quality.py
│   ├── state_machine.py
│   ├── strict_counterfactual_inference_engine.py
│   ├── timing_engine.py
│   ├── universe.py
│   ├── validator.py
│   ├── zzz1438_closure_gate.py
│   ├── zzz1439_estimand_ai_gate.py
│   ├── zzz144_ai_scaleup.py
│   ├── zzz145_ai_attribution.py
│   ├── zzz1461_reconciliation.py
│   ├── zzz1462_counterfactual_closure.py
│   ├── zzz1463_population_identity.py
│   ├── zzz146_risk_integration.py
│   ├── zzz146_syntactic_synthesis.py
│   ├── zzz1471_closure_engine.py
│   ├── zzz1472_closure_engine.py
│   ├── zzz147_ai_firewall.py
│   ├── zzz147_contradiction_attribution.py
│   ├── zzz147_drift.py
│   ├── zzz147_inference.py
│   ├── zzz147_information_layers.py
│   ├── zzz14811_identity_gate.py
│   ├── zzz14812_outcome_aggregation_gate.py
│   ├── zzz1481_closure_gate.py
│   ├── zzz148_decision_utility_gate.py
│   ├── zzz149_frozen_decision_oos_gate.py
│   ├── backtest/
│   │   ├── calendar.py
│   │   ├── costs.py
│   │   ├── dataset_splitter.py
│   │   ├── engine.py
│   │   ├── experiment_registry.py
│   │   ├── metrics.py
│   │   ├── models.py
│   │   ├── performance_attribution.py
│   │   ├── performance_validator.py
│   │   ├── replay.py
│   │   ├── robustness.py
│   │   ├── score_analysis.py
│   │   ├── walk_forward.py
│   ├── ingestion/
│   │   ├── info_source_registry.py
│   │   ├── market_ingestor.py
│   │   ├── news_rss_ingestor.py
│   │   ├── semantic_ingestor.py
│   │   ├── source_registry.py
│   │   ├── universe_builder.py
│   ├── providers/
│   │   ├── yfinance_provider.py
│   │   ├── __init__.py
├── d/
│   ├── lessons/
│   ├── missed_opportunities/
│   ├── patterns/
├── data/
│   ├── cache/
│   │   ├── .gitkeep
│   ├── duckdb/
│   │   ├── intelligence.duckdb
│   ├── intelligence/
│   ├── manifests/
│   ├── parquet/
│   │   ├── BBCA_pilot.parquet
│   │   ├── corporate_actions/
│   │   │   ├── ADRO_actions.parquet
│   │   │   ├── ANTM_actions.parquet
│   │   │   ├── ASII_actions.parquet
│   │   │   ├── BBCA_actions.parquet
│   │   │   ├── BBNI_actions.parquet
│   │   │   ├── BBRI_actions.parquet
│   │   │   ├── BMRI_actions.parquet
│   │   │   ├── INCO_actions.parquet
│   │   │   ├── ITMG_actions.parquet
│   │   │   ├── PTBA_actions.parquet
│   │   │   ├── TLKM_actions.parquet
│   │   │   ├── UNTR_actions.parquet
│   │   ├── entity/
│   │   │   ├── universe.parquet
│   │   ├── market/
│   │   │   ├── ADRO.parquet
│   │   │   ├── ANTM.parquet
│   │   │   ├── ASII.parquet
│   │   │   ├── BBCA.parquet
│   │   │   ├── BBNI.parquet
│   │   │   ├── BBRI.parquet
│   │   │   ├── BMRI.parquet
│   │   │   ├── INCO.parquet
│   │   │   ├── ITMG.parquet
│   │   │   ├── PTBA.parquet
│   │   │   ├── TLKM.parquet
│   │   │   ├── UNTR.parquet
│   ├── processed/
│   │   ├── .gitkeep
│   │   ├── IDX_DAILY_20260911_069ee2ed.json
│   │   ├── manifest.json
│   ├── raw/
│   │   ├── .gitkeep
│   │   ├── disclosures/
│   │   │   ├── idx/
│   │   │   │   ├── RAW_IDX_DISC_2025_FY_ADRO_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_FY_ITMG_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_FY_PTBA_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_ADRO_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_ANTM_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_ASII_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_BBCA_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_BBNI_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_BBRI_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_BMRI_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_INCO_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_ITMG_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_PTBA_001.json
│   │   │   │   ├── RAW_IDX_DISC_2025_Q3_UNTR_001.json
│   │   │   │   ├── RAW_IDX_DISC_CONTRACT_UNTR_001.json
│   │   │   │   ├── RAW_IDX_DISC_PROJECT_ANTM_001.json
│   │   │   ├── issuer/
│   │   │   │   ├── RAW_ISSUER_GUIDANCE_2026_ADRO_001.json
│   │   │   │   ├── RAW_ISSUER_GUIDANCE_2026_ANTM_001.json
│   │   │   │   ├── RAW_ISSUER_GUIDANCE_2026_ITMG_001.json
│   │   │   │   ├── RAW_ISSUER_GUIDANCE_2026_PTBA_001.json
│   │   │   │   ├── RAW_ISSUER_PROD_2025_Q3_INCO_001.json
│   │   │   │   ├── RAW_ISSUER_PROD_2025_Q3_UNTR_001.json
│   │   │   │   ├── RAW_ISSUER_PROD_2026_Q1_INCO_001.json
│   │   │   │   ├── RAW_ISSUER_PROD_2026_Q1_UNTR_001.json
│   │   │   ├── news/
│   │   │   │   ├── RAW_NEWS_CNBC_2026_ADRO_001.json
│   │   │   ├── regulator/
│   │   │   │   ├── RAW_ESDM_REG_2026_COAL_001.json
│   │   │   │   ├── RAW_ESDM_REG_2026_COAL_002.json
│   │   │   │   ├── RAW_ESDM_REG_2026_NICKEL_001.json
│   │   │   │   ├── RAW_ESDM_REG_2026_NICKEL_002.json
│   │   ├── historical/
│   │   │   ├── ADRO_2026-09-11T012347.581762+0000.json
│   │   │   ├── ADRO_2026-09-11T012347.581762+0000.json.meta
│   │   │   ├── ANTM_2026-09-11T012348.374726+0000.json
│   │   │   ├── ANTM_2026-09-11T012348.374726+0000.json.meta
│   │   │   ├── ASII_2026-09-11T012343.587406+0000.json
│   │   │   ├── ASII_2026-09-11T012343.587406+0000.json.meta
│   │   │   ├── BBCA_2026-09-11T012339.574069+0000.json
│   │   │   ├── BBCA_2026-09-11T012339.574069+0000.json.meta
│   │   │   ├── BBNI_2026-09-11T012341.189741+0000.json
│   │   │   ├── BBNI_2026-09-11T012341.189741+0000.json.meta
│   │   │   ├── BMRI_2026-09-11T012340.384783+0000.json
│   │   │   ├── BMRI_2026-09-11T012340.384783+0000.json.meta
│   │   │   ├── BRIS_2026-09-11T012341.949325+0000.json
│   │   │   ├── BRIS_2026-09-11T012341.949325+0000.json.meta
│   │   │   ├── ICBP_2026-09-11T012345.180439+0000.json
│   │   │   ├── ICBP_2026-09-11T012345.180439+0000.json.meta
│   │   │   ├── IHSG_2026-09-11T012338.716817+0000.json
│   │   │   ├── IHSG_2026-09-11T012338.716817+0000.json.meta
│   │   │   ├── INDF_2026-09-11T012345.997529+0000.json
│   │   │   ├── INDF_2026-09-11T012345.997529+0000.json.meta
│   │   │   ├── PGAS_2026-09-11T012346.795756+0000.json
│   │   │   ├── PGAS_2026-09-11T012346.795756+0000.json.meta
│   │   │   ├── PTBA_2026-09-11T012349.242769+0000.json
│   │   │   ├── PTBA_2026-09-11T012349.242769+0000.json.meta
│   │   │   ├── TLKM_2026-09-11T012342.761762+0000.json
│   │   │   ├── TLKM_2026-09-11T012342.761762+0000.json.meta
│   │   │   ├── UNVR_2026-09-11T012344.398170+0000.json
│   │   │   ├── UNVR_2026-09-11T012344.398170+0000.json.meta
│   │   ├── market/
│   │   │   ├── ADRO_raw.csv
│   │   │   ├── ANTM_raw.csv
│   │   │   ├── ASII_raw.csv
│   │   │   ├── BBCA_raw.csv
│   │   │   ├── BBNI_raw.csv
│   │   │   ├── BBRI_raw.csv
│   │   │   ├── BMRI_raw.csv
│   │   │   ├── INCO_raw.csv
│   │   │   ├── ITMG_raw.csv
│   │   │   ├── PTBA_raw.csv
│   │   │   ├── TLKM_raw.csv
│   │   │   ├── UNTR_raw.csv
│   │   ├── news/
│   │   │   ├── cnbc_20260914_022907.xml
│   │   │   ├── cnbc_20260914_023723.xml
│   │   ├── synthetic/
├── docs/
│   ├── ADAPTIVE_HISTORICAL_DATA_FOUNDATION_ZZZ13.md
│   ├── ARCHITECTURE_CANONICAL.md
│   ├── DATASET_V2_RESEARCH_READINESS.md
│   ├── FILE_STATUS_MANIFEST.md
│   ├── HISTORICAL_REPLAY_SPEC_ZZZ142.md
│   ├── PROJECT_MEMORY.md
│   ├── RELATIONSHIP_ARCHITECTURE.md
│   ├── REPLAY_FIREWALL_SPEC_ZZZ142.md
│   ├── RESEARCH_METHODOLOGY_LOCK_ZZZ12.md
│   ├── ZZZ147_FIREWALL_SPEC.md
│   ├── ZZZ147_SCIENTIFIC_SPEC.md
├── dummy/
│   ├── lessons/
│   ├── missed_opportunities/
│   ├── patterns/
├── gates/
│   ├── active/
│   ├── closed/
│   │   ├── batch_ar_opportunity_timing_report.md
│   │   ├── batch_as_signal_state_hardening_report.md
│   │   ├── batch_at_data_acquisition_report.json
│   │   ├── batch_at_data_acquisition_report.md
│   │   ├── batch_aw_oos_failure_diagnosis.md
│   │   ├── batch_ax_experiment_report.json
│   │   ├── batch_ax_experiment_report.md
│   │   ├── batch_ay1_statistical_robustness.md
│   │   ├── batch_ay2_cluster_validation.md
│   │   ├── batch_ay_signal_quality.json
│   │   ├── batch_ay_signal_quality.md
│   │   ├── batch_az1_alpha_discovery.md
│   │   ├── batch_az1_experiment_spec.md
│   │   ├── batch_az2_commodity_transmission.md
│   │   ├── batch_az3_gold_antm_validation.md
│   │   ├── batch_xxx4_repository_audit.md
│   │   ├── batch_yyy21r_antigravity.md
│   │   ├── batch_yyy221_antigravity_native_runtime_path.md
│   │   ├── batch_yyy22_runtime_auth_validation.md
│   │   ├── batch_yyy31_data_foundation_audit.md
│   │   ├── batch_yyy3_historical_intelligence_oos.md
│   │   ├── batch_zzz1_real_data_ingestion.md
│   │   ├── batch_zzz2_information_ledger.md
│   │   ├── batch_zzz31_semantic_data_integrity.md
│   │   ├── batch_zzz3_historical_semantic_ingestion.md
│   │   ├── batch_zzz41_agent2_adversarial_validation.md
│   │   ├── batch_zzz4_agent2_intelligence_pilot.md
│   │   ├── batch_zzz5_agent1_validation.md
│   │   ├── batch_zzz61_agent1_inactivity_root_cause.md
│   │   ├── batch_zzz6_directional_alpha_validation.md
│   │   ├── batch_zzz71_attribution_logic_audit.md
│   │   ├── batch_zzz7_historical_candidate_attribution_validation.md
│   │   ├── batch_zzz81_ablation_selection_robustness.md
│   │   ├── batch_zzz82_temporal_cross_sectional_oos_validation.md
│   │   ├── batch_zzz8_multi_agent_incremental_ev_experiment.md
│   │   ├── batch_zzz91_semantic_attribution_ablation_causal_discipline_audit.md
│   │   ├── batch_zzz9_historical_semantic_explanation_attribution.md
│   │   ├── data_source_registry_zzz1.csv
│   │   ├── zzz10_1_historical_disclosure_coverage_audit.md
│   │   ├── zzz10_2_historical_disclosure_ingestion.md
│   │   ├── zzz10_3_historical_disclosure_completeness_audit.md
│   │   ├── zzz10_company_specific_information_discrimination.md
│   │   ├── zzz11_1_coverage_aware_discrimination.md
│   │   ├── zzz11_2_identification_audit.md
│   │   ├── zzz11_3_identification_stress_test.md
│   │   ├── zzz11_4_pretrend_adjusted_information_audit.md
│   │   ├── zzz11_5_joint_identification_information_state_audit.md
│   │   ├── zzz11_6_counterfactual_peer_excess_integrity_audit.md
│   │   ├── zzz11_7_company_specific_counterfactual_purification.md
│   │   ├── zzz11_company_specific_discrimination.md
│   │   ├── zzz12_research_methodology_lock_gate.md
│   │   ├── zzz13_adaptive_historical_data_foundation.md
│   │   ├── zzz1471_canonical_observation_matrix.csv
│   │   ├── zzz14_1_1_research_readiness_evidence_audit.md
│   │   ├── zzz14_1_dataset_v2_integrity_audit.md
│   │   ├── zzz14_2_1R_independent_adversarial_acceptance_review.md
│   │   ├── zzz14_2_1_acceptance_evidence_review.md
│   │   ├── zzz14_2_1_agent2_replay_integration_pilot.md
│   │   ├── zzz14_2_historical_replay_engine.md
│   │   ├── zzz14_3_1_canonical_layer_e_replication.json
│   │   ├── zzz14_3_1_canonical_layer_e_replication.md
│   │   ├── zzz14_3_2_fixed_sample_layer_attribution.json
│   │   ├── zzz14_3_2_fixed_sample_layer_attribution.md
│   │   ├── zzz14_3_3_evidence_deconfounding_stress_test.json
│   │   ├── zzz14_3_3_evidence_deconfounding_stress_test.md
│   │   ├── zzz14_3_4_event_clusters.csv
│   │   ├── zzz14_3_4_event_reuse.csv
│   │   ├── zzz14_3_4_lodo_event.csv
│   │   ├── zzz14_3_4_manifest.json
│   │   ├── zzz14_3_4_matching_pairs.csv
│   │   ├── zzz14_3_4_pre_t_balance.csv
│   │   ├── zzz14_3_4_pre_t_matched_event_cluster_gate.md
│   │   ├── zzz14_3_4_result_matrix.csv
│   │   ├── zzz14_3_5_coverage_balance.csv
│   │   ├── zzz14_3_5_coverage_variables.csv
│   │   ├── zzz14_3_5_event_cluster_results.csv
│   │   ├── zzz14_3_5_event_density_sensitivity.csv
│   │   ├── zzz14_3_5_information_coverage_gate.md
│   │   ├── zzz14_3_5_lodo_event.csv
│   │   ├── zzz14_3_5_manifest.json
│   │   ├── zzz14_3_5_result_matrix.csv
│   │   ├── zzz14_3_5_strict_matching_pairs.csv
│   │   ├── zzz14_3_6_event_cluster_inference.csv
│   │   ├── zzz14_3_6_event_equalized.csv
│   │   ├── zzz14_3_6_inference_reconciliation.csv
│   │   ├── zzz14_3_6_information_environment.csv
│   │   ├── zzz14_3_6_lodo.csv
│   │   ├── zzz14_3_6_manifest.json
│   │   ├── zzz14_3_6_pre_t_balance.csv
│   │   ├── zzz14_3_6_result_matrix.csv
│   │   ├── zzz14_3_6_strict_counterfactual_inference_gate.md
│   │   ├── zzz14_3_6_strict_matching_pairs.csv
│   │   ├── zzz14_3_7_balance.csv
│   │   ├── zzz14_3_7_common_support_gate.md
│   │   ├── zzz14_3_7_date_support.csv
│   │   ├── zzz14_3_7_event_inference.csv
│   │   ├── zzz14_3_7_identifiable_population.csv
│   │   ├── zzz14_3_7_inference_single_source.csv
│   │   ├── zzz14_3_7_lodo.csv
│   │   ├── zzz14_3_7_manifest.json
│   │   ├── zzz14_3_7_matching_pairs.csv
│   │   ├── zzz14_3_7_result_matrix.csv
│   │   ├── zzz14_3_7_support_distances.csv
│   │   ├── zzz14_3_7_support_matrix.csv
│   │   ├── zzz14_3_7_ticker_support.csv
│   │   ├── zzz14_3_8_balance.csv
│   │   ├── zzz14_3_8_closure_gate.md
│   │   ├── zzz14_3_8_event_dependence.csv
│   │   ├── zzz14_3_8_inference_reconciled.csv
│   │   ├── zzz14_3_8_manifest.json
│   │   ├── zzz14_3_8_red_team.csv
│   │   ├── zzz14_3_8_residual_confounding.csv
│   │   ├── zzz14_3_8_support_sensitivity.csv
│   │   ├── zzz14_3_8_survivorship_provenance.csv
│   │   ├── zzz14_3_9_ai_evidence_audit.csv
│   │   ├── zzz14_3_9_ai_evidence_selection.csv
│   │   ├── zzz14_3_9_ai_pit_audit.csv
│   │   ├── zzz14_3_9_ai_red_team.csv
│   │   ├── zzz14_3_9_ai_vs_deterministic.csv
│   │   ├── zzz14_3_9_estimand_identity.md
│   │   ├── zzz14_3_9_estimand_reconciliation.csv
│   │   ├── zzz14_3_9_manifest.json
│   │   ├── zzz14_3_9_threshold_identity.csv
│   │   ├── zzz14_3_agent2_historical_discrimination_pilot.md
│   │   ├── zzz14_4_ai_coverage_bias.csv
│   │   ├── zzz14_4_ai_cross_event.csv
│   │   ├── zzz14_4_ai_cross_regime.csv
│   │   ├── zzz14_4_ai_cross_ticker.csv
│   │   ├── zzz14_4_ai_evidence_selection.csv
│   │   ├── zzz14_4_ai_oos.csv
│   │   ├── zzz14_4_ai_pit_audit.csv
│   │   ├── zzz14_4_ai_quality_matrix.csv
│   │   ├── zzz14_4_ai_red_team.csv
│   │   ├── zzz14_4_ai_reference_audit.csv
│   │   ├── zzz14_4_ai_reproducibility.csv
│   │   ├── zzz14_4_ai_scaleup.md
│   │   ├── zzz14_4_ai_vs_deterministic.csv
│   │   ├── zzz14_4_manifest.json
│   │   ├── zzz14_5_ablation_matrix.csv
│   │   ├── zzz14_5_ai_attribution.md
│   │   ├── zzz14_5_ai_drift.csv
│   │   ├── zzz14_5_ai_vs_deterministic.csv
│   │   ├── zzz14_5_coverage_attribution.csv
│   │   ├── zzz14_5_cross_cycle.csv
│   │   ├── zzz14_5_event_attribution.csv
│   │   ├── zzz14_5_information_novelty.csv
│   │   ├── zzz14_5_information_redundancy.csv
│   │   ├── zzz14_5_manifest.json
│   │   ├── zzz14_5_model_provenance.csv
│   │   ├── zzz14_5_oos.csv
│   │   ├── zzz14_5_placebo.csv
│   │   ├── zzz14_5_red_team.csv
│   │   ├── zzz14_5_regime_attribution.csv
│   │   ├── zzz14_5_structure_matched_random.csv
│   │   ├── zzz14_5_ticker_attribution.csv
│   │   ├── zzz14_6_1_baseline_identity.csv
│   │   ├── zzz14_6_1_canonical_setup_matrix.csv
│   │   ├── zzz14_6_1_contradiction_counterfactual.csv
│   │   ├── zzz14_6_1_coverage.csv
│   │   ├── zzz14_6_1_decision_transition_matrix.csv
│   │   ├── zzz14_6_1_event.csv
│   │   ├── zzz14_6_1_l5_l6_reconciliation.csv
│   │   ├── zzz14_6_1_manifest.json
│   │   ├── zzz14_6_1_oos.csv
│   │   ├── zzz14_6_1_outcome_after_freeze.csv
│   │   ├── zzz14_6_1_placebo.csv
│   │   ├── zzz14_6_1_quality_reference_audit.csv
│   │   ├── zzz14_6_1_reconciliation.md
│   │   ├── zzz14_6_1_red_team.csv
│   │   ├── zzz14_6_1_regime.csv
│   │   ├── zzz14_6_1_thesis_reconciliation.csv
│   │   ├── zzz14_6_1_ticker.csv
│   │   ├── zzz14_6_1_transmission_counterfactual.csv
│   │   ├── zzz14_6_2_avoided_loss_formula_audit.csv
│   │   ├── zzz14_6_2_c0_c1_pair_integrity.csv
│   │   ├── zzz14_6_2_capital_semantics.csv
│   │   ├── zzz14_6_2_counterfactual_closure.md
│   │   ├── zzz14_6_2_counterfactual_setup_matrix.csv
│   │   ├── zzz14_6_2_date_dependence.csv
│   │   ├── zzz14_6_2_event_dependence.csv
│   │   ├── zzz14_6_2_manifest.json
│   │   ├── zzz14_6_2_oos_outcome.csv
│   │   ├── zzz14_6_2_outcome_reconciliation.csv
│   │   ├── zzz14_6_2_red_team.csv
│   │   ├── zzz14_6_2_selection_audit.csv
│   │   ├── zzz14_6_2_ticker_dependence.csv
│   │   ├── zzz14_6_3_159_vs_161.csv
│   │   ├── zzz14_6_3_c0_c1_population_identity.csv
│   │   ├── zzz14_6_3_contradiction_population_ledger.csv
│   │   ├── zzz14_6_3_dependence.csv
│   │   ├── zzz14_6_3_formula_reconciliation.csv
│   │   ├── zzz14_6_3_manifest.json
│   │   ├── zzz14_6_3_outcome_population.csv
│   │   ├── zzz14_6_3_pit_audit.csv
│   │   ├── zzz14_6_3_population_identity.md
│   │   ├── zzz14_6_3_red_team.csv
│   │   ├── zzz14_6_contradiction_counterfactual.csv
│   │   ├── zzz14_6_coverage_attribution.csv
│   │   ├── zzz14_6_cross_cycle.csv
│   │   ├── zzz14_6_decision_delta.csv
│   │   ├── zzz14_6_decision_quality.csv
│   │   ├── zzz14_6_drift.csv
│   │   ├── zzz14_6_event_attribution.csv
│   │   ├── zzz14_6_manifest.json
│   │   ├── zzz14_6_oos.csv
│   │   ├── zzz14_6_placebo.csv
│   │   ├── zzz14_6_red_team.csv
│   │   ├── zzz14_6_reference_audit.csv
│   │   ├── zzz14_6_regime_attribution.csv
│   │   ├── zzz14_6_syntactic_synthesis.md
│   │   ├── zzz14_6_thesis_attribution.csv
│   │   ├── zzz14_6_ticker_attribution.csv
│   │   ├── zzz14_6_transmission_counterfactual.csv
│   │   ├── zzz14_7_1_canonical_inference.json
│   │   ├── zzz14_7_1_closure.md
│   │   ├── zzz14_7_1_manifest.json
│   │   ├── zzz14_7_1_red_team.csv
│   │   ├── zzz14_7_2_canonical_inference.json
│   │   ├── zzz14_7_2_closure.md
│   │   ├── zzz14_7_2_red_team.csv
│   │   ├── zzz14_7_attribution.md
│   │   ├── zzz14_7_canonical_results.json
│   │   ├── zzz14_7_drift.csv
│   │   ├── zzz14_7_inference_matrix.csv
│   │   ├── zzz14_7_information_attribution.csv
│   │   ├── zzz14_7_manifest.json
│   │   ├── zzz14_7_negative_controls.csv
│   │   ├── zzz14_7_oos.csv
│   │   ├── zzz14_7_placebo.csv
│   │   ├── zzz14_7_red_team.csv
│   │   ├── zzz14_7_setup_matrix.csv
│   │   ├── zzz14_7_support.csv
│   │   ├── zzz14_8_1_1_canonical_decision_population.csv
│   │   ├── zzz14_8_1_1_exception_ledger.csv
│   │   ├── zzz14_8_1_1_manifest.json
│   │   ├── zzz14_8_1_1_reconciliation.csv
│   │   ├── zzz14_8_1_1_red_team.csv
│   │   ├── zzz14_8_1_1_transition_matrix_25x25.csv
│   │   ├── zzz14_8_1_1_validation.json
│   │   ├── zzz14_8_1_1_validation.md
│   │   ├── zzz14_8_1_2_canonical_transition_outcomes.csv
│   │   ├── zzz14_8_1_2_manifest.json
│   │   ├── zzz14_8_1_2_reconciliation.csv
│   │   ├── zzz14_8_1_2_source_audit.json
│   │   ├── zzz14_8_1_2_validation.json
│   │   ├── zzz14_8_1_2_validation.md
│   │   ├── zzz14_8_1_calibration.csv
│   │   ├── zzz14_8_1_decision_utility_reconciliation.json
│   │   ├── zzz14_8_1_inference.json
│   │   ├── zzz14_8_1_oos_decision_utility.csv
│   │   ├── zzz14_8_1_red_team.csv
│   │   ├── zzz14_8_1_transition_matrix.csv
│   │   ├── zzz14_8_1_validation.md
│   │   ├── zzz14_8_canonical_result.json
│   │   ├── zzz14_8_canonical_setup_decision_matrix.csv
│   │   ├── zzz14_8_concentration_audit.csv
│   │   ├── zzz14_8_counterfactual_matrix.csv
│   │   ├── zzz14_8_decision_objects.json
│   │   ├── zzz14_8_inference.json
│   │   ├── zzz14_8_information_attribution.csv
│   │   ├── zzz14_8_manifest.json
│   │   ├── zzz14_8_placebo_results.csv
│   │   ├── zzz14_8_red_team.csv
│   │   ├── zzz14_8_semantic_benchmark.csv
│   │   ├── zzz14_8_temporal_results.csv
│   │   ├── zzz14_8_validation.md
│   │   ├── zzz14_historical_data_acquisition.md
│   ├── evidence/
│   │   ├── run_zzz101_historical_disclosure_coverage.py
│   │   ├── run_zzz102_historical_disclosure_ingestion.py
│   │   ├── run_zzz103_completeness_audit.py
│   │   ├── run_zzz10_company_specific_discrimination.py
│   │   ├── run_zzz111_coverage_aware_discrimination.py
│   │   ├── run_zzz112_identification_audit.py
│   │   ├── run_zzz113_identification_stress_test.cpython-312-pytest-9.1.1.pyc
│   │   ├── run_zzz113_identification_stress_test.py
│   │   ├── run_zzz114_pretrend_adjusted_information.py
│   │   ├── run_zzz115_joint_identification.py
│   │   ├── run_zzz116_counterfactual_integrity.py
│   │   ├── run_zzz117_counterfactual_purification.py
│   │   ├── run_zzz11_company_specific_discrimination.py
│   │   ├── run_zzz12_methodology_lock.py
│   │   ├── run_zzz13_adaptive_foundation.py
│   │   ├── run_zzz1411_research_readiness.py
│   │   ├── run_zzz141_dataset_v2_integrity.py
│   │   ├── run_zzz1421R_adversarial_challenge.py
│   │   ├── run_zzz1421_pilot_acceptance.py
│   │   ├── run_zzz142_historical_replay.py
│   │   ├── run_zzz1431_canonical_replication.py
│   │   ├── run_zzz1432_fixed_sample_attribution.py
│   │   ├── run_zzz1433_deconfounding.py
│   │   ├── run_zzz1434_matched_event_cluster.py
│   │   ├── run_zzz1435_information_coverage.py
│   │   ├── run_zzz1436_strict_counterfactual.py
│   │   ├── run_zzz1437_common_support.py
│   │   ├── run_zzz1438_closure_gate.py
│   │   ├── run_zzz1439_estimand_ai.py
│   │   ├── run_zzz143_historical_discrimination.py
│   │   ├── run_zzz144_ai_scaleup.py
│   │   ├── run_zzz145_ai_attribution.py
│   │   ├── run_zzz1461_reconciliation.py
│   │   ├── run_zzz1462_counterfactual_closure.py
│   │   ├── run_zzz146_synthesis_integration.py
│   │   ├── run_zzz14_historical_data_acquisition.py
│   │   ├── run_zzz62_alpha_validation.py
│   │   ├── run_zzz71_audit_population.py
│   │   ├── run_zzz7_attribution_validation.py
│   │   ├── run_zzz81_ablation_experiment.py
│   │   ├── run_zzz82_oos_validation.py
│   │   ├── run_zzz8_incremental_ev_experiment.py
│   │   ├── run_zzz91_semantic_ablation.py
│   │   ├── run_zzz9_semantic_expansion.py
│   │   ├── zzz101_coverage_results.parquet
│   │   ├── zzz101_summary.json
│   │   ├── zzz102_coverage_summary.json
│   │   ├── zzz102_disclosure_events.parquet
│   │   ├── zzz103_completeness_results.parquet
│   │   ├── zzz103_recall_audit.json
│   │   ├── zzz103_source_coverage.json
│   │   ├── zzz10_results.parquet
│   │   ├── zzz10_summary.json
│   │   ├── zzz111_coverage_control.json
│   │   ├── zzz111_matching_results.json
│   │   ├── zzz111_missingness_analysis.json
│   │   ├── zzz111_redteam.json
│   │   ├── zzz111_results.parquet
│   │   ├── zzz111_source_sensitivity.json
│   │   ├── zzz112_control_candidates.parquet
│   │   ├── zzz112_matching_results.json
│   │   ├── zzz112_missingness_analysis.json
│   │   ├── zzz112_observation_level_audit.parquet
│   │   ├── zzz112_redteam.json
│   │   ├── zzz112_source_sensitivity.json
│   │   ├── zzz112_ticker_audit.json
│   │   ├── zzz112_zero_differential_audit.json
│   │   ├── zzz113_control_candidates.parquet
│   │   ├── zzz113_event_time.json
│   │   ├── zzz113_fixed_effects.json
│   │   ├── zzz113_matching.json
│   │   ├── zzz113_missingness.json
│   │   ├── zzz113_observation_level.parquet
│   │   ├── zzz113_placebo.json
│   │   ├── zzz113_pretrend.json
│   │   ├── zzz113_redteam.json
│   │   ├── zzz113_statistical_results.json
│   │   ├── zzz114_event_time.json
│   │   ├── zzz114_information_decay.json
│   │   ├── zzz114_lead_test.json
│   │   ├── zzz114_matching.json
│   │   ├── zzz114_missingness.json
│   │   ├── zzz114_observation_level.parquet
│   │   ├── zzz114_placebo.json
│   │   ├── zzz114_pretrend_models.json
│   │   ├── zzz114_redteam.json
│   │   ├── zzz114_residual_analysis.json
│   │   ├── zzz114_same_company.json
│   │   ├── zzz114_statistical_results.json
│   │   ├── zzz114_surprise_classification.parquet
│   │   ├── zzz115_canonical_reconciliation.json
│   │   ├── zzz115_common_support.json
│   │   ├── zzz115_event_novelty.parquet
│   │   ├── zzz115_event_time.json
│   │   ├── zzz115_event_timing.parquet
│   │   ├── zzz115_joint_models.json
│   │   ├── zzz115_missingness.json
│   │   ├── zzz115_multicollinearity.json
│   │   ├── zzz115_negative_control.json
│   │   ├── zzz115_observation_level.parquet
│   │   ├── zzz115_placebo.json
│   │   ├── zzz115_propensity_diagnostic.json
│   │   ├── zzz115_propensity_matching.json
│   │   ├── zzz115_redteam.json
│   │   ├── zzz115_same_company.json
│   │   ├── zzz115_same_date_exposure.json
│   │   ├── zzz115_selection_audit.json
│   │   ├── zzz115_statistical_results.json
│   │   ├── zzz116_benchmark_sensitivity.json
│   │   ├── zzz116_cluster_inference.json
│   │   ├── zzz116_control_purity.json
│   │   ├── zzz116_date_weighting.json
│   │   ├── zzz116_duplicates.json
│   │   ├── zzz116_effective_sample.json
│   │   ├── zzz116_event_clusters.json
│   │   ├── zzz116_leave_one_out.json
│   │   ├── zzz116_observation_level.parquet
│   │   ├── zzz116_peer_contamination.json
│   │   ├── zzz116_peer_exclusion_matrix.parquet
│   │   ├── zzz116_peer_membership.parquet
│   │   ├── zzz116_redteam.json
│   │   ├── zzz116_same_date_exposure.json
│   │   ├── zzz116_statistical_results.json
│   │   ├── zzz116_ticker_weighting.json
│   │   ├── zzz117_cluster_results.json
│   │   ├── zzz117_contamination.json
│   │   ├── zzz117_counterfactual_results.json
│   │   ├── zzz117_date_purification.parquet
│   │   ├── zzz117_event_purification.parquet
│   │   ├── zzz117_observation_counterfactual_matrix.parquet
│   │   ├── zzz117_peer_purification.parquet
│   │   ├── zzz117_placebo_results.json
│   │   ├── zzz117_pretrend_results.json
│   │   ├── zzz117_redteam.json
│   │   ├── zzz117_snapshot_manifest.json
│   │   ├── zzz117_statistical_results.json
│   │   ├── zzz117_ticker_results.json
│   │   ├── zzz117_weighting_results.json
│   │   ├── zzz11_company_specific_results.parquet
│   │   ├── zzz11_coverage_analysis.json
│   │   ├── zzz11_redteam.json
│   │   ├── zzz11_source_intelligence.json
│   │   ├── zzz11_source_registry.json
│   │   ├── zzz12_gate_decision.json
│   │   ├── zzz12_methodology_manifest.json
│   │   ├── zzz12_redteam.json
│   │   ├── zzz13_branch_manifest.json
│   │   ├── zzz13_criteria_registry.json
│   │   ├── zzz13_redteam.json
│   │   ├── zzz13_schema_lineage.json
│   │   ├── zzz1411_claim_evidence_matrix.json
│   │   ├── zzz1411_contradiction_audit.json
│   │   ├── zzz1411_corporate_action_audit.json
│   │   ├── zzz1411_current_state_leakage.json
│   │   ├── zzz1411_dataset_inventory.json
│   │   ├── zzz1411_dependency_audit.json
│   │   ├── zzz1411_domain_readiness.json
│   │   ├── zzz1411_entity_resolution.json
│   │   ├── zzz1411_event_dedup.json
│   │   ├── zzz1411_event_evidence_mapping.json
│   │   ├── zzz1411_exposure_audit.json
│   │   ├── zzz1411_final_gate.json
│   │   ├── zzz1411_fundamental_restatement.json
│   │   ├── zzz1411_future_injection.json
│   │   ├── zzz1411_information_density.json
│   │   ├── zzz1411_missingness.json
│   │   ├── zzz1411_news_coverage.json
│   │   ├── zzz1411_nlp_audit.json
│   │   ├── zzz1411_outcome_blindness.json
│   │   ├── zzz1411_ownership_coverage.json
│   │   ├── zzz1411_period_readiness.json
│   │   ├── zzz1411_pit_semantic_audit.json
│   │   ├── zzz1411_provenance_sample.json
│   │   ├── zzz1411_redteam.json
│   │   ├── zzz1411_relationship_temporal.json
│   │   ├── zzz1411_replay_eligibility.json
│   │   ├── zzz1411_reproducibility.json
│   │   ├── zzz1411_snapshot_firewall.json
│   │   ├── zzz1411_source_authenticity.json
│   │   ├── zzz1411_source_quality.json
│   │   ├── zzz1411_survivorship.json
│   │   ├── zzz1411_temporal_concentration.json
│   │   ├── zzz1411_universe_history.json
│   │   ├── zzz1411_v1_observation_replication.json
│   │   ├── zzz141_concentration_audit.json
│   │   ├── zzz141_contradiction_audit.json
│   │   ├── zzz141_current_state_leakage.json
│   │   ├── zzz141_dataset_inventory.json
│   │   ├── zzz141_entity_audit.json
│   │   ├── zzz141_event_dedup.json
│   │   ├── zzz141_exposure_audit.json
│   │   ├── zzz141_future_injection.json
│   │   ├── zzz141_hash_audit.json
│   │   ├── zzz141_market_integrity.json
│   │   ├── zzz141_missingness.json
│   │   ├── zzz141_nlp_audit.json
│   │   ├── zzz141_pit_audit.json
│   │   ├── zzz141_provenance_audit.json
│   │   ├── zzz141_quality_matrix.json
│   │   ├── zzz141_redteam.json
│   │   ├── zzz141_relationship_audit.json
│   │   ├── zzz141_research_readiness.json
│   │   ├── zzz141_source_coverage.json
│   │   ├── zzz141_survivorship_audit.json
│   │   ├── zzz141_universe_audit.json
│   │   ├── zzz141_v1_replication.json
│   │   ├── zzz1421R_adversarial_review.json
│   │   ├── zzz1421R_agent2_bypass_audit.json
│   │   ├── zzz1421R_sample_selection_audit.json
│   │   ├── zzz1421R_sentinel_injection.json
│   │   ├── zzz1421_acceptance_evidence_review.json
│   │   ├── zzz1421_agent2_context_firewall.json
│   │   ├── zzz1421_derived_feature_leakage.json
│   │   ├── zzz1421_eligibility_matrix.json
│   │   ├── zzz1421_leakage_audit.json
│   │   ├── zzz1421_outcome_blindness.json
│   │   ├── zzz1421_peer_integrity.json
│   │   ├── zzz1421_pilot_observation_level.parquet
│   │   ├── zzz1421_red_team.json
│   │   ├── zzz1421_reproducibility.json
│   │   ├── zzz1421_v1_reconciliation.json
│   │   ├── zzz142_coverage_matrix.json
│   │   ├── zzz142_current_state_injection.json
│   │   ├── zzz142_domain_readiness.json
│   │   ├── zzz142_firewall_rules.json
│   │   ├── zzz142_future_injection.json
│   │   ├── zzz142_outcome_firewall.json
│   │   ├── zzz142_pilot_results.json
│   │   ├── zzz142_pit_results.json
│   │   ├── zzz142_redteam.json
│   │   ├── zzz142_replay_eligibility.json
│   │   ├── zzz142_replay_manifest.json
│   │   ├── zzz142_snapshot_hashes.json
│   │   ├── zzz1431_agent2_thesis_freeze.json
│   │   ├── zzz1431_canonical_manifest.json
│   │   ├── zzz1431_concentration_audit.json
│   │   ├── zzz1431_derived_feature_leakage.json
│   │   ├── zzz1431_layer_results.json
│   │   ├── zzz1431_leakage_audit.json
│   │   ├── zzz1431_observation_level.parquet
│   │   ├── zzz1431_peer_integrity.json
│   │   ├── zzz1431_reconciliation_ledger.json
│   │   ├── zzz1431_red_team_results.json
│   │   ├── zzz1431_replay_eligibility.json
│   │   ├── zzz1431_reproducibility.json
│   │   ├── zzz1431_silent_fallback.json
│   │   ├── zzz1431_stratification_results.json
│   │   ├── zzz1432_agent2_output_ledger.json
│   │   ├── zzz1432_concentration_audit.json
│   │   ├── zzz1432_evidence_association.json
│   │   ├── zzz1432_fixed_sample_manifest.json
│   │   ├── zzz1432_information_variation_audit.json
│   │   ├── zzz1432_layer_comparison.json
│   │   ├── zzz1432_layer_states.json
│   │   ├── zzz1432_leakage_audit.json
│   │   ├── zzz1432_preoutcome_freeze.json
│   │   ├── zzz1432_redteam_output_ledger.json
│   │   ├── zzz1432_reproducibility.json
│   │   ├── zzz1433_balance_audit.json
│   │   ├── zzz1433_control_eligibility.json
│   │   ├── zzz1433_control_manifest.json
│   │   ├── zzz1433_coverage_audit.json
│   │   ├── zzz1433_effect_attenuation.json
│   │   ├── zzz1433_event_reuse_audit.json
│   │   ├── zzz1433_fixed_effect_results.json
│   │   ├── zzz1433_leakage_audit.json
│   │   ├── zzz1433_matching_results.json
│   │   ├── zzz1433_placebo_results.json
│   │   ├── zzz1433_redteam_attacks.json
│   │   ├── zzz1433_reproducibility.json
│   │   ├── zzz1433_sample_flow.json
│   │   ├── zzz143_agent2_thesis_freeze.json
│   │   ├── zzz143_concentration_audit.json
│   │   ├── zzz143_eligibility_distribution.json
│   │   ├── zzz143_layer_results.json
│   │   ├── zzz143_observation_level.parquet
│   │   ├── zzz143_outcome_blindness.json
│   │   ├── zzz143_red_team_results.json
│   │   ├── zzz143_statistical_results.json
│   │   ├── zzz143_stratification_results.json
│   │   ├── zzz14_dataset_v2_manifest.json
│   │   ├── zzz14_historical_coverage.json
│   │   ├── zzz14_redteam.json
│   │   ├── zzz62_observations.parquet
│   │   ├── zzz62_stats_summary.json
│   │   ├── zzz71_attribution_summary.json
│   │   ├── zzz71_candidate_attributions.parquet
│   │   ├── zzz7_attribution_summary.json
│   │   ├── zzz7_candidate_attributions.parquet
│   │   ├── zzz81_ablation_results.parquet
│   │   ├── zzz81_ablation_summary.json
│   │   ├── zzz82_oos_results.parquet
│   │   ├── zzz82_oos_summary.json
│   │   ├── zzz8_experiment_results.parquet
│   │   ├── zzz8_experiment_summary.json
│   │   ├── zzz91_ablation_results.parquet
│   │   ├── zzz91_ablation_summary.json
│   │   ├── zzz9_semantic_results.parquet
│   │   ├── zzz9_semantic_summary.json
├── governance/
│   ├── architecture/
│   ├── change_control/
│   │   ├── COBA_HISTORICAL_MAPPING.md
│   │   ├── NAMING_CONVENTION.md
│   │   ├── POST_MIGRATION_DECISION_LOG.md
│   ├── frozen/
│   ├── lineage/
├── knowledge/
│   ├── canonical/
│   ├── domain/
│   ├── failures/
│   │   ├── .gitkeep
│   ├── index/
│   ├── patterns/
│   │   ├── .gitkeep
│   ├── research/
│   ├── successful_setups/
│   │   ├── .gitkeep
├── logs/
│   ├── .gitkeep
│   ├── swingdesk.log
├── migration_proposal/
│   ├── AGENTS.md
│   ├── DUPLICATE_AND_SUPERSESSION_REGISTER.md
│   ├── FILE_CLASSIFICATION.csv
│   ├── MIGRATION_MAP.md
│   ├── PHASE_1_3_AUDIT.md
│   ├── PHASE_1_REPORT.md
│   ├── README.md
├── positions/
│   ├── .gitkeep
├── queue/
│   ├── completed/
│   │   ├── .gitkeep
│   ├── dead_letter/
│   │   ├── .gitkeep
│   ├── decisions/
│   │   ├── .gitkeep
│   ├── failed/
│   │   ├── .gitkeep
│   ├── queue_01/
│   │   ├── .gitkeep
│   ├── queue_02/
│   │   ├── .gitkeep
│   ├── review/
│   │   ├── .gitkeep
├── reports/
│   ├── backtest_preflight.md
│   ├── dataset_inventory.json
│   ├── dataset_operator_checklist.md
│   ├── data_compatibility_report.md
│   ├── data_intake_status.json
│   ├── data_intake_status.md
│   ├── data_onboarding_report.json
│   ├── data_onboarding_report.md
│   ├── data_provisioning_status.json
│   ├── data_provisioning_status.md
│   ├── first_real_backtest_report.json
│   ├── first_real_backtest_report.md
│   ├── import_instructions.md
│   ├── pre_backtest_checklist.md
│   ├── principal_audit_report.json
│   ├── principal_audit_report.md
│   ├── real_backtest_report.json
│   ├── real_backtest_report.md
│   ├── test_inventory.json
│   ├── test_inventory_2.json
│   ├── alerts/
│   │   ├── all_alerts.json
│   ├── archive/
│   │   ├── .gitkeep
│   │   ├── scratch_historical/
│   │   │   ├── rewrite_engine.py
│   ├── backtest/
│   │   ├── trade_level_forensics.json
│   ├── daily/
│   │   ├── .gitkeep
│   ├── decision/
│   ├── experiments/
│   ├── operational/
│   ├── repository_audit/
│   │   ├── AGENT2_LEGACY_IMPORT_RECOVERY.md
│   │   ├── ARCHITECTURE_MAP.md
│   │   ├── CLEANUP_PLAN.md
│   │   ├── DEPENDENCY_MAP.md
│   │   ├── DUPLICATE_ANALYSIS.md
│   │   ├── POST_MIGRATION_STRUCTURAL_LINEAGE_AUDIT.md
│   │   ├── REPOSITORY_INVENTORY.md
│   ├── scientific/
│   ├── technical/
│   │   ├── POST_MIGRATION_INTEGRITY_AUDIT.md
│   │   ├── POST_MIGRATION_REFERENCE_AUDIT.md
├── research/
│   ├── analysis/
│   ├── current/
│   │   ├── ZZZ14_9_CANONICAL_INDEX.md
│   │   ├── zzz14_9_coverage_audit.csv
│   │   ├── zzz14_9_decision_stability.csv
│   │   ├── zzz14_9_frozen_decision_oos_matrix.csv
│   │   ├── zzz14_9_inference.json
│   │   ├── zzz14_9_manifest.json
│   │   ├── zzz14_9_placebo.csv
│   │   ├── zzz14_9_red_team.json
│   │   ├── zzz14_9_temporal_generalization.csv
│   │   ├── zzz14_9_transition_oos.csv
│   │   ├── zzz14_9_validation.json
│   │   ├── zzz14_9_validation.md
│   ├── experiments/
│   ├── validation/
├── scratch/
│   ├── check_ablation.py
│   ├── check_oos.py
│   ├── check_oos_split.py
│   ├── check_test_g.py
│   ├── check_test_j.py
│   ├── generate_raw_historical_disclosures.py
│   ├── inspect_db.py
│   ├── minimal_auth_test.py
│   ├── temp_test_14.duckdb
├── scripts/
│   ├── .gitkeep
│   ├── acquire_data.py
│   ├── diagnose_aw.py
│   ├── generate_fixtures.py
│   ├── onboard_data.py
│   ├── pilot_xxx2_parquet.py
│   ├── pilot_xxx2_seed.py
│   ├── real_backtest.py
│   ├── run_backtest.py
│   ├── run_experiments_ax.py
│   ├── run_forensics_aw.py
│   ├── run_research_ay.py
│   ├── run_research_ay1.py
│   ├── run_research_ay2.py
│   ├── run_research_az2.py
│   ├── run_research_az3.py
├── state/
│   ├── signal_states.json
│   ├── sys.json
│   ├── audit/
├── tests/
│   ├── test_agent1_end_to_end.py
│   ├── test_agent1_pipeline.py
│   ├── test_agent2_pipeline.py
│   ├── test_alert_engine.py
│   ├── test_batch_ab.py
│   ├── test_batch_ab_scenarios.py
│   ├── test_batch_ac.py
│   ├── test_batch_ad.py
│   ├── test_batch_ae.py
│   ├── test_batch_af.py
│   ├── test_batch_ag.py
│   ├── test_batch_ah.py
│   ├── test_batch_ai.py
│   ├── test_batch_aj.py
│   ├── test_batch_ak.py
│   ├── test_batch_al.py
│   ├── test_batch_am.py
│   ├── test_batch_ao.py
│   ├── test_batch_ap.py
│   ├── test_batch_aq.py
│   ├── test_batch_ar.py
│   ├── test_batch_as.py
│   ├── test_batch_at.py
│   ├── test_batch_av.py
│   ├── test_batch_aw.py
│   ├── test_batch_ax.py
│   ├── test_batch_ay.py
│   ├── test_batch_ay1.py
│   ├── test_batch_ay2.py
│   ├── test_batch_az3.py
│   ├── test_batch_q.py
│   ├── test_batch_r.py
│   ├── test_batch_s.py
│   ├── test_batch_t.py
│   ├── test_batch_u.py
│   ├── test_batch_v.py
│   ├── test_batch_w.py
│   ├── test_batch_xxx2.py
│   ├── test_batch_xxx3_pit.py
│   ├── test_batch_xxx4_llm_pilot.py
│   ├── test_batch_y.py
│   ├── test_batch_yyy21r_native.py
│   ├── test_batch_yyy2_historical.py
│   ├── test_batch_yyy3_oos.py
│   ├── test_batch_zzz101_historical_disclosure_coverage.py
│   ├── test_batch_zzz102_historical_disclosure_ingestion.py
│   ├── test_batch_zzz103_historical_disclosure_completeness.py
│   ├── test_batch_zzz10_company_specific_discrimination.py
│   ├── test_batch_zzz111_coverage_aware_discrimination.py
│   ├── test_batch_zzz112_identification_audit.py
│   ├── test_batch_zzz113_identification_stress_test.py
│   ├── test_batch_zzz114_pretrend_adjusted_information.py
│   ├── test_batch_zzz115_joint_identification.py
│   ├── test_batch_zzz116_counterfactual_integrity.py
│   ├── test_batch_zzz117_counterfactual_purification.py
│   ├── test_batch_zzz11_company_specific_discrimination.py
│   ├── test_batch_zzz12_methodology_lock.py
│   ├── test_batch_zzz13_adaptive_foundation.py
│   ├── test_batch_zzz1411_research_readiness.py
│   ├── test_batch_zzz141_dataset_v2_integrity.py
│   ├── test_batch_zzz1421_agent2_replay_integration.py
│   ├── test_batch_zzz142_historical_replay.py
│   ├── test_batch_zzz1_ingestion.py
│   ├── test_batch_zzz2_ledger.py
│   ├── test_batch_zzz31_pit_integrity.py
│   ├── test_batch_zzz3_semantic.py
│   ├── test_batch_zzz41_adversarial_reasoning.py
│   ├── test_batch_zzz4_pit_reasoning.py
│   ├── test_batch_zzz5_agent1_replay.py
│   ├── test_batch_zzz62_state_extraction_regression.py
│   ├── test_batch_zzz6_alpha_validation.py
│   ├── test_batch_zzz71_attribution_logic_audit.py
│   ├── test_batch_zzz7_candidate_attribution.py
│   ├── test_batch_zzz81_ablation_selection_robustness.py
│   ├── test_batch_zzz82_temporal_cross_sectional_oos.py
│   ├── test_batch_zzz8_multi_agent_incremental_ev.py
│   ├── test_batch_zzz91_semantic_ablation_causal_audit.py
│   ├── test_batch_zzz9_semantic_explanation_attribution.py
│   ├── test_config.py
│   ├── test_csv_agent1_end_to_end.py
│   ├── test_csv_data_source.py
│   ├── test_dataset_readiness.py
│   ├── test_data_engine.py
│   ├── test_data_repository.py
│   ├── test_data_source.py
│   ├── test_data_source_errors.py
│   ├── test_data_source_factory.py
│   ├── test_event_mapping.py
│   ├── test_historical_replay_engine.py
│   ├── test_indicators.py
│   ├── test_job_envelope.py
│   ├── test_liquidity.py
│   ├── test_logger.py
│   ├── test_main.py
│   ├── test_market_data_schema.py
│   ├── test_market_scanner.py
│   ├── test_mock_historical_data.py
│   ├── test_performance_attribution.py
│   ├── test_performance_batch_ab.py
│   ├── test_provider_integration.py
│   ├── test_quant_features.py
│   ├── test_queue.py
│   ├── test_queue_watcher.py
│   ├── test_red_team.py
│   ├── test_replay_firewall.py
│   ├── test_research_schema.py
│   ├── test_research_validation.py
│   ├── test_schemas.py
│   ├── test_state_machine.py
│   ├── test_universe.py
│   ├── test_walk_forward.py
│   ├── test_zzz1421R_adversarial_acceptance.py
│   ├── test_zzz1421_acceptance_evidence_review.py
│   ├── test_zzz1431_canonical_layer_e_replication.py
│   ├── test_zzz1432_fixed_sample_measurement.py
│   ├── test_zzz1433_deconfounding.py
│   ├── test_zzz1434_pre_t_matched_event_cluster.py
│   ├── test_zzz1435_information_coverage_gate.py
│   ├── test_zzz1436_strict_counterfactual_inference.py
│   ├── test_zzz1437_common_support_inference.py
│   ├── test_zzz1438_closure_gate.py
│   ├── test_zzz1439_estimand_ai_gate.py
│   ├── test_zzz143_agent2_historical_discrimination.py
│   ├── test_zzz144_ai_scaleup.py
│   ├── test_zzz145_ai_attribution.py
│   ├── test_zzz1461_reconciliation.py
│   ├── test_zzz1462_counterfactual_closure.py
│   ├── test_zzz1463_population_identity.py
│   ├── test_zzz146_risk_integration.py
│   ├── test_zzz146_syntactic_synthesis.py
│   ├── test_zzz1471_closure.py
│   ├── test_zzz1472_closure.py
│   ├── test_zzz147_ai_firewall.py
│   ├── test_zzz147_contradiction_attribution.py
│   ├── test_zzz147_drift.py
│   ├── test_zzz147_inference.py
│   ├── test_zzz147_information_layers.py
│   ├── test_zzz14811_identity.py
│   ├── test_zzz14812_outcome_aggregation.py
│   ├── test_zzz1481_closure.py
│   ├── test_zzz148_decision_utility.py
│   ├── test_zzz149_frozen_decision_oos.py
│   ├── coba/
│   ├── fixtures/
│   │   ├── ASII.csv
│   │   ├── BBCA_empty.csv
│   │   ├── BBCA_invalid_ohlc.csv
│   │   ├── BBCA_missing_value.csv
│   │   ├── BBCA_negative_volume.csv
│   │   ├── BBCA_unsorted.csv
│   │   ├── BBCA_valid.csv
│   │   ├── BBNI.csv
│   │   ├── BMRI.csv
│   │   ├── IHSG.csv
│   │   ├── IHSG_BEAR.csv
│   │   ├── TLKM.csv
│   │   ├── historical/
│   │   │   ├── ASII.csv
│   │   │   ├── BAD_COL.csv
│   │   │   ├── BBCA.csv
│   │   │   ├── BBCA_FUTURE.csv
│   │   │   ├── BBCA_MISSING_ROW.csv
│   │   │   ├── BBCA_NAN.csv
│   │   │   ├── BBCA_NEGATIVE.csv
│   │   │   ├── BBCA_SHORT.csv
│   │   │   ├── BBNI.csv
│   │   │   ├── BMRI.csv
│   │   │   ├── IHSG.csv
│   │   │   ├── TLKM.csv
│   │   ├── perf/
│   │   │   ├── SYM0.csv
│   │   │   ├── SYM1.csv
│   │   │   ├── SYM10.csv
│   │   │   ├── SYM11.csv
│   │   │   ├── SYM12.csv
│   │   │   ├── SYM13.csv
│   │   │   ├── SYM14.csv
│   │   │   ├── SYM15.csv
│   │   │   ├── SYM16.csv
│   │   │   ├── SYM17.csv
│   │   │   ├── SYM18.csv
│   │   │   ├── SYM19.csv
│   │   │   ├── SYM2.csv
│   │   │   ├── SYM20.csv
│   │   │   ├── SYM21.csv
│   │   │   ├── SYM22.csv
│   │   │   ├── SYM23.csv
│   │   │   ├── SYM24.csv
│   │   │   ├── SYM25.csv
│   │   │   ├── SYM26.csv
│   │   │   ├── SYM27.csv
│   │   │   ├── SYM28.csv
│   │   │   ├── SYM29.csv
│   │   │   ├── SYM3.csv
│   │   │   ├── SYM30.csv
│   │   │   ├── SYM31.csv
│   │   │   ├── SYM32.csv
│   │   │   ├── SYM33.csv
│   │   │   ├── SYM34.csv
│   │   │   ├── SYM35.csv
│   │   │   ├── SYM36.csv
│   │   │   ├── SYM37.csv
│   │   │   ├── SYM38.csv
│   │   │   ├── SYM39.csv
│   │   │   ├── SYM4.csv
│   │   │   ├── SYM40.csv
│   │   │   ├── SYM41.csv
│   │   │   ├── SYM42.csv
│   │   │   ├── SYM43.csv
│   │   │   ├── SYM44.csv
│   │   │   ├── SYM45.csv
│   │   │   ├── SYM46.csv
│   │   │   ├── SYM47.csv
│   │   │   ├── SYM48.csv
│   │   │   ├── SYM49.csv
│   │   │   ├── SYM5.csv
│   │   │   ├── SYM50.csv
│   │   │   ├── SYM51.csv
│   │   │   ├── SYM52.csv
│   │   │   ├── SYM53.csv
│   │   │   ├── SYM54.csv
│   │   │   ├── SYM55.csv
│   │   │   ├── SYM56.csv
│   │   │   ├── SYM57.csv
│   │   │   ├── SYM58.csv
│   │   │   ├── SYM59.csv
│   │   │   ├── SYM6.csv
│   │   │   ├── SYM60.csv
│   │   │   ├── SYM61.csv
│   │   │   ├── SYM62.csv
│   │   │   ├── SYM63.csv
│   │   │   ├── SYM64.csv
│   │   │   ├── SYM65.csv
│   │   │   ├── SYM66.csv
│   │   │   ├── SYM67.csv
│   │   │   ├── SYM68.csv
│   │   │   ├── SYM69.csv
│   │   │   ├── SYM7.csv
│   │   │   ├── SYM70.csv
│   │   │   ├── SYM71.csv
│   │   │   ├── SYM72.csv
│   │   │   ├── SYM73.csv
│   │   │   ├── SYM74.csv
│   │   │   ├── SYM75.csv
│   │   │   ├── SYM76.csv
│   │   │   ├── SYM77.csv
│   │   │   ├── SYM78.csv
│   │   │   ├── SYM79.csv
│   │   │   ├── SYM8.csv
│   │   │   ├── SYM80.csv
│   │   │   ├── SYM81.csv
│   │   │   ├── SYM82.csv
│   │   │   ├── SYM83.csv
│   │   │   ├── SYM84.csv
│   │   │   ├── SYM85.csv
│   │   │   ├── SYM86.csv
│   │   │   ├── SYM87.csv
│   │   │   ├── SYM88.csv
│   │   │   ├── SYM89.csv
│   │   │   ├── SYM9.csv
│   │   │   ├── SYM90.csv
│   │   │   ├── SYM91.csv
│   │   │   ├── SYM92.csv
│   │   │   ├── SYM93.csv
│   │   │   ├── SYM94.csv
│   │   │   ├── SYM95.csv
│   │   │   ├── SYM96.csv
│   │   │   ├── SYM97.csv
│   │   │   ├── SYM98.csv
│   │   │   ├── SYM99.csv
│   ├── integration/
│   ├── redteam/
│   ├── scientific/
│   │   ├── batch_au_real_backtest_report.md
│   │   ├── zzz1421R_test_circularity.json
│   ├── scratch/
│   │   ├── knowledge/
│   │   │   ├── lessons/
│   │   │   ├── missed_opportunities/
│   │   │   ├── patterns/
│   ├── temp/
│   │   ├── signal_states.json
│   ├── unit/
```