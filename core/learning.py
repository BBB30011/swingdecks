from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json
import os
from pathlib import Path

class TradeLesson(BaseModel):
    lesson_id: str
    position_id: str
    symbol: str
    entry_date: str
    exit_date: str
    action: str
    entry_reason: str
    exit_reason: str
    
    # Process vs Outcome
    outcome: str = "BREAKEVEN" # WIN, LOSS, BREAKEVEN
    outcome_quality: str = "BREAKEVEN"  # WIN, LOSS, BREAKEVEN
    process_quality: str = "GOOD_TRADE"  # GOOD_TRADE, BAD_TRADE_LUCKY_WIN, GOOD_THESIS_BAD_TIMING, POOR_EXECUTION
    loss_type: Optional[str] = None # THESIS_FAILURE, TIMING_FAILURE, RISK_FAILURE, MARKET_REGIME_FAILURE, FALSE_BREAKOUT, CATALYST_PRICED_IN
    
    # Metrics
    realized_pnl: float
    realized_pnl_pct: float
    holding_period: int
    
    # Context
    signal_tier: str = "UNKNOWN"
    alert_urgency: str = "UNKNOWN"
    timing_quality: str = "UNKNOWN"
    market_regime: str = "UNKNOWN"
    sector: str = "UNKNOWN"
    
    # Extraction
    mistakes: str = ""
    what_worked: str = ""
    what_failed: str = ""
    knowledge_available_at: str

class MissedOpportunity(BaseModel):
    miss_id: str
    symbol: str
    decision_date: str
    action_taken: str # WAIT, AVOID
    reason_for_action: str
    subsequent_max_favorable_excursion_pct: float
    was_decision_correct: bool
    review_notes: str
    knowledge_available_at: str

class KnowledgePattern(BaseModel):
    knowledge_id: str
    created_at: str
    knowledge_available_at: str
    source_trade_ids: List[str] = []
    symbol: Optional[str] = None
    sector: Optional[str] = None
    market_regime: Optional[str] = None
    pattern_type: str
    observation: str
    evidence: str
    confidence: float
    sample_size: int
    validation_status: str # HYPOTHESIS, OBSERVED, SUPPORTED, OOS_SUPPORTED, CONTRADICTED, INVALIDATED, EXPIRED
    oos_validated: bool = False
    contradicted_by: Optional[str] = None
    expiry_date: Optional[str] = None

