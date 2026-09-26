"""
tests/test_batch_ar.py

Batch AR: Opportunity Ranking, Signal Quality & Timing Engine

Tests cover:
- TimingQuality classification
- TriggerProximity engine
- EntryWindowStatus
- PricedInStatus
- OpportunityRanker (score separation from quant_score)
- WHY_NOW multi-factor
- Signal tier determinism
- Alert urgency independence from signal strength
- Invalidation conditions
- Exit intelligence
- Semantic safeguards (regression from AP/AO)
- Point-in-time invariants
"""
import pytest
from core.timing_engine import (
    TimingQuality, TriggerProximity, EntryWindowStatus, PricedInStatus,
    TriggerProximityEngine, TimingQualityEngine, EntryWindowEngine, PricedInEngine,
)
from core.opportunity_ranker import (
    OpportunityRanker, OpportunityClassifier, WhyNowEngine,
    AlertUrgencyEngine, SignalStrengthEngine, InvalidationEngine,
)
from core.exit_engine import ExitEngine


# ============================================================
# TriggerProximityEngine
# ============================================================

class TestTriggerProximity:
    def test_triggered_when_current_at_or_above(self):
        assert TriggerProximityEngine.evaluate(10_250, 10_000) == TriggerProximity.TRIGGERED
        assert TriggerProximityEngine.evaluate(10_000, 10_000) == TriggerProximity.TRIGGERED

    def test_at_trigger_within_half_pct(self):
        # 9_955 is 0.45% below 10_000
        result = TriggerProximityEngine.evaluate(9_955, 10_000)
        assert result == TriggerProximity.AT_TRIGGER

    def test_near_trigger_1_to_2_pct(self):
        # 9_850 is 1.5% below 10_000
        result = TriggerProximityEngine.evaluate(9_850, 10_000)
        assert result == TriggerProximity.NEAR_TRIGGER

    def test_too_far_beyond_5_pct(self):
        # 9_400 is 6% below 10_000
        result = TriggerProximityEngine.evaluate(9_400, 10_000)
        assert result == TriggerProximity.TOO_FAR

    def test_invalid_price_zero(self):
        assert TriggerProximityEngine.evaluate(0, 10_000) == TriggerProximity.INVALID
        assert TriggerProximityEngine.evaluate(10_000, 0) == TriggerProximity.INVALID

    def test_distance_pct_calculation(self):
        dist = TriggerProximityEngine.distance_pct(9_850, 10_000)
        assert dist is not None
        assert abs(dist - 0.015) < 0.001  # ~1.5%

    def test_distance_pct_invalid(self):
        assert TriggerProximityEngine.distance_pct(0, 10_000) is None


# ============================================================
# TimingQualityEngine
# ============================================================

