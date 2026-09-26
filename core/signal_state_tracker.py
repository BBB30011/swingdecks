import json
from pathlib import Path
from typing import Dict, Any
from core.schemas import SignalState

class SignalStateTracker:
    def __init__(self, state_file: str = "state/signal_states.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.states: Dict[str, str] = {}
        self._load()

    def _load(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.states = data.get("states", {})
            except json.JSONDecodeError:
                self.states = {}
        else:
            self.states = {}

    def _save(self):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({"states": self.states}, f, indent=4)

    def get_state(self, symbol: str) -> SignalState:
        state_str = self.states.get(symbol.upper(), "WATCH")
        try:
            return SignalState(state_str)
        except ValueError:
            return SignalState.WATCH

    def can_transition(self, current: SignalState, proposed: SignalState) -> bool:
        if current == proposed:
            return True
        if proposed in (SignalState.INVALIDATED, SignalState.EXIT_NOW):
            return True # Can always invalidate or exit
            
        flow = {
            SignalState.EARLY_WATCH: [SignalState.WATCH, SignalState.SETUP_FORMING],
            SignalState.WATCH: [SignalState.SETUP_FORMING, SignalState.TRIGGER_NEAR],
            SignalState.SETUP_FORMING: [SignalState.TRIGGER_NEAR, SignalState.ENTRY_READY],
            SignalState.TRIGGER_NEAR: [SignalState.ENTRY_READY],
            SignalState.ENTRY_READY: [SignalState.ENTRY_CONFIRMED, SignalState.WATCH, SignalState.SETUP_FORMING],
            SignalState.ENTRY_CONFIRMED: [SignalState.HOLD],
            SignalState.HOLD: [SignalState.EXIT_WARNING, SignalState.EXIT_NOW],
            SignalState.EXIT_WARNING: [SignalState.EXIT_NOW, SignalState.HOLD],
            SignalState.EXIT_NOW: [],
            SignalState.INVALIDATED: [SignalState.WATCH, SignalState.EARLY_WATCH] # Reset cycle
        }
        
        allowed = flow.get(current, [])
        return proposed in allowed

    def attempt_transition(self, symbol: str, proposed_state: SignalState, current_price: float = 0.0, trigger_price: float = 0.0) -> SignalState:
        current_state = self.get_state(symbol)
        
        # Point-in-time check to prevent false ENTRY_CONFIRMED
        if proposed_state == SignalState.ENTRY_CONFIRMED:
            if current_price < trigger_price or trigger_price <= 0:
                # Block false confirmation, stay in ENTRY_READY
                return SignalState.ENTRY_READY
                
        # Block regression if not in allowed transitions
        if not self.can_transition(current_state, proposed_state):
            # If regression or invalid jump, stay in current state (or fallback to safe state like WATCH)
            # EXCEPTIONS: if the system explicitly downgraded (e.g. READY -> WATCH because catalyst expired)
            if proposed_state in (SignalState.WATCH, SignalState.SETUP_FORMING) and current_state in (SignalState.ENTRY_READY, SignalState.TRIGGER_NEAR):
                self.transition_state(symbol, proposed_state)
                return proposed_state
            return current_state
            
        self.transition_state(symbol, proposed_state)
        return proposed_state

    def transition_state(self, symbol: str, new_state: SignalState):
        sym = symbol.upper()
        self.states[sym] = new_state.value
        self._save()

    def get_tracked_symbols(self) -> Dict[str, str]:
        return self.states.copy()
