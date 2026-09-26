# DUPLICATE CANONICALITY CHECK

## Principles Assessed
- **NO DUPLICATE SOURCE OF TRUTH**
- **ONE PURPOSE -> ONE CANONICAL LOCATION**

## Findings
- Duplicate configurations and outputs were historically placed in `scratch/`.
- Following the architectural contract, temporary elements in `scratch/` have no canonical weight.
- `gates/evidence/` and `gates/closed/` stand as the single source of truth for research outputs.

## Action Taken
- Migrated legacy root loose scripts to `scripts/audit/`.
- `main.py` is the singular operational entrypoint.
- Asserted `COBA_STATUS = NONE`. No duplicate experiments found.
