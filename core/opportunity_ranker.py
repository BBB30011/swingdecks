"""
core/opportunity_ranker.py

Batch AR: Opportunity Ranker — scores and ranks opportunity candidates.

IMPORTANT:
  - opportunity_score is SEPARATE from quant_score.
  - quant_score measures technical/quant signal strength.
  - opportunity_score measures "how attractive is this opportunity RIGHT NOW."
  - All weights: PRELIMINARY / NOT EMPIRICALLY VALIDATED.
  - No profitability claims. No predictive value claims.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from core.timing_engine import (
    TimingQuality, TriggerProximity, EntryWindowStatus, PricedInStatus,
    TriggerProximityEngine, TimingQualityEngine, EntryWindowEngine, PricedInEngine
)


# ---------------------------------------------------------------------------
# Opportunity Score Factors (weights PRELIMINARY / NOT EMPIRICALLY VALIDATED)
# ---------------------------------------------------------------------------

FACTOR_WEIGHTS = {
    "technical":        18,   # quant signal quality (contributes but not = quant_score)
    "flow":             14,   # volume/flow confirmation
    "relative_strength": 10,  # outperformance vs benchmark
    "sector":            8,   # sector leadership context
    "market_regime":     8,   # market regime support
    "catalyst":         14,   # active catalyst materiality
    "evidence_quality": 10,   # completeness/credibility of evidence
    "risk":             12,   # risk grade (GREEN vs RED)
    "timing":            6,   # timing bonus (READY > FORMING > EARLY)
}

TOTAL_WEIGHT = sum(FACTOR_WEIGHTS.values())  # = 100


@dataclass
class OpportunityScoreResult:
    """Decomposed opportunity score. NOT a probability of profit."""
    total_score: float = 0.0
    factor_scores: Dict[str, float] = field(default_factory=dict)
    timing_quality: TimingQuality = TimingQuality.UNKNOWN
    trigger_proximity: TriggerProximity = TriggerProximity.UNKNOWN
    entry_window_status: EntryWindowStatus = EntryWindowStatus.UNKNOWN
    priced_in_status: PricedInStatus = PricedInStatus.UNKNOWN
    signal_strength: str = "UNKNOWN"
    alert_urgency: str = "MEDIUM"
    opportunity_class: str = "UNCLASSIFIED"
    why_now: str = "NONE"
    invalidation_conditions: List[str] = field(default_factory=list)
    distance_to_trigger_pct: Optional[float] = None
    score_note: str = "PRELIMINARY / NOT EMPIRICALLY VALIDATED"


# ---------------------------------------------------------------------------
# State → Numeric mapping helpers
# ---------------------------------------------------------------------------

_STATE_SCORE = {
    "POSITIVE": 1.0, "CONFIRMED": 1.0, "RISING": 1.0, "ACTIVE": 1.0,
    "NEUTRAL": 0.5, "MIXED": 0.5, "UNKNOWN": 0.0,
    "NEGATIVE": 0.0, "EXPIRED": 0.0, "WEAK": 0.2,
    "OUTPERFORMING": 1.0, "UNDERPERFORMING": 0.0,
    "BULL": 1.0, "BEAR": 0.0, "SIDEWAYS": 0.5,
    "GREEN": 1.0, "YELLOW": 0.5, "RED": 0.0,
    "COMPLETE": 1.0, "GOOD": 0.8, "PARTIAL": 0.5, "INSUFFICIENT": 0.0,
}

_MATERIALITY_SCORE = {"CRITICAL": 1.0, "HIGH": 0.85, "MEDIUM": 0.55, "LOW": 0.2, "UNKNOWN": 0.0}

_TIMING_BONUS = {
    TimingQuality.READY:    1.0,
    TimingQuality.FORMING:  0.7,
    TimingQuality.EARLY:    0.4,
    TimingQuality.LATE:     0.2,
    TimingQuality.EXTENDED: 0.0,
    TimingQuality.INVALID:  0.0,
    TimingQuality.UNKNOWN:  0.0,
}

def _s(state: str) -> float:
    return _STATE_SCORE.get(state, 0.0)


# ---------------------------------------------------------------------------
# Opportunity Classifier
# ---------------------------------------------------------------------------

class OpportunityClassifier:
    """
    Assigns semantic opportunity_class based on available evidence.
    Only assigns a specific class if evidence supports it.
    Defaults to UNCLASSIFIED.
    """

    @staticmethod
    def classify(
        technical_state: str,
        flow_state: str,
        catalyst_state: str,
        catalyst_materiality: str,
        timing_quality: TimingQuality,
        trigger_proximity: TriggerProximity,
        relative_strength_state: str = "UNKNOWN",
        sector_state: str = "UNKNOWN",
    ) -> str:
        is_technical_positive = technical_state == "POSITIVE"
        is_flow_positive = flow_state in ("POSITIVE", "CONFIRMED")
        is_catalyst_active = catalyst_state == "ACTIVE"
        has_high_catalyst = catalyst_materiality in ("HIGH", "CRITICAL")
        is_breakout_near = trigger_proximity in (
            TriggerProximity.AT_TRIGGER, TriggerProximity.TRIGGERED, TriggerProximity.NEAR_TRIGGER
        )
        is_rs_outperforming = relative_strength_state == "OUTPERFORMING"
        is_sector_positive = sector_state == "POSITIVE"

        # CATALYST_DRIVEN: active high-impact catalyst + technical support
        if is_catalyst_active and has_high_catalyst and is_technical_positive:
            return "CATALYST_DRIVEN"

        # BREAKOUT: technical positive + flow confirming + near trigger
        if is_technical_positive and is_flow_positive and is_breakout_near:
            return "BREAKOUT"

        # SECTOR_ROTATION: strong sector + relative outperformance
        if is_sector_positive and is_rs_outperforming and is_technical_positive:
            return "SECTOR_ROTATION"

        # EARLY_MOMENTUM: positive tech but forming, not yet at trigger
        if is_technical_positive and timing_quality in (TimingQuality.EARLY, TimingQuality.FORMING):
            return "EARLY_MOMENTUM"

        # MOMENTUM_CONTINUATION: triggered + positive flow
        if trigger_proximity == TriggerProximity.TRIGGERED and is_flow_positive:
            return "MOMENTUM_CONTINUATION"

        return "UNCLASSIFIED"


# ---------------------------------------------------------------------------
# WHY NOW Engine (multi-factor)
# ---------------------------------------------------------------------------

class WhyNowEngine:
    """
    Generates a temporal explanation for WHY this stock is interesting NOW.
    Only uses evidence available at as_of_timestamp.
    Returns 'NONE' if no strong temporal reason exists.
    """

    @staticmethod
    def build(
        catalyst_state: str,
        catalyst_event_type: str = "",
        catalyst_materiality: str = "UNKNOWN",
        catalyst_decay: str = "UNKNOWN",
        flow_state: str = "UNKNOWN",
        technical_state: str = "UNKNOWN",
        trigger_proximity: TriggerProximity = TriggerProximity.UNKNOWN,
        relative_strength_state: str = "UNKNOWN",
        sector_state: str = "UNKNOWN",
        market_regime: str = "UNKNOWN",
        breakout_20d: Optional[bool] = None,
        volume_expanding: bool = False,
    ) -> str:
        reasons = []

        # Priority 1: Active high-impact catalyst
        if catalyst_state == "ACTIVE" and catalyst_decay != "EXPIRED":
            if catalyst_materiality in ("HIGH", "CRITICAL"):
                event_label = f" ({catalyst_event_type})" if catalyst_event_type else ""
                reasons.append(f"High-impact catalyst active{event_label}")
            else:
                reasons.append("Catalyst active")

        # Priority 2: Technical breakout event
        if breakout_20d is True:
            reasons.append("20-day breakout detected")
        elif trigger_proximity in (TriggerProximity.AT_TRIGGER, TriggerProximity.NEAR_TRIGGER):
            reasons.append("Near breakout trigger")

        # Priority 3: Volume confirmation
        if volume_expanding or flow_state in ("POSITIVE", "CONFIRMED"):
            reasons.append("Volume expanding" if volume_expanding else "Flow confirming")

        # Priority 4: Relative strength acceleration
        if relative_strength_state == "OUTPERFORMING":
            reasons.append("Outperforming benchmark")

        # Priority 5: Sector leadership
        if sector_state == "POSITIVE":
            reasons.append("Sector outperforming")

        # Priority 6: Supportive regime
        if market_regime == "BULL" and not reasons:
            reasons.append("Supportive market regime")

        if not reasons:
            return "NONE"

        return " + ".join(reasons)


# ---------------------------------------------------------------------------
# Urgency Engine
# ---------------------------------------------------------------------------

class AlertUrgencyEngine:
    """
    Determines alert urgency INDEPENDENTLY from signal strength.
    High-quality signal + no timing pressure → LOW urgency
    Good signal + trigger imminent → VERY_HIGH urgency
    """

    @staticmethod
    def evaluate(
        timing_quality: TimingQuality,
        trigger_proximity: TriggerProximity,
        entry_window_status: EntryWindowStatus,
        priced_in_status: PricedInStatus,
        risk_state: str = "GREEN",
        has_exit_condition: bool = False,
    ) -> str:
        # CRITICAL: exit event happening
        if has_exit_condition or risk_state == "RED":
            return "CRITICAL"

        # VERY_HIGH: trigger is AT or just TRIGGERED, window NARROW
        if trigger_proximity in (TriggerProximity.AT_TRIGGER, TriggerProximity.TRIGGERED):
            if entry_window_status not in (EntryWindowStatus.MISSED, EntryWindowStatus.CLOSED):
                return "VERY_HIGH"

        # HIGH: NEAR trigger, window still OPEN, timing READY
        if trigger_proximity == TriggerProximity.NEAR_TRIGGER and timing_quality == TimingQuality.READY:
            return "HIGH"

        # MEDIUM: FORMING, window still EARLY or OPEN
        if timing_quality in (TimingQuality.FORMING, TimingQuality.READY):
            return "MEDIUM"

        # LOW: too early, too far, or priced in
        if timing_quality in (TimingQuality.EARLY, TimingQuality.EXTENDED, TimingQuality.LATE):
            return "LOW"

        return "MEDIUM"


# ---------------------------------------------------------------------------
# Signal Strength Engine
# ---------------------------------------------------------------------------

class SignalStrengthEngine:
    """
    Measures quality of the signal (not urgency).
    Based on the number of positive aligned factors.
    """

    @staticmethod
    def evaluate(
        technical_state: str,
        flow_state: str,
        evidence_quality: str,
        contradiction_level: str,
        risk_state: str,
        relative_strength_state: str = "UNKNOWN",
    ) -> str:
        score = 0
        score += 2 if technical_state == "POSITIVE" else 1 if technical_state == "NEUTRAL" else 0
        score += 2 if flow_state in ("POSITIVE", "CONFIRMED") else 1 if flow_state == "NEUTRAL" else 0
        score += 2 if evidence_quality in ("COMPLETE", "GOOD") else 1 if evidence_quality == "PARTIAL" else 0
        score += 1 if relative_strength_state == "OUTPERFORMING" else 0
        score -= 2 if contradiction_level in ("HIGH", "CRITICAL") else 0
        score -= 1 if risk_state == "RED" else 0

        if score >= 6:
            return "VERY_HIGH"
        elif score >= 4:
            return "HIGH"
        elif score >= 2:
            return "MEDIUM"
        else:
            return "LOW"


# ---------------------------------------------------------------------------
# Invalidation Condition Builder
# ---------------------------------------------------------------------------

class InvalidationEngine:
    """
    Builds a list of explicit invalidation conditions for an opportunity.
    Point-in-time safe — only uses evidence available at decision time.
    """

    @staticmethod
    def build(
        has_stop_loss: bool,
        stop_loss: float = 0.0,
        trigger_type: str = "UNKNOWN",
        catalyst_decay: str = "UNKNOWN",
        flow_state: str = "UNKNOWN",
        technical_state: str = "UNKNOWN",
        sector_state: str = "UNKNOWN",
    ) -> List[str]:
        conditions = []

        if has_stop_loss and stop_loss > 0:
            conditions.append(f"Price closes below stop-loss ({stop_loss:.0f})")

        if trigger_type not in ("UNKNOWN", ""):
            conditions.append(f"Breakout fails — price retreats below trigger")

        if flow_state == "NEGATIVE":
            conditions.append("Flow turns negative (distribution signal)")

        if technical_state == "NEGATIVE":
            conditions.append("Technical structure deteriorates")

        if sector_state == "NEGATIVE":
            conditions.append("Sector regime breaks down")

        if catalyst_decay == "EXPIRED":
            conditions.append("Catalyst expired without price follow-through")

        conditions.append("Risk state turns RED")
        conditions.append("Thesis deteriorates materially")

        return conditions


# ---------------------------------------------------------------------------
# Main Opportunity Ranker
# ---------------------------------------------------------------------------

class OpportunityRanker:
    """
    Ranks a list of scan candidates by opportunity quality.
    Input: list of dicts with quant scan results + research summary.
    Output: list sorted by opportunity_score DESC.
    """

    @staticmethod
    def score_candidate(
        quant_score: float,
        technical_state: str = "UNKNOWN",
        flow_state: str = "UNKNOWN",
        relative_strength_state: str = "UNKNOWN",
        sector_state: str = "UNKNOWN",
        market_regime: str = "UNKNOWN",
        catalyst_materiality: str = "UNKNOWN",
        catalyst_decay: str = "UNKNOWN",
        evidence_quality: str = "UNKNOWN",
        risk_state: str = "GREEN",
        signal_state: str = "WATCH",
        current_price: float = 0.0,
        trigger_price: float = 0.0,
        stop_loss: float = 0.0,
        catalyst_state: str = "UNKNOWN",
        catalyst_event_type: str = "",
        volume_expanding: bool = False,
        breakout_20d: Optional[bool] = None,
        move_pct_from_reference: Optional[float] = None,
    ) -> OpportunityScoreResult:
        """
        Computes a transparent, factor-decomposed opportunity score.
        Score range: 0–100. NOT a probability of profit.
        Weights: PRELIMINARY / NOT EMPIRICALLY VALIDATED.
        """

        # --- Factor scores (0.0 to 1.0) ---
        f = {}

        # Technical: based on quant_score bracket, NOT = quant_score
        if quant_score >= 80:
            f["technical"] = 1.0
        elif quant_score >= 70:
            f["technical"] = 0.75
        elif quant_score >= 60:
            f["technical"] = 0.5
        else:
            f["technical"] = 0.2

        f["flow"] = _s(flow_state)
        f["relative_strength"] = _s(relative_strength_state)
        f["sector"] = _s(sector_state)
        f["market_regime"] = _s(market_regime)

        # Catalyst: combine materiality + decay
        if catalyst_decay == "EXPIRED":
            f["catalyst"] = 0.0
        else:
            f["catalyst"] = _MATERIALITY_SCORE.get(catalyst_materiality, 0.0)

        f["evidence_quality"] = _s(evidence_quality)
        f["risk"] = _s(risk_state)

        # Trigger proximity + timing
        trig_prox = TriggerProximityEngine.evaluate(current_price, trigger_price)
        dist_pct = TriggerProximityEngine.distance_pct(current_price, trigger_price)

        priced_in = PricedInEngine.evaluate(
            move_pct_from_reference=move_pct_from_reference,
            catalyst_materiality=catalyst_materiality,
            catalyst_decay=catalyst_decay,
        )

        timing = TimingQualityEngine.evaluate(
            signal_state=signal_state,
            trigger_proximity=trig_prox,
            priced_in_status=priced_in,
            technical_state=technical_state,
            evidence_state=evidence_quality,
        )

        entry_window = EntryWindowEngine.evaluate(
            timing_quality=timing,
            trigger_proximity=trig_prox,
            priced_in_status=priced_in,
            signal_state=signal_state,
        )

        f["timing"] = _TIMING_BONUS.get(timing, 0.0)

        # Penalize if priced in
        if priced_in == PricedInStatus.OVEREXTENDED:
            for key in f:
                f[key] *= 0.5  # halve all scores if overextended
        elif priced_in == PricedInStatus.LIKELY_PRICED_IN:
            for key in f:
                f[key] *= 0.7

        # --- Compute weighted total ---
        weighted = {k: f.get(k, 0.0) * FACTOR_WEIGHTS.get(k, 0) for k in FACTOR_WEIGHTS}
        raw_total = sum(weighted.values())
        total_score = min(raw_total, 100.0)

        # --- Derived classifications ---
        opp_class = OpportunityClassifier.classify(
            technical_state=technical_state,
            flow_state=flow_state,
            catalyst_state=catalyst_state,
            catalyst_materiality=catalyst_materiality,
            timing_quality=timing,
            trigger_proximity=trig_prox,
            relative_strength_state=relative_strength_state,
            sector_state=sector_state,
        )

        why_now = WhyNowEngine.build(
            catalyst_state=catalyst_state,
            catalyst_event_type=catalyst_event_type,
            catalyst_materiality=catalyst_materiality,
            catalyst_decay=catalyst_decay,
            flow_state=flow_state,
            technical_state=technical_state,
            trigger_proximity=trig_prox,
            relative_strength_state=relative_strength_state,
            sector_state=sector_state,
            market_regime=market_regime,
            breakout_20d=breakout_20d,
            volume_expanding=volume_expanding,
        )

        signal_strength = SignalStrengthEngine.evaluate(
            technical_state=technical_state,
            flow_state=flow_state,
            evidence_quality=evidence_quality,
            contradiction_level="UNKNOWN",
            risk_state=risk_state,
            relative_strength_state=relative_strength_state,
        )

        alert_urgency = AlertUrgencyEngine.evaluate(
            timing_quality=timing,
            trigger_proximity=trig_prox,
            entry_window_status=entry_window,
            priced_in_status=priced_in,
            risk_state=risk_state,
        )

        invalidation = InvalidationEngine.build(
            has_stop_loss=stop_loss > 0,
            stop_loss=stop_loss,
            trigger_type="BREAKOUT",
            catalyst_decay=catalyst_decay,
            flow_state=flow_state,
            technical_state=technical_state,
            sector_state=sector_state,
        )

        return OpportunityScoreResult(
            total_score=round(total_score, 2),
            factor_scores={k: round(v, 3) for k, v in weighted.items()},
            timing_quality=timing,
            trigger_proximity=trig_prox,
            entry_window_status=entry_window,
            priced_in_status=priced_in,
            signal_strength=signal_strength,
            alert_urgency=alert_urgency,
            opportunity_class=opp_class,
            why_now=why_now,
            invalidation_conditions=invalidation,
            distance_to_trigger_pct=round(dist_pct * 100, 2) if dist_pct is not None else None,
        )

    @staticmethod
    def rank(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks candidates by opportunity_score DESC.
        Deterministic: same input always produces same output.
        Secondary: signal_strength rank, tertiary: symbol ASC.
        """
        STRENGTH_RANK = {"VERY_HIGH": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

        def sort_key(c):
            opp_score = c.get("opportunity_score", 0.0)
            strength = STRENGTH_RANK.get(c.get("signal_strength", "UNKNOWN"), 0)
            symbol = c.get("symbol", "")
            return (-opp_score, -strength, symbol)

        return sorted(candidates, key=sort_key)
