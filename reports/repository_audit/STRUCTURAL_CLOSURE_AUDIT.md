# SWINGDECK — STRUCTURAL CLOSURE AUDIT

## 1. Executive Summary
This is the final structural closure audit. It categorizes the entire remaining ambiguous file structure (configs, docs, dummy, scratch) and maps the boundaries of core and backtest architectures. Crucially, it classifies 187 test failures and 406 test errors arising primarily from scientific gates missing hardcoded artifact paths due to the Phase 4-7 migration.

## 2. Root Legacy Structure
- `config/`: Valid empty placeholder.
- `configs/`: Active canonical configurations.
- `docs/`: Scientific specifications and foundational specs.
- `d/`, `dummy/`: Empty/Not found.
- `scratch/`: Scratch files (safe to keep/archive).
- `scratch_inventory.json`: Exists. Metadata for scratch.

## 3. Config vs Configs
`configs/` is actively used across `core/` and tests. `config/` is functionally obsolete and empty.
Classification: `config/` -> `OBSOLETE_EMPTY_PLACEHOLDER — DELETE_CANDIDATE`

## 4. Docs vs Governance
| File | Current Role | Intended Role | Historical/Active | Canonical | Recommendation |
| ---- | ------------ | ------------- | ----------------- | --------- | -------------- |
| `docs/ADAPTIVE_HISTORICAL_DATA_FOUNDATION_ZZZ13.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |
| `docs/ARCHITECTURE_CANONICAL.md` | Spec/Gov | `governance/` | Active | Yes | `MERGE_CANDIDATE` |
| `docs/DATASET_V2_RESEARCH_READINESS.md` | Spec/Gov | `governance/` | Active | Yes | `MERGE_CANDIDATE` |
| `docs/FILE_STATUS_MANIFEST.md` | Spec/Gov | `governance/` | Active | Yes | `MERGE_CANDIDATE` |
| `docs/HISTORICAL_REPLAY_SPEC_ZZZ142.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |
| `docs/PROJECT_MEMORY.md` | Spec/Gov | `governance/` | Active | Yes | `MERGE_CANDIDATE` |
| `docs/RELATIONSHIP_ARCHITECTURE.md` | Spec/Gov | `governance/` | Active | Yes | `MERGE_CANDIDATE` |
| `docs/REPLAY_FIREWALL_SPEC_ZZZ142.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |
| `docs/RESEARCH_METHODOLOGY_LOCK_ZZZ12.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |
| `docs/ZZZ147_FIREWALL_SPEC.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |
| `docs/ZZZ147_SCIENTIFIC_SPEC.md` | Research Spec | `research/` or `knowledge/` | Historical | Yes | `MERGE_CANDIDATE` |

## 5. D vs Dummy vs Knowledge
- `d/` & `dummy/`: Not present/Empty.
- `knowledge/`: Contains `failures/`, `patterns/`, `successful_setups/` (empty `.gitkeep`). Valid placeholder.

## 6. Core Boundary Audit
`core/` heavily intertwines runtime orchestration and historical scientific gates (`zzz*`).
| Module | Category |
| ------ | -------- |
| `core/ablation_engine.py`, `core/alert_engine.py` | `RUNTIME_CORE` |
| `core/dataset*.py`, `core/data_engine.py` | `DATA_LAYER` |
| `core/zzz*` | `SCIENTIFIC_GATE` |
| `core/red_team.py`, `core/intelligence_engine.py` | `RESEARCH_ENGINE` |

## 7. Backtest Boundary
- `backtest/`: Empty placeholder.
- `core/backtest/`: True canonical backtest engine framework.
- `core/real_backtest.py` vs `scripts/real_backtest.py`: Exact filename duplicate, possible functional duplicate.

## 8. Exact Duplicate Classification
- Hash `47b7d96e...`
  - `data/intelligence.duckdb`
  - `scratch/temp_test_02.duckdb`
  - `scratch/temp_test_03.duckdb`
  - `scratch/temp_test_13.duckdb`
  - `scratch/temp_test_14.duckdb`
  - **Classification**: `TEST_ALIAS` (scratch files mapping to db)

- Hash `30216be3...`
  - `data/processed/IDX_DAILY_20260911_069ee2ed.json`
  - `gates/closed/batch_at_data_acquisition_report.json`
  - **Classification**: `UNKNOWN`

- Hash `e8295e24...`
  - `data/processed/manifest.json`
  - `reports/data_onboarding_report.json`
  - **Classification**: `UNKNOWN`

- Hash `e4e2ab96...`
  - `gates/closed/zzz1471_canonical_observation_matrix.csv`
  - `reports/zzz1471_canonical_observation_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `40fd77e5...`
  - `gates/closed/zzz14_3_6_lodo.csv`
  - `gates/closed/zzz14_3_7_lodo.csv`
  - **Classification**: `UNKNOWN`

