# Batch ZZZ.2 — Historical Information Event Acquisition & Information Event Ledger

## 1. Executive Summary
We successfully expanded the SwingDeck architecture to support the comprehensive Information Event Ledger. Recognizing that **valid information is valuable regardless of its immediate price impact**, the schema now rigorously isolates Temporal states (Event Time vs Publication Time vs Decision Time) and Information Lifecycles (DETECTED -> CONTRADICTED -> SUPERSEDED). The foundation is perfectly prepared to securely ingest real historical semantic events for Agent 2.

## 2. Architectural Upgrades
- **DuckDB Schema**: `fact_event` was massively expanded into an Information Event Ledger.
- **Python Enums**: `EventType`, `InformationState`, and `InformationDelta` were integrated directly into the core Pydantic schemas.

## 3. Temporal Model Enforced
The schema now inherently prevents hindsight bias by mathematically separating:
- `event_timestamp`: When the real-world action occurred.
- `published_at`: When the information hit the public domain.
- `observed_at`: When SwingDeck algorithms detected the information.
- `retrieved_at`: When the raw data hit our Parquet ingestors.
- `decision_timestamp` / `valid_from`: The precise temporal threshold used for the Agent 2 context engine.

## 4. Information Lifecycle
The ledger now treats information as a living, breathing chain of events rather than a static truth. By leveraging `supersedes_event_id` and `contradicts_event_id`, Agent 2 can traverse a chain of:
`RUMOR (DETECTED) -> DENIAL (CONTRADICTED) -> OFFICIAL ANNOUNCEMENT (SUPERSEDED)` 
without ever deleting the historical reality that the market traded on the rumor.

## 5. Event Taxonomy
The extensible taxonomy is ready:
- CORPORATE
- CORPORATE_ACTION
- OWNERSHIP
- GOVERNMENT_POLICY
- MACRO
- COMMODITY
- FX_MONETARY
- GEOPOLITICS_GLOBAL
- MARKET_STRUCTURE
- NEWS_INFORMATION

## 6. Information Source Registry
We created `core/ingestion/info_source_registry.py` and exported `reports/info_source_registry_zzz2.csv`.
This explicitly registers the metadata and limitations of various semantic sources (e.g., *IDX Announcements*, *Government Decrees*), separating primary authoritative sources from secondary aggregators or rumors.

## 7. Next Steps
With the schema and constraints fully implemented, the pipeline is ready to actually ingest real historical text/JSON data from external APIs into the Event Ledger.
