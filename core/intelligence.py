from typing import List, Dict, Any
from core.research import NewsEvidence, CatalystEvidence

class EventClusterer:
    """
    Deduplicates news and catalysts using deterministic identity rules.
    Focuses on identity, source, symbol, and temporal boundaries.
    """
    _MATERIALITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

    @staticmethod
    def cluster_news(news_list: List[NewsEvidence]) -> List[NewsEvidence]:
        clustered = {}
        for news in news_list:
            # Deterministic key: symbol + normalized headline (alpha-only, lowercase, first 40 chars) + date
            headline_norm = "".join(c.lower() for c in news.headline if c.isalnum())[:40]
            pub_date = news.published_at.split("T")[0] if "T" in news.published_at else news.published_at
            key = f"{news.symbol}_{headline_norm}_{pub_date}"
            
            if key not in clustered:
                clustered[key] = news
            else:
                # Replace with higher materiality
                existing = clustered[key]
                cur_rank = EventClusterer._MATERIALITY_RANK.get(news.materiality, 0)
                ex_rank = EventClusterer._MATERIALITY_RANK.get(existing.materiality, 0)
                if cur_rank > ex_rank:
                    clustered[key] = news
                    
        return list(clustered.values())

    @staticmethod
    def cluster_catalysts(catalyst_list: List[CatalystEvidence]) -> List[CatalystEvidence]:
        clustered = {}
        for cat in catalyst_list:
            pub_date = cat.published_at.split("T")[0] if "T" in cat.published_at else cat.published_at
            key = f"{cat.symbol}_{cat.event_type}_{pub_date}"
            
            if key not in clustered:
                clustered[key] = cat
            else:
                existing = clustered[key]
                cur_rank = EventClusterer._MATERIALITY_RANK.get(cat.materiality, 0)
                ex_rank = EventClusterer._MATERIALITY_RANK.get(existing.materiality, 0)
                if cur_rank > ex_rank:
                    clustered[key] = cat
                    
        return list(clustered.values())
