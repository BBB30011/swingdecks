"""
core/timing_engine.py

Timing Engine for Batch AR.
Provides deterministic classification of:
  - TimingQuality (EARLY/FORMING/READY/LATE/EXTENDED/INVALID/UNKNOWN)
  - TriggerProximity (TOO_FAR/NEAR_TRIGGER/AT_TRIGGER/TRIGGERED/INVALID/UNKNOWN)
  - EntryWindowStatus (EARLY/OPEN/NARROW/MISSED/CLOSED/UNKNOWN)
  - PricedInStatus (NOT_PRICED_IN/PARTIALLY_PRICED/LIKELY_PRICED_IN/OVEREXTENDED/UNKNOWN)

NOTE: All thresholds are PRELIMINARY / NOT EMPIRICALLY VALIDATED.
      Do NOT tune these based on synthetic data.
      These represent reasonable conservative starting points only.
"""
from typing import Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TimingQuality(str, Enum):
    EARLY = "EARLY"
    FORMING = "FORMING"
    READY = "READY"
    LATE = "LATE"
    EXTENDED = "EXTENDED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class TriggerProximity(str, Enum):
    TOO_FAR = "TOO_FAR"
    NEAR_TRIGGER = "NEAR_TRIGGER"
    AT_TRIGGER = "AT_TRIGGER"
    TRIGGERED = "TRIGGERED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class EntryWindowStatus(str, Enum):
    EARLY = "EARLY"
    OPEN = "OPEN"
    NARROW = "NARROW"
    MISSED = "MISSED"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"


class PricedInStatus(str, Enum):
    NOT_PRICED_IN = "NOT_PRICED_IN"
    PARTIALLY_PRICED = "PARTIALLY_PRICED"
    LIKELY_PRICED_IN = "LIKELY_PRICED_IN"
    OVEREXTENDED = "OVEREXTENDED"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Trigger Proximity Engine
# ---------------------------------------------------------------------------

class TriggerProximityEngine:
    """
    Determines how close current_price is to trigger_price.
    All thresholds: PRELIMINARY / NOT EMPIRICALLY VALIDATED.
    """

    # Distance thresholds (percentage of trigger_price)
    TOO_FAR_THRESHOLD = 0.05      # > 5% away
    NEAR_TRIGGER_THRESHOLD = 0.02  # 2–5% away
    AT_TRIGGER_THRESHOLD = 0.005  # < 0.5% away (at or touching)

    @classmethod
    def evaluate(
        cls,
        current_price: float,
        trigger_price: float,
    ) -> TriggerProximity:
        if current_price <= 0 or trigger_price <= 0:
            return TriggerProximity.INVALID

        distance_pct = (trigger_price - current_price) / trigger_price

        # TRIGGERED: current >= trigger
        if current_price >= trigger_price:
            return TriggerProximity.TRIGGERED

        distance_abs = abs(distance_pct)

        if distance_abs <= cls.AT_TRIGGER_THRESHOLD:
            return TriggerProximity.AT_TRIGGER
        elif distance_abs <= cls.NEAR_TRIGGER_THRESHOLD:
            return TriggerProximity.NEAR_TRIGGER
        elif distance_abs <= cls.TOO_FAR_THRESHOLD:
            return TriggerProximity.NEAR_TRIGGER  # still within range
        else:
            return TriggerProximity.TOO_FAR

    @classmethod
    def distance_pct(cls, current_price: float, trigger_price: float) -> Optional[float]:
        """Returns % distance to trigger, positive means below trigger."""
        if current_price <= 0 or trigger_price <= 0:
            return None
        return (trigger_price - current_price) / trigger_price


# ---------------------------------------------------------------------------
# Timing Quality Engine
# ---------------------------------------------------------------------------

