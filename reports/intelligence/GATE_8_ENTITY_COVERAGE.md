# SWINGDECK — GATE 8: ENTITY RESOLUTION & COVERAGE REPORT

## 1. SCOPE & SUMMARY

This report audits entity resolution performance across the 120 canonical scale observations in `COHORT_GATE8_CANONICAL_V1`.

---

## 2. OBSERVED ENTITY DISTRIBUTION

Across 20 unique resolved entities:

| Entity Type | Unique Entities | Key Canonical Identifiers |
|---|---|---|
| **Listed Corporates (`COMPANY`)** | 15 | `ENT_ADRO`, `ENT_PTBA`, `ENT_ANTM`, `ENT_INCO`, `ENT_MDKA`, `ENT_MEDC`, `ENT_PGAS`, `ENT_AALI`, `ENT_BBRI`, `ENT_BMRI`, `ENT_BBNI`, `ENT_ASII`, `ENT_TLKM`, `ENT_UNTR`, `ENT_ICBP` |
| **Statutory Regulators (`REGULATOR`)** | 1 | `ENT_OJK` (Otoritas Jasa Keuangan) |
| **Government Ministries (`MINISTRY`)** | 3 | `ENT_MEMR` (ESDM), `ENT_MOF` (Kemenkeu), `ENT_MOT` (Kemendag) |
| **Central Bank (`CENTRAL_BANK`)** | 1 | `ENT_BI` (Bank Indonesia) |

---

## 3. RESOLUTION INVARIANTS & AMBIGUITY HANDLING

- **Entity Resolution Rate:** **100.00%** (120 / 120 resolved to verified canonical entity IDs).
- **Forced Match Rate:** **0.00%** (`FORCED_MATCH_RATE = 0`). The system never forces an ambiguous or unknown ticker string into an entity match.
- **Ambiguous Handling:** Ambiguous queries return `AMBIGUOUS` with candidate sets without silent guessing.
- **Unknown Handling:** Unregistered entities remain strictly `UNKNOWN`.
