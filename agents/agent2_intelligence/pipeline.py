from typing import Dict, Any, Optional, List
from core.historical_knowledge_state import HistoricalKnowledgeState
from agents.agent2_intelligence.llm_reasoner import Agent2LLMReasoner
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport
from core.intelligence_graph import IntelligenceGraphEngine
from core.research import (
    ResearchPacket, FundamentalEvidence, MacroEvidence, NewsEvidence,
    CatalystEvidence, CorporateEvent, SentimentEvidence, ResearchEvidence
)
from core.red_team import RedTeamAnalyzer
from core.data_platform_schemas import InvestigationRequest, InvestigationReport

class MockEvidenceCollector:
    """
    Mock evidence collector providing deterministic evidence scenarios for testing and offline execution.
    """
    def __init__(self, scenario: str = "BULLISH"):
        self.scenario = scenario.upper()

    def collect(self, symbol: str, as_of: str = "2020-01-01") -> ResearchPacket:
        packet = ResearchPacket(
            job_id="mock_job",
            symbol=symbol,
            as_of_timestamp=as_of,
            quant_context={}
        )
        if self.scenario == "BULLISH":
            packet.fundamental.append(FundamentalEvidence(
                evidence_id="ev_fund_1",
                symbol=symbol,
                category="FUNDAMENTAL",
                claim="Revenue grew 25% YoY",
                claim_class="FACT",
                source="Audited Financial Report",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                metric="revenue",
                value=25.0,
                unit="%",
                direction="POSITIVE"
            ))
            packet.news.append(NewsEvidence(
                evidence_id="ev_news_1",
                symbol=symbol,
                category="NEWS",
                claim="Company secures major export contract",
                claim_class="FACT",
                source="CNBC",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                headline="Export Expansion Confirmed",
                direction="POSITIVE"
            ))
            packet.macro.append(MacroEvidence(
                evidence_id="ev_macro_1",
                symbol=symbol,
                category="MACRO",
                claim="GDP expansion 5.2%",
                claim_class="FACT",
                source="BPS",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                indicator="GDP",
                value=5.2,
                unit="%",
                timestamp="2020-01-01",
                direction="POSITIVE",
                interpretation="Supportive"
            ))
            packet.catalysts.append(CatalystEvidence(
                evidence_id="ev_cat_1",
                symbol=symbol,
                category="CATALYST",
                claim="Earnings announcement scheduled",
                claim_class="FACT",
                source="IDX Disclosure",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                event_type="EARNINGS",
                decay_state="ACTIVE",
                materiality="HIGH",
                direction="POSITIVE"
            ))
            packet.corporate_events.append(CorporateEvent(
                evidence_id="ev_corp_1",
                symbol=symbol,
                category="CORPORATE_EVENT",
                claim="Interim dividend distribution",
                claim_class="FACT",
                source="IDX Disclosure",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                event_type="DIVIDEND",
                event_date="2020-01-10",
                announcement_date="2020-01-01",
                description="Dividend payout"
            ))
            packet.sentiment.append(SentimentEvidence(
                evidence_id="ev_sent_1",
                symbol=symbol,
                category="SENTIMENT",
                claim="Positive market sentiment",
                claim_class="FACT",
                source="Market Survey",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                timestamp="2020-01-01",
                sentiment="POSITIVE",
                confidence=0.85
            ))
            packet.policy.append(ResearchEvidence(
                evidence_id="ev_pol_1",
                symbol=symbol,
                category="POLICY",
                claim="Tax incentives for domestic manufacturing",
                claim_class="FACT",
                source="Ministry of Finance",
                published_at="2020-01-01",
                as_of_timestamp=as_of
            ))
        elif self.scenario == "CONTRADICTED":
            packet.fundamental.append(FundamentalEvidence(
                evidence_id="ev_fund_1",
                symbol=symbol,
                category="FUNDAMENTAL",
                claim="Revenue dropped sharply",
                claim_class="FACT",
                source="Audited Financial Report",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                metric="revenue",
                value=-15.0,
                unit="%",
                direction="NEGATIVE"
            ))
            packet.macro.append(MacroEvidence(
                evidence_id="ev_macro_1",
                symbol=symbol,
                category="MACRO",
                claim="Interest rates raised 50bps",
                claim_class="FACT",
                source="Central Bank",
                published_at="2020-01-01",
                as_of_timestamp=as_of,
                indicator="BI-Rate",
                value=6.0,
                unit="%",
                timestamp="2020-01-01",
                direction="NEGATIVE",
                interpretation="Tightening liquidity"
            ))
            packet.contradictions.append({
                "severity": "HIGH",
                "description": "Bullish quant momentum contradicted by collapsing fundamentals and rising interest rates."
            })
        elif self.scenario == "UNKNOWN":
            # No evidence added; remains empty / INSUFFICIENT
            pass
            
        return packet


