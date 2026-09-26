# PATH ALIGNMENT REMEDIATION

## 1. Remediation Scope
Fixed hardcoded paths in historical `test_zzz*.py` files that were pointing to pre-migration locations (`data/processed/`, `reports/`, etc.).

## 2. Changes Matrix
| File | Old Path | New Path | Verified Exists | Reason |
| ---- | -------- | -------- | --------------- | ------ |
| `tests/test_zzz1431_canonical_layer_e_replication.py` | `reports/zzz14_3_1_canonical_layer_e_replication.json` | `gates/closed/zzz14_3_1_canonical_layer_e_replication.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1432_fixed_sample_measurement.py` | `reports/zzz14_3_2_fixed_sample_layer_attribution.json` | `gates/closed/zzz14_3_2_fixed_sample_layer_attribution.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1433_deconfounding.py` | `reports/zzz14_3_3_evidence_deconfounding_stress_test.json` | `gates/closed/zzz14_3_3_evidence_deconfounding_stress_test.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_pre_t_balance.csv` | `gates/closed/zzz14_3_4_pre_t_balance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_matching_pairs.csv` | `gates/closed/zzz14_3_4_matching_pairs.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_event_clusters.csv` | `gates/closed/zzz14_3_4_event_clusters.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_event_reuse.csv` | `gates/closed/zzz14_3_4_event_reuse.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_lodo_event.csv` | `gates/closed/zzz14_3_4_lodo_event.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_result_matrix.csv` | `gates/closed/zzz14_3_4_result_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1434_pre_t_matched_event_cluster.py` | `reports/zzz14_3_4_manifest.json` | `gates/closed/zzz14_3_4_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_information_coverage_gate.md` | `gates/closed/zzz14_3_5_information_coverage_gate.md` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_coverage_balance.csv` | `gates/closed/zzz14_3_5_coverage_balance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_coverage_variables.csv` | `gates/closed/zzz14_3_5_coverage_variables.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_strict_matching_pairs.csv` | `gates/closed/zzz14_3_5_strict_matching_pairs.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_event_cluster_results.csv` | `gates/closed/zzz14_3_5_event_cluster_results.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_event_density_sensitivity.csv` | `gates/closed/zzz14_3_5_event_density_sensitivity.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_lodo_event.csv` | `gates/closed/zzz14_3_5_lodo_event.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_result_matrix.csv` | `gates/closed/zzz14_3_5_result_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1435_information_coverage_gate.py` | `reports/zzz14_3_5_manifest.json` | `gates/closed/zzz14_3_5_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_strict_counterfactual_inference_gate.md` | `gates/closed/zzz14_3_6_strict_counterfactual_inference_gate.md` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_information_environment.csv` | `gates/closed/zzz14_3_6_information_environment.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_pre_t_balance.csv` | `gates/closed/zzz14_3_6_pre_t_balance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_strict_matching_pairs.csv` | `gates/closed/zzz14_3_6_strict_matching_pairs.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_event_cluster_inference.csv` | `gates/closed/zzz14_3_6_event_cluster_inference.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_event_equalized.csv` | `gates/closed/zzz14_3_6_event_equalized.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_lodo.csv` | `gates/closed/zzz14_3_6_lodo.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_inference_reconciliation.csv` | `gates/closed/zzz14_3_6_inference_reconciliation.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_result_matrix.csv` | `gates/closed/zzz14_3_6_result_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1436_strict_counterfactual_inference.py` | `reports/zzz14_3_6_manifest.json` | `gates/closed/zzz14_3_6_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_support_matrix.csv` | `gates/closed/zzz14_3_7_support_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_support_distances.csv` | `gates/closed/zzz14_3_7_support_distances.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_identifiable_population.csv` | `gates/closed/zzz14_3_7_identifiable_population.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_matching_pairs.csv` | `gates/closed/zzz14_3_7_matching_pairs.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_balance.csv` | `gates/closed/zzz14_3_7_balance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_inference_single_source.csv` | `gates/closed/zzz14_3_7_inference_single_source.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_event_inference.csv` | `gates/closed/zzz14_3_7_event_inference.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_lodo.csv` | `gates/closed/zzz14_3_7_lodo.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_ticker_support.csv` | `gates/closed/zzz14_3_7_ticker_support.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_date_support.csv` | `gates/closed/zzz14_3_7_date_support.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_result_matrix.csv` | `gates/closed/zzz14_3_7_result_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1437_common_support_inference.py` | `reports/zzz14_3_7_manifest.json` | `gates/closed/zzz14_3_7_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_inference_reconciled.csv` | `gates/closed/zzz14_3_8_inference_reconciled.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_support_sensitivity.csv` | `gates/closed/zzz14_3_8_support_sensitivity.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_balance.csv` | `gates/closed/zzz14_3_8_balance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_residual_confounding.csv` | `gates/closed/zzz14_3_8_residual_confounding.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_survivorship_provenance.csv` | `gates/closed/zzz14_3_8_survivorship_provenance.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_event_dependence.csv` | `gates/closed/zzz14_3_8_event_dependence.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_red_team.csv` | `gates/closed/zzz14_3_8_red_team.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1438_closure_gate.py` | `reports/zzz14_3_8_manifest.json` | `gates/closed/zzz14_3_8_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_estimand_identity.md` | `gates/closed/zzz14_3_9_estimand_identity.md` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_estimand_reconciliation.csv` | `gates/closed/zzz14_3_9_estimand_reconciliation.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_threshold_identity.csv` | `gates/closed/zzz14_3_9_threshold_identity.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_ai_evidence_selection.csv` | `gates/closed/zzz14_3_9_ai_evidence_selection.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_ai_evidence_audit.csv` | `gates/closed/zzz14_3_9_ai_evidence_audit.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_ai_vs_deterministic.csv` | `gates/closed/zzz14_3_9_ai_vs_deterministic.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_ai_pit_audit.csv` | `gates/closed/zzz14_3_9_ai_pit_audit.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_ai_red_team.csv` | `gates/closed/zzz14_3_9_ai_red_team.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz1439_estimand_ai_gate.py` | `reports/zzz14_3_9_manifest.json` | `gates/closed/zzz14_3_9_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_scaleup.md` | `gates/closed/zzz14_4_ai_scaleup.md` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_quality_matrix.csv` | `gates/closed/zzz14_4_ai_quality_matrix.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_evidence_selection.csv` | `gates/closed/zzz14_4_ai_evidence_selection.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_reference_audit.csv` | `gates/closed/zzz14_4_ai_reference_audit.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_pit_audit.csv` | `gates/closed/zzz14_4_ai_pit_audit.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_coverage_bias.csv` | `gates/closed/zzz14_4_ai_coverage_bias.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_cross_ticker.csv` | `gates/closed/zzz14_4_ai_cross_ticker.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_cross_event.csv` | `gates/closed/zzz14_4_ai_cross_event.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_cross_regime.csv` | `gates/closed/zzz14_4_ai_cross_regime.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_oos.csv` | `gates/closed/zzz14_4_ai_oos.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_vs_deterministic.csv` | `gates/closed/zzz14_4_ai_vs_deterministic.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_reproducibility.csv` | `gates/closed/zzz14_4_ai_reproducibility.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_ai_red_team.csv` | `gates/closed/zzz14_4_ai_red_team.csv` | True | Artifact migrated to canonical location |
| `tests/test_zzz144_ai_scaleup.py` | `reports/zzz14_4_manifest.json` | `gates/closed/zzz14_4_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1461_reconciliation.py` | `reports/zzz14_6_1_manifest.json` | `gates/closed/zzz14_6_1_manifest.json` | True | Artifact migrated to canonical location |
| `tests/test_zzz1462_counterfactual_closure.py` | `reports/zzz14_6_2_manifest.json` | `gates/closed/zzz14_6_2_manifest.json` | True | Artifact migrated to canonical location |