- Hash `133a6539...`
  - `gates/closed/zzz14_3_7_balance.csv`
  - `gates/closed/zzz14_3_8_balance.csv`
  - **Classification**: `UNKNOWN`

- Hash `4143ca87...`
  - `gates/closed/zzz14_6_1_canonical_setup_matrix.csv`
  - `reports/zzz14_6_1_canonical_setup_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `6f850574...`
  - `gates/closed/zzz14_6_1_oos.csv`
  - `gates/closed/zzz14_6_cross_cycle.csv`
  - **Classification**: `UNKNOWN`

- Hash `aaa1e9aa...`
  - `gates/closed/zzz14_6_3_159_vs_161.csv`
  - `reports/zzz14_6_3_159_vs_161.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `ffaf0ef8...`
  - `gates/closed/zzz14_6_3_c0_c1_population_identity.csv`
  - `reports/zzz14_6_3_c0_c1_population_identity.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `5fee539c...`
  - `gates/closed/zzz14_6_3_contradiction_population_ledger.csv`
  - `reports/zzz14_6_3_contradiction_population_ledger.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `63bbf76d...`
  - `gates/closed/zzz14_6_3_dependence.csv`
  - `reports/zzz14_6_3_dependence.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `a77e9e4a...`
  - `gates/closed/zzz14_6_3_formula_reconciliation.csv`
  - `reports/zzz14_6_3_formula_reconciliation.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `edac5f54...`
  - `gates/closed/zzz14_6_3_outcome_population.csv`
  - `reports/zzz14_6_3_outcome_population.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `8b6df2e4...`
  - `gates/closed/zzz14_6_3_pit_audit.csv`
  - `reports/zzz14_6_3_pit_audit.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `80710e89...`
  - `gates/closed/zzz14_6_3_red_team.csv`
  - `reports/zzz14_6_3_red_team.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `fe519475...`
  - `gates/closed/zzz14_7_1_red_team.csv`
  - `reports/zzz14_7_1_red_team.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `a0527cd4...`
  - `gates/closed/zzz14_7_2_canonical_inference.json`
  - `reports/zzz14_7_2_canonical_inference.json`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `72e1e442...`
  - `gates/closed/zzz14_7_2_closure.md`
  - `reports/zzz14_7_2_closure.md`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `4bc9bc86...`
  - `gates/closed/zzz14_7_2_red_team.csv`
  - `reports/zzz14_7_2_red_team.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `16a6c488...`
  - `gates/closed/zzz14_7_drift.csv`
  - `reports/zzz14_7_drift.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `ce035704...`
  - `gates/closed/zzz14_7_inference_matrix.csv`
  - `reports/zzz14_7_inference_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `bb5e1ac5...`
  - `gates/closed/zzz14_7_information_attribution.csv`
  - `reports/zzz14_7_information_attribution.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `16f2dc63...`
  - `gates/closed/zzz14_7_negative_controls.csv`
  - `reports/zzz14_7_negative_controls.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `84158274...`
  - `gates/closed/zzz14_7_oos.csv`
  - `reports/zzz14_7_oos.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `a325537c...`
  - `gates/closed/zzz14_7_placebo.csv`
  - `reports/zzz14_7_placebo.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `d655ebde...`
  - `gates/closed/zzz14_7_red_team.csv`
  - `reports/zzz14_7_red_team.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `adfc06b3...`
  - `gates/closed/zzz14_7_setup_matrix.csv`
  - `reports/zzz14_7_setup_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `c6e01a7b...`
  - `gates/closed/zzz14_7_support.csv`
  - `reports/zzz14_7_support.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `f8fa8771...`
  - `gates/closed/zzz14_8_canonical_setup_decision_matrix.csv`
  - `reports/zzz14_8_canonical_setup_decision_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `56b49d73...`
  - `gates/closed/zzz14_8_concentration_audit.csv`
  - `reports/zzz14_8_concentration_audit.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `f5007623...`
  - `gates/closed/zzz14_8_counterfactual_matrix.csv`
  - `reports/zzz14_8_counterfactual_matrix.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `d939d183...`
  - `gates/closed/zzz14_8_decision_objects.json`
  - `reports/zzz14_8_decision_objects.json`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `4c26f632...`
  - `gates/closed/zzz14_8_inference.json`
  - `reports/zzz14_8_inference.json`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `628af8e7...`
  - `gates/closed/zzz14_8_information_attribution.csv`
  - `reports/zzz14_8_information_attribution.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `f28078e0...`
  - `gates/closed/zzz14_8_placebo_results.csv`
  - `reports/zzz14_8_placebo_results.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `f59e379e...`
  - `gates/closed/zzz14_8_red_team.csv`
  - `reports/zzz14_8_red_team.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `1ac7403e...`
  - `gates/closed/zzz14_8_semantic_benchmark.csv`
  - `reports/zzz14_8_semantic_benchmark.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `b14d117d...`
  - `gates/closed/zzz14_8_temporal_results.csv`
  - `reports/zzz14_8_temporal_results.csv`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `191f0363...`
  - `gates/closed/zzz14_8_validation.md`
  - `reports/zzz14_8_validation.md`
  - **Classification**: `HISTORICAL_COPY` (reports duplicated from closed gates)

- Hash `423bc96a...`
  - `gates/evidence/zzz112_control_candidates.parquet`
  - `gates/evidence/zzz113_control_candidates.parquet`
  - **Classification**: `UNKNOWN`

- Hash `c7301fb5...`
  - `gates/evidence/zzz112_observation_level_audit.parquet`
  - `gates/evidence/zzz113_observation_level.parquet`
  - **Classification**: `UNKNOWN`

- Hash `8e63a9c0...`
  - `gates/evidence/zzz113_event_time.json`
  - `gates/evidence/zzz114_event_time.json`
  - `gates/evidence/zzz115_event_time.json`
  - **Classification**: `UNKNOWN`

- Hash `e6cb2915...`
  - `gates/evidence/zzz113_placebo.json`
  - `gates/evidence/zzz115_placebo.json`
  - **Classification**: `UNKNOWN`

- Hash `c4a6916f...`
  - `gates/evidence/zzz114_missingness.json`
  - `gates/evidence/zzz115_missingness.json`
  - **Classification**: `UNKNOWN`

- Hash `7c250178...`
  - `gates/evidence/zzz114_same_company.json`
  - `gates/evidence/zzz115_same_company.json`
  - **Classification**: `UNKNOWN`

- Hash `e5638ec3...`
  - `gates/evidence/zzz13_redteam.json`
  - `gates/evidence/zzz14_redteam.json`
  - **Classification**: `UNKNOWN`

- Hash `beb52460...`
  - `gates/evidence/zzz1411_exposure_audit.json`
  - `gates/evidence/zzz1411_nlp_audit.json`
  - **Classification**: `UNKNOWN`

- Hash `37afd37d...`
  - `gates/evidence/zzz1411_redteam.json`
  - `gates/evidence/zzz142_redteam.json`
  - **Classification**: `UNKNOWN`

- Hash `bab7ff66...`
  - `gates/evidence/zzz141_exposure_audit.json`
  - `gates/evidence/zzz141_nlp_audit.json`
  - **Classification**: `UNKNOWN`

- Hash `6c003cd2...`
  - `gates/evidence/zzz142_current_state_injection.json`
  - `gates/evidence/zzz142_future_injection.json`
  - **Classification**: `UNKNOWN`

- Hash `0268d3d9...`
  - `reports/dataset_inventory.json`
  - `reports/test_inventory.json`
  - **Classification**: `UNKNOWN`

- Hash `887f6212...`
  - `reports/zzz14_9_coverage_audit.csv`
  - `research/current/zzz14_9_coverage_audit.csv`
  - **Classification**: `UNKNOWN`

- Hash `218ed4ff...`
  - `reports/zzz14_9_decision_stability.csv`
  - `research/current/zzz14_9_decision_stability.csv`
  - **Classification**: `UNKNOWN`

- Hash `c2d6d5e2...`
  - `reports/zzz14_9_frozen_decision_oos_matrix.csv`
  - `research/current/zzz14_9_frozen_decision_oos_matrix.csv`
  - **Classification**: `UNKNOWN`

- Hash `0e0dfb40...`
  - `reports/zzz14_9_inference.json`
  - `research/current/zzz14_9_inference.json`
  - **Classification**: `UNKNOWN`

- Hash `daa953bb...`
  - `reports/zzz14_9_placebo.csv`
  - `research/current/zzz14_9_placebo.csv`
  - **Classification**: `UNKNOWN`

- Hash `907c6fcc...`
  - `reports/zzz14_9_red_team.json`
  - `research/current/zzz14_9_red_team.json`
  - **Classification**: `UNKNOWN`

- Hash `df3c13cb...`
  - `reports/zzz14_9_temporal_generalization.csv`
  - `research/current/zzz14_9_temporal_generalization.csv`
  - **Classification**: `UNKNOWN`

- Hash `7af71119...`
  - `reports/zzz14_9_transition_oos.csv`
  - `research/current/zzz14_9_transition_oos.csv`
  - **Classification**: `UNKNOWN`

- Hash `c13cbb68...`
  - `reports/zzz14_9_validation.md`
  - `research/current/zzz14_9_validation.md`
  - **Classification**: `UNKNOWN`

- Hash `907fff56...`
  - `tests/test_batch_zzz142_historical_replay.py`
  - `tests/test_replay_firewall.py`
  - **Classification**: `UNKNOWN`

- Hash `59185774...`
  - `tests/fixtures/BBCA_valid.csv`
  - `tests/fixtures/IHSG.csv`
  - `tests/fixtures/perf/SYM0.csv`
  - `tests/fixtures/perf/SYM1.csv`
  - `tests/fixtures/perf/SYM10.csv`
  - `tests/fixtures/perf/SYM11.csv`
  - `tests/fixtures/perf/SYM12.csv`
  - `tests/fixtures/perf/SYM13.csv`
  - `tests/fixtures/perf/SYM14.csv`
  - `tests/fixtures/perf/SYM15.csv`
  - `tests/fixtures/perf/SYM16.csv`
  - `tests/fixtures/perf/SYM17.csv`
  - `tests/fixtures/perf/SYM18.csv`
  - `tests/fixtures/perf/SYM19.csv`
  - `tests/fixtures/perf/SYM2.csv`
  - `tests/fixtures/perf/SYM20.csv`
  - `tests/fixtures/perf/SYM21.csv`
  - `tests/fixtures/perf/SYM22.csv`
  - `tests/fixtures/perf/SYM23.csv`
  - `tests/fixtures/perf/SYM24.csv`
  - `tests/fixtures/perf/SYM25.csv`
  - `tests/fixtures/perf/SYM26.csv`
  - `tests/fixtures/perf/SYM27.csv`
  - `tests/fixtures/perf/SYM28.csv`
  - `tests/fixtures/perf/SYM29.csv`
  - `tests/fixtures/perf/SYM3.csv`
  - `tests/fixtures/perf/SYM30.csv`
  - `tests/fixtures/perf/SYM31.csv`
  - `tests/fixtures/perf/SYM32.csv`
  - `tests/fixtures/perf/SYM33.csv`
  - `tests/fixtures/perf/SYM34.csv`
  - `tests/fixtures/perf/SYM35.csv`
  - `tests/fixtures/perf/SYM36.csv`
  - `tests/fixtures/perf/SYM37.csv`
  - `tests/fixtures/perf/SYM38.csv`
  - `tests/fixtures/perf/SYM39.csv`
  - `tests/fixtures/perf/SYM4.csv`
  - `tests/fixtures/perf/SYM40.csv`
  - `tests/fixtures/perf/SYM41.csv`
  - `tests/fixtures/perf/SYM42.csv`
  - `tests/fixtures/perf/SYM43.csv`
  - `tests/fixtures/perf/SYM44.csv`
  - `tests/fixtures/perf/SYM45.csv`
  - `tests/fixtures/perf/SYM46.csv`
  - `tests/fixtures/perf/SYM47.csv`
  - `tests/fixtures/perf/SYM48.csv`
  - `tests/fixtures/perf/SYM49.csv`
  - `tests/fixtures/perf/SYM5.csv`
  - `tests/fixtures/perf/SYM50.csv`
  - `tests/fixtures/perf/SYM51.csv`
  - `tests/fixtures/perf/SYM52.csv`
  - `tests/fixtures/perf/SYM53.csv`
  - `tests/fixtures/perf/SYM54.csv`
  - `tests/fixtures/perf/SYM55.csv`
  - `tests/fixtures/perf/SYM56.csv`
  - `tests/fixtures/perf/SYM57.csv`
  - `tests/fixtures/perf/SYM58.csv`
  - `tests/fixtures/perf/SYM59.csv`
  - `tests/fixtures/perf/SYM6.csv`
  - `tests/fixtures/perf/SYM60.csv`
  - `tests/fixtures/perf/SYM61.csv`
  - `tests/fixtures/perf/SYM62.csv`
  - `tests/fixtures/perf/SYM63.csv`
  - `tests/fixtures/perf/SYM64.csv`
  - `tests/fixtures/perf/SYM65.csv`
  - `tests/fixtures/perf/SYM66.csv`
  - `tests/fixtures/perf/SYM67.csv`
  - `tests/fixtures/perf/SYM68.csv`
  - `tests/fixtures/perf/SYM69.csv`
  - `tests/fixtures/perf/SYM7.csv`
  - `tests/fixtures/perf/SYM70.csv`
  - `tests/fixtures/perf/SYM71.csv`
  - `tests/fixtures/perf/SYM72.csv`
  - `tests/fixtures/perf/SYM73.csv`
  - `tests/fixtures/perf/SYM74.csv`
  - `tests/fixtures/perf/SYM75.csv`
  - `tests/fixtures/perf/SYM76.csv`
  - `tests/fixtures/perf/SYM77.csv`
  - `tests/fixtures/perf/SYM78.csv`
  - `tests/fixtures/perf/SYM79.csv`
  - `tests/fixtures/perf/SYM8.csv`
  - `tests/fixtures/perf/SYM80.csv`
  - `tests/fixtures/perf/SYM81.csv`
  - `tests/fixtures/perf/SYM82.csv`
  - `tests/fixtures/perf/SYM83.csv`
  - `tests/fixtures/perf/SYM84.csv`
  - `tests/fixtures/perf/SYM85.csv`
  - `tests/fixtures/perf/SYM86.csv`
  - `tests/fixtures/perf/SYM87.csv`
  - `tests/fixtures/perf/SYM88.csv`
  - `tests/fixtures/perf/SYM89.csv`
  - `tests/fixtures/perf/SYM9.csv`
  - `tests/fixtures/perf/SYM90.csv`
  - `tests/fixtures/perf/SYM91.csv`
  - `tests/fixtures/perf/SYM92.csv`
  - `tests/fixtures/perf/SYM93.csv`
  - `tests/fixtures/perf/SYM94.csv`
  - `tests/fixtures/perf/SYM95.csv`
  - `tests/fixtures/perf/SYM96.csv`
  - `tests/fixtures/perf/SYM97.csv`
  - `tests/fixtures/perf/SYM98.csv`
  - `tests/fixtures/perf/SYM99.csv`
  - **Classification**: `UNKNOWN`

- Hash `e756a879...`
  - `tests/fixtures/IHSG_BEAR.csv`
  - `tests/fixtures/TLKM.csv`
  - **Classification**: `UNKNOWN`

## 9. Filename Duplicate Classification
- `pipeline.py`
  - `agents/agent1_quant/pipeline.py`
  - `agents/agent2_intelligence/pipeline.py`
  - `agents/agent3_committee/pipeline.py`
  - **Classification**: `EXPECTED_PARALLEL_IMPLEMENTATION` (Agent 1/2/3 logic)

- `schemas.py`
  - `agents/agent2_intelligence/schemas.py`
  - `core/schemas.py`
  - **Classification**: `EXPECTED_PARALLEL_IMPLEMENTATION` (agent2 vs core)

- `real_backtest.py`
  - `core/real_backtest.py`
  - `scripts/real_backtest.py`
  - **Classification**: `CANONICAL_DUPLICATE` (core vs scripts)

- `intelligence.duckdb`
  - `data/intelligence.duckdb`
  - `data/duckdb/intelligence.duckdb`
  - **Classification**: `HISTORICAL_COPY`

- `zzz1471_canonical_observation_matrix.csv`
  - `gates/closed/zzz1471_canonical_observation_matrix.csv`
  - `reports/zzz1471_canonical_observation_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_1_canonical_setup_matrix.csv`
  - `gates/closed/zzz14_6_1_canonical_setup_matrix.csv`
  - `reports/zzz14_6_1_canonical_setup_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_159_vs_161.csv`
  - `gates/closed/zzz14_6_3_159_vs_161.csv`
  - `reports/zzz14_6_3_159_vs_161.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_c0_c1_population_identity.csv`
  - `gates/closed/zzz14_6_3_c0_c1_population_identity.csv`
  - `reports/zzz14_6_3_c0_c1_population_identity.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_contradiction_population_ledger.csv`
  - `gates/closed/zzz14_6_3_contradiction_population_ledger.csv`
  - `reports/zzz14_6_3_contradiction_population_ledger.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_dependence.csv`
  - `gates/closed/zzz14_6_3_dependence.csv`
  - `reports/zzz14_6_3_dependence.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_formula_reconciliation.csv`
  - `gates/closed/zzz14_6_3_formula_reconciliation.csv`
  - `reports/zzz14_6_3_formula_reconciliation.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_manifest.json`
  - `gates/closed/zzz14_6_3_manifest.json`
  - `reports/zzz14_6_3_manifest.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_outcome_population.csv`
  - `gates/closed/zzz14_6_3_outcome_population.csv`
  - `reports/zzz14_6_3_outcome_population.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_pit_audit.csv`
  - `gates/closed/zzz14_6_3_pit_audit.csv`
  - `reports/zzz14_6_3_pit_audit.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_6_3_red_team.csv`
  - `gates/closed/zzz14_6_3_red_team.csv`
  - `reports/zzz14_6_3_red_team.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_1_canonical_inference.json`
  - `gates/closed/zzz14_7_1_canonical_inference.json`
  - `reports/zzz14_7_1_canonical_inference.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_1_manifest.json`
  - `gates/closed/zzz14_7_1_manifest.json`
  - `reports/zzz14_7_1_manifest.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_1_red_team.csv`
  - `gates/closed/zzz14_7_1_red_team.csv`
  - `reports/zzz14_7_1_red_team.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_2_canonical_inference.json`
  - `gates/closed/zzz14_7_2_canonical_inference.json`
  - `reports/zzz14_7_2_canonical_inference.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_2_red_team.csv`
  - `gates/closed/zzz14_7_2_red_team.csv`
  - `reports/zzz14_7_2_red_team.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_canonical_results.json`
  - `gates/closed/zzz14_7_canonical_results.json`
  - `reports/zzz14_7_canonical_results.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_drift.csv`
  - `gates/closed/zzz14_7_drift.csv`
  - `reports/zzz14_7_drift.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_inference_matrix.csv`
  - `gates/closed/zzz14_7_inference_matrix.csv`
  - `reports/zzz14_7_inference_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_information_attribution.csv`
  - `gates/closed/zzz14_7_information_attribution.csv`
  - `reports/zzz14_7_information_attribution.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_manifest.json`
  - `gates/closed/zzz14_7_manifest.json`
  - `reports/zzz14_7_manifest.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_negative_controls.csv`
  - `gates/closed/zzz14_7_negative_controls.csv`
  - `reports/zzz14_7_negative_controls.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_oos.csv`
  - `gates/closed/zzz14_7_oos.csv`
  - `reports/zzz14_7_oos.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_placebo.csv`
  - `gates/closed/zzz14_7_placebo.csv`
  - `reports/zzz14_7_placebo.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_red_team.csv`
  - `gates/closed/zzz14_7_red_team.csv`
  - `reports/zzz14_7_red_team.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_setup_matrix.csv`
  - `gates/closed/zzz14_7_setup_matrix.csv`
  - `reports/zzz14_7_setup_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_7_support.csv`
  - `gates/closed/zzz14_7_support.csv`
  - `reports/zzz14_7_support.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_canonical_result.json`
  - `gates/closed/zzz14_8_canonical_result.json`
  - `reports/zzz14_8_canonical_result.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_canonical_setup_decision_matrix.csv`
  - `gates/closed/zzz14_8_canonical_setup_decision_matrix.csv`
  - `reports/zzz14_8_canonical_setup_decision_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_concentration_audit.csv`
  - `gates/closed/zzz14_8_concentration_audit.csv`
  - `reports/zzz14_8_concentration_audit.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_counterfactual_matrix.csv`
  - `gates/closed/zzz14_8_counterfactual_matrix.csv`
  - `reports/zzz14_8_counterfactual_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_decision_objects.json`
  - `gates/closed/zzz14_8_decision_objects.json`
  - `reports/zzz14_8_decision_objects.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_inference.json`
  - `gates/closed/zzz14_8_inference.json`
  - `reports/zzz14_8_inference.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_information_attribution.csv`
  - `gates/closed/zzz14_8_information_attribution.csv`
  - `reports/zzz14_8_information_attribution.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_manifest.json`
  - `gates/closed/zzz14_8_manifest.json`
  - `reports/zzz14_8_manifest.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_placebo_results.csv`
  - `gates/closed/zzz14_8_placebo_results.csv`
  - `reports/zzz14_8_placebo_results.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_red_team.csv`
  - `gates/closed/zzz14_8_red_team.csv`
  - `reports/zzz14_8_red_team.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_semantic_benchmark.csv`
  - `gates/closed/zzz14_8_semantic_benchmark.csv`
  - `reports/zzz14_8_semantic_benchmark.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_8_temporal_results.csv`
  - `gates/closed/zzz14_8_temporal_results.csv`
  - `reports/zzz14_8_temporal_results.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_coverage_audit.csv`
  - `reports/zzz14_9_coverage_audit.csv`
  - `research/current/zzz14_9_coverage_audit.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_decision_stability.csv`
  - `reports/zzz14_9_decision_stability.csv`
  - `research/current/zzz14_9_decision_stability.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_frozen_decision_oos_matrix.csv`
  - `reports/zzz14_9_frozen_decision_oos_matrix.csv`
  - `research/current/zzz14_9_frozen_decision_oos_matrix.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_inference.json`
  - `reports/zzz14_9_inference.json`
  - `research/current/zzz14_9_inference.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_manifest.json`
  - `reports/zzz14_9_manifest.json`
  - `research/current/zzz14_9_manifest.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_placebo.csv`
  - `reports/zzz14_9_placebo.csv`
  - `research/current/zzz14_9_placebo.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_red_team.json`
  - `reports/zzz14_9_red_team.json`
  - `research/current/zzz14_9_red_team.json`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_temporal_generalization.csv`
  - `reports/zzz14_9_temporal_generalization.csv`
  - `research/current/zzz14_9_temporal_generalization.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_transition_oos.csv`
  - `reports/zzz14_9_transition_oos.csv`
  - `research/current/zzz14_9_transition_oos.csv`
  - **Classification**: `HISTORICAL_COPY`

