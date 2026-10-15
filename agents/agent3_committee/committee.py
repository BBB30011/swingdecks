from typing import Dict, Any, List
from core.decision import (
    DecisionResult, InvestmentThesis, EvidenceMatrix, EvidenceFactor,
    FactorState, FactorImpact, EvidenceContradiction, ContradictionSeverity,
    OpportunityAssessment, TriggerInfo
)
from core.opportunity_ranker import (
    OpportunityRanker, OpportunityClassifier, WhyNowEngine, AlertUrgencyEngine,
    SignalStrengthEngine, InvalidationEngine
)
from core.timing_engine import (
    TriggerProximityEngine, TimingQualityEngine, EntryWindowEngine, PricedInEngine
)
import datetime

class InvestmentCommittee:
    def __init__(self):
        pass

    def synthesize(self, 
                   job_id: str,
                   symbol: str, 
                   as_of_timestamp: str,
                   quant_data: Dict[str, Any],
                   research_data: Dict[str, Any],
                   risk_evaluation: Dict[str, Any]) -> DecisionResult:
                   
        # 1. Build Evidence Matrix
        factors = {}
        contradictions = []
        
        # Technical Factor
        q_score = quant_data.get("quant_score", 0)
        factors["technical"] = EvidenceFactor(
            factor_name="technical",
            state=FactorState.POSITIVE if q_score > 80 else FactorState.NEUTRAL if q_score > 60 else FactorState.NEGATIVE,
            impact=FactorImpact.HIGH,
            freshness="LIVE",
            reason=f"Quant score {q_score}"
        )
        
        # Flow Factor
        flow_state = research_data.get("flow_state", "UNKNOWN")
        factors["flow"] = EvidenceFactor(
            factor_name="flow",
            state=FactorState(flow_state) if flow_state in [e.value for e in FactorState] else FactorState.UNKNOWN,
            impact=FactorImpact.MEDIUM,
            freshness="LIVE",
            reason=f"Flow state from quant engine is {flow_state}"
        )

        # Mechanism / Graph Intelligence Factor
        mechanisms = research_data.get("mechanisms", [])
        economic_trans = research_data.get("economic_transmission", {})
        price_exp = economic_trans.get("price_expectation") if isinstance(economic_trans, dict) else getattr(economic_trans, "price_expectation", "UNKNOWN")
        
        if mechanisms:
            mech_state = FactorState.POSITIVE if price_exp == "POSITIVE" else (FactorState.NEGATIVE if price_exp == "NEGATIVE" else FactorState.NEUTRAL)
            factors["mechanism"] = EvidenceFactor(
                factor_name="mechanism",
                state=mech_state,
                impact=FactorImpact.HIGH,
                freshness="LIVE",
                reason=f"Economic channel: {economic_trans.get('business_impact', 'unspecified') if isinstance(economic_trans, dict) else getattr(economic_trans, 'business_impact', 'unspecified')}"
            )
        
        # Check Contradictions: Technical vs Flow
        if factors["technical"].state == FactorState.POSITIVE and factors["flow"].state == FactorState.NEGATIVE:
            contradictions.append(EvidenceContradiction(
                topic="Technical vs Flow",
                description="Technical breakout lacks flow confirmation.",
                severity=ContradictionSeverity.HIGH
            ))

        # Check Contradictions: Technical vs Mechanism Direction
        if "mechanism" in factors and factors["technical"].state == FactorState.POSITIVE and factors["mechanism"].state == FactorState.NEGATIVE:
            contradictions.append(EvidenceContradiction(
                topic="Technical vs Mechanism",
                description="Technical breakout contradicted by negative transmission mechanism.",
                severity=ContradictionSeverity.HIGH
            ))
            
        research_contradictions_raw = research_data.get("contradictions", [])
        for c in research_contradictions_raw:
            topic = c.get("topic", "Conflict") if isinstance(c, dict) else "Conflict"
            desc = c.get("description", "Unknown contradiction") if isinstance(c, dict) else str(c)
            sev_str = c.get("severity", "MEDIUM") if isinstance(c, dict) else "MEDIUM"
            sev = ContradictionSeverity(sev_str) if sev_str in [e.value for e in ContradictionSeverity] else ContradictionSeverity.MEDIUM
            contradictions.append(EvidenceContradiction(topic=topic, description=desc, severity=sev))

        # Red Team Contradicting Evidence from Agent 2
        red_team_data = research_data.get("red_team", {})
        if isinstance(red_team_data, dict):
            contra_ev = red_team_data.get("contradicting_evidence", [])
            for cev in contra_ev:
                desc = cev.get("description", str(cev)) if isinstance(cev, dict) else getattr(cev, "description", str(cev))
                contradictions.append(EvidenceContradiction(
                    topic="Red Team Challenge",
                    description=desc,
                    severity=ContradictionSeverity.HIGH
                ))
        
        ev_matrix = EvidenceMatrix(
            factors=factors,
            convergence_summary="Multi-factor evaluation completed.",
            contradictions=contradictions
        )

        thesis_deteriorating = False
        if q_score < 60:
            thesis_deteriorating = True

        catalyst_claims = []
        if research_data.get("catalysts"):
            catalyst_claims.extend(["Expected " + c.get("claim", "catalyst") for c in research_data.get("catalysts", [])])
        if mechanisms:
            for m in mechanisms:
                catalyst_claims.append(f"Mechanism: {m.get('mechanism_type', '')} ({m.get('economic_channel', '')}) -> {m.get('expected_direction', '')}")

        thesis = InvestmentThesis(
            bull_thesis="Quant score indicates bullish momentum with aligned intelligence." if q_score > 80 and price_exp != "NEGATIVE" else "UNKNOWN",
            bear_thesis="Contradictions exist." if len(contradictions) > 0 else "UNKNOWN",
            thesis_deteriorating=thesis_deteriorating,
            key_catalysts=catalyst_claims,
            contradictions=contradictions
        )
        
        action = risk_evaluation["action"]
        blockers = list(risk_evaluation.get("blockers", []))

        # Check Intelligence / MNPI / Untrusted Content Firewall
        firewall_status = research_data.get("firewall_status", "PASS")
        if firewall_status in ["BLOCKED_UNTRUSTED", "BLOCKED_MNPI"]:
            action = "AVOID"
            blockers.append(f"FIREWALL_BLOCKED: {firewall_status}")

        # Check Red Team Block
        red_team_dec = research_data.get("red_team_decision", "")
        if isinstance(red_team_data, dict) and not red_team_dec:
            red_team_dec = red_team_data.get("red_team_decision", "")
        if red_team_dec == "BLOCK":
            if action == "BUY":
                action = "AVOID"
            if "RED_TEAM_BLOCK" not in blockers:
                blockers.append("RED_TEAM_BLOCK")

        # Check Major Contradictions
        has_major_contradiction = any(c.severity in [ContradictionSeverity.HIGH, ContradictionSeverity.CRITICAL] for c in contradictions)
        if action == "BUY" and has_major_contradiction:
            action = "WAIT" # Force downgrade if MAJOR contradiction exists

        # Check Dynamic Thesis Delta (Gate 6)
        thesis_delta = research_data.get("thesis_delta") or quant_data.get("thesis_delta")
        if thesis_delta:
            t_state = getattr(thesis_delta, "thesis_state", None) or thesis_delta.get("thesis_state")
            t_state_val = t_state.value if hasattr(t_state, "value") else str(t_state)
            t_reason = getattr(thesis_delta, "reason", "") or thesis_delta.get("reason", "")
            if t_state_val == "INVALIDATED":
                action = "AVOID" if action == "BUY" else "SELL"
                blockers.append(f"THESIS_INVALIDATED: {t_reason}")
            elif t_state_val == "WEAKENING" and action == "BUY":
                action = "WAIT"
                blockers.append(f"THESIS_WEAKENING: {t_reason}")

        # If evidence state is INSUFFICIENT / UNKNOWN, do not force BUY
        evidence_quality_str = research_data.get("evidence_state", "UNKNOWN")
        if research_data.get("research_status") in ["UNKNOWN", "REJECTED"] and action == "BUY":
            action = "WAIT"
            blockers.append("INSUFFICIENT_INTELLIGENCE_CONFIRMATION")


        # --- Timing & Opportunity Engine ---
        current_price = quant_data.get("price", {}).get("current", 0.0) if "price" in quant_data else quant_data.get("entry_price", 0.0)
        
        # Extract true TriggerInfo
        trigger_info_dict = quant_data.get("trigger", {})
        if trigger_info_dict and "trigger_price" in trigger_info_dict:
            trigger_price_val = trigger_info_dict.get("trigger_price", 0.0)
            actual_trigger = TriggerInfo(
                trigger_type=trigger_info_dict.get("trigger_type", "UNKNOWN"),
                trigger_price=trigger_price_val,
                trigger_condition=trigger_info_dict.get("trigger_condition", "UNKNOWN"),
                timestamp=trigger_info_dict.get("timestamp", as_of_timestamp)
            )
        else:
            # Legacy fallback
            trigger_price_val = quant_data.get("entry_price", 0.0)
            actual_trigger = TriggerInfo(trigger_type="LEGACY_FALLBACK", trigger_price=trigger_price_val, timestamp=as_of_timestamp)

        stop_loss_val = quant_data.get("stop_loss", 0.0)

        # Derive signal_state from action
        if action == "BUY":
            signal_state_str = "ENTRY_READY"
        elif action == "SELL":
            signal_state_str = "EXIT_NOW"
        elif action == "AVOID":
            signal_state_str = "BLOCKED"
        else:
            signal_state_str = "SETUP_FORMING"

        catalyst_state_str = "ACTIVE" if (research_data.get("why_now", "NONE") != "NONE" or len(mechanisms) > 0) else "UNKNOWN"
        catalyst_materiality = research_data.get("catalyst_materiality", "HIGH" if mechanisms else "UNKNOWN")
        catalyst_decay = research_data.get("catalyst_decay", "UNKNOWN")
        flow_state_str = research_data.get("flow_state", "UNKNOWN")
        technical_state_str = factors["technical"].state.value
        market_regime = quant_data.get("market_regime", "UNKNOWN")

        trig_prox = TriggerProximityEngine.evaluate(current_price, trigger_price_val)
        dist_pct = TriggerProximityEngine.distance_pct(current_price, trigger_price_val)

        reference_price = quant_data.get("reference_price")
        if reference_price is None:
            price_action = quant_data.get("price_action", {})
            reference_price = price_action.get("low_20d")
        
        move_pct = None
        if reference_price and reference_price > 0 and current_price:
            move_pct = (current_price - reference_price) / reference_price

        priced_in = PricedInEngine.evaluate(
            move_pct_from_reference=move_pct,
            catalyst_materiality=catalyst_materiality,
            catalyst_decay=catalyst_decay,
        )

        timing = TimingQualityEngine.evaluate(
            signal_state=signal_state_str,
            trigger_proximity=trig_prox,
            priced_in_status=priced_in,
            technical_state=technical_state_str,
            evidence_state=evidence_quality_str,
        )

        entry_window = EntryWindowEngine.evaluate(
            timing_quality=timing,
            trigger_proximity=trig_prox,
            priced_in_status=priced_in,
            signal_state=signal_state_str,
        )

        opp_result = OpportunityRanker.score_candidate(
            quant_score=q_score,
            technical_state=technical_state_str,
            flow_state=flow_state_str,
            market_regime=market_regime,
            catalyst_materiality=catalyst_materiality,
            catalyst_decay=catalyst_decay,
            catalyst_state=catalyst_state_str,
            evidence_quality=evidence_quality_str,
            risk_state=risk_evaluation["risk_state"],
            signal_state=signal_state_str,
            current_price=current_price,
            trigger_price=trigger_price_val,
            stop_loss=stop_loss_val,
            relative_strength_state=factors.get("relative_strength", EvidenceFactor(factor_name="rs", state=FactorState.UNKNOWN)).state.value
        )

        inv_report = research_data.get("investigation_report")
        if inv_report:
            inv_why_now = getattr(inv_report, "why_now_assessment", "") or (inv_report.get("why_now_assessment", "") if isinstance(inv_report, dict) else "")
            if inv_why_now and inv_why_now != "NONE":
                why_now = inv_why_now
            else:
                why_now = research_data.get("why_now", opp_result.why_now)
        else:
            why_now = research_data.get("why_now", opp_result.why_now)
        opp_class = opp_result.opportunity_class


        signal_strength = SignalStrengthEngine.evaluate(
            technical_state=technical_state_str,
            flow_state=flow_state_str,
            evidence_quality=evidence_quality_str,
            contradiction_level="HIGH" if has_major_contradiction else "LOW",
            risk_state=risk_evaluation["risk_state"],
        )

        alert_urgency = AlertUrgencyEngine.evaluate(
            timing_quality=timing,
            trigger_proximity=trig_prox,
            entry_window_status=entry_window,
            priced_in_status=priced_in,
            risk_state=risk_evaluation["risk_state"],
        )

        has_evidence = evidence_quality_str in ("COMPLETE", "GOOD") or len(mechanisms) > 0
        tier_score = opp_result.total_score
        if action == "BUY" and tier_score >= 60 and has_evidence and not has_major_contradiction and firewall_status == "PASS":
            tier = "TIER 1"
        elif tier_score >= 45 or (action == "WAIT" and q_score > 70):
            tier = "TIER 2"
        else:
            tier = "TIER 3"

        invalidation_conds = InvalidationEngine.build(
            has_stop_loss=stop_loss_val > 0,
            stop_loss=stop_loss_val,
            catalyst_decay=catalyst_decay,
            flow_state=flow_state_str,
            technical_state=technical_state_str,
        )

        opp_assessment = OpportunityAssessment(
            symbol=symbol,
            setup_state=technical_state_str,
            opportunity_score=opp_result.total_score,
            technical_state=technical_state_str,
            flow_state=flow_state_str,
            sector_state="UNKNOWN",
            market_state=market_regime,
            catalyst_state=catalyst_state_str,
            fundamental_state=factors["fundamental"].state.value if "fundamental" in factors else "UNKNOWN",
            risk_state=risk_evaluation["risk_state"],
            evidence_quality=evidence_quality_str,
            contradiction_level="HIGH" if has_major_contradiction else "LOW",
            entry_readiness="READY" if action == "BUY" else "NOT_READY",
            opportunity_class=opp_class,
            why_now=why_now,
            signal_tier=tier,
            timing_quality=timing.value,
            trigger_proximity=trig_prox.value,
            entry_window_status=entry_window.value,
            priced_in_status=priced_in.value,
            alert_urgency=alert_urgency,
            signal_strength=signal_strength,
            invalidation_conditions=invalidation_conds,
            distance_to_trigger_pct=round(dist_pct * 100, 2) if dist_pct is not None else None,
        )
        
        # Build trace preserving all graph intelligence and evidence references
        trace_dict = dict(risk_evaluation.get("trace", {}))
        evidence_list = research_data.get("evidence", [])
        extracted_refs = []
        for ev in evidence_list:
            if isinstance(ev, dict):
                extracted_refs.append(ev.get("event_id", ""))
            else:
                extracted_refs.append(getattr(ev, "event_id", str(ev)))
                
        trace_dict["evidence_refs"] = extracted_refs
        trace_dict["graph_intelligence"] = {
            "mechanisms": mechanisms,
            "exposures": research_data.get("exposures", []),
            "relationships": research_data.get("relationships", []),
            "firewall_status": firewall_status,
            "contradictions_found": len(contradictions)
        }
            
        reason_str = "Synthesized from Quant and Research evidence."
        if action == "AVOID" and firewall_status != "PASS":
            reason_str = f"Blocked by Intelligence Firewall: {firewall_status}"
        elif action == "WAIT" and has_major_contradiction:
            reason_str = "Downgraded to WAIT due to major intelligence / red team contradictions."
        elif action == "WAIT" and risk_evaluation["action"] == "BUY":
            reason_str = "Downgraded to WAIT due to incomplete intelligence confirmation."

        conf_raw = research_data.get("confidence", quant_data.get("quant_confidence", 0.0))
        if isinstance(conf_raw, str):
            conf_map = {"HIGH": 90.0, "MEDIUM": 75.0, "LOW": 30.0, "UNKNOWN": 0.0}
            decision_confidence = conf_map.get(conf_raw.upper(), 50.0)
        else:
            try:
                decision_confidence = float(conf_raw)
            except (ValueError, TypeError):
                decision_confidence = 50.0

        return DecisionResult(
            job_id=job_id,
            symbol=symbol,
            as_of_timestamp=as_of_timestamp,
            action=action,
            risk_state=risk_evaluation["risk_state"],
            confidence=decision_confidence,
            opportunity_score=opp_result.total_score,
            thesis=thesis,
            evidence_matrix=ev_matrix,
            reason=reason_str,
            blockers=blockers,
            strengths=[],
            weaknesses=[],
            current_price=current_price,
            entry_price=quant_data.get("entry_price", 0.0),
            trigger_price=trigger_price_val,
            trigger=actual_trigger,
            stop_loss=quant_data.get("stop_loss", 0.0),
            target_price=quant_data.get("target_price", 0.0),
            risk_per_share=risk_evaluation["risk_per_share"],
            reward_per_share=risk_evaluation["reward_per_share"],
            risk_reward_ratio=risk_evaluation["risk_reward_ratio"],
            position_size=risk_evaluation["position_size"],
            position_lots=risk_evaluation["position_lots"],
            position_value=risk_evaluation["position_value"],
            portfolio_risk=risk_evaluation["portfolio_risk"],
            evidence_state=research_data.get("evidence_state", "UNKNOWN"),
            red_team_status=research_data.get("red_team_decision", "UNKNOWN"),
            decision_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            decision_source="AGENT3_COMMITTEE",
            opportunity_assessment=opp_assessment,
            trace=trace_dict
        )
