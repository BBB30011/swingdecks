import pytest
from core.daily_cycle import DailyOperatingCycle

class DummyAgent:
    def __init__(self, name: str):
        self.name = name

def test_daily_operating_cycle_initialization():
    a1 = DummyAgent("agent1_quant")
    a2 = DummyAgent("agent2_intelligence")
    a3 = DummyAgent("agent3_committee")
    cycle = DailyOperatingCycle(a1, a2, a3)
    assert cycle.agent1.name == "agent1_quant"
    assert cycle.agent2.name == "agent2_intelligence"
    assert cycle.agent3.name == "agent3_committee"

def test_daily_operating_cycle_slots():
    a1 = DummyAgent("agent1_quant")
    a2 = DummyAgent("agent2_intelligence")
    a3 = DummyAgent("agent3_committee")
    cycle = DailyOperatingCycle(a1, a2, a3)
    as_of = "2026-03-20"
    
    # 08:30 Discover
    res = cycle.run_cycle(as_of, "08:30")
    assert res["phase"] == "DISCOVER"
    assert res["status"] == "COMPLETED"
    
    # 11:00 Confirm
    res = cycle.run_cycle(as_of, "11:00")
    assert res["phase"] == "CONFIRM"
    assert res["status"] == "COMPLETED"
    
    # 14:00 Challenge
    res = cycle.run_cycle(as_of, "14:00")
    assert res["phase"] == "CHALLENGE"
    assert res["status"] == "COMPLETED"
    
    # 15:30 Exit/Risk
    res = cycle.run_cycle(as_of, "15:30")
    assert res["phase"] == "EXIT_RISK"
    assert res["status"] == "COMPLETED"
    
    # 16:00 Learning
    res = cycle.run_cycle(as_of, "16:00")
    assert res["phase"] == "LEARNING"
    assert res["status"] == "COMPLETED"

def test_daily_operating_cycle_invalid_slot():
    a1 = DummyAgent("agent1_quant")
    a2 = DummyAgent("agent2_intelligence")
    a3 = DummyAgent("agent3_committee")
    cycle = DailyOperatingCycle(a1, a2, a3)
    
    with pytest.raises(ValueError, match="Unknown time slot: 12:00"):
        cycle.run_cycle("2026-03-20", "12:00")
