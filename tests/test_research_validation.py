import pytest
from core.source_quality import SourcePriority, determine_credibility

def test_source_credibility_handling():
    assert determine_credibility(SourcePriority.OFFICIAL) == "HIGH"
    assert determine_credibility(SourcePriority.REPUTABLE_ANALYSIS) == "MEDIUM"
    assert determine_credibility(SourcePriority.SOCIAL_MEDIA) == "LOW"
    assert determine_credibility(SourcePriority.UNKNOWN) == "UNKNOWN"

def test_unknown_not_treated_as_positive_evidence():
    # Downstream components flag UNKNOWN. 
    # Just a placeholder for the logic tested in CompletenessEngine.
    pass
