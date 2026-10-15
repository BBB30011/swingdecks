import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

class InformationDeltaTaxonomy:
    NEW = "NEW"
    UPDATED = "UPDATED"
    UNCHANGED = "UNCHANGED"
    STALE = "STALE"
    REMOVED = "REMOVED"
    CONTRADICTORY = "CONTRADICTORY"
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"

class MarketDeltaEngine:
    """
    Computes MARKET INFORMATION DELTA across sessions.
    Answers: What changed? What is moving? Why is it moving? What contradicts the thesis?
    """
    def __init__(self, state_dir: str):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "market_delta_state.json"
        self._load_state()

    def _load_state(self):
        self.previous_session = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    self.previous_session = json.load(f)
            except Exception:
                pass

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.previous_session, f, indent=2)

    def compute_deltas(self, 
                      current_session_timestamp: str,
                      market_bars: Dict[str, Any],
                      features_per_symbol: Dict[str, Any],
                      intel_per_symbol: Dict[str, Any],
                      position_contexts: Dict[str, Any]) -> Dict[str, Any]:
        
        all_deltas = {}
        new_state = {}

        for sym, bar in market_bars.items():
            prev = self.previous_session.get(sym, {})
            current = {
                "price": bar.close,
                "volume": bar.volume,
                "features": features_per_symbol.get(sym, {}) if features_per_symbol else {},
                "intel": intel_per_symbol.get(sym, {}) if intel_per_symbol else {},
                "position": position_contexts.get(sym, {}) if position_contexts else {}
            }
            new_state[sym] = current
            
            delta = {
                "symbol": sym,
                "timestamp": current_session_timestamp,
                "agent1_delta": self._compute_agent1_delta(prev, current),
                "agent2_delta": self._compute_agent2_delta(prev, current),
                "red_team_delta": self._compute_red_team_delta(prev, current)
            }
            all_deltas[sym] = delta
            
        self.previous_session = new_state
        self._save_state()
        return all_deltas

    def _compute_agent1_delta(self, prev: Dict, current: Dict) -> Dict:
        # WHAT CHANGED IN THE MARKET?
        if not prev:
            return {"status": InformationDeltaTaxonomy.NEW, "changes": ["NEW_CANDIDATE_DETECTED"]}
            
        changes = []
        prev_price = prev.get("price", 0)
        curr_price = current.get("price", 0)
        prev_vol = prev.get("volume", 0)
        curr_vol = current.get("volume", 0)
        
        if prev_price > 0 and curr_price > prev_price * 1.05:
            changes.append("BREAKOUT")
        elif prev_price > 0 and curr_price < prev_price * 0.95:
            changes.append("BREAKDOWN")
            
        if prev_vol > 0 and curr_vol > prev_vol * 1.5:
            changes.append("VOLUME_EXPANSION")
        elif prev_vol > 0 and curr_vol < prev_vol * 0.5:
            changes.append("VOLUME_CONTRACTION")
            
        prev_sma20 = prev.get("features", {}).get("trend", {}).get("sma20", 0)
        curr_sma20 = current.get("features", {}).get("trend", {}).get("sma20", 0)
        
        if curr_price > curr_sma20 and prev_price <= prev_sma20 and prev_sma20 > 0:
            changes.append("MOMENTUM_STRENGTHENED")
        elif curr_price < curr_sma20 and prev_price >= prev_sma20 and prev_sma20 > 0:
            changes.append("MOMENTUM_WEAKENED")
            
        if not changes:
            return {"status": InformationDeltaTaxonomy.UNCHANGED, "changes": ["NO_SIGNIFICANT_MARKET_CHANGE"]}
            
        return {"status": InformationDeltaTaxonomy.UPDATED, "changes": changes}

    def _compute_agent2_delta(self, prev: Dict, current: Dict) -> Dict:
        # WHY COULD THIS BE HAPPENING?
        prev_intel = prev.get("intel", {})
        curr_intel = current.get("intel", {})
        
        if not curr_intel:
            return {"status": InformationDeltaTaxonomy.UNKNOWN, "explanation": "NOT_AVAILABLE", "source": "UNKNOWN"}
            
        prev_cats = set(prev_intel.get("catalysts", []))
        curr_cats = set(curr_intel.get("catalysts", []))
        
        new_cats = curr_cats - prev_cats
        removed_cats = prev_cats - curr_cats
        
        timestamp = curr_intel.get("timestamp", "UNKNOWN")
        source = curr_intel.get("source", "UNKNOWN")
        if not timestamp or timestamp == "UNKNOWN":
            return {"status": InformationDeltaTaxonomy.UNKNOWN, "explanation": "AVAILABILITY=UNKNOWN", "source": source}
            
        if new_cats:
            return {
                "status": InformationDeltaTaxonomy.NEW, 
                "explanation": f"New catalysts detected: {', '.join(new_cats)}",
                "source": source,
                "timestamp": timestamp
            }
        elif removed_cats:
            return {
                "status": InformationDeltaTaxonomy.REMOVED,
                "explanation": f"Catalysts removed: {', '.join(removed_cats)}",
                "source": source,
                "timestamp": timestamp
            }
        elif curr_cats:
            return {
                "status": InformationDeltaTaxonomy.UNCHANGED,
                "explanation": f"Existing catalysts persist: {', '.join(curr_cats)}",
                "source": source,
                "timestamp": timestamp
            }
        else:
            return {"status": InformationDeltaTaxonomy.UNKNOWN, "explanation": "NOT_AVAILABLE", "source": source}

    def _compute_red_team_delta(self, prev: Dict, current: Dict) -> Dict:
        # WHAT NEWLY CONTRADICTS THE CURRENT VIEW?
        prev_contra = {c.get("topic"): c for c in prev.get("intel", {}).get("contradictions", []) if isinstance(c, dict)}
        curr_contra = {c.get("topic"): c for c in current.get("intel", {}).get("contradictions", []) if isinstance(c, dict)}
        
        new_topics = set(curr_contra.keys()) - set(prev_contra.keys())
        resolved_topics = set(prev_contra.keys()) - set(curr_contra.keys())
        persistent_topics = set(curr_contra.keys()) & set(prev_contra.keys())
        
        changes = []
        if new_topics:
            changes.append(f"NEW_CONTRADICTION: {', '.join(new_topics)}")
        if resolved_topics:
            changes.append(f"RESOLVED_CONTRADICTION: {', '.join(resolved_topics)}")
        if persistent_topics:
            # Check for severity updates
            for t in persistent_topics:
                if curr_contra[t].get("severity") != prev_contra[t].get("severity"):
                    changes.append(f"UPDATED_CONTRADICTION_SEVERITY: {t} ({prev_contra[t].get('severity')} -> {curr_contra[t].get('severity')})")
                else:
                    changes.append(f"PERSISTENT_CONTRADICTION: {t}")
                    
        if not changes:
            return {"status": InformationDeltaTaxonomy.UNCHANGED, "changes": ["CONTRADICTION_UNCHANGED"]}
            
        status = InformationDeltaTaxonomy.CONTRADICTORY if new_topics else InformationDeltaTaxonomy.UPDATED
        return {"status": status, "changes": changes}
