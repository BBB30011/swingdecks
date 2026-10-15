# DATA OWNERSHIP MAP

## AUTHORITY
This document is the **Single Canonical Source of Truth** for the data layer boundaries of the SwingDeck repository. 

## PRIMARY DATABASE CONTRACTS
- **Intelligence Database (DuckDB)**
  - Canonical Path: `data/duckdb/intelligence.duckdb`
  - Ownership: Managed by `core/ingestion` and read by Agents for fundamental reasoning and scoring.
  - *Legacy Note*: The root path `data/intelligence.duckdb` is strictly deprecated and must not be used.

## DATA HIERARCHY
- `data/`
  - `duckdb/` : Analytical relational databases (DuckDB).
  - `parquet/` : Columnar datasets for fast quantitative reads.
    - `/corporate_actions`
    - `/entity`
    - `/market`
  - `raw/` : Unaltered incoming data (immutable layer).
    - `/disclosures` (`/idx`, `/issuer`, `/news`, `/regulator`)
    - `/historical`
    - `/market`
    - `/news`
    - `/synthetic`
  - `processed/` : Intermediate transformed files.
  - `cache/` : Ephemeral cache files to speed up queries.
  - `manifests/` : Tracking files for data lineage and state.
  - `intelligence/` : (Deprecated/Consolidated) Legacy intelligence path.

## TEST DATA
- Mock and test databases must be placed in `tests/fixtures/`.
- Tests must NOT mutate canonical databases in `data/duckdb/`.
