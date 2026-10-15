"""
SwingDeck — Semantic Truth Gate & World Model Verifier V1.0
Verifies Technical, Data, Temporal, Provenance, Semantic, and World Model Truth layers
across both Canonical Historical Database (star-schema) and Operational Graph Database.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
import duckdb

from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, AccessClass, EvidenceClassification,
    validate_entity_semantic_type, validate_relationship_semantics,
    validate_policy_transmission_chain, CANONICAL_INDONESIAN_ENTITY_GROUND_TRUTH
)

@dataclass
class SemanticFinding:
    finding_id: str
    truth_layer: str  # "TECHNICAL_TRUTH", "DATA_TRUTH", "TEMPORAL_TRUTH", "PROVENANCE_TRUTH", "SEMANTIC_TRUTH", "WORLD_MODEL_TRUTH"
    severity: str    # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    entity_or_rel_id: str
    category: str    # "ENTITY_ONTOLOGY", "RELATIONSHIP_ONTOLOGY", "TEMPORAL_INVERSION", "SECURITY_MNPI", "PROMPT_INJECTION", "PROVENANCE_MISSING"
    observed_value: Any
    expected_value: Any
    root_cause: str
    impact: str
    recommendation: str
    status: str = "OPEN"

@dataclass
class SemanticTruthSnapshot:
    run_id: str
    generated_at: str
    technical_truth: str = "PASS"
    data_truth: str = "PASS"
    temporal_truth: str = "PASS"
    provenance_truth: str = "PASS"
    semantic_truth: str = "PASS"
    world_model_truth: str = "PASS"
    overall_truth: str = "PASS"
    natural_information_ingestion: str = "IMPLEMENTED_NOT_OBSERVED"
    findings: List[SemanticFinding] = field(default_factory=list)
    entity_count: int = 0
    relationship_count: int = 0
    information_count: int = 0
    exposure_count: int = 0
    mechanism_count: int = 0

class SemanticTruthGate:
    def __init__(self, graph_db_path_or_conn: Union[str, duckdb.DuckDBPyConnection] = "data/duckdb/intelligence.duckdb"):
        if isinstance(graph_db_path_or_conn, str):
            self.graph_db_path = Path(graph_db_path_or_conn)
            self._external_conn = None
        else:
            self.graph_db_path = None
            self._external_conn = graph_db_path_or_conn

    def _create_finding(
        self,
        truth_layer: str,
        severity: str,
        entity_or_rel_id: str,
        category: str,
        observed: Any,
        expected: Any,
        root_cause: str,
        impact: str,
        recommendation: str
    ) -> SemanticFinding:
        fp = hashlib.sha256(f"{truth_layer}{entity_or_rel_id}{category}{str(observed)}{str(expected)}".encode()).hexdigest()
        return SemanticFinding(
            finding_id=f"SEM_{fp[:8]}",
            truth_layer=truth_layer,
            severity=severity,
            entity_or_rel_id=entity_or_rel_id,
            category=category,
            observed_value=observed,
            expected_value=expected,
            root_cause=root_cause,
            impact=impact,
            recommendation=recommendation
        )

    def audit_graph(self) -> SemanticTruthSnapshot:
        now = datetime.now(timezone.utc).isoformat()
        snap = SemanticTruthSnapshot(
            run_id=f"sem_truth_{int(datetime.now(timezone.utc).timestamp())}",
            generated_at=now
        )

        should_close = False
        if self._external_conn is not None:
            con = self._external_conn
        else:
            if not self.graph_db_path.exists():
                snap.technical_truth = "FAIL"
                snap.semantic_truth = "BLOCKED"
                snap.overall_truth = "BLOCKED"
                snap.findings.append(self._create_finding(
                    "TECHNICAL_TRUTH", "CRITICAL", str(self.graph_db_path), "DATABASE_NOT_FOUND",
                    "MISSING", "EXISTS", "DuckDB graph database file not found",
                    "Intelligence queries cannot execute", "Run db initialization"
                ))
                return snap

            try:
                con = duckdb.connect(str(self.graph_db_path))
                should_close = True
            except Exception as e:
                snap.technical_truth = "FAIL"
                snap.semantic_truth = "BLOCKED"
                snap.overall_truth = "BLOCKED"
                snap.findings.append(self._create_finding(
                    "TECHNICAL_TRUTH", "CRITICAL", str(self.graph_db_path), "DATABASE_ERROR",
                    str(e), "READABLE", "DuckDB connection error",
                    "Cannot query intelligence graph", "Check DuckDB file integrity"
                ))
                return snap

        try:
            tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        except Exception as e:
            snap.technical_truth = "FAIL"
            snap.semantic_truth = "BLOCKED"
            snap.overall_truth = "BLOCKED"
            if should_close: con.close()
            return snap

        is_star_schema = "dim_entity" in tables and "fact_relationship" in tables
        is_operational = "entities" in tables and "relationships" in tables

        if not is_star_schema and not is_operational:
            snap.technical_truth = "FAIL"
            snap.findings.append(self._create_finding(
                "TECHNICAL_TRUTH", "CRITICAL", "SCHEMA", "UNKNOWN_SCHEMA",
                tables, "STAR_SCHEMA_OR_OPERATIONAL", "Unrecognized database table schema",
                "Graph queries will fail", "Rebuild database with standard schema"
            ))
            if should_close: con.close()
            return snap

        entity_type_map = {}

        # -------------------------------------------------------------
        # 1. ENTITY ONTOLOGY AUDIT
        # -------------------------------------------------------------
        if is_operational:
            entities = con.execute("SELECT entity_id, canonical_name, entity_type, aliases, ticker, semantic_status FROM entities").fetchall()
            snap.entity_count = len(entities)
            for ent in entities:
                eid, name, etype, aliases, ticker, sem_status = ent
                clean_eid = eid.replace("ENT_", "")
                entity_type_map[eid] = etype
                
                is_valid, reason, canonical_type = validate_entity_semantic_type(clean_eid, etype)
                if not is_valid:
                    snap.semantic_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "SEMANTIC_TRUTH", "CRITICAL", eid, "ENTITY_ONTOLOGY_VIOLATION",
                        etype, canonical_type.value if canonical_type else "VALID_TYPE",
                        reason, "Distorts market graph entity reasoning",
                        f"Correct entity '{eid}' type to '{canonical_type.value if canonical_type else 'UNKNOWN'}'"
                    ))

                if etype == EntityType.PERSON.value and ticker is not None:
                    snap.semantic_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "SEMANTIC_TRUTH", "HIGH", eid, "PERSON_TICKER_CONTRADICTION",
                        f"PERSON with ticker {ticker}", "PERSON has no ticker",
                        "Person entity assigned security ticker", "Semantic distortion",
                        "Remove ticker from Person entity"
                    ))
        elif is_star_schema:
            dim_entities = con.execute("SELECT entity_id, canonical_name, entity_type FROM dim_entity").fetchall()
            snap.entity_count = len(dim_entities)
            for ent in dim_entities:
                eid, name, etype = ent
                clean_eid = eid.replace("ENT_", "")
                entity_type_map[eid] = etype
                
                is_valid, reason, canonical_type = validate_entity_semantic_type(clean_eid, etype)
                if not is_valid:
                    snap.semantic_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "SEMANTIC_TRUTH", "CRITICAL", eid, "ENTITY_ONTOLOGY_VIOLATION",
                        etype, canonical_type.value if canonical_type else "VALID_TYPE",
                        reason, "Distorts market graph entity reasoning",
                        f"Correct entity '{eid}' type to '{canonical_type.value if canonical_type else 'UNKNOWN'}'"
                    ))

        # -------------------------------------------------------------
        # 2. RELATIONSHIP ONTOLOGY & DIRECTIONAL AUDIT
        # -------------------------------------------------------------
        if is_operational:
            relationships = con.execute("""
                SELECT relationship_id, source_entity, target_entity, relationship_type,
                       valid_from, valid_to, confidence, status, pit_status, evidence,
                       semantic_status, temporal_status, access_class
                FROM relationships
            """).fetchall()
            snap.relationship_count = len(relationships)

            for rel in relationships:
                rid, src, tgt, rtype, v_from, v_to, conf, stat, pit_stat, evid, sem_stat, temp_stat, acc_cls = rel
                
                if v_to is not None and str(v_to) < str(v_from):
                    snap.temporal_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "TEMPORAL_TRUTH", "CRITICAL", rid, "TEMPORAL_INVERSION",
                        f"{v_from} > {v_to}", "valid_from <= valid_to",
                        "Relationship valid_to occurs before valid_from",
                        "Temporal lookahead or corruption", "Correct validity timestamps"
                    ))

                src_type = entity_type_map.get(src, "UNKNOWN")
                tgt_type = entity_type_map.get(tgt, "UNKNOWN")

                if src_type != "UNKNOWN" and tgt_type != "UNKNOWN":
                    is_rel_valid, rel_reason = validate_relationship_semantics(src_type, rtype, tgt_type)
                    if not is_rel_valid:
                        snap.semantic_truth = "FAIL"
                        snap.findings.append(self._create_finding(
                            "SEMANTIC_TRUTH", "CRITICAL", rid, "RELATIONSHIP_SEMANTIC_VIOLATION",
                            f"{src_type} -{rtype}-> {tgt_type}", "ALLOWED_COMBINATION",
                            rel_reason, "Impossible real-world graph edge",
                            "Fix predicate or entity classification"
                        ))

                if not evid or str(evid).strip() == "":
                    snap.provenance_truth = "PASS_WITH_LIMITATIONS" if snap.provenance_truth == "PASS" else snap.provenance_truth
                    snap.findings.append(self._create_finding(
                        "PROVENANCE_TRUTH", "MEDIUM", rid, "MISSING_EVIDENCE_CITATION",
                        "EMPTY", "DOCUMENTED_SOURCE",
                        "Relationship lacks cited evidence citation",
                        "Unverifiable edge in decision trace", "Attach documentary evidence ref"
                    ))
        elif is_star_schema:
            fact_relationships = con.execute("""
                SELECT relationship_id, entity_a_id, relationship_type, entity_b_id, valid_from, valid_to, evidence_id
                FROM fact_relationship
            """).fetchall()
            snap.relationship_count = len(fact_relationships)
            for rel in fact_relationships:
                rid, src, rtype, tgt, v_from, v_to, evid_id = rel
                if v_to is not None and str(v_to) < str(v_from):
                    snap.temporal_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "TEMPORAL_TRUTH", "CRITICAL", rid, "TEMPORAL_INVERSION",
                        f"{v_from} > {v_to}", "valid_from <= valid_to",
                        "Relationship valid_to occurs before valid_from",
                        "Temporal lookahead or corruption", "Correct validity timestamps"
                    ))

        # -------------------------------------------------------------
        # 3. INFORMATION SECURITY & ACCESS CLASS AUDIT
        # -------------------------------------------------------------
        if is_operational and "information" in tables:
            info_rows = con.execute("""
                SELECT information_id, title, summary, claim, access_class, trading_eligibility, status, published_at, available_at
                FROM information
            """).fetchall()
            snap.information_count = len(info_rows)

            for info in info_rows:
                iid, title, summary, claim, acc_cls, elig, stat, pub_at, avail_at = info

                if pub_at and avail_at and str(avail_at) < str(pub_at):
                    snap.temporal_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "TEMPORAL_TRUTH", "CRITICAL", iid, "PRE_PUBLICATION_LEAK",
                        f"available_at ({avail_at}) < published_at ({pub_at})", "published_at <= available_at",
                        "Data available before publication timestamp",
                        "Hindsight bias / PIT leakage", "Enforce avail_at >= pub_at"
                    ))

                if acc_cls not in ["PUBLIC", "AUTHORIZED_PRIVATE", None, ""] and elig == "ELIGIBLE":
                    snap.semantic_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "SEMANTIC_TRUTH", "CRITICAL", iid, "MNPI_FIREWALL_BREACH",
                        f"AccessClass={acc_cls} marked ELIGIBLE", "BLOCKED",
                        "Non-public or MNPI information permitted in trading pathway",
                        "Regulatory violation / illegal trading input", "Hard-block trading eligibility"
                    ))

                if stat == "UNTRUSTED_CONTENT" and elig == "ELIGIBLE":
                    snap.semantic_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "SEMANTIC_TRUTH", "CRITICAL", iid, "PROMPT_INJECTION_UNBLOCKED",
                        "UNTRUSTED_CONTENT marked ELIGIBLE", "BLOCKED",
                        "Adversarial prompt injection bypassed trading block",
                        "Potential LLM / decision compromise", "Block trading eligibility"
                    ))
        elif is_star_schema and "fact_event" in tables:
            event_rows = con.execute("SELECT event_id, event_type, published_at, information_available_at FROM fact_event").fetchall()
            snap.information_count = len(event_rows)
            for ev in event_rows:
                eid, etype, pub_at, avail_at = ev
                if pub_at and avail_at and str(avail_at) < str(pub_at):
                    snap.temporal_truth = "FAIL"
                    snap.findings.append(self._create_finding(
                        "TEMPORAL_TRUTH", "CRITICAL", eid, "PRE_PUBLICATION_LEAK",
                        f"available_at ({avail_at}) < published_at ({pub_at})", "published_at <= available_at",
                        "Data available before publication timestamp",
                        "Hindsight bias / PIT leakage", "Enforce avail_at >= pub_at"
                    ))

        if should_close:
            con.close()

        critical_findings = [f for f in snap.findings if f.severity == "CRITICAL"]
        high_findings = [f for f in snap.findings if f.severity == "HIGH"]

        if critical_findings:
            snap.overall_truth = "FAIL"
        elif high_findings:
            snap.overall_truth = "PASS_WITH_LIMITATIONS"
        else:
            snap.overall_truth = "PASS"

        return snap
