from enum import Enum
from typing import Optional

class SourcePriority(Enum):
    OFFICIAL = 1
    REGULATORY = 2
    COMPANY_FILING = 3
    REPUTABLE_FINANCIAL_NEWS = 4
    REPUTABLE_ANALYSIS = 5
    SOCIAL_MEDIA = 6
    FORUM = 7
    UNKNOWN = 99

def determine_credibility(priority: SourcePriority) -> str:
    if priority in [SourcePriority.OFFICIAL, SourcePriority.REGULATORY, SourcePriority.COMPANY_FILING]:
        return "HIGH"
    elif priority in [SourcePriority.REPUTABLE_FINANCIAL_NEWS, SourcePriority.REPUTABLE_ANALYSIS]:
        return "MEDIUM"
    elif priority in [SourcePriority.SOCIAL_MEDIA, SourcePriority.FORUM]:
        return "LOW"
    return "UNKNOWN"
