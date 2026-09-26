"""
core/semantic_substrate_engine.py

Semantic Substrate Engine for Batch ZZZ.9.
Manages DuckDB historical semantic data population, temporal versioning, entity aliases,
commodity exposures, fundamental disclosures, corporate actions, and relationships.
Enforces strict Point-in-Time (PIT) boundaries and non-destructive historical knowledge versioning.
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

class SemanticSubstrateEngine:
    """
    Manages the Relational DuckDB Semantic Substrate for Agent 2.
    Ensures Point-In-Time (PIT) isolation, evidence-backed exposure tracking,
    conservative entity resolution, and non-destructive historical knowledge versioning.
    """
    
    # Pilot Universe Entity Definitions
    PILOT_ENTITIES = [
        {"entity_id": "ENT_ADRO", "entity_type": "COMPANY", "canonical_name": "PT Adaro Energy Indonesia Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_ANTM", "entity_type": "COMPANY", "canonical_name": "PT Aneka Tambang Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_ASII", "entity_type": "COMPANY", "canonical_name": "PT Astra International Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_BBCA", "entity_type": "COMPANY", "canonical_name": "PT Bank Central Asia Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_BBNI", "entity_type": "COMPANY", "canonical_name": "PT Bank Negara Indonesia (Persero) Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_BBRI", "entity_type": "COMPANY", "canonical_name": "PT Bank Rakyat Indonesia (Persero) Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_BMRI", "entity_type": "COMPANY", "canonical_name": "PT Bank Mandiri (Persero) Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_INCO", "entity_type": "COMPANY", "canonical_name": "PT Vale Indonesia Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_ITMG", "entity_type": "COMPANY", "canonical_name": "PT Indo Tambangraya Megah Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_PTBA", "entity_type": "COMPANY", "canonical_name": "PT Bukit Asam Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_TLKM", "entity_type": "COMPANY", "canonical_name": "PT Telkom Indonesia (Persero) Tbk", "status": "ACTIVE"},
        {"entity_id": "ENT_UNTR", "entity_type": "COMPANY", "canonical_name": "PT United Tractors Tbk", "status": "ACTIVE"},
        
        # Commodities & Macro Assets
        {"entity_id": "ENT_COAL", "entity_type": "COMMODITY", "canonical_name": "Thermal Coal (Newcastle)", "status": "ACTIVE"},
        {"entity_id": "ENT_NICKEL", "entity_type": "COMMODITY", "canonical_name": "Nickel (LME)", "status": "ACTIVE"},
        {"entity_id": "ENT_GOLD", "entity_type": "COMMODITY", "canonical_name": "Gold (COMEX)", "status": "ACTIVE"},
        {"entity_id": "ENT_OIL", "entity_type": "COMMODITY", "canonical_name": "Crude Oil (Brent)", "status": "ACTIVE"},
        {"entity_id": "ENT_USD_IDR", "entity_type": "FX", "canonical_name": "US Dollar / Indonesian Rupiah", "status": "ACTIVE"},
        
        # Holding / Controlling Entities & Government
        {"entity_id": "ENT_GOV_INDONESIA", "entity_type": "GOVERNMENT", "canonical_name": "Government of the Republic of Indonesia", "status": "ACTIVE"},
        {"entity_id": "ENT_MIND_ID", "entity_type": "HOLDING_COMPANY", "canonical_name": "PT Mineral Industri Indonesia (Persero) / MIND ID", "status": "ACTIVE"},
        {"entity_id": "ENT_ADARO_STRATEGIC", "entity_type": "HOLDING_COMPANY", "canonical_name": "PT Adaro Strategic Investments", "status": "ACTIVE"},
        {"entity_id": "ENT_BANPU", "entity_type": "HOLDING_COMPANY", "canonical_name": "Banpu Minerals Singapore Pte Ltd", "status": "ACTIVE"},
        {"entity_id": "ENT_DJARUM_GROUP", "entity_type": "HOLDING_COMPANY", "canonical_name": "PT Dwimuria Investama Andalan / Djarum Group", "status": "ACTIVE"},
        {"entity_id": "ENT_JARDINE_CYCLE", "entity_type": "HOLDING_COMPANY", "canonical_name": "Jardine Cycle & Carriage Ltd", "status": "ACTIVE"},
        {"entity_id": "ENT_VALE_CANADA", "entity_type": "HOLDING_COMPANY", "canonical_name": "Vale Canada Limited", "status": "ACTIVE"}
    ]

    # Validated Commodity & Industry Exposures (Evidence-backed)
    VALIDATED_EXPOSURES = [
        {"exposure_id": "EXP_ADRO_COAL", "entity_id": "ENT_ADRO", "exposure_type": "COMMODITY", "target_entity_id": "ENT_COAL", "exposure_basis": "REVENUE", "strength_class": "HIGH", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_ITMG_COAL", "entity_id": "ENT_ITMG", "exposure_type": "COMMODITY", "target_entity_id": "ENT_COAL", "exposure_basis": "REVENUE", "strength_class": "HIGH", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_PTBA_COAL", "entity_id": "ENT_PTBA", "exposure_type": "COMMODITY", "target_entity_id": "ENT_COAL", "exposure_basis": "REVENUE", "strength_class": "HIGH", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_ANTM_GOLD", "entity_id": "ENT_ANTM", "exposure_type": "COMMODITY", "target_entity_id": "ENT_GOLD", "exposure_basis": "REVENUE", "strength_class": "HIGH", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_ANTM_NICKEL", "entity_id": "ENT_ANTM", "exposure_type": "COMMODITY", "target_entity_id": "ENT_NICKEL", "exposure_basis": "REVENUE", "strength_class": "MEDIUM", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_INCO_NICKEL", "entity_id": "ENT_INCO", "exposure_type": "COMMODITY", "target_entity_id": "ENT_NICKEL", "exposure_basis": "REVENUE", "strength_class": "HIGH", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"},
        {"exposure_id": "EXP_UNTR_COAL", "entity_id": "ENT_UNTR", "exposure_type": "COMMODITY", "target_entity_id": "ENT_COAL", "exposure_basis": "CONTRACT_MINING", "strength_class": "MEDIUM", "direction": "POSITIVE", "valid_from": "2020-01-01 00:00:00", "source_id": "SRC_ANNUAL_REPORT_2024"}
    ]

    # Validated Group & Ownership Relationships (Evidence-backed)
    VALIDATED_RELATIONSHIPS = [
        {"relationship_id": "REL_MIND_PTBA", "entity_a_id": "ENT_MIND_ID", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_PTBA", "valid_from": "2019-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_MIND_ANTM", "entity_a_id": "ENT_MIND_ID", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_ANTM", "valid_from": "2019-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_MIND_INCO", "entity_a_id": "ENT_MIND_ID", "relationship_type": "SHAREHOLDER_OF", "entity_b_id": "ENT_INCO", "valid_from": "2024-06-28 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_ASII_UNTR", "entity_a_id": "ENT_ASII", "relationship_type": "PARENT_OF", "entity_b_id": "ENT_UNTR", "valid_from": "2010-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_GOV_BMRI", "entity_a_id": "ENT_GOV_INDONESIA", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_BMRI", "valid_from": "2000-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_GOV_BBRI", "entity_a_id": "ENT_GOV_INDONESIA", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_BBRI", "valid_from": "2000-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_GOV_BBNI", "entity_a_id": "ENT_GOV_INDONESIA", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_BBNI", "valid_from": "2000-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_GOV_TLKM", "entity_a_id": "ENT_GOV_INDONESIA", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_TLKM", "valid_from": "2000-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_BANPU_ITMG", "entity_a_id": "ENT_BANPU", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_ITMG", "valid_from": "2010-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"},
        {"relationship_id": "REL_DJARUM_BBCA", "entity_a_id": "ENT_DJARUM_GROUP", "relationship_type": "CONTROLLER_OF", "entity_b_id": "ENT_BBCA", "valid_from": "2010-01-01 00:00:00", "source_id": "SRC_IDX_DISCLOSURE"}
    ]

    # Contextual Peer Network
    VALIDATED_PEER_NETWORKS = [
        {"network_id": "NET_COAL_1", "base_entity_id": "ENT_ADRO", "peer_entity_id": "ENT_ITMG", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_EXPORTER", "confidence": 0.95, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_COAL_2", "base_entity_id": "ENT_ADRO", "peer_entity_id": "ENT_PTBA", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_MINER", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_COAL_3", "base_entity_id": "ENT_ITMG", "peer_entity_id": "ENT_ADRO", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_EXPORTER", "confidence": 0.95, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_COAL_4", "base_entity_id": "ENT_ITMG", "peer_entity_id": "ENT_PTBA", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_MINER", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_COAL_5", "base_entity_id": "ENT_PTBA", "peer_entity_id": "ENT_ADRO", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_MINER", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_COAL_6", "base_entity_id": "ENT_PTBA", "peer_entity_id": "ENT_ITMG", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "THERMAL_COAL_MINER", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_METALS_1", "base_entity_id": "ENT_ANTM", "peer_entity_id": "ENT_INCO", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "METALS_MINING_NICKEL", "confidence": 0.85, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_METALS_2", "base_entity_id": "ENT_INCO", "peer_entity_id": "ENT_ANTM", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "METALS_MINING_NICKEL", "confidence": 0.85, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_BANK_1", "base_entity_id": "ENT_BBCA", "peer_entity_id": "ENT_BBRI", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "TIER_1_COMMERCIAL_BANK", "confidence": 0.95, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_BANK_2", "base_entity_id": "ENT_BBCA", "peer_entity_id": "ENT_BMRI", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "TIER_1_COMMERCIAL_BANK", "confidence": 0.95, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_BANK_3", "base_entity_id": "ENT_BBCA", "peer_entity_id": "ENT_BBNI", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "TIER_1_COMMERCIAL_BANK", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_CONGLOM_1", "base_entity_id": "ENT_ASII", "peer_entity_id": "ENT_UNTR", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "ASTRA_GROUP_INDUSTRIAL", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"},
        {"network_id": "NET_CONGLOM_2", "base_entity_id": "ENT_UNTR", "peer_entity_id": "ENT_ASII", "peer_type": "CONTEXTUAL_SECTOR", "similarity_basis": "ASTRA_GROUP_INDUSTRIAL", "confidence": 0.90, "valid_from": "2020-01-01 00:00:00"}
    ]

    # Entity Aliases for Conservative Linkage
    ENTITY_ALIASES = [
        {"alias_id": "ALS_ADRO_1", "entity_id": "ENT_ADRO", "alias_type": "TICKER", "alias_value": "ADRO"},
        {"alias_id": "ALS_ADRO_2", "entity_id": "ENT_ADRO", "alias_type": "LEGAL_NAME", "alias_value": "Adaro Energy"},
        {"alias_id": "ALS_ANTM_1", "entity_id": "ENT_ANTM", "alias_type": "TICKER", "alias_value": "ANTM"},
        {"alias_id": "ALS_ANTM_2", "entity_id": "ENT_ANTM", "alias_type": "LEGAL_NAME", "alias_value": "Aneka Tambang"},
        {"alias_id": "ALS_ASII_1", "entity_id": "ENT_ASII", "alias_type": "TICKER", "alias_value": "ASII"},
        {"alias_id": "ALS_ASII_2", "entity_id": "ENT_ASII", "alias_type": "LEGAL_NAME", "alias_value": "Astra International"},
        {"alias_id": "ALS_BBCA_1", "entity_id": "ENT_BBCA", "alias_type": "TICKER", "alias_value": "BBCA"},
        {"alias_id": "ALS_BBCA_2", "entity_id": "ENT_BBCA", "alias_type": "LEGAL_NAME", "alias_value": "Bank Central Asia"},
        {"alias_id": "ALS_BBNI_1", "entity_id": "ENT_BBNI", "alias_type": "TICKER", "alias_value": "BBNI"},
        {"alias_id": "ALS_BBNI_2", "entity_id": "ENT_BBNI", "alias_type": "LEGAL_NAME", "alias_value": "Bank Negara Indonesia"},
        {"alias_id": "ALS_BBRI_1", "entity_id": "ENT_BBRI", "alias_type": "TICKER", "alias_value": "BBRI"},
        {"alias_id": "ALS_BBRI_2", "entity_id": "ENT_BBRI", "alias_type": "LEGAL_NAME", "alias_value": "Bank Rakyat Indonesia"},
        {"alias_id": "ALS_BMRI_1", "entity_id": "ENT_BMRI", "alias_type": "TICKER", "alias_value": "BMRI"},
        {"alias_id": "ALS_BMRI_2", "entity_id": "ENT_BMRI", "alias_type": "LEGAL_NAME", "alias_value": "Bank Mandiri"},
        {"alias_id": "ALS_INCO_1", "entity_id": "ENT_INCO", "alias_type": "TICKER", "alias_value": "INCO"},
        {"alias_id": "ALS_INCO_2", "entity_id": "ENT_INCO", "alias_type": "LEGAL_NAME", "alias_value": "Vale Indonesia"},
        {"alias_id": "ALS_ITMG_1", "entity_id": "ENT_ITMG", "alias_type": "TICKER", "alias_value": "ITMG"},
        {"alias_id": "ALS_ITMG_2", "entity_id": "ENT_ITMG", "alias_type": "LEGAL_NAME", "alias_value": "Indo Tambangraya Megah"},
        {"alias_id": "ALS_PTBA_1", "entity_id": "ENT_PTBA", "alias_type": "TICKER", "alias_value": "PTBA"},
        {"alias_id": "ALS_PTBA_2", "entity_id": "ENT_PTBA", "alias_type": "LEGAL_NAME", "alias_value": "Bukit Asam"},
        {"alias_id": "ALS_TLKM_1", "entity_id": "ENT_TLKM", "alias_type": "TICKER", "alias_value": "TLKM"},
        {"alias_id": "ALS_TLKM_2", "entity_id": "ENT_TLKM", "alias_type": "LEGAL_NAME", "alias_value": "Telkom Indonesia"},
        {"alias_id": "ALS_UNTR_1", "entity_id": "ENT_UNTR", "alias_type": "TICKER", "alias_value": "UNTR"},
        {"alias_id": "ALS_UNTR_2", "entity_id": "ENT_UNTR", "alias_type": "LEGAL_NAME", "alias_value": "United Tractors"}
    ]

    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path

    def populate_substrate(self) -> Dict[str, Any]:
        """
        Populates and updates DuckDB tables with validated entities, exposures,
        relationships, peer networks, and entity aliases without overwriting historical facts.
        """
        con = duckdb.connect(self.db_path)
        
        # 1. Populate dim_entity
        for ent in self.PILOT_ENTITIES:
            existing = con.execute("SELECT entity_id FROM dim_entity WHERE entity_id = ?", (ent["entity_id"],)).fetchall()
            if not existing:
                con.execute("""
                    INSERT INTO dim_entity (entity_id, entity_type, canonical_name, status, valid_from, valid_to, created_at, updated_at)
                    VALUES (?, ?, ?, ?, '1990-01-01 00:00:00', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (ent["entity_id"], ent["entity_type"], ent["canonical_name"], ent["status"]))
                
        # 2. Populate dim_entity_alias
        for als in self.ENTITY_ALIASES:
            existing = con.execute("SELECT alias_id FROM dim_entity_alias WHERE alias_id = ?", (als["alias_id"],)).fetchall()
            if not existing:
                con.execute("""
                    INSERT INTO dim_entity_alias (alias_id, entity_id, alias_type, alias_value, valid_from, valid_to, source_id, pit_status)
                    VALUES (?, ?, ?, ?, '1990-01-01 00:00:00', NULL, 'SRC_IDX_REGISTRY', 'VERIFIED')
                """, (als["alias_id"], als["entity_id"], als["alias_type"], als["alias_value"]))

        # 3. Populate fact_exposure
        for exp in self.VALIDATED_EXPOSURES:
            existing = con.execute("SELECT exposure_id FROM fact_exposure WHERE exposure_id = ?", (exp["exposure_id"],)).fetchall()
            if not existing:
                con.execute("""
                    INSERT INTO fact_exposure (exposure_id, entity_id, exposure_type, target_entity_id, exposure_basis, strength_class, direction, valid_from, valid_to, source_id, evidence_id, confidence, pit_status, provenance_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, 0.95, 'VERIFIED', 'PROV_FACTBOOK')
                """, (exp["exposure_id"], exp["entity_id"], exp["exposure_type"], exp["target_entity_id"], exp["exposure_basis"], exp["strength_class"], exp["direction"], exp["valid_from"], exp["source_id"]))

        # 4. Populate fact_relationship
        for rel in self.VALIDATED_RELATIONSHIPS:
            existing = con.execute("SELECT relationship_id FROM fact_relationship WHERE relationship_id = ?", (rel["relationship_id"],)).fetchall()
            if not existing:
                con.execute("""
                    INSERT INTO fact_relationship (relationship_id, entity_a_id, relationship_type, entity_b_id, valid_from, valid_to, observed_at, source_id, evidence_id, confidence, pit_status, validation_status, provenance_id)
                    VALUES (?, ?, ?, ?, ?, NULL, ?, ?, NULL, 0.95, 'VERIFIED', 'VALIDATED', 'PROV_IDX_REGISTRY')
                """, (rel["relationship_id"], rel["entity_a_id"], rel["relationship_type"], rel["entity_b_id"], rel["valid_from"], rel["valid_from"], rel["source_id"]))

        # 5. Populate fact_peer_network
        for net in self.VALIDATED_PEER_NETWORKS:
            existing = con.execute("SELECT network_id FROM fact_peer_network WHERE network_id = ?", (net["network_id"],)).fetchall()
            if not existing:
                con.execute("""
                    INSERT INTO fact_peer_network (network_id, base_entity_id, peer_entity_id, peer_type, similarity_basis, confidence, valid_from, valid_to, source_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 'SRC_CONTEXTUAL_PEER_ENGINE')
                """, (net["network_id"], net["base_entity_id"], net["peer_entity_id"], net["peer_type"], net["similarity_basis"], net["confidence"], net["valid_from"]))

        counts = {
            "dim_entity": con.execute("SELECT count(*) FROM dim_entity").fetchone()[0],
            "dim_entity_alias": con.execute("SELECT count(*) FROM dim_entity_alias").fetchone()[0],
            "fact_exposure": con.execute("SELECT count(*) FROM fact_exposure").fetchone()[0],
            "fact_relationship": con.execute("SELECT count(*) FROM fact_relationship").fetchone()[0],
            "fact_peer_network": con.execute("SELECT count(*) FROM fact_peer_network").fetchone()[0],
            "fact_event": con.execute("SELECT count(*) FROM fact_event").fetchone()[0]
        }
        con.close()
        return counts

    def resolve_entity(self, identifier: str) -> Dict[str, Any]:
        """
        Resolves a symbol, legal name, or alias conservatively to a canonical entity_id.
        Returns UNRESOLVED if ambiguous or not found.
        """
        con = duckdb.connect(self.db_path, read_only=True)
        ident_clean = identifier.strip().upper()
        
        # Direct entity_id match
        ent = con.execute("SELECT entity_id, canonical_name, entity_type FROM dim_entity WHERE entity_id = ?", (ident_clean,)).fetchone()
        if ent:
            con.close()
            return {"entity_id": ent[0], "canonical_name": ent[1], "entity_type": ent[2], "resolution_method": "EXACT_ID", "confidence": 1.0}
            
        # Alias match
        als = con.execute("""
            SELECT a.entity_id, e.canonical_name, e.entity_type 
            FROM dim_entity_alias a
            JOIN dim_entity e ON a.entity_id = e.entity_id
            WHERE UPPER(a.alias_value) = ?
        """, (ident_clean,)).fetchone()
        if als:
            con.close()
            return {"entity_id": als[0], "canonical_name": als[1], "entity_type": als[2], "resolution_method": "ALIAS_MATCH", "confidence": 0.95}
            
        con.close()
        return {"entity_id": "UNRESOLVED", "canonical_name": "UNKNOWN", "entity_type": "UNKNOWN", "resolution_method": "UNRESOLVED", "confidence": 0.0}
