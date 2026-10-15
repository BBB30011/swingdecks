# COBA Auto-Sync & Foundation Update Rule

## Scope & Scientific Firewall
> **MANDATORY GOVERNANCE NOTICE**: The scientific research branch across `COBA_001` through `COBA_018` is **PERMANENTLY CLOSED AND IMMUTABLE**. No new scientific alpha experiments may be created (`COBA_019 = NOT_CREATED`), and strategy optimization is strictly blocked (`STRATEGY_OPTIMIZATION = BLOCKED`).

This rule applies **strictly to operational, architectural, and intelligence validation gates** (e.g., Intelligence V2.1 Gate, Truth Gate scans, Operational Soak tests) that result in a shift in system documentation, data sources, or architectural contracts.

## Trigger Condition
Whenever you complete an operational or intelligence milestone that modifies foundational data pipelines, entity graphs, security firewalls, or architectural contracts.

## Automatic Actions
If the trigger condition is met, perform the following updates:

1. **Project Memory (`knowledge/canonical/PROJECT_MEMORY.md`)**:
   - Append a concise summary of the newly validated operational milestone, including its scope, core findings, and final classification.
2. **Project Context (`knowledge/canonical/PROJECT_CONTEXT.md`)**:
   - Update `Engineering Status`, `Operational Status`, and current node status to reflect the latest validated gate.
3. **Configurations (`configs/`)**:
   - If operational parameters, data source paths, or universe definitions change, update the respective configuration files.
4. **Governance & Change Control (`governance/`)**:
   - If an architectural shift occurs, document the rationale in `governance/change_control/` and update `governance/architecture/`.

## Exception Rule
If a task is purely diagnostic, produces no findings that alter the baseline understanding, or produces a temporary scratch artifact, **DO NOT** perform structural updates. Only update when foundational parameters or verified gates shift.
