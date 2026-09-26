import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.attribution_schemas import (
    HistoricalCandidateAttribution,
    EvidenceCoverageSummary,
    PeerReactionSummary,
    AttributionComponents,
    SpecificityStatus,
    RedTeamStatus,
    RedTeamCheckResult,
    CausalityLevel,
    CoverageState,
    AttributionState
)

ENTITY_MAP = {
    "ADRO": "ENT_ADRO",
    "ANTM": "ENT_ANTM",
    "ASII": "ENT_ASII",
    "BBCA": "ENT_BBCA",
    "BBNI": "ENT_BBNI",
    "BBRI": "ENT_BBRI",
    "BMRI": "ENT_BMRI",
    "INCO": "ENT_INCO",
    "ITMG": "ENT_ITMG",
    "PTBA": "ENT_PTBA",
    "TLKM": "ENT_TLKM",
    "UNTR": "ENT_UNTR"
}

CONTEXTUAL_PEERS = {
    "BBCA": ["BBNI", "BBRI", "BMRI"],
    "BBNI": ["BBCA", "BBRI", "BMRI"],
    "BBRI": ["BBCA", "BBNI", "BMRI"],
    "BMRI": ["BBCA", "BBNI", "BBRI"],
    "ADRO": ["ITMG", "PTBA"],
    "ITMG": ["ADRO", "PTBA"],
    "PTBA": ["ADRO", "ITMG"],
    "ANTM": ["INCO"],
    "INCO": ["ANTM"],
    "ASII": ["UNTR"],
    "UNTR": ["ASII"],
    "TLKM": []  # Solitary telecom in 12-pilot universe
}

