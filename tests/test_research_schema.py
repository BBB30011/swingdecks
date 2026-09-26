import pytest
from core.research import ResearchEvidence, MacroEvidence, FundamentalEvidence, CorporateEvent, SentimentEvidence
from pydantic import ValidationError

def test_valid_research_evidence():
    ev = ResearchEvidence(
        evidence_id="1", symbol="BBCA", category="NEWS", claim="Profit up",
        claim_class="FACT", source="Reuters", published_at="2020-01-01", as_of_timestamp="2020-01-02"
    )
    assert ev.claim == "Profit up"

def test_fact_requires_source():
    with pytest.raises(ValidationError):
        ResearchEvidence(
            evidence_id="1", symbol="BBCA", category="NEWS", claim="Profit up",
            claim_class="FACT", source="UNKNOWN", published_at="2020-01-01", as_of_timestamp="2020-01-02"
        )

def test_macro_evidence_schema():
    ev = MacroEvidence(
        evidence_id="1", symbol="BBCA", category="MACRO", claim="Rates", claim_class="FACT", source="BI",
        published_at="2020", as_of_timestamp="2020", indicator="Rate", value=5.0, unit="%", direction="POSITIVE", interpretation="Good", timestamp="2020"
    )
    assert ev.direction == "POSITIVE"

def test_fundamental_evidence_schema():
    ev = FundamentalEvidence(
        evidence_id="1", symbol="BBCA", category="FUNDAMENTAL", claim="Rev up", claim_class="FACT", source="Q1",
        published_at="2020", as_of_timestamp="2020", metric="revenue", value=100.0, direction="POSITIVE"
    )
    assert ev.metric == "revenue"

def test_corporate_event_schema():
    ev = CorporateEvent(
        evidence_id="1", symbol="BBCA", category="CORPORATE_EVENT", claim="Div", claim_class="FACT", source="IDX",
        published_at="2020", as_of_timestamp="2020", event_type="DIVIDEND", event_date="2020-01-01", announcement_date="2020-01-01", description="Div"
    )
    assert ev.event_type == "DIVIDEND"

def test_sentiment_schema():
    ev = SentimentEvidence(
        evidence_id="1", symbol="BBCA", category="SENTIMENT", claim="Good", claim_class="INFERENCE", source="Twitter",
        published_at="2020", as_of_timestamp="2020", timestamp="2020", sentiment="POSITIVE", confidence=0.8
    )
    assert ev.sentiment == "POSITIVE"