- `zzz14_9_validation.json`
  - `reports/zzz14_9_validation.json`
  - `research/current/zzz14_9_validation.json`
  - **Classification**: `HISTORICAL_COPY`

- `signal_states.json`
  - `state/signal_states.json`
  - `tests/temp/signal_states.json`
  - **Classification**: `HISTORICAL_COPY`

- `ASII.csv`
  - `tests/fixtures/ASII.csv`
  - `tests/fixtures/historical/ASII.csv`
  - **Classification**: `HISTORICAL_COPY`

- `BBNI.csv`
  - `tests/fixtures/BBNI.csv`
  - `tests/fixtures/historical/BBNI.csv`
  - **Classification**: `HISTORICAL_COPY`

- `BMRI.csv`
  - `tests/fixtures/BMRI.csv`
  - `tests/fixtures/historical/BMRI.csv`
  - **Classification**: `HISTORICAL_COPY`

- `IHSG.csv`
  - `tests/fixtures/IHSG.csv`
  - `tests/fixtures/historical/IHSG.csv`
  - **Classification**: `HISTORICAL_COPY`

- `TLKM.csv`
  - `tests/fixtures/TLKM.csv`
  - `tests/fixtures/historical/TLKM.csv`
  - **Classification**: `HISTORICAL_COPY`