class CandidateAttributionEngine:
    """
    Deterministic Historical Candidate Attribution & Intelligence Coverage Engine for Agent 2.
    Evaluates historical candidates against DuckDB PIT evidence, contextual peer reactions,
    and 4-dimension Red Team adversarial checks without LLM dependency.
    """
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path
        self._con = None
        
    def _get_connection(self):
        return duckdb.connect(self.db_path, read_only=True)

    def evaluate_candidate(
        self,
        candidate_row: Dict[str, Any],
        day_universe_rows: List[Dict[str, Any]],
        pit_mode: str = "PUBLIC_PIT"
    ) -> HistoricalCandidateAttribution:
        """
        Evaluates a single historical candidate at decision timestamp T.
        Strictly decouples SPECIFICITY (observation) from ATTRIBUTION (evidence-based).
        """
        symbol = candidate_row["symbol"]
        ts_str = candidate_row["date"]
        entity_id = ENTITY_MAP.get(symbol)
        
        # 1. Base Identifiers
        candidate_id = f"CAND_{symbol}_{ts_str[:10]}"
        state = candidate_row.get("signal_state", "UNKNOWN")
        score = float(candidate_row.get("quant_score", 0.0) or 0.0)
        day_return = float(candidate_row.get("ret_c_prev_to_close", 0.0) or 0.0)
        
        # 2. Database PIT Queries
        con = self._get_connection()
        time_field = "published_at" if pit_mode == "PUBLIC_PIT" else "information_available_at"
        
        # Valid events at T
        event_query = f"""
            SELECT event_id, event_type, event_subtype, published_at, information_available_at, 
                   supersedes_event_id, contradicts_event_id, raw_reference
            FROM fact_event
            WHERE entity_id = ?
              AND {time_field} <= ?
            ORDER BY {time_field} DESC
        """
        valid_event_rows = con.execute(event_query, (entity_id, ts_str)).fetchall()
        
        # Future events (excluded at T)
        future_event_query = f"""
            SELECT count(*)
            FROM fact_event
            WHERE entity_id = ?
              AND {time_field} > ?
        """
        future_count = con.execute(future_event_query, (entity_id, ts_str)).fetchone()[0]
        
        # Entity metadata & status
        ent_rows = con.execute("SELECT entity_id, status FROM dim_entity WHERE entity_id = ?", (entity_id,)).fetchall()
        entity_status = CoverageState.AVAILABLE if ent_rows else CoverageState.NOT_AVAILABLE
        
        # Relationships valid at T
        rel_query = """
            SELECT count(*)
            FROM fact_relationship
            WHERE (entity_a_id = ? OR entity_b_id = ?)
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        rel_count = con.execute(rel_query, (entity_id, entity_id, ts_str, ts_str)).fetchone()[0]
        relationship_status = CoverageState.AVAILABLE if rel_count > 0 else CoverageState.NOT_AVAILABLE
        
        # Exposures valid at T
        exp_query = """
            SELECT count(*)
            FROM fact_exposure
            WHERE entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        exp_count = con.execute(exp_query, (entity_id, ts_str, ts_str)).fetchone()[0]
        exposure_status = CoverageState.AVAILABLE if exp_count > 0 else CoverageState.NOT_AVAILABLE
        
        # Peer network valid at T
        peer_query = """
            SELECT count(*)
            FROM fact_peer_network
            WHERE base_entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """
        peer_count_db = con.execute(peer_query, (entity_id, ts_str, ts_str)).fetchone()[0]
        peer_status_db = CoverageState.AVAILABLE if peer_count_db > 0 else CoverageState.PARTIAL
        
        con.close()
        
        # 3. Evidence Coverage Audit (18 dimensions)
        coverage = EvidenceCoverageSummary()
        
        # Contemporary events within relevance window of decision date T
        try:
            t_date = pd.to_datetime(ts_str)
            if hasattr(t_date, 'tz') and t_date.tz is not None:
                t_date = t_date.tz_localize(None) if hasattr(t_date, 'tz_localize') else t_date.tz_convert(None)
        except Exception:
            t_date = pd.to_datetime(ts_str[:10])
            
        def is_contemporary(event_time, max_days):
            if event_time is None:
                return False
            try:
                ev_dt = pd.to_datetime(event_time)
                if hasattr(ev_dt, 'tz') and ev_dt.tz is not None:
                    ev_dt = ev_dt.tz_localize(None) if hasattr(ev_dt, 'tz_localize') else ev_dt.tz_convert(None)
                diff_days = (t_date - ev_dt).total_seconds() / 86400.0
                return -0.5 <= diff_days <= float(max_days)
            except Exception:
                return False

        contemp_news_events = [r for r in valid_event_rows if r[1] == "NEWS_INFORMATION" and is_contemporary(r[3], 3.0)]
        contemp_corp_events = [r for r in valid_event_rows if r[1] == "CORPORATE_ACTION" and is_contemporary(r[3], 5.0)]
        
        coverage.news = CoverageState.AVAILABLE if contemp_news_events else CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.corporate_action = CoverageState.AVAILABLE if contemp_corp_events else CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.relationship = relationship_status
        coverage.exposure = exposure_status
        coverage.peer_information = CoverageState.AVAILABLE
        coverage.flow = CoverageState.AVAILABLE if candidate_row.get("rel_vol") is not None else CoverageState.NOT_AVAILABLE
        coverage.market_structure = CoverageState.AVAILABLE
        
        # Missing tables / dimensions in dataset
        coverage.fundamental = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.macro = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.commodity = CoverageState.PARTIAL if exp_count > 0 else CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.fx = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.monetary = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.policy = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.politics = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.geopolitics = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.ownership = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.sentiment = CoverageState.NO_EVIDENCE_IN_DATASET
        coverage.event_calendar = CoverageState.PARTIAL if contemp_corp_events or valid_event_rows else CoverageState.NO_EVIDENCE_IN_DATASET
        
        event_status = CoverageState.AVAILABLE if valid_event_rows else CoverageState.NO_EVIDENCE_IN_DATASET
        
        # Contradictions in event graph
        contradictory_count = sum(1 for r in valid_event_rows if r[6] is not None)
        unresolved_count = sum(1 for r in valid_event_rows if r[5] is None and r[6] is None and r[1] == "NEWS_INFORMATION")
        
        # 4. Contextual Peer & Differential Reaction Calculation on day T (SPECIFICITY OBSERVATION)
        day_map = {row["symbol"]: float(row.get("ret_c_prev_to_close", 0.0) or 0.0) for row in day_universe_rows}
        peer_symbols = CONTEXTUAL_PEERS.get(symbol, [])
        peer_returns = [day_map[p] for p in peer_symbols if p in day_map]
        
        market_returns = [v for k, v in day_map.items() if k != symbol]
        market_mean = float(np.mean(market_returns)) if market_returns else 0.0
        
        peer_mean = float(np.mean(peer_returns)) if peer_returns else market_mean
        peer_median = float(np.median(peer_returns)) if peer_returns else market_mean
        diff_return = day_return - peer_mean
        
        # Specificity Classification (Pure Price Divergence Observation)
        if len(peer_returns) > 0:
            if abs(diff_return) >= 0.025:  # > 2.5% differential vs contextual peers
                specificity = SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE
            elif abs(peer_mean) >= 0.015 and np.sign(day_return) == np.sign(peer_mean):
                specificity = SpecificityStatus.SECTOR_WIDE
            elif abs(market_mean) >= 0.015 and np.sign(day_return) == np.sign(market_mean):
                specificity = SpecificityStatus.MARKET_WIDE
            else:
                specificity = SpecificityStatus.FACTOR_WIDE
        else:
            if abs(day_return - market_mean) >= 0.025:
                specificity = SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE
            elif abs(market_mean) >= 0.015:
                specificity = SpecificityStatus.MARKET_WIDE
            else:
                specificity = SpecificityStatus.UNKNOWN
                
        peer_summary = PeerReactionSummary(
            peer_group_type="CONTEXTUAL_SECTOR",
            peers=peer_symbols,
            peer_count=len(peer_returns),
            target_day_return=day_return,
            peer_mean_return=peer_mean,
            peer_median_return=peer_median,
            differential_return=diff_return,
            specificity_status=specificity
        )
        
        # 5. Attribution Decomposition (11 components - Evidence-Based)
        attrib = AttributionComponents()
        
        # Market Component
        if abs(market_mean) >= 0.008 and np.sign(day_return) == np.sign(market_mean):
            attrib.market_component = AttributionState.SUPPORTED
        elif abs(market_mean) >= 0.004:
            attrib.market_component = AttributionState.CANDIDATE
        else:
            attrib.market_component = AttributionState.WEAK
            
        # Sector Component
        if len(peer_returns) > 0 and abs(peer_mean) >= 0.008 and np.sign(day_return) == np.sign(peer_mean):
            attrib.sector_component = AttributionState.SUPPORTED
        elif len(peer_returns) > 0:
            attrib.sector_component = AttributionState.CANDIDATE
        else:
            attrib.sector_component = AttributionState.NOT_AVAILABLE
            
        # Factor Component (Momentum / Beta)
        if score >= 80:
            attrib.factor_component = AttributionState.SUPPORTED
        else:
            attrib.factor_component = AttributionState.CANDIDATE
            
        # News Component
        if contemp_news_events:
            attrib.news_component = AttributionState.SUPPORTED
        else:
            attrib.news_component = AttributionState.NOT_AVAILABLE
            
        # Corporate Action / Ownership Component
        if contemp_corp_events:
            attrib.ownership_component = AttributionState.CANDIDATE
        else:
            attrib.ownership_component = AttributionState.NOT_AVAILABLE
            
        # Flow Component
        rel_vol = candidate_row.get("rel_vol")
        if rel_vol is not None and rel_vol > 1.5:
            attrib.flow_component = AttributionState.SUPPORTED
        elif rel_vol is not None and rel_vol > 1.0:
            attrib.flow_component = AttributionState.CANDIDATE
        else:
            attrib.flow_component = AttributionState.WEAK
            
        # Commodity Component
        if exp_count > 0:
            attrib.commodity_component = AttributionState.CANDIDATE
        else:
            attrib.commodity_component = AttributionState.NOT_AVAILABLE
            
        # Company Specific Component (HARDENED: requires contemporary factual company evidence)
        if contemp_news_events:
            attrib.company_specific_component = AttributionState.SUPPORTED
        elif contemp_corp_events:
            attrib.company_specific_component = AttributionState.CANDIDATE
        else:
            attrib.company_specific_component = AttributionState.NOT_AVAILABLE
            
        attrib.relationship_component = AttributionState.CANDIDATE if rel_count > 0 else AttributionState.NOT_AVAILABLE
        attrib.macro_component = AttributionState.NOT_AVAILABLE
        attrib.unknown_component = AttributionState.SUPPORTED
        
        # Primary attribution selection (HARDENED: Decoupled from specificity)
        alt_attributions = []
        
        if contemp_news_events:
            primary_attrib = "NEWS_COMPONENT"
            alt_attributions.extend(["FLOW_COMPONENT", "MARKET_COMPONENT", "UNKNOWN_COMPONENT"])
        elif contemp_corp_events and abs(day_return) >= 0.02:
            primary_attrib = "OWNERSHIP_COMPONENT"
            alt_attributions.extend(["MARKET_COMPONENT", "FLOW_COMPONENT", "UNKNOWN_COMPONENT"])
        elif specificity == SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE:
            # Target diverged from peers.
            # If broad market had a massive rally (>=2.5%), market component may confound
            if abs(market_mean) >= 0.025 and np.sign(day_return) == np.sign(market_mean):
                primary_attrib = "MARKET_COMPONENT"
                alt_attributions.extend(["FLOW_COMPONENT", "UNKNOWN_COMPONENT"])
            elif attrib.flow_component == AttributionState.SUPPORTED and abs(day_return) >= 0.03:
                primary_attrib = "FLOW_COMPONENT"
                alt_attributions.extend(["FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
            else:
                # Without factual company evidence, attribution MUST be UNKNOWN_COMPONENT
                primary_attrib = "UNKNOWN_COMPONENT"
                alt_attributions.extend(["FLOW_COMPONENT", "FACTOR_COMPONENT", "MARKET_COMPONENT"])
        elif specificity == SpecificityStatus.SECTOR_WIDE and attrib.sector_component == AttributionState.SUPPORTED:
            primary_attrib = "SECTOR_COMPONENT"
            alt_attributions.extend(["MARKET_COMPONENT", "FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
        elif specificity == SpecificityStatus.MARKET_WIDE and attrib.market_component == AttributionState.SUPPORTED:
            primary_attrib = "MARKET_COMPONENT"
            alt_attributions.extend(["SECTOR_COMPONENT", "FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
        elif attrib.market_component == AttributionState.SUPPORTED:
            primary_attrib = "MARKET_COMPONENT"
            alt_attributions.extend(["SECTOR_COMPONENT", "FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
        elif attrib.sector_component == AttributionState.SUPPORTED:
            primary_attrib = "SECTOR_COMPONENT"
            alt_attributions.extend(["MARKET_COMPONENT", "FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
        elif attrib.flow_component == AttributionState.SUPPORTED and abs(day_return) >= 0.02:
            primary_attrib = "FLOW_COMPONENT"
            alt_attributions.extend(["FACTOR_COMPONENT", "UNKNOWN_COMPONENT"])
        else:
            # When no independent evidence explains the move, attribution MUST be UNKNOWN_COMPONENT
            primary_attrib = "UNKNOWN_COMPONENT"
            alt_attributions.extend(["MARKET_COMPONENT", "FACTOR_COMPONENT"])
                
        # 6. Causality Level Assignment
        if primary_attrib == "NEWS_COMPONENT" and contemp_news_events:
            causality = CausalityLevel.ECONOMICALLY_PLAUSIBLE
        elif primary_attrib in ["MARKET_COMPONENT", "SECTOR_COMPONENT", "FLOW_COMPONENT", "OWNERSHIP_COMPONENT"]:
            causality = CausalityLevel.CORRELATED
        else:
            causality = CausalityLevel.OBSERVED
            
        # 7. Red Team / 4-Dimension Adversarial Audit
        red_reasons = []
        contradictions = []
        unknowns = []
        
        # Check 1: Time-Series Leakage
        time_leakage = "PASS"
        for ev in valid_event_rows:
            ev_pub = ev[3]
            ev_avail = ev[4]
            if ev_pub and str(ev_pub) > ts_str:
                time_leakage = "FAIL"
                red_reasons.append(f"Time leakage: event published at {ev_pub} > decision {ts_str}")
            if ev_avail and str(ev_avail) > ts_str and pit_mode == "SYSTEM_PIT":
                time_leakage = "FAIL"
                red_reasons.append(f"Time leakage: event available at {ev_avail} > decision {ts_str}")
                
        # Check 2: Evidence / Hallucination Check
        evidence_hallucination = "PASS"
        if primary_attrib == "NEWS_COMPONENT" and not contemp_news_events:
            evidence_hallucination = "FAIL"
            red_reasons.append("Hallucination: attributed to NEWS_COMPONENT without contemporary PIT news records.")
        elif primary_attrib == "COMPANY_SPECIFIC_COMPONENT" and not contemp_news_events and not contemp_corp_events:
            evidence_hallucination = "FAIL"
            red_reasons.append("Hallucination: attributed to COMPANY_SPECIFIC_COMPONENT without contemporary PIT evidence.")
        elif primary_attrib == "OWNERSHIP_COMPONENT" and not contemp_corp_events:
            evidence_hallucination = "FAIL"
            red_reasons.append("Hallucination: attributed to OWNERSHIP_COMPONENT without contemporary corporate action records.")
        elif primary_attrib in ["MARKET_COMPONENT", "SECTOR_COMPONENT", "FLOW_COMPONENT"]:
            evidence_hallucination = "WEAK"
            red_reasons.append("Attribution relies on market/flow proxy due to absent fundamental disclosure.")
        elif primary_attrib == "UNKNOWN_COMPONENT":
            evidence_hallucination = "PASS"  # Truthfully stating lack of evidence is a PASS
            
        # Check 3: Logic Consistency Check
        logic_consistency = "PASS"
        if primary_attrib == "MARKET_COMPONENT" and abs(market_mean) < 0.002:
            logic_consistency = "FAIL"
            contradictions.append("Attributed to market movement but market mean was flat (<0.2%).")
            red_reasons.append("Logic contradiction: market flat while attributed to market.")
        if primary_attrib == "SECTOR_COMPONENT" and len(peer_returns) > 0 and peer_mean * day_return < 0:
            logic_consistency = "FAIL"
            contradictions.append("Attributed to sector momentum but peer mean moved in opposite direction.")
            red_reasons.append("Logic contradiction: peer mean moved opposite to target.")
        if specificity == SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE and abs(diff_return) < 0.02:
            logic_consistency = "FAIL"
            red_reasons.append("Logic contradiction: specificity marked COMPANY_SPECIFIC without sufficient divergence.")
            
        # Check 4: Alternative Explanation / Confounding Check
        alternative_explanation = "PASS"
        if specificity == SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE and abs(market_mean) >= 0.03:
            alternative_explanation = "WEAK"
            red_reasons.append("Confounding: Strong broad market rally (>3%) may confound company divergence.")
        elif primary_attrib == "UNKNOWN_COMPONENT":
            alternative_explanation = "INSUFFICIENT_EVIDENCE"
            unknowns.append("No contemporary PIT news, fundamentals, or ownership records available in dataset.")
        elif contradictions:
            alternative_explanation = "CONTRADICTED"
            
        if not contemp_news_events:
            unknowns.append("No contemporary PIT news available in dataset for this date.")
        if coverage.fundamental == CoverageState.NO_EVIDENCE_IN_DATASET:
            unknowns.append("Fundamental/earnings data not present in dataset.")
            
        # Overall Red Team Status Aggregation
        if time_leakage == "FAIL" or evidence_hallucination == "FAIL" or logic_consistency == "FAIL":
            overall_red_team = RedTeamStatus.CONTRADICTED
        elif alternative_explanation == "CONTRADICTED":
            overall_red_team = RedTeamStatus.CONTRADICTED
        elif alternative_explanation == "INSUFFICIENT_EVIDENCE" or evidence_hallucination == "WEAK":
            overall_red_team = RedTeamStatus.WEAK
        else:
            overall_red_team = RedTeamStatus.PASS
            
        red_team_audit = RedTeamCheckResult(
            time_leakage=time_leakage,
            evidence_hallucination=evidence_hallucination,
            logic_consistency=logic_consistency,
            alternative_explanation=alternative_explanation,
            overall_status=overall_red_team,
            reasons=red_reasons
        )
        
        # 8. Forward Outcomes (OUTCOME_AFTER_T strictly separated from KNOWABLE_AT_T)
        fwd_h1 = candidate_row.get("H1")
        fwd_h5 = candidate_row.get("H5")
        fwd_h20 = candidate_row.get("H20")
        
        return HistoricalCandidateAttribution(
            candidate_id=candidate_id,
            symbol=symbol,
            signal_timestamp=ts_str,
            official_signal_state=state,
            quant_score=score,
            signal_day_return=day_return,
            pit_mode=pit_mode,
            evidence_count=len(valid_event_rows) + rel_count + exp_count,
            pit_valid_evidence_count=len(valid_event_rows),
            future_evidence_excluded_count=future_count,
            contradictory_evidence_count=contradictory_count,
            unresolved_evidence_count=unresolved_count,
            evidence_coverage=coverage,
            entity_id=entity_id,
            entity_status=entity_status,
            relationship_status=relationship_status,
            exposure_status=exposure_status,
            peer_status=peer_status_db,
            event_status=event_status,
            peer_reaction=peer_summary,
            specificity_status=specificity,
            attribution_components=attrib,
            primary_attribution=primary_attrib,
            alternative_attributions=alt_attributions,
            causality_level=causality,
            red_team_status=overall_red_team,
            red_team_audit=red_team_audit,
            contradictions=contradictions,
            unknowns=unknowns,
            forward_h1_return=float(fwd_h1) if fwd_h1 is not None and not np.isnan(fwd_h1) else None,
            forward_h5_return=float(fwd_h5) if fwd_h5 is not None and not np.isnan(fwd_h5) else None,
            forward_h20_return=float(fwd_h20) if fwd_h20 is not None and not np.isnan(fwd_h20) else None
        )
