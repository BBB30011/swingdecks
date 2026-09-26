from typing import Dict, Any, List
from core.research import ResearchPacket

class ContradictionEngine:
    @staticmethod
    def detect(packet: ResearchPacket) -> List[Dict[str, Any]]:
        contradictions = []
        
        quant_bullish = packet.quant_context.get("quant_score", 0) >= 80
        
        has_bear_fundamental = any(f.direction == "NEGATIVE" for f in packet.fundamental)
        has_bear_macro = any(m.direction == "NEGATIVE" for m in packet.macro)
        
        if quant_bullish and (has_bear_fundamental or has_bear_macro):
            contradictions.append({
                "topic": "REGIME",
                "bull_evidence": "Quant Score is highly bullish.",
                "bear_evidence": "Negative Fundamental or Macro evidence detected.",
                "severity": "HIGH" if has_bear_fundamental and has_bear_macro else "MEDIUM"
            })
            
        return contradictions
