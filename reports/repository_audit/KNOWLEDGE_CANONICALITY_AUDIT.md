# KNOWLEDGE CANONICALITY AUDIT

## Initial State
The `knowledge/` directory lacked structural discipline and indexability.

## Remediation
Implemented a rigid structure:
- `knowledge/canonical/`
- `knowledge/domain/`
- `knowledge/research/`
- `knowledge/failures/`
- `knowledge/patterns/`
- `knowledge/successful_setups/`

## Indexing
Generated `knowledge_registry.json` and `KNOWLEDGE_INDEX.md` as the unified source for tracking KNW-* IDs.

## Future Protocol
No knowledge artifact can be created without an explicit KNW-* ID, status, and trace/lineage entry in the registry.
