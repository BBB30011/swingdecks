# KNOWLEDGE INDEX & REGISTRY

This registry serves as the master catalog of all authoritative governance rules, architectural specifications, domain knowledge, failure post-mortems, and agent contracts in the SwingDeck repository.

| Knowledge ID | Title | Type | Status | Owner | Canonical Path | Related Agent | Related Research / Gate | Scope & Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KN-001** | Governance & Scientific Firewall | Canonical Rule | ACTIVE | System | `knowledge/canonical/GOVERNANCE.md` | All Agents | COBA_001–018 | Core epistemology (FACT $\rightarrow$ HYPOTHESIS), missingness axioms, and research immutability. |
| **KN-002** | System Architecture Canonical | Architecture | ACTIVE | Engineering | `governance/architecture/CURRENT_SYSTEM_ARCHITECTURE.md` | All Agents | System-wide | Complete 3-Agent architecture, PIT timestamps, DuckDB models, queue design, and fail-safes. |
| **KN-003** | Repository Structural Map | Architecture | ACTIVE | Engineering | `governance/architecture/REPOSITORY_MAP.md` | All Agents | System-wide | Single canonical source of truth for repository structure and folder boundaries. |
| **KN-004** | Agent Knowledge Map | Specification | ACTIVE | System | `knowledge/agent/AGENT_KNOWLEDGE_MAP.md` | Agent 1, 2, 3 | V2.1 Pipeline | Inputs, reasoning engines, firewall rules, schemas, and prohibitions for Agents 1, 2, and 3. |
| **KN-005** | Relationship & Graph Architecture | Domain Knowledge | ACTIVE | Intelligence | `knowledge/domain/RELATIONSHIP_ARCHITECTURE.md` | Agent 2 | V2.1 Graph | Entity taxonomy, temporal edge validation (`valid_from`, `valid_to`), and multi-hop traversal. |
| **KN-006** | Project Context & Operational State | Canonical Context | ACTIVE | System | `knowledge/canonical/PROJECT_CONTEXT.md` | All Agents | Post-Research | Current operational readiness, frozen scientific branch state, and security boundaries. |
| **KN-007** | Project Memory & Experiment Ledger | Canonical Memory | ACTIVE | System | `knowledge/canonical/PROJECT_MEMORY.md` | All Agents | COBA_001–018 | Exhaustive historical experiment memory, statistical findings, and research closure logs. |
| **KN-008** | ZZZ147 Scientific & Firewall Spec | Scientific Spec | FROZEN | Research | `knowledge/canonical/ZZZ147_FIREWALL_SPEC.md` | Agent 1, 2, 3 | COBA_017–018 | Outcome blindness, PIT replay firewall, and peer exclusion mathematical proofs. |
| **KN-009** | Replay Firewall Specification | Operational Spec | ACTIVE | Engineering | `knowledge/canonical/REPLAY_FIREWALL_SPEC_ZZZ142.md` | Agent 2, 3 | Post-Research | 5-timestamp Point-In-Time enforcement engine (`core/replay_firewall.py`). |
| **KN-010** | Intelligence V2.1 Integration Report | Audit & Evidence | ACTIVE | Intelligence | `reports/intelligence/INTELLIGENCE_DECISION_INTEGRATION_REPORT.md` | Agent 2, 3 | V2.1 Gate | Complete validation of Information $\rightarrow$ Entity $\rightarrow$ Exposure $\rightarrow$ Mechanism $\rightarrow$ Agent 2 $\rightarrow$ Agent 3. |
| **KN-011** | Intelligence V2.1 Final Acceptance | Acceptance Gate | ACTIVE | Intelligence | `reports/intelligence/GRAPH_FINAL_ACCEPTANCE.md` | All Agents | V2.1 Gate | Forensic defect reconciliation, test pass rates (67/67), and Truth Gate closure. |
| **KN-012** | COBA Historical Mapping & Lineage | Governance Map | FROZEN | Governance | `governance/change_control/COBA_HISTORICAL_MAPPING.md` | All Agents | COBA_001–018 | Complete historical lineage mapping from COBA_001 through COBA_018 closure. |
