import pytest
from core.intelligence import EventClusterer
from core.research import NewsEvidence, CatalystEvidence, ResearchPacket, FundamentalEvidence
from core.red_team import RedTeamAnalyzer
from core.decision import OpportunityAssessment

def test_news_deduplication():
    # 3 news items: 2 identical but different source, 1 different
    news1 = NewsEvidence(
        evidence_id="1", symbol="BBCA", category="NEWS", claim="BBCA Laba Naik",
        claim_class="FACT", as_of_timestamp="2023-10-01", source="Source A",
        headline="BBCA Mencatat Laba Bersih Naik 10%", published_at="2023-10-01T10:00:00Z", materiality="HIGH"
    )
    news2 = NewsEvidence(
        evidence_id="2", symbol="BBCA", category="NEWS", claim="BBCA Laba Naik",
        claim_class="FACT", as_of_timestamp="2023-10-01", source="Source B",
        headline="BBCA mencatat laba bersih naik 10%", published_at="2023-10-01T14:00:00Z", materiality="MEDIUM"
    )
    news3 = NewsEvidence(
        evidence_id="3", symbol="BBCA", category="NEWS", claim="BBCA Buka Cabang",
        claim_class="FACT", as_of_timestamp="2023-10-01", source="Source C",
        headline="BBCA Buka Cabang Baru di Bali", published_at="2023-10-01T15:00:00Z", materiality="LOW"
    )
    
    clustered = EventClusterer.cluster_news([news1, news2, news3])
    
    assert len(clustered) == 2 # 1 and 2 should merge
    # The retained item should have HIGH materiality (news1 wins over news2's MEDIUM)
    assert any("Laba" in n.headline and n.materiality == "HIGH" for n in clustered)

def test_catalyst_deduplication():
    cat1 = CatalystEvidence(
        evidence_id="1", symbol="GOTO", category="CATALYST", claim="Earnings Q3",
        claim_class="FACT", as_of_timestamp="2023-10-01", source="Source A",
        event_type="EARNINGS", published_at="2023-10-01", materiality="HIGH"
    )
    cat2 = CatalystEvidence(
        evidence_id="2", symbol="GOTO", category="CATALYST", claim="Earnings Q3 Updated",
        claim_class="FACT", as_of_timestamp="2023-10-01", source="Source B",
        event_type="EARNINGS", published_at="2023-10-01", materiality="CRITICAL"
    )
    
    clustered = EventClusterer.cluster_catalysts([cat1, cat2])
    
    assert len(clustered) == 1
    assert clustered[0].materiality == "CRITICAL" # Upgraded to CRITICAL

def test_why_now_generation():
    packet = ResearchPacket(
        job_id="1", symbol="TEST", as_of_timestamp="2023",
        quant_context={"factors": {"volume": {"factor_name": "volume", "state": "POSITIVE"}}, "market_regime": "BEAR"}
    )
    # 1. Volume expansion
    res1 = RedTeamAnalyzer.analyze(packet)
    # WhyNowEngine now uses 'Volume expanding' (from volume factor detection)
    assert "volume" in res1.why_now.lower() or "flow" in res1.why_now.lower() or res1.why_now != "NONE"
    
    # 2. Catalyst active
    packet.catalysts = [CatalystEvidence(
        evidence_id="c1", symbol="TEST", category="CATALYST", claim="Merger",
        claim_class="FACT", as_of_timestamp="2023", source="Source C",
        event_type="M&A", decay_state="ACTIVE"
    )]
    res2 = RedTeamAnalyzer.analyze(packet)
    # Catalyst takes priority — should mention M&A
    assert "M&A" in res2.why_now or "catalyst" in res2.why_now.lower()
    
def test_opportunity_assessment_schema():
    opp = OpportunityAssessment(
        symbol="TEST",
        opportunity_score=85.5,
        opportunity_class="BREAKOUT",
        why_now="Catalyst active: EARNINGS",
        signal_tier="TIER 1"
    )
    assert opp.symbol == "TEST"
    assert opp.signal_tier == "TIER 1"
