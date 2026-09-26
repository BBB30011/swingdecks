from typing import Any, Dict, List, Optional
import json
import uuid
from core.historical_knowledge_state import HistoricalKnowledgeState
from core.replay_firewall import ReplayFirewall
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport, EvidenceReference

class Agent2LLMReasoner:
    """
    Agent 2 (Market Intelligence & Red Team) Reasoning Core.
    STRICT BOUNDARY: Consumes ONLY HistoricalKnowledgeState(T).
    Direct SQL or Dataset V2 queries are forbidden.
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

[CONTEXTUAL PEERS (LEAVE-ONE-OUT)]
{json.dumps(state.peer_state, indent=2)}

[INSTRUCTIONS]
1. Determine what changed (Information Delta).
2. Propose an Economic Transmission chain.
3. Challenge your own thesis using the Red Team framework.
4. Output strictly according to the Agent2IntelligenceReport schema.
5. If evidence is lacking or coverage is LIMITED/BLOCKED, declare UNKNOWN. Do not hallucinate external knowledge.
"""
        return prompt

    def execute_reasoning(self, state: HistoricalKnowledgeState) -> Agent2IntelligenceReport:
        """
        Generates deterministic intelligence report based strictly on the HistoricalKnowledgeState.
        """
        prompt = self.generate_prompt(state)
        events = state.event_state
        
        if not events:
            return Agent2IntelligenceReport(
                analysis_id=str(uuid.uuid4()),
                decision_timestamp=f"{state.decision_date} {state.decision_time}",
                pit_mode="PUBLIC_PIT",
                entity=state.entity_id,
                evidence=[],
                information_state="OBSERVATION",
                information_delta="UNCHANGED",
                relationships=[r.get("relationship_type", "") for r in state.relationship_state],
                exposures=[x.get("exposure_type", "") for x in state.exposure_state],
                economic_transmission={
                    "event_impact": None,
                    "business_impact": None,
                    "financial_impact": None,
                    "price_expectation": "UNKNOWN"
                },
                differential_assessment={
                    "target_reaction": None,
                    "peer_reaction": None,
                    "market_reaction": None,
                    "differential_status": "UNKNOWN"
                },
                thesis="No historical disclosure events found at this Point-In-Time timestamp.",
                red_team={
                    "supporting_evidence": [],
                    "contradicting_evidence": [],
                    "alternative_explanations": ["Lack of primary disclosure evidence in dataset"],
                    "missing_information": ["Primary regulatory filings"],
                    "invalidation_conditions": ["Peer synchronization without specific catalyst"]
                },
                confidence="LOW",
                research_status="UNKNOWN"
            )
            
        latest_event = events[0]
        evidence_ref = EvidenceReference(
            event_id=str(latest_event.get("event_id", "HIST_EVENT")),
            source_id=str(latest_event.get("source", "DATASET_V2")),
            published_at=str(latest_event.get("published_at", "") or latest_event.get("available_at", "")),
            description=str(latest_event.get("description", latest_event.get("event_type", "DISCLOSURE")))
        )
        
        report = Agent2IntelligenceReport(
            analysis_id=str(uuid.uuid4()),
            decision_timestamp=f"{state.decision_date} {state.decision_time}",
            pit_mode="PUBLIC_PIT",
            entity=state.entity_id,
            evidence=[evidence_ref],
            information_state="FACT",
            information_delta="NEW",
            relationships=[r.get("relationship_type", "") for r in state.relationship_state],
            exposures=[x.get("exposure_type", "") for x in state.exposure_state],
            economic_transmission={
                "event_impact": "Direct",
                "business_impact": "Operational Update",
                "financial_impact": "Pending Verification",
                "price_expectation": "UNKNOWN"
            },
            differential_assessment={
                "target_reaction": "Pending",
                "peer_reaction": "Pending",
                "market_reaction": "Pending",
                "differential_status": "COMPANY_SPECIFIC_CANDIDATE"
            },
            thesis=f"PIT Disclosure {latest_event.get('event_type', 'EVENT')} observed for {state.ticker}.",
            red_team={
                "supporting_evidence": [evidence_ref],
                "contradicting_evidence": [],
                "alternative_explanations": ["Market beta / Commodity factor continuation"],
                "missing_information": ["Quantified revenue impact"],
                "invalidation_conditions": ["If peer group moves synchronously with same magnitude"]
            },
            confidence="MEDIUM",
            research_status="OBSERVATION"
        )
        return report