class Agent2IntelligencePipeline:
    """
    Agent 2 Pipeline supporting Historical Replay Firewall, Graph Engine Integration, and Job-based Orchestration.
    """
    def __init__(self, collector_or_reasoner: Any = None, graph_engine: Optional[IntelligenceGraphEngine] = None):
        self.graph_engine = graph_engine
        if isinstance(collector_or_reasoner, MockEvidenceCollector):
            self.collector = collector_or_reasoner
            self.reasoner = Agent2LLMReasoner()
        elif isinstance(collector_or_reasoner, Agent2LLMReasoner):
            self.collector = None
            self.reasoner = collector_or_reasoner
        else:
            self.collector = None
            self.reasoner = collector_or_reasoner or Agent2LLMReasoner()

    def process_job(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes job-based research synthesis, graph intelligence extraction, and Red Team validation.
        """
        symbol = payload.get("symbol", "UNKNOWN")
        as_of = payload.get("as_of_timestamp", "2020-01-01")
        collector = self.collector or MockEvidenceCollector("BULLISH")
        packet = collector.collect(symbol, as_of)
        packet.quant_context = {
            "quant_score": payload.get("quant_score", 90),
            "quant_confidence": payload.get("quant_confidence", 90),
            "market_regime": payload.get("market_regime", "UNKNOWN"),
            "stock_regime": payload.get("stock_regime", "UNKNOWN")
        }
        packet.filter_by_timestamp(as_of)
        red_team = RedTeamAnalyzer.analyze(packet)
        
        # If graph context is provided or graph_engine is attached, query graph
        report = None
        if "graph_context" in payload:
            report = self.process_graph_subgraph(payload["graph_context"], as_of)
        elif self.graph_engine:
            subgraph = self.graph_engine.get_entity_subgraph(symbol, as_of)
            report = self.process_graph_subgraph(subgraph, as_of)
            
        result = {
            "status": "COMPLETED",
            "job_id": payload.get("job_id", ""),
            "symbol": symbol,
            "packet": packet.model_dump(),
            "red_team_decision": report.red_team_status if report and hasattr(report, "red_team_status") else red_team.decision,
            "red_team_reasons": red_team.reasons,
            "why_now": red_team.why_now
        }
        if report:
            result["intelligence_report"] = report.model_dump()
            if report.firewall_status != "PASS":
                result["red_team_decision"] = "BLOCK"
                result["red_team_reasons"].append(f"Firewall tripped: {report.firewall_status}")
        return result

    def process_historical_state(self, state: HistoricalKnowledgeState) -> Agent2IntelligenceReport:
        """
        Executes Agent 2 intelligence synthesis and Red Team analysis from historical knowledge state.
        """
        if self.reasoner is None:
            self.reasoner = Agent2LLMReasoner()
        return self.reasoner.execute_reasoning(state)

    def process_graph_subgraph(self, subgraph: Dict[str, Any], pit: str = "2026-09-29T10:00:00Z") -> Agent2IntelligenceReport:
        """
        Ingests a point-in-time subgraph from IntelligenceGraphEngine and executes Agent 2 reasoning.
        """
        if self.reasoner is None:
            self.reasoner = Agent2LLMReasoner()
            
        ent_info = subgraph.get("entity", {}) or {}
        ent_id = ent_info.get("entity_id", "ENT_UNKNOWN")
        ticker = ent_info.get("canonical_name", ent_id)
        
        date_part = pit.split("T")[0] if "T" in pit else pit.split(" ")[0]
        time_part = pit.split("T")[1] if "T" in pit else (pit.split(" ")[1] if " " in pit else "09:00:00")
        
        state = HistoricalKnowledgeState(
            ticker=ticker,
            decision_date=date_part,
            decision_time=time_part,
            entity_id=ent_id,
            event_state=subgraph.get("information", []),
            relationship_state=subgraph.get("relationships", []),
            exposure_state=subgraph.get("exposures", []),
            mechanism_state=subgraph.get("mechanisms", []),
            coverage_state={"status": "COVERED" if subgraph.get("information") or subgraph.get("exposures") else "UNKNOWN"}
        )
        return self.reasoner.execute_reasoning(state)

    def investigate_candidate(self, request: InvestigationRequest, retrieval_engine: Optional[Any] = None) -> InvestigationReport:
        """
        Processes an on-demand reverse investigation from Agent 1 to explain why a stock is moving.
        Executes point-in-time retrieval across recent deltas, event clusters, and macro transmission paths.
        """
        if retrieval_engine is not None:
            return retrieval_engine.investigate(
                symbol=request.symbol,
                trigger_type=request.trigger_type,
                as_of=request.as_of_timestamp,
                lookback_hours=request.lookback_hours,
                trigger_context=request.trigger_context
            )
        
        # Fallback offline report if no retrieval engine is passed
        return InvestigationReport(
            request_id=request.request_id,
            symbol=request.symbol,
            entity_id=request.entity_id,
            has_matching_catalyst=False,
            novelty_summary="NONE",
            why_now_assessment=f"Offline investigation completed for {request.symbol} ({request.trigger_type.value}).",
            investigation_status="COMPLETED",
            as_of=request.as_of_timestamp
        )

