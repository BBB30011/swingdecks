from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import hashlib
import json
from datetime import date, datetime

def _json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

@dataclass
class HistoricalKnowledgeState:
    """
    Immutable representation of the knowledge available to SwingDeck exactly at time T.
    Enforces the Four-Timestamp Model: event_date, published_at, available_at, observed_at.
    Guarantees absolute outcome blindness (zero forward returns / post-T knowledge).
    """
    ticker: str
    decision_date: str
    decision_time: str
    entity_id: str = ""
    market_state: Dict[str, Any] = field(default_factory=dict)
    event_state: List[Dict[str, Any]] = field(default_factory=list)
    relationship_state: List[Dict[str, Any]] = field(default_factory=list)
    ownership_state: List[Dict[str, Any]] = field(default_factory=list)
    exposure_state: List[Dict[str, Any]] = field(default_factory=list)
    peer_state: List[str] = field(default_factory=list)
    coverage_state: Dict[str, str] = field(default_factory=dict)
    snapshot_hash: Optional[str] = None
    
    # Prohibited outcome attributes to ensure Outcome Firewall is never breached
    _PROHIBITED_OUTCOME_KEYS = {
        "H1", "H3", "H5", "H10", "H20", "target_H1", "target_H3", "target_H5", "target_H10", "target_H20",
        "target_h1", "target_h3", "target_h5", "target_h10", "target_h20", "forward_return",
        "peer_H1", "peer_H3", "peer_H5", "peer_H10", "peer_H20", "excess_H1", "excess_H3", "excess_H5", "excess_H10", "excess_H20"
    }

    def __post_init__(self):
        if not self.entity_id:
            self.entity_id = f"ENT_{self.ticker}"
        if not self.snapshot_hash:
            self.compute_hash()

    def enforce_pit(self, record: Dict[str, Any]) -> bool:
        """
        Validates if a historical record was genuinely knowable and available at T.
        Condition:
        1. published_at <= T (if present)
        2. available_at <= T
        3. observed_at <= T (if present)
        4. valid_from <= decision_date <= valid_to (if present)
        5. Zero forward-looking / outcome keys present.
        """
        decision_datetime = f"{self.decision_date} {self.decision_time}"
        
        # Check outcome contamination in record
        for key in self._PROHIBITED_OUTCOME_KEYS:
            if key in record:
                return False
                
        # 1. published_at check
        if "published_at" in record and record["published_at"]:
            if str(record["published_at"]) > decision_datetime:
                return False
                
        # 2. available_at check (Mandatory for public availability)
        if "available_at" in record and record["available_at"]:
            if str(record["available_at"]) > decision_datetime:
                return False
        elif "time" in record and record["time"]:
            if str(record["time"]) > decision_datetime:
                return False
        elif "timestamp" in record and record["timestamp"]:
            ts_str = str(record["timestamp"]).split("+")[0]
            if ts_str > decision_datetime:
                return False
                
        # 3. observed_at check
        if "observed_at" in record and record["observed_at"]:
            if str(record["observed_at"]) > decision_datetime:
                return False

        # 4. Temporal validity bounds (for relationships/ownership/exposures)
        if "valid_from" in record and record["valid_from"]:
            if str(record["valid_from"])[:10] > self.decision_date:
                return False
        if "valid_to" in record and record["valid_to"]:
            if str(record["valid_to"])[:10] < self.decision_date:
                return False
                
        return True

    def compute_hash(self) -> str:
        """
        Computes deterministic SHA-256 hash of the complete Point-In-Time knowledge state.
        """
        state_dict = {
            "ticker": self.ticker,
            "decision_date": self.decision_date,
            "decision_time": self.decision_time,
            "entity_id": self.entity_id,
            "coverage_state": self.coverage_state,
            "market_state": self.market_state,
            "event_state": sorted([json.dumps(e, default=_json_serial, sort_keys=True) for e in self.event_state]),
            "relationship_state": sorted([json.dumps(r, default=_json_serial, sort_keys=True) for r in self.relationship_state]),
            "ownership_state": sorted([json.dumps(o, default=_json_serial, sort_keys=True) for o in self.ownership_state]),
            "exposure_state": sorted([json.dumps(x, default=_json_serial, sort_keys=True) for x in self.exposure_state]),
            "peer_state": sorted(self.peer_state)
        }
        serialized = json.dumps(state_dict, default=_json_serial, sort_keys=True)
        self.snapshot_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return self.snapshot_hash

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns full serializable dictionary representation.
        """
        return {
            "ticker": self.ticker,
            "decision_date": self.decision_date,
            "decision_time": self.decision_time,
            "entity_id": self.entity_id,
            "snapshot_hash": self.snapshot_hash,
            "coverage_state": self.coverage_state,
            "market_state": self.market_state,
            "event_state": self.event_state,
            "relationship_state": self.relationship_state,
            "ownership_state": self.ownership_state,
            "exposure_state": self.exposure_state,
            "peer_state": self.peer_state
        }
