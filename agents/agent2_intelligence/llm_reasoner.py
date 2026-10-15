from typing import Any, Dict, List, Optional
import json
import uuid
from core.historical_knowledge_state import HistoricalKnowledgeState
from core.replay_firewall import ReplayFirewall
from agents.agent2_intelligence.schemas import (
    Agent2IntelligenceReport, EvidenceReference, EconomicTransmission,
    DifferentialAssessment, RedTeamChallenge
)

class Agent2LLMReasoner:
    """
    Agent 2 (Market Intelligence & Red Team) Reasoning Core.
    STRICT BOUNDARY: Consumes ONLY HistoricalKnowledgeState(T) or validated point-in-time graph state.
    Distinguishes FACTS, OBSERVATIONS, INTERPRETATIONS, and HYPOTHESES.
    Enforces Security & MNPI Firewalls.
    Zero Agent 4.
    """
    def __init__(self):
        pass
    
    def generate_prompt(self, state: HistoricalKnowledgeState) -> str:
        """
        Constructs the strict, outcome-blind prompt for Agent 2 from HistoricalKnowledgeState(T).
        Enforces Database, File, Memory, and Prompt firewalls.
        """
        # Validate that no forward outcome or holding return is leaked into state
        ReplayFirewall.prevent_outcome_leak(state.to_dict())
        
        prompt = f"""
You are Agent 2 (Market Intelligence & Red Team) of SwingDeck.
Decision Date: {state.decision_date}
Decision Time: {state.decision_time}
Entity: {state.entity_id} ({state.ticker})
Snapshot Hash: {state.snapshot_hash}

[ELIGIBILITY & COVERAGE STATE]
{json.dumps(state.coverage_state, indent=2)}

[EVIDENCE REPOSITORY (HISTORICAL EVENTS <= {state.decision_date} {state.decision_time})]
{json.dumps(state.event_state, indent=2)}

[ENTITY CONTEXT (RELATIONSHIPS & OWNERSHIP VALID AT {state.decision_date})]
Relationships:
{json.dumps(state.relationship_state, indent=2)}
Ownership:
{json.dumps(state.ownership_state, indent=2)}

[EXPOSURES]
{json.dumps(state.exposure_state, indent=2)}

[MECHANISM HYPOTHESES]
{json.dumps(state.mechanism_state, indent=2)}

[CONTEXTUAL PEERS (LEAVE-ONE-OUT)]
{json.dumps(state.peer_state, indent=2)}

[INSTRUCTIONS]
1. Determine what changed (Information Delta).
2. Distinguish FACTS, OBSERVATIONS, INTERPRETATIONS, and HYPOTHESES.
3. Propose an Economic Transmission chain from mechanism hypotheses.
4. Challenge your own thesis using the Red Team framework.
5. Output strictly according to the Agent2IntelligenceReport schema.
6. If evidence is lacking or coverage is LIMITED/BLOCKED, declare UNKNOWN. Do not hallucinate external knowledge.
"""
        return prompt

    def execute_reasoning(self, state: HistoricalKnowledgeState) -> Agent2IntelligenceReport:
        """
        Generates deterministic intelligence report based strictly on the HistoricalKnowledgeState.
        """
        prompt = self.generate_prompt(state)
        events = state.event_state
        relationships = state.relationship_state
        exposures = state.exposure_state
        mechanisms = state.mechanism_state
        
        # 1. Check Security & MNPI Firewalls
        for ev in events:
            status = ev.get("status", "")
            access_class = ev.get("access_class", "PUBLIC")
            trading_eligibility = ev.get("trading_eligibility", "ELIGIBLE")
            if status == "UNTRUSTED_CONTENT":
                return self._create_firewall_blocked_report(state, "BLOCKED_UNTRUSTED", "Prompt injection or untrusted content detected in information feed.")
            if access_class not in ["PUBLIC", None, ""] or trading_eligibility != "ELIGIBLE" or status == "RESTRICTED_MNPI":
                return self._create_firewall_blocked_report(state, "BLOCKED_MNPI", "Restricted or Material Non-Public Information (MNPI) detected. Decision pathway blocked.")

        # 2. Check for Empty/Insufficient state
        if not events and not exposures and not mechanisms:
            return Agent2IntelligenceReport(
                analysis_id=str(uuid.uuid4()),
                decision_timestamp=f"{state.decision_date} {state.decision_time}",
                pit_mode="PUBLIC_PIT",
                entity=state.entity_id,
                evidence=[],
                information_state="OBSERVATION",
                information_delta="UNCHANGED",
                relationships=[r.get("relationship_type", "") for r in relationships],
                exposures=[x.get("exposure_type", "") for x in exposures],
                mechanisms=mechanisms,
                graph_paths=state.graph_path_state,
                economic_transmission=EconomicTransmission(
                    event_impact=None,
                    business_impact=None,
                    financial_impact=None,
                    price_expectation="UNKNOWN"
                ),
                differential_assessment=DifferentialAssessment(
                    target_reaction=None,
                    peer_reaction=None,
                    market_reaction=None,
                    differential_status="UNKNOWN"
                ),
                thesis="No historical disclosure events or active mechanisms found at this Point-In-Time timestamp.",
                red_team=RedTeamChallenge(
                    supporting_evidence=[],
                    contradicting_evidence=[],
                    alternative_explanations=["Lack of primary disclosure evidence in dataset"],
                    missing_information=["Primary regulatory filings", "Exposure mappings"],
                    invalidation_conditions=["Peer synchronization without specific catalyst"]
                ),
                confidence="LOW",
                research_status="UNKNOWN",
                firewall_status="PASS",
                provenance_sources=[],
                contradictions_found=0
            )

        # 3. Assemble Evidence References
        evidence_refs: List[EvidenceReference] = []
        provenance_list: List[str] = []
        for ev in events:
            source = str(ev.get("source_id", "") or ev.get("source", "") or ev.get("publisher", "DATASET_V2"))
            eid = str(ev.get("event_id", "") or ev.get("information_id", "HIST_EVENT"))
            pub_at = str(ev.get("published_at", "") or ev.get("available_at", "") or f"{state.decision_date} {state.decision_time}")
            desc = str(ev.get("claim", "") or ev.get("title", "") or ev.get("description", ev.get("event_type", "DISCLOSURE")))
            prov = str(ev.get("source_url_or_reference", "") or ev.get("provenance", source))
            
            evidence_refs.append(EvidenceReference(
                event_id=eid,
                source_id=source,
                published_at=pub_at,
                description=desc,
                access_class=str(ev.get("access_class", "PUBLIC")),
                confidence=str(ev.get("confidence", "UNKNOWN")),
                provenance=prov
            ))
            if prov and prov not in provenance_list:
                provenance_list.append(prov)

        # 4. Determine Information State (FACT vs OBSERVATION vs INTERPRETATION vs HYPOTHESIS)
        # If mechanisms dominate with no primary filings -> HYPOTHESIS
        # If primary disclosures/filings exist -> FACT
        # If only market/peer movements exist -> OBSERVATION
        info_state = "OBSERVATION"
        if events:
            first_ev_type = events[0].get("event_type", "") or events[0].get("information_type", "")
            if first_ev_type in ["CORPORATE_ACTION", "DISCLOSURE", "FILING", "REGULATORY_ANNOUNCEMENT", "POLICY"]:
                info_state = "FACT"
            elif first_ev_type in ["NEWS", "INTERPRETATION", "ARTICLE"]:
                info_state = "INTERPRETATION"
            elif first_ev_type in ["MECHANISM", "HYPOTHESIS"]:
                info_state = "HYPOTHESIS"
        elif mechanisms:
            info_state = "HYPOTHESIS"

        # 5. Extract Economic Transmission from Mechanisms or Events
        event_impact = "Direct" if exposures else "Indirect"
        business_impact = "Operational transmission"
        financial_impact = "Pending verification"
        price_exp = "UNKNOWN"
        
        if mechanisms:
            mech0 = mechanisms[0]
            event_impact = f"{mech0.get('mechanism_type', 'Direct')}"
            business_impact = f"Channel: {mech0.get('economic_channel', 'Operational')}"
            financial_impact = f"Effect: {mech0.get('expected_effect', 'Neutral')}"
            direction_raw = str(mech0.get("expected_direction", "UNKNOWN")).upper()
            if direction_raw in ["POSITIVE", "NEGATIVE", "MIXED", "UNKNOWN"]:
                price_exp = direction_raw
        elif events:
            business_impact = f"Event: {events[0].get('event_type', 'Corporate')}"

        # 6. Extract Contradictions & Red Team Challenge
        contradicting_refs: List[EvidenceReference] = []
        alt_explanations: List[str] = ["Market beta / macroeconomic factor continuation"]
        missing_info: List[str] = []
        invalidation_conds: List[str] = ["If peer group moves synchronously with same magnitude without idiosyncratic differentiation"]
        
        contradictions_count = 0
        for mech in mechanisms:
            contra = mech.get("contradicting_evidence", [])
            if contra:
                contradictions_count += len(contra)
                for c_item in contra:
                    contradicting_refs.append(EvidenceReference(
                        event_id=f"CONTRA_{str(c_item)[:8]}",
                        source_id="CONTRADICTION_ENGINE",
                        published_at=f"{state.decision_date} {state.decision_time}",
                        description=str(c_item)
                    ))
            inv = mech.get("invalidation_condition")
            if inv and inv != "UNKNOWN":
                invalidation_conds.append(inv)

        if not exposures:
            missing_info.append("Company-to-event exposure channel unverified")
        if not mechanisms:
            missing_info.append("Formal mechanism hypothesis unmapped")

        # 7. Synthesize Thesis
        event_desc = events[0].get("title", events[0].get("claim", events[0].get("event_type", "Event"))) if events else "Graph node active"
        mech_desc = f" via {mechanisms[0].get('economic_channel', 'channel')}" if mechanisms else ""
        thesis_text = f"PIT Intelligence: {event_desc} for {state.ticker}{mech_desc}."
        if contradictions_count > 0:
            thesis_text += f" (CONTRADICTION DETECTED: {contradictions_count} opposing factor(s))"

        # Determine Differential Status
        diff_status = "COMPANY_SPECIFIC_CANDIDATE" if (exposures and len(state.peer_state) > 0) else "UNKNOWN"
        if not exposures and not events:
            diff_status = "NO_CLEAR_DIFFERENTIAL"

        confidence_val = "HIGH" if (info_state == "FACT" and exposures and mechanisms and contradictions_count == 0) else ("MEDIUM" if events or mechanisms else "LOW")
        research_st = "SUPPORTED" if (confidence_val == "HIGH") else ("TESTING" if mechanisms else ("OBSERVATION" if events else "UNKNOWN"))
        if contradictions_count > 0:
            research_st = "UNRESOLVED"

        return Agent2IntelligenceReport(
            analysis_id=str(uuid.uuid4()),
            decision_timestamp=f"{state.decision_date} {state.decision_time}",
            pit_mode="PUBLIC_PIT",
            entity=state.entity_id,
            evidence=evidence_refs,
            information_state=info_state,
            information_delta="NEW" if events else "UNCHANGED",
            relationships=[r.get("relationship_type", "") for r in relationships],
            exposures=[x.get("exposure_type", "") for x in exposures],
            mechanisms=mechanisms,
            graph_paths=state.graph_path_state,
            economic_transmission=EconomicTransmission(
                event_impact=event_impact,
                business_impact=business_impact,
                financial_impact=financial_impact,
                price_expectation=price_exp
            ),
            differential_assessment=DifferentialAssessment(
                target_reaction="Pending",
                peer_reaction="Pending",
                market_reaction="Pending",
                differential_status=diff_status
            ),
            thesis=thesis_text,
            red_team=RedTeamChallenge(
                supporting_evidence=evidence_refs,
                contradicting_evidence=contradicting_refs,
                alternative_explanations=alt_explanations,
                missing_information=missing_info,
                invalidation_conditions=invalidation_conds
            ),
            confidence=confidence_val,
            research_status=research_st,
            firewall_status="PASS",
            provenance_sources=provenance_list,
            contradictions_found=contradictions_count
        )

    def _create_firewall_blocked_report(self, state: HistoricalKnowledgeState, block_reason: str, detail: str) -> Agent2IntelligenceReport:
        return Agent2IntelligenceReport(
            analysis_id=str(uuid.uuid4()),
            decision_timestamp=f"{state.decision_date} {state.decision_time}",
            pit_mode="PUBLIC_PIT",
            entity=state.entity_id,
            evidence=[],
            information_state="OBSERVATION",
            information_delta="REMOVED",
            relationships=[],
            exposures=[],
            mechanisms=[],
            graph_paths=[],
            economic_transmission=EconomicTransmission(
                event_impact="BLOCKED",
                business_impact="SECURITY_FIREWALL_TRIPPED",
                financial_impact="EXECUTION_BLOCKED",
                price_expectation="UNKNOWN"
            ),
            differential_assessment=DifferentialAssessment(
                target_reaction=None,
                peer_reaction=None,
                market_reaction=None,
                differential_status="UNKNOWN"
            ),
            thesis=f"SECURITY_FIREWALL_BLOCKED: {detail}",
            red_team=RedTeamChallenge(
                supporting_evidence=[],
                contradicting_evidence=[],
                alternative_explanations=["Adversarial injection or unauthorized MNPI attempt"],
                missing_information=["Public verification missing"],
                invalidation_conditions=["All trade proposals from this source are void"]
            ),
            confidence="LOW",
            research_status="REJECTED",
            firewall_status=block_reason,
            provenance_sources=[],
            contradictions_found=1
        )
