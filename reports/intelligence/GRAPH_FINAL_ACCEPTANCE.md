# SWINGDECK MARKET INTELLIGENCE ENGINE V2.1
## GRAPH & DECISION INTEGRATION FINAL ACCEPTANCE REPORT

RUN_ID: b03dc220-a5f7-4b8f-aeaa-f63fa67e0c18-v2.1
START_TIMESTAMP: 2026-09-29T12:40:00Z
END_TIMESTAMP: 2026-09-29T12:55:00Z
ACTUAL_RUNTIME_SECONDS: 900

FILES_ANALYZED: 154
FILES_CREATED: 2
FILES_MODIFIED: 8

NATURAL_INFORMATION: IMPLEMENTED_NOT_OBSERVED
HISTORICAL_INFORMATION: YES (ADRO 2024 Corporate Action / Spin-off, PTBA, ANTM, UNVR)
FIXTURE_INFORMATION: YES (BBCA Rate Cut & Contradiction Suites)
CONTROLLED_INTEGRATION_CASES: YES (Adversarial MNPI, Injection, Metamorphic, Multi-Hop)

ENTITIES: 5 (ADRO, AADI, BBCA, BI, IDX)
RELATIONSHIPS: 7
EXPOSURES: 3
MECHANISMS: 3
CONTRADICTIONS: 2
MARKET_LINKS: 2

MULTI_HOP_PATHS: 4
PIT_REPLAYS: 3
AGENT2_CASES: 17 (VALIDATED)
AGENT3_CASES: 17 (VALIDATED)

TESTS: 67
PASSED: 67
FAILED: 0
SKIPPED: 0

FAILURE_INJECTIONS: 10
METAMORPHIC_TESTS: 5
SECURITY_TESTS: 4 (Prompt Injection, MNPI, Access Class, Untrusted Source)
PRIVACY_TESTS: 2 (Data Leakage, Unverified Entity Firewall)

DEFECTS_FOUND: 4
1. Dashboard missing dynamic mechanism links and graph engine connection (Static BBCA hardcoded text).
2. DuckDB float representation mismatch in exact equality assertions.
3. DecisionTrace schema omitted `evidence_refs` and `graph_intelligence` attributes during committee synthesis serialization.
4. Agent 2 emitted confidence strings ("HIGH"/"MEDIUM"/"LOW") which caused type mismatch against Agent 3 numeric threshold comparisons.

DEFECTS_FIXED: 4
1. Dashboard connected to dynamic `IntelligenceGraphEngine`, Agent 2 reasoning, and Agent 3 decision pipeline.
2. DuckDB float assertions updated to `pytest.approx` and schema typing.
3. `DecisionTrace` updated with `evidence_refs` and `graph_intelligence` fields; committee synthesis preserves trace data.
4. Added numeric confidence mappings and type-safe coercion across Agent 2 schemas and Agent 3 / RiskEngine.

REGRESSIONS_ADDED: 17 (Full suite in `tests/test_intelligence_decision_integration.py`)

PIT_STATUS: PASS
PROVENANCE_STATUS: PASS
SECURITY_STATUS: PASS (Prompt Injection & MNPI firewalls active)
PRIVACY_STATUS: PASS
DETERMINISM_STATUS: PASS
TRUTH_GATE_STATUS: PASS (0 findings across full repository scan)

REMAINING_UNKNOWN: NONE
REMAINING_LIMITATIONS: NATURAL_INGESTION_NOT_OBSERVED_IN_PROD (Live streaming ingestion code exists but unobserved in live market due to LIVE_EXECUTION=BLOCKED)
REMAINING_BLOCKERS: NONE

---

SCIENTIFIC_BRANCH = CLOSED
SCIENTIFIC_RESULTS = IMMUTABLE

CAUSALITY = NOT_PROVEN
STANDALONE_ALPHA = NOT_PROVEN
STRATEGY_READINESS = NOT_READY

COBA_019 = NOT_CREATED
STRATEGY_OPTIMIZATION = NOT_PERFORMED

RUNTIME_AGENTS = EXACTLY_3

PAPER_ONLY = TRUE
LIVE_EXECUTION = BLOCKED

FINAL_STATUS: INTELLIGENCE_DECISION_CHAIN_VALIDATED_WITH_LIMITATIONS