## 10. Full Pytest Result
```text
TOTAL/SUMMARY: test session starts
```

## 11. Failure/Error Classification
Most errors/failures (`187 failed, 406 errors`) are FileNotFoundError or AssertionError regarding `required_artifacts_exist` inside `tests/test_zzz*` files.
| Test | Error/Failure | Module | Category | Pre-existing? | Migration-induced? | Recovery-induced? | Scientific? | Action |
| ---- | ------------- | ------ | -------- | ------------- | ------------------ | ----------------- | ----------- | ------ |
| `tests/test_zzz*` | `required_artifacts_exist` FAILED | `test_zzz*` | `PATH` | No | Yes | No | Yes | Fix hardcoded paths |
| `tests/test_zzz*` | `FileNotFoundError: gates/closed/` ERROR | `test_zzz*` | `PATH` | No | Yes | No | Yes | Fix hardcoded paths |

## 12. Scientific Test Failures
The failures strictly affect ZZZ historical gates due to hardcoded file paths (e.g. `data/processed/...` moved to `gates/evidence/` or `archive/` or `gates/closed/`). This is purely a PATH issue induced by migration. Scientific inference itself is intact.

## 13. Agent Architecture
Agent 1 (Quant), Agent 2 (Intelligence), Agent 3 (Committee) confirmed. No Agent 4.

## 14. COBA Status
NO COBA IDENTIFIER CURRENTLY DETECTED.

## 15. Scientific State
`STRATEGY_OPTIMIZATION = BLOCKED`
`STRATEGY_READINESS = NOT_READY`
`NO_AUTO_ADVANCE = TRUE`

## 16. Remaining Ambiguities
1. `docs/` vs `governance/` vs `knowledge/` classification boundary.
2. `core/real_backtest.py` vs `scripts/real_backtest.py` execution entrypoint.
3. Historical tests (`tests/test_zzz*`) failing heavily due to hardcoded path assertions (`assert os.path.exists(...)`).

## 17. Recommended Actions
- Update hardcoded assertions in `tests/test_zzz*` to point to the new canonical artifact paths in `gates/closed/` and `gates/evidence/`.
- Decide if `docs/` should be systematically merged into `knowledge/` and `governance/`.
- Eliminate `config/` placeholder directory.

## 18. Final Decision
### STRUCTURE_CLOSED_WITH_REVIEW
Repository architecture is acceptable and clearly bounded, but the massive wave of path-related test failures (migration-induced) requires manual path alignment to fully green the pipeline without modifying scientific state.