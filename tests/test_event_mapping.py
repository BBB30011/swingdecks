from core.event_mapping import EventMapper

def test_event_mapping_rate_cut():
    mapping = EventMapper.map_event("BI rate cut")
    assert mapping.mechanism == "cost of funding"
    assert mapping.potential_price_impact == "POSITIVE"

def test_event_mapping_unknown():
    mapping = EventMapper.map_event("Alien invasion")
    assert mapping.potential_price_impact == "UNKNOWN"
