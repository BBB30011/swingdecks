import json
from typing import Dict, Any, List, Optional
from core.decision_trace import AuditedDecisionTrace, DecisionTraceAPI

class MarketNarrativeEngine:
    """
    Transforms structured DecisionTrace into a Human-Readable Market Narrative.
    Strictly adheres to Language Firewall: OBSERVED EVIDENCE vs AGENT INTERPRETATION.
    Does NOT infer causality unless explicitly recorded in canonical sources.
    """
    def __init__(self, trace_api: DecisionTraceAPI):
        self.trace_api = trace_api

    def build_narrative(self, symbol: str, decision_timestamp: Optional[str] = None) -> str:
        timeline = self.trace_api.get_timeline(symbol)
        if not timeline:
            return f"==================================================\n{symbol} — MARKET NARRATIVE & DECISION TRACE\n==================================================\n\nNO_RECORDED_EVENTS"

        if not decision_timestamp:
            decision_timestamp = timeline[-1]["timestamp"]

        trace = self.trace_api.build_trace(symbol, decision_timestamp)
        post_outcomes = self.trace_api.get_post_decision_outcomes(symbol, decision_timestamp)
        
        # Build sections
        header = self._render_header(trace)
        s1_changed = self._render_what_changed(trace)
        s2_why = self._render_why_happening(trace)
        s3_contradicts = self._render_what_contradicts(trace)
        s4_decision = self._render_agent3_decision(trace)
        s5_thesis = self._render_thesis_changes(symbol, decision_timestamp)
        s6_afterward = self._render_what_happened_afterward(post_outcomes)
        s7_current = self._render_current_state(symbol)
        s8_invalidation = self._render_invalidation(trace)
        s9_timeline = self._render_full_timeline(timeline)
        footer = self._render_footer(trace)

        narrative = f"""==================================================
{symbol} — MARKET NARRATIVE & DECISION TRACE
==================================================

{header}

{s1_changed}

{s2_why}

{s3_contradicts}

{s4_decision}

{s5_thesis}

{s6_afterward}

{s7_current}

{s8_invalidation}

{s9_timeline}

{footer}
=================================================="""
        return narrative

    def _render_header(self, trace: AuditedDecisionTrace) -> str:
        current_decision = trace.agent3_decision.get("action", "UNKNOWN")
        risk = trace.agent3_decision.get("risk_state", "UNKNOWN")
        thesis_state = trace.agent3_decision.get("evidence_state", "UNKNOWN")
        
        # Extract regime from agent 1 if available
        regime = trace.agent1_observation.get("market_regime", "UNKNOWN")
        
        # Determine position state (simplified, usually checked against portfolio)
        position = "NONE" if current_decision in ["AVOID", "WAIT"] else "UNKNOWN"
        
        return f"""CURRENT STATE

Decision       : {current_decision}
Risk           : {risk}
Thesis         : {thesis_state}
Position       : {position}
Regime         : {regime}"""

    def _render_what_changed(self, trace: AuditedDecisionTrace) -> str:
        lines = []
        a1_delta = trace.market_delta.get("agent1_delta")
        
        if not trace.agent1_observation:
            return "WHAT CHANGED?\n\nAgent 1 observation NOT_AVAILABLE."

        if a1_delta == "UPDATED" or a1_delta == "NEW":
            lines.append("• Market conditions changed.")
            # We don't infer price direction, we just say what agent 1 detected
            lines.append(f"• Agent 1 detected market change classified as: {a1_delta}.")
        elif a1_delta == "UNCHANGED":
            lines.append("• No significant market condition change recorded.")
        else:
            lines.append(f"• Agent 1 reported market delta: {a1_delta if a1_delta else 'UNKNOWN'}.")
            
        status = trace.agent1_observation.get("status")
        if status:
            lines.append(f"• Agent 1 scanner status: {status}.")

        return "WHAT CHANGED?\n\n" + "\n".join(lines)

    def _render_why_happening(self, trace: AuditedDecisionTrace) -> str:
        if not trace.agent2_intelligence:
            return "WHY COULD IT BE HAPPENING?\n\nOBSERVED:\nNOT_AVAILABLE\n\nAGENT 2 INTERPRETATION:\nNOT_AVAILABLE\n\nEVIDENCE:\nNOT_AVAILABLE"

        lines = ["WHY COULD IT BE HAPPENING?\n"]
        
        lines.append("OBSERVED:")
        cats = trace.agent2_intelligence.get("catalysts", [])
        if cats:
            lines.append(f"Recorded catalysts: {', '.join(cats)}")
        else:
            lines.append("No catalysts recorded.")
            
        a2_delta = trace.market_delta.get("agent2_delta", "UNKNOWN")
        lines.append(f"\nAGENT 2 INTERPRETATION:\nAgent 2 categorized intelligence delta as: {a2_delta}.")
        
        lines.append("\nEVIDENCE:")
        refs = [r for r in trace.evidence_refs if r]
        if refs:
            lines.append(f"[{', '.join(refs)}]")
        else:
            lines.append("NOT_AVAILABLE")
            
        return "\n".join(lines)

    def _render_what_contradicts(self, trace: AuditedDecisionTrace) -> str:
        if not trace.red_team_assessment:
            return "WHAT CONTRADICTS THE VIEW?\n\nNOT_AVAILABLE\n\nRED TEAM:\nNOT_AVAILABLE"

        lines = ["WHAT CONTRADICTS THE VIEW?\n"]
        contra_count = trace.red_team_assessment.get("contradiction_count", 0)
        lines.append(f"Recorded contradictions: {contra_count}.")
        
        rt_delta = trace.red_team_assessment.get("red_team_delta_status", "UNKNOWN")
        rt_dec = trace.red_team_assessment.get("red_team_decision", "UNKNOWN")
        
        lines.append("\nRED TEAM:")
        lines.append(f"Red Team categorized contradiction delta as: {rt_delta}.")
        lines.append(f"Red Team decision: {rt_dec}.")
        
        return "\n".join(lines)

    def _render_agent3_decision(self, trace: AuditedDecisionTrace) -> str:
        if not trace.agent3_decision:
            return "WHAT DID AGENT 3 DECIDE?\n\nNOT_AVAILABLE"

        curr_decision = trace.agent3_decision.get("action", "UNKNOWN")
        risk = trace.agent3_decision.get("risk_state", "UNKNOWN")
        reason = trace.agent3_decision.get("reason", "NOT_RECORDED")
        
        # Compute previous decision from trace api context if possible, but trace.decision_change holds the delta.
        # Since trace only stores current, we derive previous from change type loosely for text
        prev_text = "UNKNOWN"
        if trace.decision_change == "NEW_ACTION":
            prev_text = "NONE"
        elif trace.decision_change == "NO_CHANGE":
            prev_text = curr_decision
        elif trace.decision_change in ["UPGRADE", "DOWNGRADE", "ACTION_CHANGED"]:
            prev_text = "[Derived Change]"
            
        return f"""WHAT DID AGENT 3 DECIDE?

Previous:
{prev_text}

Current:
{curr_decision}

Decision Change:
{trace.decision_change}

Reason:
Agent 3 recorded reason: "{reason}"

Risk:
{risk}"""

    def _render_thesis_changes(self, symbol: str, decision_timestamp: str) -> str:
        changes = self.trace_api.get_thesis_changes(symbol)
        if not changes:
            return "WHAT CHANGED IN THE THESIS?\n\nNOT_RECORDED"
            
        lines = ["WHAT CHANGED IN THE THESIS?\n"]
        for c in changes:
            if c["timestamp"] <= decision_timestamp:
                lines.append(f"• {c['timestamp']}: Red Team Decision = {c['red_team_decision']} (Delta: {c['delta']})")
                
        return "\n".join(lines)

    def _render_what_happened_afterward(self, post_outcomes: Dict[str, Any]) -> str:
        lines = ["WHAT HAPPENED AFTERWARD?\n\nPOST-DECISION OUTCOME\n"]
        events = post_outcomes.get("subsequent_events", [])
        
        if not events:
            lines.append("No subsequent events recorded.")
        else:
            for e in events:
                lines.append(f"• {e['timestamp']}: [{e['stage']}] {e['event_type']}")
                
        lines.append("\nThis section MUST NOT influence historical decision reasoning.")
        return "\n".join(lines)

    def _render_current_state(self, symbol: str) -> str:
        current = self.trace_api.get_current_state(symbol)
        if not current:
            return "CURRENT STATE\n\nNOT_AVAILABLE"
            
        action = current.get("agent3_decision", {}).get("action", "UNKNOWN")
        ts = current.get("decision_timestamp", "UNKNOWN")
        return f"CURRENT STATE\n\nLatest canonical decision timestamp: {ts}\nAction: {action}"

    def _render_invalidation(self, trace: AuditedDecisionTrace) -> str:
        # Check if agent3 recorded invalidating conditions
        inv = "NOT_RECORDED"
        if trace.agent3_decision:
            thesis = trace.agent3_decision.get("thesis", {})
            if isinstance(thesis, dict):
                inval_conds = thesis.get("invalidating_conditions", [])
                if inval_conds:
                    inv = ", ".join(inval_conds)
            
        return f"""WHAT WOULD INVALIDATE THIS?

Canonical invalidation condition:
{inv}"""

    def _render_full_timeline(self, timeline: List[Dict[str, Any]]) -> str:
        lines = ["FULL TIMELINE\n"]
        for t in timeline:
            lines.append(t["timestamp"])
            events = t["events"]
            for e in events:
                lines.append(f" ├─ {e['stage'].replace('AGENT_1_', '').replace('AGENT_2_', '').replace('AGENT_3_', '')} - {e['event_type']}")
            lines.append(" │")
            
        lines.append("CURRENT")
        return "\n".join(lines)

    def _render_footer(self, trace: AuditedDecisionTrace) -> str:
        return f"""PIT:
{trace.pit_status}

SOURCE COMPLETENESS:
{trace.source_completeness}

TRACE HASH:
{trace.get_hash()}"""
