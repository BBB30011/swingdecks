import duckdb
import os
from datetime import datetime, timezone

DB_PATH = "data/duckdb/intelligence.duckdb"

def init_duckdb():
    print(f"Initializing DuckDB at {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = duckdb.connect(DB_PATH)
    
    # 1. Entity Master
    con.execute("""
        CREATE SEQUENCE IF NOT EXISTS seq_entity_id;
        CREATE TABLE IF NOT EXISTS dim_entity (
            entity_id VARCHAR PRIMARY KEY,
            entity_type VARCHAR, -- COMPANY, COMMODITY, POLICY, SECTOR, EVENT
            canonical_name VARCHAR,
            status VARCHAR DEFAULT 'ACTIVE',
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Entity Alias
    con.execute("""
        CREATE TABLE IF NOT EXISTS dim_entity_alias (
            alias_id VARCHAR PRIMARY KEY,
            entity_id VARCHAR REFERENCES dim_entity(entity_id),
            alias_type VARCHAR, -- TICKER, FORMER_NAME, YFINANCE_ID
            alias_value VARCHAR,
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            source_id VARCHAR,
            pit_status VARCHAR
        );
    """)

    # 3. Evidence Ledger
    con.execute("""
        CREATE TABLE IF NOT EXISTS dim_evidence (
            evidence_id VARCHAR PRIMARY KEY,
            evidence_type VARCHAR, -- FACT, INFERENCE, HYPOTHESIS
            claim VARCHAR,
            source VARCHAR,
            source_identifier VARCHAR,
            published_at TIMESTAMP,
            observed_at TIMESTAMP,
            retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reliability VARCHAR,
            confidence FLOAT,
            pit_status VARCHAR,
            provenance VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Relationship Ledger
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_relationship (
            relationship_id VARCHAR PRIMARY KEY,
            entity_a_id VARCHAR REFERENCES dim_entity(entity_id),
            relationship_type VARCHAR, -- OWNS, EXPOSED_TO, AFFECTS
            entity_b_id VARCHAR REFERENCES dim_entity(entity_id),
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            observed_at TIMESTAMP,
            source_id VARCHAR,
            evidence_id VARCHAR REFERENCES dim_evidence(evidence_id),
            confidence FLOAT,
            pit_status VARCHAR,
            validation_status VARCHAR,
            provenance_id VARCHAR
        );
    """)

    # 5. Exposure Table
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_exposure (
            exposure_id VARCHAR PRIMARY KEY,
            entity_id VARCHAR REFERENCES dim_entity(entity_id),
            exposure_type VARCHAR, -- COMMODITY, POLICY, SECTOR
            target_entity_id VARCHAR REFERENCES dim_entity(entity_id),
            exposure_basis VARCHAR, -- REVENUE, PERMIT, COST
            strength_class VARCHAR, -- HIGH, MEDIUM, LOW
            direction VARCHAR, -- POSITIVE, NEGATIVE
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            source_id VARCHAR,
            evidence_id VARCHAR REFERENCES dim_evidence(evidence_id),
            confidence FLOAT,
            pit_status VARCHAR,
            provenance_id VARCHAR
        );
    """)

    # 6. Event Table (Information Event Ledger)
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_event (
            event_id VARCHAR PRIMARY KEY,
            event_type VARCHAR,
            event_subtype VARCHAR,
            
            entity_id VARCHAR REFERENCES dim_entity(entity_id),
            entity_type VARCHAR,
            
            event_timestamp TIMESTAMP,
            published_at TIMESTAMP,
            information_available_at TIMESTAMP,
            observed_at TIMESTAMP,
            retrieved_at TIMESTAMP,
            
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            
            source_id VARCHAR,
            source_name VARCHAR,
            source_url VARCHAR,
            source_quality VARCHAR,
            source_type VARCHAR,
            
            raw_reference VARCHAR,
            provenance VARCHAR,
            
            information_state VARCHAR,
            information_delta VARCHAR,
            
            materiality VARCHAR,
            relevance VARCHAR,
            confidence FLOAT,
            
            is_pit_valid BOOLEAN,
            pit_reason VARCHAR,
            
            supersedes_event_id VARCHAR,
            contradicts_event_id VARCHAR,
            
            status VARCHAR DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 7. Peer Network (Contextual)
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_peer_network (
            network_id VARCHAR PRIMARY KEY,
            base_entity_id VARCHAR REFERENCES dim_entity(entity_id),
            peer_entity_id VARCHAR REFERENCES dim_entity(entity_id),
            peer_type VARCHAR, -- SECTOR, COMMODITY, POLICY
            similarity_basis VARCHAR, -- The target_entity_id or logic that groups them
            confidence FLOAT,
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            source_id VARCHAR
        );
    """)
    
    # 8. Market Reaction
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_reaction (
            reaction_id VARCHAR PRIMARY KEY,
            event_id VARCHAR REFERENCES fact_event(event_id),
            entity_id VARCHAR REFERENCES dim_entity(entity_id),
            reaction_window VARCHAR, -- OPENING_GAP, H1, H10
            return_pct FLOAT,
            abnormal_return FLOAT,
            benchmark_return FLOAT,
            sector_return FLOAT,
            volume_change FLOAT,
            observed_at TIMESTAMP,
            pit_status VARCHAR
        );
    """)

    # 9. Information Impact & Asymmetric Beneficiary
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_information_impact (
            impact_id VARCHAR PRIMARY KEY,
            event_id VARCHAR REFERENCES fact_event(event_id),
            entity_id VARCHAR REFERENCES dim_entity(entity_id),
            exposure_id VARCHAR REFERENCES fact_exposure(exposure_id),
            expected_direction VARCHAR,
            expected_materiality VARCHAR,
            actual_direction VARCHAR,
            actual_magnitude FLOAT,
            peer_reaction FLOAT,
            specificity_status VARCHAR, -- ASYMMETRIC_BENEFICIARY, MARKET_BETA, SECTOR_BETA
            evidence_id VARCHAR REFERENCES dim_evidence(evidence_id),
            confidence FLOAT,
            pit_status VARCHAR,
            provenance_id VARCHAR
        );
    """)

    # 10. Hypothesis Registry
    con.execute("""
        CREATE TABLE IF NOT EXISTS fact_hypothesis (
            hypothesis_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            description VARCHAR,
            event_id VARCHAR REFERENCES fact_event(event_id),
            target_entity_id VARCHAR REFERENCES dim_entity(entity_id),
            status VARCHAR, -- OBSERVATION, HYPOTHESIS, TESTING, SUPPORTED, REJECTED, OOS_VALIDATED, PRODUCTION_APPROVED
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            evidence_id VARCHAR REFERENCES dim_evidence(evidence_id),
            experiment_id VARCHAR,
            validation_status VARCHAR,
            provenance VARCHAR
        );
    """)

    print("DuckDB Schema initialized successfully.")
    con.close()

if __name__ == "__main__":
    init_duckdb()
