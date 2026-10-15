# SwingDeck Knowledge Data Platform — Entity & Relationship Model V1

## 1. Entity Lifecycle & Identification

Entities in SwingDeck represent real-world actors within the Indonesian Capital Market ecosystem:
- **Canonical Master:** `entities` (`entity_id`, `canonical_name`, `entity_type`, `jurisdiction`, `status`, `valid_from`, `valid_to`)
- **Identifiers:** `entity_identifiers` (`identifier_type`, `identifier_value`, `issuer`) supporting `IDX_TICKER`, `ISIN`, `LEI`, and `COMPANY_REGISTRATION`.
- **Aliases:** `entity_aliases` (`alias`, `alias_type`, `language`) supporting historical, common, and abbreviated names.

### Layered Entity Resolution
When an incoming disclosure or query refers to an entity, resolution follows strict deterministic priority:
1. **Tier 1 — Exact Identifier Match:** `IDX_TICKER` (e.g. `BBCA`), `ISIN` (e.g. `ID1000106808`).
2. **Tier 2 — Exact Canonical Alias Match:** (e.g. `BCA`, `Adaro`).
3. **Tier 3 — Exact Canonical Name Match:** (e.g. `PT Bank Central Asia Tbk`).
4. **Tier 4 — Contextual Candidate Match:** If exactly 1 candidate matches with high confidence.
5. **Tier 5 — Unresolved / Ambiguous:** Reverts strictly to `UNKNOWN / NEEDS_REVIEW` without forced merge.

## 2. Directed Semantic Relationship Model

Relationships are directional, typed subject-predicate-object triples stored in `entity_relationships`.

### Subject-Predicate-Object Compatibility Firewall
Every relationship insertion and traversal is validated against `RELATIONSHIP_COMPATIBILITY_RULES`:
- `OWNS` / `CONTROLS`: Subject must be an owner entity (`COMPANY`, `HOLDING_COMPANY`, `PERSON`, `STATE_OWNED_ENTITY`, `GOVERNMENT`); object must be an ownable entity (`COMPANY`, `SUBSIDIARY`, `STATE_OWNED_ENTITY`, `PROJECT`).
- `REGULATES`: Subject must be a regulator (`REGULATOR`, `CENTRAL_BANK`, `MINISTRY`); object must be a regulated entity or market.
- `LISTED_ON`: Subject must be a security/company; object must be an `EXCHANGE`.
- `SUBSIDIARY_OF`: Subject must be a `SUBSIDIARY` or `COMPANY`; object must be a `COMPANY` or `HOLDING_COMPANY`.

### Relationship Evidence Linkage
A relationship is never created in isolation. `relationship_evidence` links each edge to one or more `evidence` records with explicit roles:
- `PRIMARY`
- `SECONDARY`
- `CORROBORATING`
- `CONTRADICTING`
