from typing import Dict, Any, Optional
from core.historical_knowledge_state import HistoricalKnowledgeState
from agents.agent2_intelligence.llm_reasoner import Agent2LLMReasoner
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport

class Agent2IntelligencePipeline:
    """
    Agent 2 Pipeline with strict Historical Replay Firewall.
    Consumes ONLY HistoricalKnowledgeState.
    """
    def __init__(self, reasoner: Optional[Agent2LLMReasoner] = None):
        self.reasoner = reasoner or Agent2LLMReasoner()

    def process_historical_state(self, state: HistoricalKnowledgeState) -> Agent2IntelligenceReport:
        """
        Executes Agent 2 intelligence synthesis and Red Team analysis from historical knowledge state.
        """
        return self.reasoner.execute_reasoning(state)
