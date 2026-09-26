from typing import Dict, Any
from core.decision import PortfolioContext
from core.risk_engine import RiskEngine, RiskEngineConfig
from agents.agent3_committee.committee import InvestmentCommittee

class Agent3DecisionPipeline:
    def __init__(self, risk_config: Dict[str, Any] = None):
        self.risk_engine = RiskEngine(RiskEngineConfig(risk_config))
        self.committee = InvestmentCommittee()

    def process_job(self, 
                    job_payload: Dict[str, Any], 
                    portfolio: PortfolioContext) -> Dict[str, Any]:
                    
        job_id = job_payload.get("job_id", "UNKNOWN")
        symbol = job_payload["symbol"]
        as_of = job_payload.get("as_of_timestamp", "9999-99-99")
        
        quant_data = job_payload.get("quant_context", {})
        research_data = job_payload.get("research_context", {})
        
        entry = quant_data.get("entry_price", 0.0)
        stop = quant_data.get("stop_loss", 0.0)
        target = quant_data.get("target_price", 0.0)
        
        risk_eval = self.risk_engine.evaluate(
            symbol=symbol,
            entry=entry,
            stop=stop,
            target=target,
            portfolio=portfolio,
            quant_data=quant_data,
            research_data=research_data
        )
        
        decision = self.committee.synthesize(
            job_id=job_id,
            symbol=symbol,
            as_of_timestamp=as_of,
            quant_data=quant_data,
            research_data=research_data,
            risk_evaluation=risk_eval
        )
        
        return {
            "status": "COMPLETED",
            "decision": decision.model_dump()
        }
