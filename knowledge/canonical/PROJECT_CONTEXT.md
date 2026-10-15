# PROJECT_CONTEXT

Current operational context for SwingDeck.

## Scientific State
- **STRATEGY_OPTIMIZATION**: BLOCKED
- **STRATEGY_READINESS**: NOT_READY
- **TEMPORAL_DIRECTIONAL_PERSISTENCE**: OBSERVED
- **INFERENCE_ROBUSTNESS**: METHOD_SENSITIVE
- **TEMPORAL_GENERALIZATION**: CONDITIONAL
- **OOS_DECISION_UTILITY**: CONDITIONAL_OBSERVED_ASSOCIATION

## Current Node & Gate
- **Current Node**: COBA_018
- **Current Status**: COBA_018_COMPLETED (RESEARCH_CLOSURE)
- **Primary Finding**: Within the frozen SwingDeck 3-agent architecture and historical replay framework evaluated through COBA_018, no statistically reliable portfolio-level discrimination was identified that remained robust to candidate ordering, sector-allocation sensitivity, concurrency sensitivity, temporal variation, regime variation, benchmark representation, and multiple-comparison controls. P&L attribution demonstrates that 99.05% of executed positions in COBA_016/017 were concentrated in Energy and Mining (ENERGY_COAL_OIL: +42.81M IDR; BASIC_MATERIALS_MINING: -6.25M IDR; FINANCIALS: -0.03M IDR; 4 other sectors 100% excluded), showing historical profits are not separable from those allocation and commodity cycle exposure effects. Seven deterministic candidate orderings show extreme fragility (equity spans from 91.46M to 136.52M IDR). Under sector-balanced allocation (Policy C), profit drops by 74% to +9.52M IDR. Counterfactual non-ACT cohorts (WATCH: +13.00M IDR; REJECT: +7.57M IDR; naive ALL: +19.78M IDR) perform comparably, and differences between ACT and REJECT lose statistical significance after multiple testing control (p > 0.10). The research branch across COBA_001 to COBA_018 is formally and scientifically closed.
- **Objective**: Master Portfolio Allocation, Order-Invariance & Final Generalization Closure Gate
- **Firewall**: CAUSALITY = NOT_PROVEN, STANDALONE_ALPHA = NOT_PROVEN, STRATEGY_OPTIMIZATION = BLOCKED, STRATEGY_READINESS = NOT_READY

## Agent Capabilities
- **Agent 2**: Fully upgraded to Dual Research Mode (`WEB` and `API`). WEB mode enables IDE-native Internet Research for semi-manual intelligence ingestion.

## Post-Research Engineering Phase
- **Phase Status**: DEEP_AUDIT_AND_FOUNDATION_HARDENING = COMPLETE
- **Engineering Status**: ENGINEERING_READY_WITH_LIMITATIONS
- **Operational Status**: OPERATIONALLY_READY_WITH_LIMITATIONS
- **Circular Dependencies**: 0 cycles detected (decoupled `core/data_source_factory.py`)
- **Operational Scope**: Strictly bounded to research, deterministic replay, backtesting/evaluation, and semi-manual paper trading. Full autonomous live trading is BLOCKED.
- **Security Status**: NO_HARDCODED_SECRET_DETECTED_BY_CONFIGURED_SCANNERS
- **Operational Tests**: 243/243 PASS (100% PASS via `pytest -m operational`, 0 failed, 3 legacy skipped)
- **Runtime Agent Boundary**: EXACTLY_3_AGENTS = TRUE, AGENT_4 = FORBIDDEN
- **Next Research Gate**: NEXT_COBA = NONE (COBA_001–COBA_018 permanently frozen).


