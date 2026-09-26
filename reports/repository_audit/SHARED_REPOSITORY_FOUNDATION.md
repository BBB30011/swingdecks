# SHARED REPOSITORY FOUNDATION

## 1. Definitive Folder Contract

### Production/Runtime Code
- **`agents/`**: Core logic for the strictly 3 agents (Quant, Intelligence, Committee). No Agent 4 permitted.
- **`core/`**: Reusable runtime engines, historical research gates (`zzz*.py`) acting as research engines.
- **`scripts/`**: Executable operational entrypoints and wrappers. Never tests or experiment outputs.

### Research & Testing
- **`research/current/`**: Current research state (frozen at ZZZ.14.9).
- **`tests/scientific/`**: Location for historical scientific tests retaining lineage.
- **`tests/coba/` & `research/experiments/COBA_XXX/`**: Future namespace for standalone controlled experiments.

### Knowledge & Governance
- **`knowledge/`**: Shared organizational memory (canonical, domain, research, failures, patterns, successful_setups, index).
- **`reports/`**: Artifacts categorised into scientific, technical, operational, repository_audit, archive. Not a canonical store if artifact exists in `gates/closed/`.

### Artifact Gates
- **`gates/active/`**: Active gate artifacts.
- **`gates/closed/`**: Canonical historical closed gate artifacts.
- **`gates/evidence/`**: Canonical evidence supporting gates.

### Ephemeral
- **`scratch/`**: Temporary workspace (must be deleted, promoted, or archived).
- **`archive/`**: Inactive artifacts preserved for lineage.

## 2. Root Directory Contract
The root directory is strictly for coordination. Current classification of loose root files:
1. `audit_v2.py`: **AUDIT** -> Move to `scripts/audit/`
2. `baseline_audit.py`: **AUDIT** -> Move to `scripts/audit/`
3. `patch_obsolete_tests.py`: **SCRIPT** -> Move to `scripts/audit/`
4. `MIGRATION_EXECUTION_REPORT.md`: **HISTORICAL** -> Move to `reports/repository_audit/`
5. `scratch_inventory.json`: **ACTIVE** -> Moved to `scratch/`
6. `main.py`: **ACTIVE_ENTRYPOINT** -> Remains in root.

## 3. COBA Contract
Status: `COBA_STATUS = NONE`. No COBA experiments exist. Sequential naming (`COBA_001`) mandated for future.

## 4. Main.py Audit
`main.py` verified as a pure entrypoint placeholder currently printing environment statuses. Safe to remain in root.