class LearningLedger:
    def __init__(self, directory: str = "knowledge"):
        self.directory = Path(directory)
        self.lessons_dir = self.directory / "lessons"
        self.success_dir = self.directory / "successful_setups"
        self.missed_dir = self.directory / "missed_opportunities"
        self.patterns_dir = self.directory / "patterns"
        
        self.lessons_dir.mkdir(parents=True, exist_ok=True)
        self.success_dir.mkdir(parents=True, exist_ok=True)
        self.missed_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
    def _evaluate_process_quality(self, outcome: str, close_reason: str, pnl_pct: float) -> str:
        if outcome == "WIN":
            if close_reason == "TARGET_HIT": return "GOOD_TRADE"
            return "BAD_TRADE_LUCKY_WIN" if pnl_pct < 0.02 else "GOOD_TRADE"
        elif outcome == "LOSS":
            if close_reason == "STOP_LOSS": return "GOOD_THESIS_BAD_TIMING"
            if close_reason == "THESIS_INVALIDATED": return "POOR_EXECUTION"
        return "UNKNOWN"

    def _determine_loss_type(self, outcome: str, close_reason: str) -> Optional[str]:
        if outcome != "LOSS": return None
        if close_reason == "STOP_LOSS": return "TIMING_FAILURE"
        if close_reason == "THESIS_INVALIDATED": return "THESIS_FAILURE"
        return "UNKNOWN"

    def generate_lesson(self, position_data: Any, context: Dict[str, Any]) -> TradeLesson:
        if hasattr(position_data, "model_dump"):
            pos_dict = position_data.model_dump()
        elif isinstance(position_data, dict):
            pos_dict = dict(position_data)
        else:
            pos_dict = getattr(position_data, "__dict__", {})

        pnl = pos_dict.get("realized_pnl", 0.0)
        pnl_pct = pos_dict.get("realized_pnl_pct", 0.0)
        if not pnl_pct:
            entry = pos_dict.get("entry_price") or 0.0
            close = pos_dict.get("close_price") or 0.0
            if entry > 0 and close > 0:
                pnl_pct = (close - entry) / entry
        close_reason = pos_dict.get("close_reason") or "UNKNOWN"
        
        outcome = "BREAKEVEN"
        if pnl > 0: outcome = "WIN"
        elif pnl < 0: outcome = "LOSS"
        
        process_quality = self._evaluate_process_quality(outcome, close_reason, pnl_pct)
        loss_type = self._determine_loss_type(outcome, close_reason)
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        return TradeLesson(
            lesson_id=f"L_{pos_dict.get('position_id', 'unknown')}",
            position_id=pos_dict.get("position_id", "unknown"),
            symbol=pos_dict.get("symbol", "UNKNOWN"),
            entry_date=pos_dict.get("entry_timestamp", "") or "",
            exit_date=pos_dict.get("closed_timestamp", "") or "",
            action="BUY",
            entry_reason=pos_dict.get("thesis", "") or "",
            exit_reason=close_reason,
            outcome=outcome,
            outcome_quality=outcome,
            process_quality=process_quality,
            loss_type=loss_type,
            realized_pnl=pnl,
            realized_pnl_pct=pnl_pct,
            holding_period=pos_dict.get("holding_bars", 0),
            signal_tier=context.get("signal_tier", "UNKNOWN"),
            alert_urgency=context.get("alert_urgency", "UNKNOWN"),
            timing_quality=context.get("timing_quality", "UNKNOWN"),
            market_regime=context.get("market_regime", "UNKNOWN"),
            sector=context.get("sector", "UNKNOWN"),
            mistakes="TBD" if outcome == "LOSS" else "",
            what_worked="TBD" if outcome == "WIN" else "",
            what_failed=str(loss_type) if loss_type else "",
            knowledge_available_at=timestamp
        )

    def save_lesson(self, lesson: TradeLesson):
        file_path = self.lessons_dir / f"{lesson.lesson_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(lesson.model_dump_json(indent=4))
        if getattr(lesson, "outcome", None) == "WIN" or getattr(lesson, "outcome_quality", None) == "WIN":
            succ_path = self.success_dir / f"{lesson.lesson_id}.json"
            with open(succ_path, "w", encoding="utf-8") as f:
                f.write(lesson.model_dump_json(indent=4))

    def log_missed_opportunity(self, missed: MissedOpportunity):
        file_path = self.missed_dir / f"{missed.miss_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(missed.model_dump_json(indent=4))
            
    def save_knowledge_pattern(self, pattern: KnowledgePattern):
        file_path = self.patterns_dir / f"{pattern.knowledge_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(pattern.model_dump_json(indent=4))

    def get_pattern_statistics(self, min_sample: int = 10) -> Dict[str, Any]:
        lessons = []
        if self.lessons_dir.exists():
            for p in self.lessons_dir.glob("*.json"):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        lessons.append(json.load(f))
                except Exception:
                    pass
        if len(lessons) < min_sample:
            return {"status": "INSUFFICIENT_SAMPLE", "sample_size": len(lessons)}
        sample_size = len(lessons)
        wins = sum(1 for l in lessons if l.get("realized_pnl", 0.0) > 0)
        win_rate = wins / sample_size if sample_size > 0 else 0.0
        avg_pnl = sum(l.get("realized_pnl", 0.0) for l in lessons) / sample_size if sample_size > 0 else 0.0
        return {
            "status": "VALID",
            "sample_size": sample_size,
            "win_rate": win_rate,
            "avg_pnl": avg_pnl
        }