class TimingQualityEngine:
    """
    Classifies the timing quality of a setup.
    Thresholds: PRELIMINARY / NOT EMPIRICALLY VALIDATED.

    Inputs:
      - signal_state: str (WATCH, SETUP_FORMING, TRIGGER_NEAR, ENTRY_READY, etc.)
      - trigger_proximity: TriggerProximity
      - priced_in_status: PricedInStatus
      - technical_state: str (POSITIVE, NEUTRAL, NEGATIVE, UNKNOWN)
      - evidence_state: str (COMPLETE, GOOD, PARTIAL, WEAK, INSUFFICIENT)
    """

    @staticmethod
    def evaluate(
        signal_state: str,
        trigger_proximity: TriggerProximity,
        priced_in_status: PricedInStatus,
        technical_state: str = "UNKNOWN",
        evidence_state: str = "UNKNOWN",
    ) -> TimingQuality:

        # INVALID: setup broken
        if signal_state in ("INVALIDATED", "EXIT_NOW"):
            return TimingQuality.INVALID

        # EXTENDED: price already too far, chasing risk
        if priced_in_status in (PricedInStatus.OVEREXTENDED, PricedInStatus.LIKELY_PRICED_IN):
            return TimingQuality.EXTENDED

        # READY: everything aligned and trigger actionable
        if signal_state in ("ENTRY_READY", "ENTRY_CONFIRMED"):
            if trigger_proximity in (TriggerProximity.AT_TRIGGER, TriggerProximity.TRIGGERED, TriggerProximity.NEAR_TRIGGER):
                return TimingQuality.READY
            elif trigger_proximity == TriggerProximity.TOO_FAR:
                return TimingQuality.FORMING

        # LATE: trigger already passed but not captured
        if trigger_proximity == TriggerProximity.TRIGGERED and signal_state not in ("ENTRY_CONFIRMED", "HOLD"):
            return TimingQuality.LATE

        # FORMING: evidence accumulating but not ready yet
        if signal_state in ("SETUP_FORMING", "TRIGGER_NEAR"):
            if technical_state in ("POSITIVE", "NEUTRAL"):
                return TimingQuality.FORMING
            return TimingQuality.EARLY

        # EARLY: too early, only initial watch
        if signal_state in ("WATCH", "EARLY_WATCH"):
            return TimingQuality.EARLY

        return TimingQuality.UNKNOWN


# ---------------------------------------------------------------------------
# Entry Window Engine
# ---------------------------------------------------------------------------

class EntryWindowEngine:
    """
    Determines whether the entry window is still open.
    Thresholds: PRELIMINARY / NOT EMPIRICALLY VALIDATED.
    """

    @staticmethod
    def evaluate(
        timing_quality: TimingQuality,
        trigger_proximity: TriggerProximity,
        priced_in_status: PricedInStatus,
        signal_state: str = "UNKNOWN",
    ) -> EntryWindowStatus:

        if timing_quality == TimingQuality.INVALID:
            return EntryWindowStatus.CLOSED

        if timing_quality == TimingQuality.EXTENDED:
            return EntryWindowStatus.MISSED

        if timing_quality == TimingQuality.LATE:
            return EntryWindowStatus.MISSED

        if timing_quality == TimingQuality.READY:
            if trigger_proximity in (TriggerProximity.AT_TRIGGER, TriggerProximity.TRIGGERED):
                return EntryWindowStatus.NARROW
            return EntryWindowStatus.OPEN

        if timing_quality == TimingQuality.FORMING:
            return EntryWindowStatus.EARLY

        if timing_quality == TimingQuality.EARLY:
            return EntryWindowStatus.EARLY

        return EntryWindowStatus.UNKNOWN


# ---------------------------------------------------------------------------
# Priced-In Detection Engine
# ---------------------------------------------------------------------------

class PricedInEngine:
    """
    Estimates whether an opportunity is already priced in.
    Uses available evidence — no future leakage.
    Thresholds: PRELIMINARY / NOT EMPIRICALLY VALIDATED.

    Inputs:
      - current_price: float
      - reference_price: float  (last support, entry zone, or trigger reference)
      - catalyst_materiality: str (LOW/MEDIUM/HIGH/CRITICAL/UNKNOWN)
      - catalyst_decay: str (ACTIVE/EXPIRED/UNKNOWN)
      - momentum_state: str (positive string from quant features, e.g. POSITIVE/EXTENDED)
      - move_pct_from_reference: float  (how much price moved from reference)
    """

    PARTIALLY_PRICED_MOVE = 0.05   # > 5% from reference
    LIKELY_PRICED_MOVE = 0.10      # > 10%
    OVEREXTENDED_MOVE = 0.20       # > 20%

    @classmethod
    def evaluate(
        cls,
        move_pct_from_reference: Optional[float],
        catalyst_materiality: str = "UNKNOWN",
        catalyst_decay: str = "UNKNOWN",
        momentum_state: str = "UNKNOWN",
    ) -> PricedInStatus:

        if move_pct_from_reference is None:
            return PricedInStatus.UNKNOWN

        move = abs(move_pct_from_reference)

        # Overextended regardless of catalyst
        if move >= cls.OVEREXTENDED_MOVE:
            return PricedInStatus.OVEREXTENDED

        # Catalyst expired → likely priced in regardless of move
        if catalyst_decay == "EXPIRED":
            if move >= cls.PARTIALLY_PRICED_MOVE:
                return PricedInStatus.LIKELY_PRICED_IN
            return PricedInStatus.PARTIALLY_PRICED

        # Large move + high catalyst materiality = likely fully priced
        if move >= cls.LIKELY_PRICED_MOVE:
            if catalyst_materiality in ("HIGH", "CRITICAL"):
                return PricedInStatus.LIKELY_PRICED_IN
            return PricedInStatus.PARTIALLY_PRICED

        if move >= cls.PARTIALLY_PRICED_MOVE:
            return PricedInStatus.PARTIALLY_PRICED

        return PricedInStatus.NOT_PRICED_IN
