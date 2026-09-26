import pytest
from core.learning import LearningLedger, TradeLesson, MissedOpportunity, KnowledgePattern

def test_learning_ledger_win_classification():
    ledger = LearningLedger("tests/scratch/knowledge")
    
    pos_data = {
        "position_id": "test_win",
        "symbol": "BBCA",
        "realized_pnl": 500000,
        "realized_pnl_pct": 0.05,
        "close_reason": "TARGET_HIT"
    }
    context = {"signal_tier": "TIER 2", "timing_quality": "READY"}
    
    lesson = ledger.generate_lesson(pos_data, context)
    assert lesson.outcome_quality == "WIN"
    assert lesson.process_quality == "GOOD_TRADE"
    assert lesson.loss_type is None
    assert "knowledge_available_at" in lesson.model_dump()

def test_learning_ledger_loss_classification():
    ledger = LearningLedger("tests/scratch/knowledge")
    
    pos_data = {
        "position_id": "test_loss",
        "symbol": "GOTO",
        "realized_pnl": -200000,
        "realized_pnl_pct": -0.05,
        "close_reason": "STOP_LOSS"
    }
    
    lesson = ledger.generate_lesson(pos_data, {})
    assert lesson.outcome_quality == "LOSS"
    assert lesson.process_quality == "GOOD_THESIS_BAD_TIMING"
    assert lesson.loss_type == "TIMING_FAILURE"

def test_missed_opportunity():
    miss = MissedOpportunity(
        miss_id="M_01",
        symbol="BMRI",
        decision_date="2026-09-11",
        action_taken="AVOID",
        reason_for_action="Poor Liquidity",
        subsequent_max_favorable_excursion_pct=0.15,
        was_decision_correct=True,
        review_notes="Stock surged but liquidity was too low to safely enter sizing.",
        knowledge_available_at="2026-09-11T12:00:00Z"
    )
    assert miss.was_decision_correct is True

def test_knowledge_pattern():
    pattern = KnowledgePattern(
        knowledge_id="K_01",
        created_at="2026-09-11T12:00:00Z",
        knowledge_available_at="2026-09-11T12:00:00Z",
        pattern_type="Tier 2 Expectancy",
        observation="Tier 2 setups exhibit robust edge",
        evidence="Backtest across 5 years",
        confidence=85.0,
        sample_size=114,
        validation_status="SUPPORTED"
    )
    assert pattern.oos_validated is False
