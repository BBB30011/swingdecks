# SwingDeck Entity Resolution & Semantic Ontology V1

## 1. 5-Tier Hierarchical Entity Resolution

Entity resolution in SwingDeck maps diverse textual mentions in news, filings, and policy documents to unique, canonical capital market entities without fuzzy guess-matching.

```text
TIER 1 — Exact Canonical Identifier (e.g. ENT_BBCA, ENT_IDX, ENT_OJK)
   │
   ▼
TIER 2 — Official Identifier / Ticker (e.g. BBCA, IDX, OJK)
   │
   ▼
TIER 3 — Exact Normalized Legal Name (e.g. PT Bank Central Asia Tbk)
   │
   ▼
TIER 4 — Known Alias / Historical Name (e.g. Bank BCA, Bapepam-LK)
   │
   ▼
TIER 5 — Candidate Match Requiring Review
   │
   ▼
FAIL CLOSED: UNKNOWN (Never force an ambiguous match)
```

---

## 2. Indonesian Capital Market Ontology & Semantic Firewall

The ontology layer (`core/semantic_ontology.py`) defines formal taxonomy, mutually exclusive groups, and relationship compatibility rules:

### 2.1 Critical Semantic Truths
- **Exchange vs Regulator**:
  - `IDX` (`PT Bursa Efek Indonesia`) is strictly an `EXCHANGE` (market operator / SRO), **NEVER A REGULATOR**.
  - `OJK` (`Otoritas Jasa Keuangan`) is strictly a `REGULATOR`, **NEVER AN EXCHANGE**.
- **Central Bank**:
  - `BI` (`Bank Indonesia`) is strictly a `CENTRAL_BANK`.
- **State-Owned vs Private**:
  - `PTBA`, `BMRI`, `BBRI`, `BBNI`, `TLKM` are `STATE_OWNED_ENTITY` / state banks.
  - `BBCA` is a private commercial bank.

### 2.2 Corporate Action Case: ADRO / AADI Divestment
- `ADRO` (`PT Adaro Energy Indonesia Tbk`) is a `COMPANY` listed on `IDX`.
- `AADI` (`PT Alamtri Resources Indonesia Tbk`) is a `SUBSIDIARY` spun off / divested from `ADRO` in 2024.
- The relationship between `ADRO` and `AADI` is classified as `RelationshipType.DISPOSES` with status `ACTIVE`.
- In compliance with the "Never Invent" axiom, effective dates and consolidation states that cannot be proved from canonical evidence are classified as `UNKNOWN`.

---

## 3. Relationship Compatibility Matrix

Relationships must satisfy subject-predicate-object semantic constraints before ingestion into the Knowledge Platform:

| Predicate | Allowed Subject Types | Allowed Object Types |
| :--- | :--- | :--- |
| `OWNS` | `COMPANY`, `HOLDING_COMPANY`, `INVESTOR`, `PERSON`, `GOVERNMENT` | `COMPANY`, `SUBSIDIARY`, `PROJECT`, `SECURITY` |
| `CONTROLS` | `COMPANY`, `HOLDING_COMPANY`, `PERSON`, `GOVERNMENT` | `COMPANY`, `SUBSIDIARY`, `PROJECT` |
| `SUBSIDIARY_OF` | `SUBSIDIARY`, `COMPANY`, `BANK` | `COMPANY`, `HOLDING_COMPANY`, `STATE_OWNED_ENTITY` |
| `REGULATES` | `REGULATOR`, `CENTRAL_BANK`, `GOVERNMENT`, `MINISTRY` | `COMPANY`, `EXCHANGE`, `BANK`, `MARKET`, `SECTOR` |
| `OPERATES` | `EXCHANGE`, `COMPANY`, `INSTITUTION` | `MARKET`, `INDEX`, `PROJECT` |
| `LISTED_ON` | `COMPANY`, `HOLDING_COMPANY`, `STATE_OWNED_ENTITY`, `BANK` | `EXCHANGE`, `MARKET` |
| `DISPOSES` | `COMPANY`, `HOLDING_COMPANY`, `STATE_OWNED_ENTITY` | `COMPANY`, `SUBSIDIARY`, `PROJECT`, `SECURITY` |
| `ACQUIRES` | `COMPANY`, `HOLDING_COMPANY`, `INVESTOR`, `BANK` | `COMPANY`, `SUBSIDIARY`, `PROJECT`, `SECURITY` |
