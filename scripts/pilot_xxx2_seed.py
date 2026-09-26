import duckdb
from datetime import datetime, timezone
import uuid

DB_PATH = "tests/fixtures/intelligence_mock.duckdb"

def get_utc_now():
    return datetime.now(timezone.utc).isoformat()

def seed_pilot_data():
    print(f"Seeding pilot data to {DB_PATH}")
    con = duckdb.connect(DB_PATH)
    
    now = get_utc_now()
    
    # 1. Insert Entities
    entities = [
        ('ENT_ANTM', 'COMPANY', 'Aneka Tambang Tbk'),
        ('ENT_PTBA', 'COMPANY', 'Bukit Asam Tbk'),
        ('ENT_ADRO', 'COMPANY', 'Adaro Energy Indonesia Tbk'),
        ('ENT_BBCA', 'COMPANY', 'Bank Central Asia Tbk'),
        ('ENT_UNVR', 'COMPANY', 'Unilever Indonesia Tbk'),
        ('ENT_GOLD', 'COMMODITY', 'Gold'),
        ('ENT_COAL', 'COMMODITY', 'Coal (Newcastle)'),
        ('ENT_GOV', 'GOVERNMENT', 'Government of Indonesia'),
        ('ENT_POLICY_COAL_BAN', 'POLICY', 'Coal Export Ban')
    ]
    
    for eid, etype, ename in entities:
        con.execute(f"""
            INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from)
            VALUES ('{eid}', '{etype}', '{ename}', '{now}')
        """)
        
    # 2. Insert Evidence
    evidences = [
        ('EVID_1', 'FACT', 'ANTM produces gold.', 'Company Filing', 'IDX:ANTM:2023'),
        ('EVID_2', 'FACT', 'PTBA produces coal.', 'Company Filing', 'IDX:PTBA:2023'),
        ('EVID_3', 'FACT', 'ADRO produces coal.', 'Company Filing', 'IDX:ADRO:2023'),
        ('EVID_4', 'FACT', 'Gov bans coal export.', 'Ministry of Energy', 'MEMR:2024')
    ]
    
    for evid, etype, claim, source, src_id in evidences:
        con.execute(f"""
            INSERT INTO dim_evidence (evidence_id, evidence_type, claim, source, source_identifier, published_at, pit_status)
            VALUES ('{evid}', '{etype}', '{claim}', '{source}', '{src_id}', '{now}', 'FRESH')
        """)

    # 3. Insert Exposures
    exposures = [
        ('EXP_1', 'ENT_ANTM', 'COMMODITY', 'ENT_GOLD', 'REVENUE', 'HIGH', 'POSITIVE', 'EVID_1'),
        ('EXP_2', 'ENT_PTBA', 'COMMODITY', 'ENT_COAL', 'REVENUE', 'HIGH', 'POSITIVE', 'EVID_2'),
        ('EXP_3', 'ENT_ADRO', 'COMMODITY', 'ENT_COAL', 'REVENUE', 'HIGH', 'POSITIVE', 'EVID_3'),
    ]
    
    for exp_id, eid, etype, target, basis, strength, direction, evid in exposures:
        con.execute(f"""
            INSERT INTO fact_exposure (exposure_id, entity_id, exposure_type, target_entity_id, exposure_basis, strength_class, direction, valid_from, evidence_id, pit_status)
            VALUES ('{exp_id}', '{eid}', '{etype}', '{target}', '{basis}', '{strength}', '{direction}', '{now}', '{evid}', 'FRESH')
        """)
        
    # 4. Insert Event
    event_id = 'EVT_COAL_BAN'
    con.execute(f"""
        INSERT INTO fact_event (event_id, event_type, publication_time, materiality, novelty, pit_status, evidence_id)
        VALUES ('{event_id}', 'POLICY', '{now}', 'HIGH', 'HIGH', 'FRESH', 'EVID_4')
    """)
    
    # 5. Insert Relationship (Event -> Entity Exposure)
    con.execute(f"""
        INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from)
        VALUES ('EVT_COAL_BAN', 'EVENT', 'Coal Export Ban Event', '{now}')
    """)
    con.execute(f"""
        INSERT INTO fact_relationship (relationship_id, entity_a_id, relationship_type, entity_b_id, valid_from, evidence_id, pit_status)
        VALUES ('REL_1', 'EVT_COAL_BAN', 'AFFECTS', 'ENT_COAL', '{now}', 'EVID_4', 'FRESH')
    """)
    
    # 6. Insert Peer Network
    # We define PTBA and ADRO as peers based on Coal exposure
    con.execute(f"""
        INSERT INTO fact_peer_network (network_id, base_entity_id, peer_entity_id, peer_type, similarity_basis, valid_from)
        VALUES ('NET_1', 'ENT_PTBA', 'ENT_ADRO', 'COMMODITY', 'ENT_COAL', '{now}')
    """)
    
    # Reverse peer relationship
    con.execute(f"""
        INSERT INTO fact_peer_network (network_id, base_entity_id, peer_entity_id, peer_type, similarity_basis, valid_from)
        VALUES ('NET_2', 'ENT_ADRO', 'ENT_PTBA', 'COMMODITY', 'ENT_COAL', '{now}')
    """)

    # 7. Insert Market Reaction (Synthetic Validation Scenario)
    # Market Reaction: PTBA drops 10%, ADRO drops 2%.
    reactions = [
        ('RX_PTBA', 'EVT_COAL_BAN', 'ENT_PTBA', 'OPENING_GAP', -10.0, -10.0, -0.5, -2.0),
        ('RX_ADRO', 'EVT_COAL_BAN', 'ENT_ADRO', 'OPENING_GAP', -2.0, -2.0, -0.5, -2.0)
    ]
    
    for rx_id, evt_id, eid, window, ret, abn, bmk, sec in reactions:
        con.execute(f"""
            INSERT INTO fact_reaction (reaction_id, event_id, entity_id, reaction_window, return_pct, abnormal_return, benchmark_return, sector_return, observed_at, pit_status)
            VALUES ('{rx_id}', '{evt_id}', '{eid}', '{window}', {ret}, {abn}, {bmk}, {sec}, '{now}', 'FRESH')
        """)

    print("Pilot Data Seeded.")
    con.close()

if __name__ == "__main__":
    seed_pilot_data()
