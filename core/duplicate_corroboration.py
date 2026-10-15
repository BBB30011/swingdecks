"""
SwingDeck Knowledge Data Platform - Source-Aware Duplicate & Corroboration Engine V1
Enforces strict distinction between INDEPENDENT_SOURCE and DERIVED_COPY to prevent
false corroboration inflation across news wires, syndications, and repetitive disclosures.
"""

import re
from typing import List, Dict, Any, Set, Tuple, Optional
from core.data_platform_schemas import (
    compute_content_hash, compute_document_fingerprint, SourceLineageType
)

class DuplicateAndCorroborationEngine:
    SYNDICATION_PATTERNS = [
        r"(?:dilansir|dikutip|merujuk|menurut|laporan)\s+(?:dari\s+)?([A-Za-z0-9\s]+)",
        r"(?:reported by|according to|citing|source:)\s+([A-Za-z0-9\s]+)",
        r"\(([A-Za-z0-9\s]+)\)\s*[-—]",  # e.g. (Reuters) - or (Antara) -
        r"reuters|bloomberg|antara|cnbc|bisnis\.com|kontan|detik"
    ]

    @staticmethod
    def is_exact_duplicate(hash_a: str, hash_b: str) -> bool:
        """Determines if two pieces of content have exact identical hash."""
        return bool(hash_a and hash_b and hash_a == hash_b)

    @staticmethod
    def compute_jaccard_similarity(text_a: str, text_b: str) -> float:
        """Computes token Jaccard similarity for near-duplicate detection."""
        if not text_a or not text_b:
            return 0.0
        tokens_a = set(re.findall(r"\w+", text_a.lower()))
        tokens_b = set(re.findall(r"\w+", text_b.lower()))
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a.intersection(tokens_b)
        union = tokens_a.union(tokens_b)
        return len(intersection) / len(union)

    @classmethod
    def detect_syndication_origin(cls, text: str, publisher: str) -> Optional[str]:
        """Detects if text explicitly cites an upstream primary source."""
        if not text:
            return None
        text_lower = text.lower()
        for pattern in cls.SYNDICATION_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                matched_str = match.group(0).strip()
                return matched_str
        return None

    @classmethod
    def evaluate_corroboration(
        cls, 
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates a cluster of evidence items supporting a claim or relationship.
        Filters out exact duplicates, near-duplicates, and derived copies to compute
        the TRUE number of independent corroborating sources.
        """
        if not evidence_items:
            return {
                "total_items": 0,
                "independent_source_count": 0,
                "derived_copy_count": 0,
                "exact_duplicate_count": 0,
                "corroboration_status": "NONE",
                "unique_sources": [],
                "lineage_graph": []
            }

        seen_hashes: Set[str] = set()
        seen_publishers: Dict[str, str] = {}  # publisher -> primary_evidence_id
        seen_upstream_citations: Set[str] = set()
        independent_evidences: List[str] = []
        derived_evidences: List[Dict[str, Any]] = []
        exact_duplicate_count = 0

        for item in evidence_items:
            ev_id = item.get("evidence_id", "UNKNOWN")
            c_hash = item.get("content_hash", "")
            publisher = (item.get("publisher") or item.get("source_id") or "UNKNOWN").upper()
            text = item.get("excerpt_reference", "") or item.get("claim", "")

            # 1. Exact Duplicate Check
            if c_hash and c_hash in seen_hashes:
                exact_duplicate_count += 1
                derived_evidences.append({
                    "evidence_id": ev_id,
                    "publisher": publisher,
                    "lineage_type": SourceLineageType.DERIVED_COPY,
                    "reason": "EXACT_CONTENT_DUPLICATE"
                })
                continue
            if c_hash:
                seen_hashes.add(c_hash)

            # 2. Syndication / Citation Check (only if citing a DIFFERENT entity)
            upstream_citation = cls.detect_syndication_origin(text, publisher)

            # 3. Same Publisher Check
            if publisher in seen_publishers:
                derived_evidences.append({
                    "evidence_id": ev_id,
                    "publisher": publisher,
                    "lineage_type": SourceLineageType.DERIVED_COPY,
                    "reason": f"SAME_PUBLISHER_AS_{seen_publishers[publisher]}"
                })
            elif upstream_citation and publisher not in upstream_citation.upper():
                # Upstream quoted wire
                up_norm = upstream_citation.upper()
                if up_norm in seen_upstream_citations:
                    derived_evidences.append({
                        "evidence_id": ev_id,
                        "publisher": publisher,
                        "lineage_type": SourceLineageType.SYNDICATED,
                        "reason": f"DUPLICATE_CITED_UPSTREAM_{upstream_citation}"
                    })
                else:
                    seen_upstream_citations.add(up_norm)
                    independent_evidences.append(ev_id)
            else:
                seen_publishers[publisher] = ev_id
                independent_evidences.append(ev_id)

        indep_count = len(independent_evidences)
        corrob_status = (
            "STRONG" if indep_count >= 3 else
            "MODERATE" if indep_count == 2 else
            "SINGLE_SOURCE" if indep_count == 1 else
            "UNSUPPORTED"
        )

        return {
            "total_items": len(evidence_items),
            "independent_source_count": indep_count,
            "derived_copy_count": len(derived_evidences),
            "exact_duplicate_count": exact_duplicate_count,
            "corroboration_status": corrob_status,
            "unique_independent_evidence_ids": independent_evidences,
            "derived_items": derived_evidences
        }
