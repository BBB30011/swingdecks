import json
from enum import Enum
from pathlib import Path

class SystemState(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"

class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"

class HealthMonitor:
    def __init__(self, state_file: str = "state/system_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self._write_state(SystemState.RUNNING)

    def _write_state(self, state: SystemState):
        with open(self.state_file, "w") as f:
            json.dump({"state": state.value}, f)

    def set_pause(self, paused: bool):
        self._write_state(SystemState.PAUSED if paused else SystemState.RUNNING)

    def get_system_state(self) -> SystemState:
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
                return SystemState(data.get("state", "RUNNING"))
        except Exception:
            return SystemState.PAUSED  # Safe default if corrupt

    def check_health(self) -> HealthStatus:
        if self.get_system_state() == SystemState.PAUSED:
            return HealthStatus.PAUSED
            
        # Mock basic checks - in reality checks directories, disks, etc.
        state_dir = Path("state")
        if not state_dir.exists():
            return HealthStatus.FAILED
            
        return HealthStatus.HEALTHY