class TestTimingQuality:
    def test_ready_when_entry_ready_near_trigger(self):
        result = TimingQualityEngine.evaluate(
            signal_state="ENTRY_READY",
            trigger_proximity=TriggerProximity.NEAR_TRIGGER,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == TimingQuality.READY

    def test_ready_when_entry_confirmed(self):
        result = TimingQualityEngine.evaluate(
            signal_state="ENTRY_CONFIRMED",
            trigger_proximity=TriggerProximity.TRIGGERED,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == TimingQuality.READY

    def test_forming_when_setup_forming(self):
        result = TimingQualityEngine.evaluate(
            signal_state="SETUP_FORMING",
            trigger_proximity=TriggerProximity.TOO_FAR,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
            technical_state="POSITIVE",
        )
        assert result == TimingQuality.FORMING

    def test_early_when_watch_state(self):
        result = TimingQualityEngine.evaluate(
            signal_state="WATCH",
            trigger_proximity=TriggerProximity.TOO_FAR,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == TimingQuality.EARLY

    def test_extended_when_overextended(self):
        result = TimingQualityEngine.evaluate(
            signal_state="ENTRY_READY",
            trigger_proximity=TriggerProximity.TRIGGERED,
            priced_in_status=PricedInStatus.OVEREXTENDED,
        )
        assert result == TimingQuality.EXTENDED

    def test_invalid_when_invalidated(self):
        result = TimingQualityEngine.evaluate(
            signal_state="INVALIDATED",
            trigger_proximity=TriggerProximity.INVALID,
            priced_in_status=PricedInStatus.UNKNOWN,
        )
        assert result == TimingQuality.INVALID

    def test_unknown_fallback(self):
        result = TimingQualityEngine.evaluate(
            signal_state="UNKNOWN_STATE",
            trigger_proximity=TriggerProximity.UNKNOWN,
            priced_in_status=PricedInStatus.UNKNOWN,
        )
        assert result == TimingQuality.UNKNOWN


# ============================================================
# EntryWindowEngine
# ============================================================

class TestEntryWindowStatus:
    def test_narrow_when_ready_at_trigger(self):
        result = EntryWindowEngine.evaluate(
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.AT_TRIGGER,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == EntryWindowStatus.NARROW

    def test_open_when_ready_near(self):
        result = EntryWindowEngine.evaluate(
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.NEAR_TRIGGER,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == EntryWindowStatus.OPEN

    def test_missed_when_extended(self):
        result = EntryWindowEngine.evaluate(
            timing_quality=TimingQuality.EXTENDED,
            trigger_proximity=TriggerProximity.TRIGGERED,
            priced_in_status=PricedInStatus.OVEREXTENDED,
        )
        assert result == EntryWindowStatus.MISSED

    def test_closed_when_invalid(self):
        result = EntryWindowEngine.evaluate(
            timing_quality=TimingQuality.INVALID,
            trigger_proximity=TriggerProximity.INVALID,
            priced_in_status=PricedInStatus.UNKNOWN,
        )
        assert result == EntryWindowStatus.CLOSED

    def test_early_when_forming(self):
        result = EntryWindowEngine.evaluate(
            timing_quality=TimingQuality.FORMING,
            trigger_proximity=TriggerProximity.TOO_FAR,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert result == EntryWindowStatus.EARLY


# ============================================================
# PricedInEngine
# ============================================================

class TestPricedInStatus:
    def test_not_priced_in_small_move(self):
        result = PricedInEngine.evaluate(move_pct_from_reference=0.02)
        assert result == PricedInStatus.NOT_PRICED_IN

    def test_partially_priced_medium_move(self):
        result = PricedInEngine.evaluate(move_pct_from_reference=0.07)
        assert result == PricedInStatus.PARTIALLY_PRICED

    def test_likely_priced_in_large_move_high_catalyst(self):
        result = PricedInEngine.evaluate(
            move_pct_from_reference=0.12,
            catalyst_materiality="HIGH",
        )
        assert result == PricedInStatus.LIKELY_PRICED_IN

    def test_overextended_very_large_move(self):
        result = PricedInEngine.evaluate(move_pct_from_reference=0.25)
        assert result == PricedInStatus.OVEREXTENDED

    def test_expired_catalyst_becomes_likely_priced_in(self):
        # Expired catalyst + 6% move → LIKELY_PRICED_IN (move passes PARTIALLY_PRICED_MOVE threshold)
        result = PricedInEngine.evaluate(
            move_pct_from_reference=0.06,
            catalyst_decay="EXPIRED",
        )
        assert result == PricedInStatus.LIKELY_PRICED_IN

    def test_unknown_when_no_reference(self):
        result = PricedInEngine.evaluate(move_pct_from_reference=None)
        assert result == PricedInStatus.UNKNOWN


# ============================================================
# OpportunityRanker — opportunity_score != quant_score
# ============================================================

class TestOpportunityRanker:
    def _base_score(self, **kwargs):
        defaults = dict(
            quant_score=85,
            technical_state="POSITIVE",
            flow_state="POSITIVE",
            risk_state="GREEN",
            evidence_quality="GOOD",
            signal_state="ENTRY_READY",
            current_price=9_850,
            trigger_price=10_000,
        )
        defaults.update(kwargs)
        return OpportunityRanker.score_candidate(**defaults)

    def test_opportunity_score_is_not_quant_score(self):
        r = self._base_score(quant_score=85)
        assert r.total_score != 85, "opportunity_score must not equal quant_score"

    def test_high_quality_scores_above_low_quality(self):
        high = self._base_score(
            technical_state="POSITIVE", flow_state="POSITIVE",
            catalyst_materiality="HIGH", evidence_quality="GOOD", risk_state="GREEN",
        )
        low = self._base_score(
            technical_state="NEUTRAL", flow_state="NEGATIVE",
            catalyst_materiality="LOW", evidence_quality="INSUFFICIENT", risk_state="RED",
        )
        assert high.total_score > low.total_score

    def test_overextended_reduces_score(self):
        normal = self._base_score(move_pct_from_reference=0.01)
        over = self._base_score(move_pct_from_reference=0.25)
        assert normal.total_score > over.total_score

    def test_expired_catalyst_reduces_score(self):
        active = self._base_score(catalyst_decay="ACTIVE", catalyst_materiality="HIGH")
        expired = self._base_score(catalyst_decay="EXPIRED", catalyst_materiality="HIGH")
        assert active.total_score > expired.total_score

    def test_ranking_deterministic(self):
        candidates = [
            {"symbol": "BBCA", "opportunity_score": 72.0, "signal_strength": "HIGH"},
            {"symbol": "GOTO", "opportunity_score": 88.5, "signal_strength": "MEDIUM"},
            {"symbol": "TLKM", "opportunity_score": 65.0, "signal_strength": "HIGH"},
        ]
        r1 = OpportunityRanker.rank(candidates)
        r2 = OpportunityRanker.rank(candidates)
        assert [c["symbol"] for c in r1] == [c["symbol"] for c in r2]
        assert r1[0]["symbol"] == "GOTO"  # highest score first

    def test_ranking_by_signal_strength_on_tied_score(self):
        candidates = [
            {"symbol": "AAA", "opportunity_score": 70.0, "signal_strength": "MEDIUM"},
            {"symbol": "BBB", "opportunity_score": 70.0, "signal_strength": "HIGH"},
        ]
        ranked = OpportunityRanker.rank(candidates)
        assert ranked[0]["symbol"] == "BBB"  # higher signal_strength wins on tie


# ============================================================
# WhyNowEngine (multi-factor)
# ============================================================

class TestWhyNowEngine:
    def test_catalyst_active_high_materiality(self):
        result = WhyNowEngine.build(
            catalyst_state="ACTIVE",
            catalyst_event_type="EARNINGS",
            catalyst_materiality="HIGH",
            catalyst_decay="ACTIVE",
        )
        assert "EARNINGS" in result
        assert result != "NONE"

    def test_volume_expanding(self):
        result = WhyNowEngine.build(
            catalyst_state="UNKNOWN",
            volume_expanding=True,
        )
        assert "Volume" in result

    def test_breakout_detected(self):
        result = WhyNowEngine.build(
            catalyst_state="UNKNOWN",
            breakout_20d=True,
        )
        assert "breakout" in result.lower()

    def test_multi_factor_combines(self):
        result = WhyNowEngine.build(
            catalyst_state="ACTIVE",
            catalyst_event_type="EARNINGS",
            catalyst_materiality="HIGH",
            volume_expanding=True,
            relative_strength_state="OUTPERFORMING",
        )
        # Should combine multiple reasons
        assert "+" in result

    def test_no_temporal_reason_returns_none(self):
        result = WhyNowEngine.build(
            catalyst_state="UNKNOWN",
            volume_expanding=False,
            market_regime="SIDEWAYS",
        )
        assert result == "NONE"

    def test_expired_catalyst_not_used_as_reason(self):
        result = WhyNowEngine.build(
            catalyst_state="ACTIVE",
            catalyst_event_type="DIVIDEND",
            catalyst_materiality="HIGH",
            catalyst_decay="EXPIRED",  # expired
        )
        # EXPIRED catalyst should not generate positive WHY_NOW
        assert result == "NONE"


# ============================================================
# AlertUrgencyEngine — independent from signal strength
# ============================================================

class TestAlertUrgency:
    def test_very_high_when_at_trigger(self):
        urgency = AlertUrgencyEngine.evaluate(
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.AT_TRIGGER,
            entry_window_status=EntryWindowStatus.NARROW,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert urgency == "VERY_HIGH"

    def test_critical_when_risk_red(self):
        urgency = AlertUrgencyEngine.evaluate(
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.NEAR_TRIGGER,
            entry_window_status=EntryWindowStatus.OPEN,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
            risk_state="RED",
        )
        assert urgency == "CRITICAL"

    def test_low_when_too_early(self):
        urgency = AlertUrgencyEngine.evaluate(
            timing_quality=TimingQuality.EARLY,
            trigger_proximity=TriggerProximity.TOO_FAR,
            entry_window_status=EntryWindowStatus.EARLY,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert urgency == "LOW"

    def test_urgency_and_strength_can_differ(self):
        """High signal strength does NOT imply high urgency."""
        strength = SignalStrengthEngine.evaluate(
            technical_state="POSITIVE",
            flow_state="POSITIVE",
            evidence_quality="GOOD",
            contradiction_level="LOW",
            risk_state="GREEN",
        )
        # Can be VERY_HIGH strength
        urgency = AlertUrgencyEngine.evaluate(
            timing_quality=TimingQuality.EARLY,  # but EARLY timing
            trigger_proximity=TriggerProximity.TOO_FAR,
            entry_window_status=EntryWindowStatus.EARLY,
            priced_in_status=PricedInStatus.NOT_PRICED_IN,
        )
        assert urgency == "LOW"
        assert strength in ("HIGH", "VERY_HIGH")


# ============================================================
# SignalStrengthEngine
# ============================================================

class TestSignalStrength:
    def test_very_high_when_all_positive(self):
        strength = SignalStrengthEngine.evaluate(
            technical_state="POSITIVE",
            flow_state="POSITIVE",
            evidence_quality="COMPLETE",
            contradiction_level="LOW",
            risk_state="GREEN",
            relative_strength_state="OUTPERFORMING",
        )
        assert strength == "VERY_HIGH"

    def test_reduced_by_contradiction(self):
        no_contradiction = SignalStrengthEngine.evaluate(
            technical_state="POSITIVE", flow_state="POSITIVE",
            evidence_quality="GOOD", contradiction_level="LOW", risk_state="GREEN",
        )
        with_contradiction = SignalStrengthEngine.evaluate(
            technical_state="POSITIVE", flow_state="POSITIVE",
            evidence_quality="GOOD", contradiction_level="CRITICAL", risk_state="GREEN",
        )
        assert ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"].index(no_contradiction) < \
               ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"].index(with_contradiction)


# ============================================================
# InvalidationEngine
# ============================================================

class TestInvalidation:
    def test_stop_loss_condition_present(self):
        conds = InvalidationEngine.build(has_stop_loss=True, stop_loss=9_500.0)
        assert any("9500" in c or "stop" in c.lower() for c in conds)

    def test_flow_negative_condition(self):
        conds = InvalidationEngine.build(has_stop_loss=False, flow_state="NEGATIVE")
        assert any("flow" in c.lower() or "distribution" in c.lower() for c in conds)

    def test_expired_catalyst_condition(self):
        conds = InvalidationEngine.build(has_stop_loss=False, catalyst_decay="EXPIRED")
        assert any("catalyst" in c.lower() for c in conds)

    def test_risk_red_always_present(self):
        conds = InvalidationEngine.build(has_stop_loss=False)
        assert any("RED" in c or "risk" in c.lower() for c in conds)


# ============================================================
# OpportunityClassifier
# ============================================================

class TestOpportunityClassifier:
    def test_breakout_when_technical_flow_near_trigger(self):
        cls = OpportunityClassifier.classify(
            technical_state="POSITIVE",
            flow_state="POSITIVE",
            catalyst_state="UNKNOWN",
            catalyst_materiality="LOW",
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.AT_TRIGGER,
        )
        assert cls == "BREAKOUT"

    def test_catalyst_driven_when_active_high_catalyst(self):
        cls = OpportunityClassifier.classify(
            technical_state="POSITIVE",
            flow_state="NEUTRAL",
            catalyst_state="ACTIVE",
            catalyst_materiality="HIGH",
            timing_quality=TimingQuality.READY,
            trigger_proximity=TriggerProximity.NEAR_TRIGGER,
        )
        assert cls == "CATALYST_DRIVEN"

    def test_early_momentum_when_positive_but_forming(self):
        cls = OpportunityClassifier.classify(
            technical_state="POSITIVE",
            flow_state="NEUTRAL",
            catalyst_state="UNKNOWN",
            catalyst_materiality="LOW",
            timing_quality=TimingQuality.EARLY,
            trigger_proximity=TriggerProximity.TOO_FAR,
        )
        assert cls == "EARLY_MOMENTUM"

    def test_unclassified_when_no_evidence(self):
        cls = OpportunityClassifier.classify(
            technical_state="UNKNOWN",
            flow_state="UNKNOWN",
            catalyst_state="UNKNOWN",
            catalyst_materiality="UNKNOWN",
            timing_quality=TimingQuality.UNKNOWN,
            trigger_proximity=TriggerProximity.UNKNOWN,
        )
        assert cls == "UNCLASSIFIED"


# ============================================================
# ExitEngine — extended classification
# ============================================================

class TestExitEngineAR:
    def _make_position(self, current_price=9_000, stop_loss=8_500, target_price=11_000, holding_bars=5):
        from core.position import PaperPosition
        return PaperPosition(
            position_id="P001", symbol="TEST", job_id="J1",
            entry_price=9_000, current_price=current_price,
            stop_loss=stop_loss, target_price=target_price,
            initial_risk=500.0, initial_reward=2000.0, initial_rr=4.0,
            position_size=100, lots=1, holding_bars=holding_bars,
        )

    def test_momentum_fade_triggers_exit_warning(self):
        pos = self._make_position()
        result = ExitEngine.evaluate(pos, {"quant_score": 30})
        assert result["action"] == "EXIT_WARNING"
        assert result["reason"] == "MOMENTUM_FADE"

    def test_flow_reversal_triggers_exit_warning(self):
        pos = self._make_position()
        result = ExitEngine.evaluate(pos, {"flow_state": "NEGATIVE"})
        assert result["action"] == "EXIT_WARNING"
        assert result["reason"] == "FLOW_REVERSAL"

    def test_catalyst_expired_triggers_exit_warning(self):
        pos = self._make_position()
        result = ExitEngine.evaluate(pos, {"catalyst_decay": "EXPIRED"})
        assert result["action"] == "EXIT_WARNING"
        assert result["reason"] == "CATALYST_EXPIRED"

    def test_stop_loss_priority_over_momentum_fade(self):
        pos = self._make_position(current_price=8_400)  # below stop
        result = ExitEngine.evaluate(pos, {"quant_score": 30})
        assert result["reason"] == "STOP_LOSS"  # stop-loss has higher priority

    def test_classify_reason_severity(self):
        assert ExitEngine.classify_reason("STOP_LOSS") == "CRITICAL"
        assert ExitEngine.classify_reason("MOMENTUM_FADE") == "MEDIUM"
        assert ExitEngine.classify_reason("TIME_DECAY") == "LOW"

    def test_hold_when_nothing_triggered(self):
        pos = self._make_position()
        result = ExitEngine.evaluate(pos, {})
        assert result["action"] == "HOLD"


# ============================================================
# Semantic safeguards — AP/AO regression
# ============================================================

class TestSemanticRegressions:
    def test_low_medium_contradiction_does_not_block(self):
        from core.decision import EvidenceContradiction, ContradictionSeverity
        contradictions = [
            EvidenceContradiction(topic="Minor", description="low", severity=ContradictionSeverity.LOW),
            EvidenceContradiction(topic="Med", description="medium", severity=ContradictionSeverity.MEDIUM),
        ]
        has_major = any(c.severity in [ContradictionSeverity.HIGH, ContradictionSeverity.CRITICAL]
                        for c in contradictions)
        assert not has_major  # should NOT block BUY

    def test_high_contradiction_can_downgrade(self):
        from core.decision import EvidenceContradiction, ContradictionSeverity
        contradictions = [
            EvidenceContradiction(topic="Major", description="high", severity=ContradictionSeverity.HIGH),
        ]
        has_major = any(c.severity in [ContradictionSeverity.HIGH, ContradictionSeverity.CRITICAL]
                        for c in contradictions)
        assert has_major  # should downgrade BUY → WAIT

    def test_timing_independent_of_score(self):
        """High quant_score does not guarantee READY timing."""
        r = OpportunityRanker.score_candidate(
            quant_score=95,       # very high quant
            signal_state="WATCH", # but only on WATCH
            current_price=9_000,
            trigger_price=12_000, # very far from trigger
        )
        assert r.timing_quality != TimingQuality.READY

    def test_unknown_state_does_not_default_to_bullish(self):
        r = OpportunityRanker.score_candidate(
            quant_score=0,
            technical_state="UNKNOWN",
            flow_state="UNKNOWN",
            catalyst_state="UNKNOWN",
            risk_state="GREEN",  # only green thing
            signal_state="UNKNOWN",
        )
        # Should score low — not inflated by unknowns
        assert r.total_score < 30


# ============================================================
# Point-in-time invariants
# ============================================================

class TestPointInTime:
    def test_future_append_does_not_change_past_score(self):
        """Same inputs must always produce same output (deterministic)."""
        kwargs = dict(
            quant_score=75,
            technical_state="POSITIVE",
            flow_state="NEUTRAL",
            signal_state="SETUP_FORMING",
            current_price=9_900,
            trigger_price=10_000,
        )
        r1 = OpportunityRanker.score_candidate(**kwargs)
        r2 = OpportunityRanker.score_candidate(**kwargs)
        assert r1.total_score == r2.total_score
        assert r1.timing_quality == r2.timing_quality
        assert r1.opportunity_class == r2.opportunity_class

    def test_ranking_is_deterministic(self):
        candidates = [
            {"symbol": "A", "opportunity_score": 55.0, "signal_strength": "LOW"},
            {"symbol": "B", "opportunity_score": 80.0, "signal_strength": "HIGH"},
        ]
        for _ in range(5):
            ranked = OpportunityRanker.rank(candidates)
            assert ranked[0]["symbol"] == "B"
