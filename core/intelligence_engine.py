import duckdb
from typing import List, Dict, Any

class IntelligenceEngine:
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path
        
    def _execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        con = duckdb.connect(self.db_path, read_only=True)
        result = con.execute(query, params).fetchall()
        con.close()
        return result
    def get_historical_information_state(self, entity_id: str, decision_timestamp: str, pit_mode: str = "PUBLIC_PIT") -> List[Dict[str, Any]]:
        """
        Retrieves all valid events for an entity under the selected PIT mode.
        """
        time_field = "published_at" if pit_mode == "PUBLIC_PIT" else "information_available_at"
        
        query = f"""
            SELECT event_id, event_type, {time_field}, raw_reference, information_state
            FROM fact_event
            WHERE entity_id = ?
              AND {time_field} <= ?
              AND event_timestamp <= ?
            ORDER BY {time_field} DESC
        """
        rows = self._execute_query(query, (entity_id, decision_timestamp, decision_timestamp))
        
        return [
            {
                "event_id": r[0],
                "event_type": r[1],
                "time": r[2].isoformat() if r[2] else None,
                "description": r[3],
                "information_state": r[4]
            }
            for r in rows
        ]

    def get_entity_context(self, entity_id: str, decision_timestamp: str) -> Dict[str, Any]:
        """
        Retrieves entity aliases and direct relationships valid at the decision timestamp.
        """
        alias_query = """
            SELECT alias_type, alias_value
            FROM dim_entity_alias
            WHERE entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        aliases = self._execute_query(alias_query, (entity_id, decision_timestamp, decision_timestamp))
        
        rel_query = """
            SELECT relationship_type, entity_b_id
            FROM fact_relationship
            WHERE entity_a_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        relationships = self._execute_query(rel_query, (entity_id, decision_timestamp, decision_timestamp))
        
        return {
            "aliases": [{"type": r[0], "value": r[1]} for r in aliases],
            "relationships": [{"type": r[0], "target": r[1]} for r in relationships]
        }

    def get_exposures(self, entity_id: str, as_of: str) -> List[Dict[str, Any]]:
        # Demonstrate PIT capability
        query = """
            SELECT e.exposure_type, t.canonical_name, e.exposure_basis, e.direction
            FROM fact_exposure e
            JOIN dim_entity t ON e.target_entity_id = t.entity_id
            WHERE e.entity_id = ?
              AND e.valid_from <= ?
              AND (e.valid_to IS NULL OR e.valid_to > ?)
        """
        rows = self._execute_query(query, (entity_id, as_of, as_of))
        return [{"type": r[0], "target": r[1], "basis": r[2], "direction": r[3]} for r in rows]

    def get_contextual_peers(self, entity_id: str, as_of: str) -> List[str]:
        query = """
            SELECT peer_entity_id 
            FROM fact_peer_network 
            WHERE base_entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        rows = self._execute_query(query, (entity_id, as_of, as_of))
        return [r[0] for r in rows]

    def analyze_event_impact(self, event_id: str, as_of: str) -> Dict[str, Any]:
        """
        Analyzes the market reaction of entities exposed to an event,
        compares them to their peers, and identifies specific beneficiaries.
        """
        
        # 1. Find the target of the event
        rel_query = """
            SELECT entity_b_id 
            FROM fact_relationship 
            WHERE entity_a_id = ? AND relationship_type = 'AFFECTS'
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        rel_rows = self._execute_query(rel_query, (event_id, as_of, as_of))
        if not rel_rows:
            return {"status": "NO_RELATIONSHIP_FOUND"}
            
        affected_target = rel_rows[0][0] # e.g. ENT_COAL
        
        # 2. Find companies exposed to this target
        exp_query = """
            SELECT entity_id 
            FROM fact_exposure 
            WHERE target_entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        exp_rows = self._execute_query(exp_query, (affected_target, as_of, as_of))
        exposed_entities = [r[0] for r in exp_rows]
        
        # 3. Analyze Market Reaction for exposed entities vs their peers
        analysis = []
        for entity in exposed_entities:
            # Get target reaction
            rx_query = """
                SELECT return_pct 
                FROM fact_reaction 
                WHERE event_id = ? AND entity_id = ?
            """
            rx_rows = self._execute_query(rx_query, (event_id, entity))
            if not rx_rows:
                continue
            target_return = rx_rows[0][0]
            
            # Get peers and their reactions
            peers = self.get_contextual_peers(entity, as_of)
            peer_returns = []
            for peer in peers:
                prx_rows = self._execute_query(rx_query, (event_id, peer))
                if prx_rows:
                    peer_returns.append(prx_rows[0][0])
            
            peer_avg = sum(peer_returns) / len(peer_returns) if peer_returns else 0.0
            
            # Differential Logic
            differential = target_return - peer_avg
            
            status = "IN_LINE_WITH_PEERS"
            if abs(differential) > 5.0: # Material threshold
                if differential > 0:
                    status = "ASYMMETRIC_BENEFICIARY_CANDIDATE"
                else:
                    status = "ASYMMETRIC_DETRIMENT_CANDIDATE"
            
            analysis.append({
                "entity": entity,
                "target_reaction": target_return,
                "peer_average_reaction": peer_avg,
                "differential": differential,
                "specificity_status": status
            })
            
        return {
            "status": "ANALYSIS_COMPLETE",
            "event_id": event_id,
            "affected_target": affected_target,
            "results": analysis
        }
