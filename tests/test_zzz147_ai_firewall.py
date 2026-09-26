"""
tests/test_zzz147_ai_firewall.py

Unit test suite for Batch ZZZ.14.7:
AI / Agent 2 Context Firewall, Placebos, Negative Controls & Decision Attribution.
Contains 20 automated unit tests verifying:
1. AST/Regex prohibited token scanner across all setup records.
2. High-entropy sentinel token injection and blocking.
3. Full 7-probe Placebo Battery (P1 to P7) execution and attenuation.
4. Placebo P7 future-evidence sentinel strict blocking.
5. Negative Control probes (irrelevant, non-material, unrelated entity disclosures).
6. Agent 3 multi-layer decision attribution breakdown (Layers A through F).
7. Epistemological terminology firewall compliance.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz147_information_layers import ZZZ147InformationLadderEngine
from core.zzz147_ai_firewall import ZZZ147AIFirewallEngine


@pytest.fixture(scope="module")
def ladder_engine():
    return ZZZ147InformationLadderEngine()


@pytest.fixture(scope="module")
def firewall_engine():
    return ZZZ147AIFirewallEngine()


@pytest.fixture(scope="module")
def ladder_data(ladder_engine):
    df_matrix, df_population, _ = ladder_engine.load_canonical_data()
    df_ladder, _ = ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    return df_ladder


# 1. Prohibited Token Scanner on Canonical Data
def test_prohibited_token_scanner_clean(firewall_engine, ladder_data):
    df_scan, summary = firewall_engine.scan_prohibited_tokens_and_fields(ladder_data)
    assert summary["prohibited_token_violations"] == 0
    assert summary["firewall_scan_verdict"] == "PASS"


# 2. Prohibited Token Scanner Detects Injected Forbidden Keys
def test_prohibited_token_scanner_detects_violation(firewall_engine, ladder_data):
    dirty_ladder = ladder_data.copy()
    dirty_ladder.loc[0, "contradiction_type"] = "PRICE_CRASH_AFTER_H5_PEER_EXCESS"
    df_scan, summary = firewall_engine.scan_prohibited_tokens_and_fields(dirty_ladder)
    assert summary["prohibited_token_violations"] == 1
    assert summary["firewall_scan_verdict"] == "FAIL"


# 3. Placebo Battery Execution Shape
def test_placebo_suite_shape(firewall_engine, ladder_data):
    df_placebo, summary = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    assert len(df_placebo) == 7
    assert summary["total_placebo_probes"] == 7
    assert summary["placebo_suite_verdict"] == "PASS"


# 4. Placebo P1 Random Contradiction Attenuation
def test_placebo_p1_random_assignment(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p1 = df_placebo[df_placebo["probe_id"] == "P1_RANDOM_CONTRADICTION"].iloc[0]
    assert abs(p1["placebo_effect_pp"]) < 0.50
    assert "PASS" in p1["verdict"]


# 5. Placebo P2 Date Shuffled Attenuation
def test_placebo_p2_date_shuffled(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p2 = df_placebo[df_placebo["probe_id"] == "P2_DATE_SHUFFLED_CONTRADICTION"].iloc[0]
    assert abs(p2["placebo_effect_pp"]) < 0.50
    assert "PASS" in p2["verdict"]


# 6. Placebo P3 Ticker Shuffled Attenuation
def test_placebo_p3_ticker_shuffled(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p3 = df_placebo[df_placebo["probe_id"] == "P3_TICKER_SHUFFLED_CONTRADICTION"].iloc[0]
    assert abs(p3["placebo_effect_pp"]) < 0.50
    assert "PASS" in p3["verdict"]


# 7. Placebo P4 Event Shuffled Attenuation
def test_placebo_p4_event_shuffled(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p4 = df_placebo[df_placebo["probe_id"] == "P4_EVENT_SHUFFLED_CONTRADICTION"].iloc[0]
    assert abs(p4["placebo_effect_pp"]) < 0.50
    assert "PASS" in p4["verdict"]


# 8. Placebo P5 Pre-T Within-Ticker Evidence Shuffled
def test_placebo_p5_within_ticker_shuffled(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p5 = df_placebo[df_placebo["probe_id"] == "P5_PRE_T_WITHIN_TICKER_SHUFFLE"].iloc[0]
    assert abs(p5["placebo_effect_pp"]) < 0.50
    assert "PASS" in p5["verdict"]


# 9. Placebo P6 Structure Matched Random Evidence
def test_placebo_p6_structure_matched(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p6 = df_placebo[df_placebo["probe_id"] == "P6_STRUCTURE_MATCHED_RANDOM"].iloc[0]
    assert abs(p6["placebo_effect_pp"]) < 0.50
    assert "PASS" in p6["verdict"]


# 10. Placebo P7 Future Evidence Sentinel Strict Blocking
def test_placebo_p7_future_sentinel_blocked(firewall_engine, ladder_data):
    df_placebo, _ = firewall_engine.execute_placebo_suite_p1_to_p7(ladder_data)
    p7 = df_placebo[df_placebo["probe_id"] == "P7_FUTURE_EVIDENCE_SENTINEL"].iloc[0]
    assert p7["placebo_effect_pp"] == 0.0
    assert "PASS" in p7["verdict"]


# 11. Negative Controls Execution Shape
def test_negative_controls_shape(firewall_engine, ladder_data):
    df_neg, summary = firewall_engine.evaluate_negative_controls(ladder_data)
    assert len(df_neg) == 3
    assert summary["total_negative_controls"] == 3
    assert summary["negative_controls_verdict"] == "PASS"


# 12. Negative Controls Directional Non-Significance
def test_negative_controls_null_distribution(firewall_engine, ladder_data):
    df_neg, _ = firewall_engine.evaluate_negative_controls(ladder_data)
    for _, row in df_neg.iterrows():
        assert abs(row["observed_H5_excess_pp"]) < 0.50
        assert row["p_value"] > 0.50
        assert "PASS" in row["verdict"]


# 13. Decision Attribution: Information Enrichment (Layer A)
def test_decision_attribution_layer_a(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    la = df_da[df_da["channel_id"] == "A_INFORMATION_ENRICHMENT"].iloc[0]
    assert la["affected_setups"] > 1000
    assert la["operational_classification"] == "INFORMATION_ENRICHMENT"


# 14. Decision Attribution: Thesis State Change (Layer B)
def test_decision_attribution_layer_b(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    lb = df_da[df_da["channel_id"] == "B_THESIS_STATE_CHANGE"].iloc[0]
    assert lb["affected_setups"] > 500
    assert lb["operational_classification"] == "THESIS_STATE_CHANGE"


# 15. Decision Attribution: Contradiction / Invalidation (Layer C)
def test_decision_attribution_layer_c(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    lc = df_da[df_da["channel_id"] == "C_CONTRADICTION_INVALIDATION"].iloc[0]
    assert lc["affected_setups"] == 161
    assert lc["operational_classification"] == "CONTRADICTION_DEFENSE"


# 16. Decision Attribution: Timing Change (Layer D)
def test_decision_attribution_layer_d(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    ld = df_da[df_da["channel_id"] == "D_TIMING_CHANGE"].iloc[0]
    assert ld["affected_setups"] > 0
    assert ld["operational_classification"] == "TIMING_CHANGE"


# 17. Decision Attribution: Risk Field Change (Layer E)
def test_decision_attribution_layer_e(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    le = df_da[df_da["channel_id"] == "E_RISK_FIELD_CHANGE"].iloc[0]
    assert le["operational_classification"] == "RISK_INTEGRATION"


# 18. Decision Attribution: Action State Change (Layer F)
def test_decision_attribution_layer_f(firewall_engine, ladder_data):
    df_da, _ = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    lf = df_da[df_da["channel_id"] == "F_ACTION_STATE_CHANGE"].iloc[0]
    assert lf["affected_setups"] == 161
    assert lf["operational_classification"] == "ACTION_DISCRIMINATION"


# 19. Decision Hierarchy Non-Collapsing Invariant
def test_decision_attribution_distinctness(firewall_engine, ladder_data):
    df_da, summary = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    assert len(df_da) == 6
    assert summary["decision_attribution_verdict"] == "CHANNEL_SEPARATION_VERIFIED"


# 20. Summary Verification
def test_decision_attribution_summary(firewall_engine, ladder_data):
    _, summary = firewall_engine.decompose_agent3_decision_attribution(ladder_data)
    assert summary["action_rejection_count"] == 161
    assert summary["contradiction_defense_count"] == 161
