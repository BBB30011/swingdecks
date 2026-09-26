from typing import Dict, Any, List
from core.decision import PortfolioContext, DecisionTrace
import math

class RiskEngineConfig:
    def __init__(self, config_dict: Dict[str, Any] = None):
        cfg = config_dict or {}
        risk = cfg.get("risk", {})
        trade = cfg.get("trade", {})
        decision = cfg.get("decision", {})
        
        self.max_single_position_risk = risk.get("max_single_position_risk", 0.005)
        self.max_portfolio_risk = risk.get("max_portfolio_risk", 0.02)
        
        self.minimum_rr = trade.get("minimum_rr", 2.0)
        self.maximum_positions = trade.get("maximum_positions", 5)
        self.lot_size = trade.get("lot_size", 100)
        
        self.minimum_confidence = decision.get("minimum_confidence", 70)

class RiskEngine:
    def __init__(self, config: RiskEngineConfig):
        self.config = config

    def evaluate(self, 
                 symbol: str,
                 entry: float, 
                 stop: float, 
                 target: float, 
                 portfolio: PortfolioContext, 
                 quant_data: Dict[str, Any],
                 research_data: Dict[str, Any]) -> Dict[str, Any]:
                 
        trace = DecisionTrace()
        blockers = []
        action = "BUY"
        risk_state = "GREEN"
        
        # 1. R/R & Position Risk Calc
        if stop <= 0.0 or entry <= stop:
            blockers.append("INVALID_RISK_STRUCTURE")
            trace.failed_gates.append("RISK_STRUCTURE")
            risk_per_share = 0
            reward_per_share = 0
        else:
            risk_per_share = entry - stop
            reward_per_share = target - entry
            
        if risk_per_share <= 0 and "INVALID_RISK_STRUCTURE" not in blockers:
            blockers.append("INVALID_RISK_STRUCTURE")
            trace.failed_gates.append("RISK_STRUCTURE")
        elif reward_per_share <= 0:
            blockers.append("INVALID_REWARD_STRUCTURE")
            trace.failed_gates.append("REWARD_STRUCTURE")
        else:
            rr = reward_per_share / risk_per_share
            if rr < self.config.minimum_rr:
                blockers.append("RISK_GATE_FAILED_RR")
                trace.failed_gates.append("MINIMUM_RR")
            else:
                trace.passed_gates.append("RR_VALID")
                
        # 2. Data Quality & Evidence Gates
        data_quality = quant_data.get("data_quality", "VALID")
        if data_quality in ["INVALID", "INSUFFICIENT_DATA"]:
            blockers.append("DATA_QUALITY_GATE_FAILED")
            trace.failed_gates.append("DATA_QUALITY")
        elif data_quality == "STALE_DATA":
            # For live-like decision
            blockers.append("DATA_STALE")
            trace.failed_gates.append("DATA_FRESHNESS")
            
        research_completeness = research_data.get("completeness", "INSUFFICIENT")
        red_team_decision = research_data.get("red_team_decision", "BLOCK")
        
        if research_completeness == "INSUFFICIENT":
            blockers.append("RESEARCH_INSUFFICIENT")
            trace.failed_gates.append("RESEARCH_COMPLETENESS")
            
        if red_team_decision == "BLOCK":
            blockers.append("RED_TEAM_BLOCK")
            trace.failed_gates.append("RED_TEAM")
            
        # 3. Contradiction Gate
        contradictions = research_data.get("contradictions", [])
        has_major_contradiction = any(c.get("severity") == "HIGH" for c in contradictions)
        if has_major_contradiction:
            blockers.append("MAJOR_CONTRADICTION")
            trace.failed_gates.append("CONTRADICTION_GATE")
            
        # 4. Speculation Gate
        depends_on_speculation = research_data.get("depends_on_speculation", False)
        if depends_on_speculation:
            blockers.append("THESIS_DEPENDS_ON_SPECULATION")
            trace.failed_gates.append("SPECULATION_GATE")
            
        # 5. Confidence Gate
        confidence = research_data.get("confidence", 0)
        if confidence < self.config.minimum_confidence:
            blockers.append("LOW_CONFIDENCE")
            trace.failed_gates.append("CONFIDENCE_GATE")
            
        # 6. Portfolio & Position Limits
        if symbol in portfolio.current_positions:
            # We don't block just yet, but we change action to HOLD or SELL later
            pass
        elif portfolio.number_of_positions >= self.config.maximum_positions:
            blockers.append("MAX_POSITION_LIMIT_REACHED")
            trace.failed_gates.append("POSITION_LIMIT")
            
        # Sizing Calculation
        allowed_risk_amount = portfolio.capital * self.config.max_single_position_risk
        position_shares = 0
        position_lots = 0
        position_value = 0.0
        portfolio_risk_pct = 0.0
        
        if risk_per_share > 0 and not blockers:
            raw_shares = allowed_risk_amount / risk_per_share
            position_lots = int(raw_shares // self.config.lot_size)
            position_shares = position_lots * self.config.lot_size
            position_value = position_shares * entry
            
            if position_value > portfolio.available_cash:
                # scale down to available cash
                max_lots_by_cash = int((portfolio.available_cash // entry) // self.config.lot_size)
                position_lots = min(position_lots, max_lots_by_cash)
                position_shares = position_lots * self.config.lot_size
                position_value = position_shares * entry
                
            actual_risk = position_shares * risk_per_share
            
            risk_pct = (actual_risk / portfolio.capital) if portfolio.capital > 0 else 0
            projected_total_risk = portfolio.total_risk + risk_pct
            
            if projected_total_risk > self.config.max_portfolio_risk:
                blockers.append("PORTFOLIO_RISK_EXCEEDED")
                trace.failed_gates.append("PORTFOLIO_RISK")
            else:
                trace.passed_gates.append("PORTFOLIO_RISK_OK")
                portfolio_risk_pct = risk_pct

        # Determine Risk State and Action
        if blockers:
            risk_state = "RED"
            # Decide if AVOID or WAIT
            if "INVALID_RISK_STRUCTURE" in blockers or "MAJOR_CONTRADICTION" in blockers or "THESIS_DEPENDS_ON_SPECULATION" in blockers:
                action = "AVOID"
            else:
                action = "WAIT"
        else:
            risk_state = "GREEN"
            
        # Existing position logic overrides
        if symbol in portfolio.current_positions:
            if risk_state == "RED":
                action = "SELL"
            else:
                action = "HOLD"
                
        # Final safety check
        if action == "BUY" and position_shares <= 0:
            action = "WAIT"
            risk_state = "RED"
            blockers.append("ZERO_POSITION_SIZE")
            
        return {
            "action": action,
            "risk_state": risk_state,
            "blockers": blockers,
            "risk_per_share": risk_per_share if risk_per_share > 0 else 0,
            "reward_per_share": reward_per_share if reward_per_share > 0 else 0,
            "risk_reward_ratio": (reward_per_share / risk_per_share) if risk_per_share > 0 and reward_per_share > 0 else 0,
            "position_size": position_shares,
            "position_lots": position_lots,
            "position_value": position_value,
            "portfolio_risk": portfolio_risk_pct,
            "trace": trace
        }
