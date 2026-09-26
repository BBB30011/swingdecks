from typing import Dict, Any, List
from pydantic import BaseModel
from core.research import ResearchPacket, ResearchCompletenessEngine
from core.research_contradiction import ContradictionEngine
from core.opportunity_ranker import WhyNowEngine
from core.timing_engine import TriggerProximity

class RedTeamResult(BaseModel):
    decision: str  # PASS, REWORK, BLOCK
    reasons: List[str]
    why_buy: str = "UNKNOWN"
    why_not_buy: str = "UNKNOWN"
    why_now: str = "UNKNOWN"
    strongest_bear_case: str = "UNKNOWN"
    what_breaks_thesis: str = "UNKNOWN"
    missing_evidence: str = "UNKNOWN"
    contradictions: str = "UNKNOWN"
    fragile_assumptions: str = "UNKNOWN"

class RedTeamAnalyzer:
    @staticmethod
    def analyze(packet: ResearchPacket) -> RedTeamResult:
        reasons = []
        completeness = ResearchCompletenessEngine.evaluate(packet)
        contradictions = ContradictionEngine.detect(packet)
        
        has_speculation = any(
            ev.claim_class == "SPECULATION" 
            for cat in [packet.fundamental, packet.macro, packet.policy, packet.news, packet.catalysts, packet.risks]
            for ev in cat
        )
        
        has_critical_contradiction = any(c["severity"] == "HIGH" for c in contradictions)
        
        decision = "PASS"
        
        if completeness == "INSUFFICIENT":
            decision = "BLOCK"
            reasons.append("Critical evidence missing.")
            
        if has_critical_contradiction:
            decision = "BLOCK"
            reasons.append("Major contradiction unresolved.")
            
        if has_speculation and decision != "BLOCK":
            decision = "BLOCK"
            reasons.append("Thesis depends on speculation.")
            
        if decision == "PASS" and completeness in ["WEAK", "PARTIAL"]:
            decision = "REWORK"
            reasons.append("Evidence incomplete but thesis is investigable.")
            
        if decision == "PASS" and contradictions and not has_critical_contradiction:
            decision = "REWORK"
            reasons.append("Manageable contradictions need review.")
            
        # Generate why_now using multi-factor WhyNowEngine
        active_catalysts = [c for c in packet.catalysts if getattr(c, "decay_state", "UNKNOWN") == "ACTIVE"]
        first_cat = active_catalysts[0] if active_catalysts else None
        volume_expanding = any(
            f.get("factor_name") == "volume" and f.get("state") == "POSITIVE"
            for f in packet.quant_context.get("factors", {}).values()
            if isinstance(f, dict)
        )
        why_now = WhyNowEngine.build(
            catalyst_state="ACTIVE" if first_cat else "UNKNOWN",
            catalyst_event_type=getattr(first_cat, "event_type", "") if first_cat else "",
            catalyst_materiality=getattr(first_cat, "materiality", "UNKNOWN") if first_cat else "UNKNOWN",
            catalyst_decay=getattr(first_cat, "decay_state", "UNKNOWN") if first_cat else "UNKNOWN",
            volume_expanding=volume_expanding,
            market_regime=packet.quant_context.get("market_regime", "UNKNOWN"),
        )

        return RedTeamResult(
            decision=decision,
            reasons=reasons,
            why_now=why_now,
            missing_evidence=f"Completeness is {completeness}",
            contradictions=str(contradictions)
        )
