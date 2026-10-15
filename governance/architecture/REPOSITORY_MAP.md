# REPOSITORY STRUCTURAL MAP

## AUTHORITY
This document is the **Single Canonical Source of Truth** for the structural boundaries of the SwingDeck repository. Any new folders, modules, or artifacts MUST be placed according to this map. If a structure conflicts with this map, the structure is invalid.

## THE THREE AGENTS
The system is explicitly bounded to exactly three agents. **Agent 4 does not exist.**

1. `agents/agent1_quant/` : Quantitative filtering and market scanning.
2. `agents/agent2_intelligence/` : Market intelligence, reasoning, and adversarial red-teaming.
3. `agents/agent3_committee/` : Final investment committee decision and risk sizing.

## CORE ARCHITECTURE
- `core/` : Reusable engine logic. No runtime state.
  - `core/backtest/` : Engine for backtesting and simulation.
  - `core/ingestion/` : Data ingestion and cleaning pipelines.
  - `core/providers/` : Integrations with external data providers.

## DATA ARCHITECTURE
- `data/` : Local canonical data storage (See `DATA_MAP.md` for ownership).

## EXECUTION AND STATE
- `queue/` : Cross-agent communication and staging.
  - `/completed`, `/dead_letter`, `/decisions`, `/failed`, `/review`
- `state/` : Current mutable runtime state (e.g., `sys.json`, `signal_states.json`).
- `logs/` : Execution telemetry.
- `positions/` : Current trading positions.

## KNOWLEDGE AND GOVERNANCE
- `knowledge/` : The repository brain (See `AGENT_KNOWLEDGE_MAP.md` for agent boundaries).
  - `/canonical` : Core system rules.
  - `/domain` : Trading domain knowledge.
  - `/failures` : Post-mortems.
  - `/index` : Knowledge registry.
  - `/patterns` : Approved coding patterns.
  - `/research` : Accepted research documents.
  - `/successful_setups` : Historical successful configurations.
- `governance/` : Project control layer.
  - `/architecture` : Architectural maps (like this one).
  - `/change_control` : Decision logs and naming conventions.
  - `/frozen` : Immutable frozen artifacts.
  - `/lineage` : Project history mapping.

## RESEARCH AND AUDIT
- `research/` : Historical research and experiments (COBA_001 through COBA_018 permanently frozen).
  - `/analysis`, `/current`, `/experiments`, `/validation`
- `gates/` : Lifecycle boundaries.
  - `/evidence` : Immutable evidence for gate transitions.
  - `/closed` : Historical completed gates.
- `reports/` : Human-readable outputs and audit results.
  - `/alerts`, `/backtest`, `/daily`, `/repository_audit`, `/technical`
- `tests/` : System validation and testing.
  - `/fixtures` : Test data.
  - Subdirectory `tests/scratch/` is FORBIDDEN and eliminated (use standard pytest `tmp_path`).
- `configs/` : Static configuration templates and data source configurations.
- `scripts/` : Maintenance tools (`/audit`, etc).
- `scratch/` : Ephemeral scratch workspace for temporary batch calculations (cleared between major phases).

## FORBIDDEN PATHS & DRIFT PREVENTION
- Ghost directories such as `archive/`, `dummy/`, `d/`, or `tests/scratch/` are strictly FORBIDDEN.
- Exactly 3 runtime agents (`agent1_quant`, `agent2_intelligence`, `agent3_committee`). Zero Agent 4.

