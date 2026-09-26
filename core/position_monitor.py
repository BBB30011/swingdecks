from typing import Dict, Any, List
from core.position import PaperPosition, PositionMonitorEvent
from core.exit_engine import ExitEngine
from core.materiality import MaterialityEngine
import uuid

class PositionMonitorResult:
    def __init__(self, position: PaperPosition, events: List[PositionMonitorEvent], action: str, reason: str):
        self.position_id = position.position_id
        self.symbol = position.symbol
        self.timestamp = position.current_price # Need a way to pass timestamp
        self.current_price = position.current_price
        self.unrealized_pnl = position.unrealized_pnl
        self.unrealized_pnl_pct = position.unrealized_pnl_pct
        self.distance_to_stop = (position.current_price - position.stop_loss) / position.current_price if position.current_price and position.stop_loss else 0
        self.distance_to_target = (position.target_price - position.current_price) / position.current_price if position.current_price and position.target_price else 0
        self.stop_triggered = reason == "STOP_LOSS"
        self.target_triggered = reason == "TARGET_REACHED"
        self.thesis_invalidated = reason == "THESIS_INVALIDATED"
        self.risk_state = "UNKNOWN"
        self.action = action
        self.reason = reason
        self.events = events

class PositionMonitor:
    @staticmethod
    def monitor(position: PaperPosition, current_price: float, current_timestamp: str, context: Dict[str, Any]) -> PositionMonitorResult:
        events = []
        
        # Determine safety if data invalid
        if context.get("data_quality") == "INVALID":
            # Do not fabricate price, use existing or None
            # But we must generate an event
            events.append(PositionMonitorEvent(
                event_id=str(uuid.uuid4()),
                position_id=position.position_id,
                symbol=position.symbol,
                timestamp=current_timestamp,
                event_type="DATA_QUALITY_CHANGED",
                severity="CRITICAL",
                reason="Market data invalid"
            ))
            
        else:
            # Update price
            prev_price = position.current_price
            position.update_price(current_price)
            position.holding_bars += 1
            
            # Check materiality of price move
            severity = MaterialityEngine.classify_price_movement(
                position.current_price, position.entry_price, position.stop_loss, position.target_price
            )
            
            if severity != "LOW":
                event_type = "PRICE_UPDATE"
                if severity == "CRITICAL":
                    if position.current_price <= position.stop_loss:
                        event_type = "STOP_TRIGGERED"
                    else:
                        event_type = "TARGET_TRIGGERED"
                elif severity == "HIGH":
                    if position.current_price - position.stop_loss < position.target_price - position.current_price:
                        event_type = "STOP_APPROACHING"
                    else:
                        event_type = "TARGET_APPROACHING"
                        
                events.append(PositionMonitorEvent(
                    event_id=str(uuid.uuid4()),
                    position_id=position.position_id,
                    symbol=position.symbol,
                    timestamp=current_timestamp,
                    event_type=event_type,
                    severity=severity,
                    previous_value=prev_price,
                    current_value=position.current_price,
                    reason=f"Significant price movement to {position.current_price}"
                ))

        # Check Risk State changes
        risk_state = context.get("risk_state", "GREEN")
        # Assume context passes prev_risk_state if changed
        if "prev_risk_state" in context and context["prev_risk_state"] != risk_state:
            severity = "HIGH" if risk_state == "RED" else "MEDIUM"
            events.append(PositionMonitorEvent(
                event_id=str(uuid.uuid4()),
                position_id=position.position_id,
                symbol=position.symbol,
                timestamp=current_timestamp,
                event_type="RISK_CHANGED",
                severity=severity,
                previous_value=context["prev_risk_state"],
                current_value=risk_state,
                reason=f"Risk changed to {risk_state}"
            ))

        # Check Thesis invalidation
        active_invals = context.get("active_invalidations", [])
        if active_invals:
            position.invalidation_conditions = active_invals
            events.append(PositionMonitorEvent(
                event_id=str(uuid.uuid4()),
                position_id=position.position_id,
                symbol=position.symbol,
                timestamp=current_timestamp,
                event_type="THESIS_INVALIDATED",
                severity="CRITICAL",
                current_value=active_invals,
                reason="Thesis invalidated by context"
            ))

        # Evaluate exit
        exit_res = ExitEngine.evaluate(position, context)
        
        result = PositionMonitorResult(
            position=position,
            events=events,
            action=exit_res["action"],
            reason=exit_res["reason"]
        )
        result.timestamp = current_timestamp
        result.risk_state = risk_state
        return result
