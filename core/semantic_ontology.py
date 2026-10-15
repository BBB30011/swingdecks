"""
SwingDeck — Market World Model & Semantic Ontology Layer V1.0
Canonical definitions, compatibility rules, conflict matrices, and semantic validators.
"""

from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field

class EntityType(str, Enum):
    COMPANY = "COMPANY"
    HOLDING_COMPANY = "HOLDING_COMPANY"
    SUBSIDIARY = "SUBSIDIARY"
    PERSON = "PERSON"
    GOVERNMENT = "GOVERNMENT"
    MINISTRY = "MINISTRY"
    REGULATOR = "REGULATOR"
    EXCHANGE = "EXCHANGE"
    CENTRAL_BANK = "CENTRAL_BANK"
    POLITICAL_PARTY = "POLITICAL_PARTY"
    POLITICAL_ACTOR = "POLITICAL_ACTOR"
    STATE_OWNED_ENTITY = "STATE_OWNED_ENTITY"
    INVESTOR = "INVESTOR"
    FUND = "FUND"
    BANK = "BANK"
    INSURER = "INSURER"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    COMMODITY = "COMMODITY"
    FX = "FX"
    CURRENCY = "CURRENCY"
    COUNTRY = "COUNTRY"
    REGION = "REGION"
    PROJECT = "PROJECT"
    POLICY = "POLICY"
    LAW = "LAW"
    REGULATION = "REGULATION"
    EVENT = "EVENT"
    SOCIAL_GROUP = "SOCIAL_GROUP"
    INSTITUTION = "INSTITUTION"
    INDEX = "INDEX"
    SECURITY = "SECURITY"
    MARKET = "MARKET"
    UNKNOWN = "UNKNOWN"

class RelationshipType(str, Enum):
    OWNS = "OWNS"
    CONTROLS = "CONTROLS"
    SUBSIDIARY_OF = "SUBSIDIARY_OF"
    MANAGES = "MANAGES"
    INVESTS_IN = "INVESTS_IN"
    LENDS_TO = "LENDS_TO"
    SUPPLIES = "SUPPLIES"
    CUSTOMER_OF = "CUSTOMER_OF"
    COMPETES_WITH = "COMPETES_WITH"
    REGULATES = "REGULATES"
    OPERATES = "OPERATES"
    LISTED_ON = "LISTED_ON"
    ISSUES = "ISSUES"
    ACQUIRES = "ACQUIRES"
    DISPOSES = "DISPOSES"
    PARTNERS_WITH = "PARTNERS_WITH"
    EXPOSED_TO = "EXPOSED_TO"
    DEPENDS_ON = "DEPENDS_ON"
    BENEFITS_FROM = "BENEFITS_FROM"
    HARMED_BY = "HARMED_BY"
    SUBJECT_TO = "SUBJECT_TO"
    ANNOUNCES = "ANNOUNCES"
    IMPLEMENTS = "IMPLEMENTS"
    PROPOSES = "PROPOSES"
    OPPOSES = "OPPOSES"
    IMPACTS = "IMPACTS"
    OPERATES_IN = "OPERATES_IN"
    PEER = "PEER"
    RELATED_TO = "RELATED_TO"

class EconomicChannel(str, Enum):
    TAX = "TAX"
    SUBSIDY = "SUBSIDY"
    IMPORT_DUTY = "IMPORT_DUTY"
    EXPORT_RESTRICTION = "EXPORT_RESTRICTION"
    LICENSING = "LICENSING"
    PERMIT = "PERMIT"
    PROCUREMENT = "PROCUREMENT"
    GOVERNMENT_SPENDING = "GOVERNMENT_SPENDING"
    INTEREST_RATE = "INTEREST_RATE"
    FX = "FX"
    COMMODITY_PRICE = "COMMODITY_PRICE"
    ENERGY_COST = "ENERGY_COST"
    INPUT_COST = "INPUT_COST"
    DEMAND = "DEMAND"
    SUPPLY = "SUPPLY"
    CAPEX = "CAPEX"
    REGULATORY_COST = "REGULATORY_COST"
    MARKET_ACCESS = "MARKET_ACCESS"
    CREDIT = "CREDIT"
    LIQUIDITY = "LIQUIDITY"
    OWNERSHIP = "OWNERSHIP"
    COMPETITION = "COMPETITION"

class ExposureType(str, Enum):
    DIRECT_EXPOSURE = "DIRECT_EXPOSURE"
    INDIRECT_EXPOSURE = "INDIRECT_EXPOSURE"
    SECOND_ORDER_EXPOSURE = "SECOND_ORDER_EXPOSURE"
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    REVENUE = "REVENUE"
    COST = "COST"
    COMMODITY = "COMMODITY"
    POLICY = "POLICY"
    REGULATORY = "REGULATORY"
    GEOGRAPHIC = "GEOGRAPHIC"
    OWNERSHIP = "OWNERSHIP"
    CONTROL = "CONTROL"
    FINANCING = "FINANCING"
    UNKNOWN_EXPOSURE = "UNKNOWN_EXPOSURE"

class ContradictionType(str, Enum):
    FACTUAL_CONTRADICTION = "FACTUAL_CONTRADICTION"
    TEMPORAL_CONTRADICTION = "TEMPORAL_CONTRADICTION"
    ENTITY_CONTRADICTION = "ENTITY_CONTRADICTION"
    RELATIONSHIP_CONTRADICTION = "RELATIONSHIP_CONTRADICTION"
    MAGNITUDE_CONTRADICTION = "MAGNITUDE_CONTRADICTION"
    INTERPRETATION_CONTRADICTION = "INTERPRETATION_CONTRADICTION"
    MECHANISM_CONTRADICTION = "MECHANISM_CONTRADICTION"

class AccessClass(str, Enum):
    PUBLIC = "PUBLIC"
    AUTHORIZED_PRIVATE = "AUTHORIZED_PRIVATE"
    RESTRICTED = "RESTRICTED"
    MNPI = "MNPI"
    UNKNOWN = "UNKNOWN"

class EvidenceClassification(str, Enum):
    NATURAL = "NATURAL"
    HISTORICAL = "HISTORICAL"
    FIXTURE = "FIXTURE"
    SYNTHETIC = "SYNTHETIC"
    FAILURE_INJECTION = "FAILURE_INJECTION"
    CONTROLLED = "CONTROLLED"


# =====================================================================
# ENTITY SEMANTIC CONFLICT & COMPATIBILITY RULES
# =====================================================================

ENTITY_MUTUALLY_EXCLUSIVE_GROUPS: List[Set[EntityType]] = [
    {EntityType.EXCHANGE, EntityType.REGULATOR, EntityType.CENTRAL_BANK, EntityType.MINISTRY, EntityType.POLITICAL_PARTY},
    {EntityType.PERSON, EntityType.COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.GOVERNMENT, EntityType.COUNTRY},
    {EntityType.POLICY, EntityType.COMPANY, EntityType.PERSON, EntityType.COMMODITY, EntityType.BANK},
    {EntityType.COMMODITY, EntityType.COMPANY, EntityType.REGULATOR, EntityType.EXCHANGE}
]

CANONICAL_INDONESIAN_ENTITY_GROUND_TRUTH: Dict[str, Dict[str, Any]] = {
    "IDX": {
        "canonical_name": "PT Bursa Efek Indonesia",
        "entity_type": EntityType.EXCHANGE,
        "forbidden_types": {EntityType.REGULATOR, EntityType.MINISTRY, EntityType.CENTRAL_BANK, EntityType.POLITICAL_PARTY},
        "description": "Indonesian stock exchange / market operator (Self-Regulatory Organization, corporation)"
    },
    "OJK": {
        "canonical_name": "Otoritas Jasa Keuangan",
        "entity_type": EntityType.REGULATOR,
        "forbidden_types": {EntityType.EXCHANGE, EntityType.COMPANY, EntityType.BANK},
        "description": "Statutory financial services and capital market regulator of Indonesia"
    },
    "BI": {
        "canonical_name": "Bank Indonesia",
        "entity_type": EntityType.CENTRAL_BANK,
        "forbidden_types": {EntityType.EXCHANGE, EntityType.REGULATOR, EntityType.COMPANY, EntityType.COMMODITY},
        "description": "Central Bank of the Republic of Indonesia"
    },
    "BAPEPAM_LK": {
        "canonical_name": "Badan Pengawas Pasar Modal dan Lembaga Keuangan",
        "entity_type": EntityType.REGULATOR,
        "forbidden_types": {EntityType.EXCHANGE, EntityType.COMPANY},
        "description": "Historical Indonesian capital market supervisory agency (pre-OJK)"
    },
    "KEMENKEU": {
        "canonical_name": "Kementerian Keuangan Republik Indonesia",
        "entity_type": EntityType.MINISTRY,
        "forbidden_types": {EntityType.EXCHANGE, EntityType.COMPANY, EntityType.REGULATOR},
        "description": "Ministry of Finance of Indonesia"
    },
    "MEMR": {
        "canonical_name": "Kementerian Energi dan Sumber Daya Mineral",
        "entity_type": EntityType.MINISTRY,
        "forbidden_types": {EntityType.EXCHANGE, EntityType.COMPANY, EntityType.REGULATOR},
        "description": "Ministry of Energy and Mineral Resources of Indonesia"
    },
    "ADRO": {
        "canonical_name": "PT Adaro Energy Indonesia Tbk",
        "entity_type": EntityType.COMPANY,
        "forbidden_types": {EntityType.REGULATOR, EntityType.EXCHANGE, EntityType.PERSON, EntityType.CENTRAL_BANK},
        "description": "Private integrated energy holding conglomerate listed on IDX"
    },
    "AADI": {
        "canonical_name": "PT Adaro Andalan Indonesia Tbk",
        "entity_type": EntityType.SUBSIDIARY,
        "forbidden_types": {EntityType.REGULATOR, EntityType.EXCHANGE, EntityType.PERSON},
        "description": "Thermal coal mining subsidiary spun off from ADRO in 2024"
    },
    "BBCA": {
        "canonical_name": "PT Bank Central Asia Tbk",
        "entity_type": EntityType.BANK,
        "forbidden_types": {EntityType.REGULATOR, EntityType.CENTRAL_BANK, EntityType.EXCHANGE, EntityType.PERSON},
        "description": "Private commercial bank listed on IDX"
    },
    "PTBA": {
        "canonical_name": "PT Bukit Asam Tbk",
        "entity_type": EntityType.STATE_OWNED_ENTITY,
        "forbidden_types": {EntityType.REGULATOR, EntityType.EXCHANGE, EntityType.CENTRAL_BANK},
        "description": "State-owned coal mining enterprise (MIND ID member)"
    },
    "ANTM": {
        "canonical_name": "PT Aneka Tambang Tbk",
        "entity_type": EntityType.STATE_OWNED_ENTITY,
        "forbidden_types": {EntityType.REGULATOR, EntityType.EXCHANGE, EntityType.CENTRAL_BANK},
        "description": "State-owned diversified mining enterprise"
    }
}


RELATIONSHIP_COMPATIBILITY_RULES: Dict[RelationshipType, Dict[str, Set[EntityType]]] = {
    RelationshipType.OWNS: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.INVESTOR, EntityType.FUND, EntityType.PERSON, EntityType.BANK, EntityType.INSURER, EntityType.GOVERNMENT},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.BANK, EntityType.INSURER, EntityType.PROJECT, EntityType.SECURITY}
    },
    RelationshipType.CONTROLS: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.INVESTOR, EntityType.PERSON, EntityType.GOVERNMENT},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.BANK, EntityType.PROJECT}
    },
    RelationshipType.SUBSIDIARY_OF: {
        "allowed_subjects": {EntityType.SUBSIDIARY, EntityType.COMPANY, EntityType.BANK, EntityType.INSURER},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.BANK}
    },
    RelationshipType.REGULATES: {
        "allowed_subjects": {EntityType.REGULATOR, EntityType.CENTRAL_BANK, EntityType.GOVERNMENT, EntityType.MINISTRY},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.EXCHANGE, EntityType.BANK, EntityType.INSURER, EntityType.MARKET, EntityType.SECTOR, EntityType.INDUSTRY, EntityType.SECURITY}
    },
    RelationshipType.OPERATES: {
        "allowed_subjects": {EntityType.EXCHANGE, EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.INSTITUTION},
        "allowed_objects": {EntityType.MARKET, EntityType.EXCHANGE, EntityType.PROJECT, EntityType.INDEX}
    },
    RelationshipType.LISTED_ON: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.INSURER, EntityType.SECURITY, EntityType.FUND},
        "allowed_objects": {EntityType.EXCHANGE, EntityType.MARKET}
    },
    RelationshipType.ISSUES: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.GOVERNMENT, EntityType.MINISTRY, EntityType.CENTRAL_BANK, EntityType.BANK},
        "allowed_objects": {EntityType.SECURITY, EntityType.POLICY, EntityType.REGULATION, EntityType.LAW}
    },
    RelationshipType.SUPPLIES: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.COMMODITY},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.SECTOR, EntityType.INDUSTRY}
    },
    RelationshipType.CUSTOMER_OF: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.PERSON, EntityType.GOVERNMENT},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK}
    },
    RelationshipType.COMPETES_WITH: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.INSURER},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.INSURER}
    },
    RelationshipType.PROPOSES: {
        "allowed_subjects": {EntityType.GOVERNMENT, EntityType.MINISTRY, EntityType.REGULATOR, EntityType.POLITICAL_PARTY, EntityType.POLITICAL_ACTOR, EntityType.PERSON},
        "allowed_objects": {EntityType.POLICY, EntityType.LAW, EntityType.REGULATION, EntityType.PROJECT}
    },
    RelationshipType.IMPLEMENTS: {
        "allowed_subjects": {EntityType.GOVERNMENT, EntityType.MINISTRY, EntityType.REGULATOR, EntityType.CENTRAL_BANK, EntityType.STATE_OWNED_ENTITY, EntityType.INSTITUTION},
        "allowed_objects": {EntityType.POLICY, EntityType.LAW, EntityType.REGULATION, EntityType.PROJECT}
    },
    RelationshipType.EXPOSED_TO: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.INSURER, EntityType.SECTOR, EntityType.INDUSTRY, EntityType.FUND},
        "allowed_objects": {EntityType.COMMODITY, EntityType.FX, EntityType.CURRENCY, EntityType.POLICY, EntityType.LAW, EntityType.REGULATION, EntityType.EVENT, EntityType.COUNTRY, EntityType.REGION, EntityType.MARKET}
    },
    RelationshipType.DEPENDS_ON: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.SECTOR},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.COMMODITY, EntityType.FX, EntityType.POLICY, EntityType.COUNTRY, EntityType.PROJECT}
    },
    RelationshipType.IMPACTS: {
        "allowed_subjects": {EntityType.POLICY, EntityType.LAW, EntityType.REGULATION, EntityType.EVENT, EntityType.COMMODITY, EntityType.FX, EntityType.CENTRAL_BANK, EntityType.REGULATOR, EntityType.MINISTRY},
        "allowed_objects": {EntityType.SECTOR, EntityType.INDUSTRY, EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.MARKET, EntityType.BANK}
    },
    RelationshipType.OPERATES_IN: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.SUBSIDIARY, EntityType.BANK, EntityType.INSURER},
        "allowed_objects": {EntityType.SECTOR, EntityType.INDUSTRY, EntityType.COMMODITY, EntityType.MARKET, EntityType.REGION, EntityType.COUNTRY}
    },
    RelationshipType.DISPOSES: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.INVESTOR, EntityType.GOVERNMENT},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.PROJECT, EntityType.SECURITY}
    },
    RelationshipType.ACQUIRES: {
        "allowed_subjects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.STATE_OWNED_ENTITY, EntityType.INVESTOR, EntityType.GOVERNMENT, EntityType.BANK},
        "allowed_objects": {EntityType.COMPANY, EntityType.HOLDING_COMPANY, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.PROJECT, EntityType.SECURITY}
    },
    RelationshipType.PEER: {
        "allowed_subjects": set(EntityType),
        "allowed_objects": set(EntityType)
    },
    RelationshipType.RELATED_TO: {
        "allowed_subjects": set(EntityType),
        "allowed_objects": set(EntityType)
    }
}


def validate_entity_semantic_type(entity_id: str, proposed_type: str) -> Tuple[bool, str, Optional[EntityType]]:
    try:
        e_type = EntityType(proposed_type)
    except ValueError:
        return False, f"Invalid entity type: '{proposed_type}' is not recognized in semantic ontology", EntityType.UNKNOWN

    norm_id = entity_id.upper().strip()
    clean_id = norm_id.replace("ENT_", "")
    
    # Check by key or canonical name
    ground_truth = None
    if clean_id in CANONICAL_INDONESIAN_ENTITY_GROUND_TRUTH:
        ground_truth = CANONICAL_INDONESIAN_ENTITY_GROUND_TRUTH[clean_id]
    else:
        for k, v in CANONICAL_INDONESIAN_ENTITY_GROUND_TRUTH.items():
            if norm_id == v["canonical_name"].upper().strip() or clean_id == v["canonical_name"].upper().strip():
                ground_truth = v
                break

    if ground_truth:
        expected_type = ground_truth["entity_type"]
        forbidden = ground_truth["forbidden_types"]
        
        if e_type in forbidden:
            return False, f"Semantic violation: Entity '{norm_id}' cannot be classified as '{e_type.value}' (Forbidden for {ground_truth['canonical_name']}. Expected: {expected_type.value})", expected_type
            
        if e_type != expected_type and expected_type != EntityType.UNKNOWN:
            if expected_type == EntityType.BANK and e_type in [EntityType.COMPANY, EntityType.HOLDING_COMPANY]:
                return True, "Valid generalized classification", expected_type
            if expected_type == EntityType.STATE_OWNED_ENTITY and e_type in [EntityType.COMPANY, EntityType.HOLDING_COMPANY]:
                return True, "Valid generalized classification", expected_type
            if expected_type == EntityType.SUBSIDIARY and e_type in [EntityType.COMPANY, EntityType.HOLDING_COMPANY]:
                return True, "Valid generalized classification", expected_type
            if expected_type == EntityType.COMPANY and e_type in [EntityType.HOLDING_COMPANY, EntityType.SUBSIDIARY]:
                return True, "Valid generalized classification", expected_type
            return False, f"Semantic mismatch: Entity '{norm_id}' is canonically '{expected_type.value}', not '{e_type.value}'", expected_type

    return True, "Semantic classification valid", e_type


def validate_relationship_semantics(subject_type: str, predicate: str, object_type: str) -> Tuple[bool, str]:
    try:
        s_type = EntityType(subject_type)
        p_type = RelationshipType(predicate)
        o_type = EntityType(object_type)
    except ValueError as err:
        return False, f"Invalid ontology symbol: {err}"

    if p_type not in RELATIONSHIP_COMPATIBILITY_RULES:
        return True, "Predicate has no restrictive compatibility rules"

    rules = RELATIONSHIP_COMPATIBILITY_RULES[p_type]
    allowed_subs = rules.get("allowed_subjects", set())
    allowed_objs = rules.get("allowed_objects", set())

    if p_type == RelationshipType.SUBSIDIARY_OF and o_type == EntityType.SUBSIDIARY:
        return False, "Semantic invalidity: A SUBSIDIARY cannot be the parent object of SUBSIDIARY_OF"

    eff_sub = s_type
    if eff_sub in {EntityType.BANK, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.HOLDING_COMPANY} and EntityType.COMPANY in allowed_subs:
        pass
    elif eff_sub not in allowed_subs:
        return False, f"Semantic invalidity: Subject '{s_type.value}' cannot perform predicate '{p_type.value}' (Allowed subjects: {[t.value for t in allowed_subs]})"

    eff_obj = o_type
    if eff_obj in {EntityType.BANK, EntityType.SUBSIDIARY, EntityType.STATE_OWNED_ENTITY, EntityType.HOLDING_COMPANY} and EntityType.COMPANY in allowed_objs:
        pass
    elif eff_obj not in allowed_objs:
        return False, f"Semantic invalidity: Object '{o_type.value}' cannot be target of predicate '{p_type.value}' (Allowed objects: {[t.value for t in allowed_objs]})"

    return True, "Relationship semantics valid"


def validate_policy_transmission_chain(
    event_type: str,
    policy_type: str,
    implementer_type: str,
    economic_channel: str,
    target_sector_or_company: str
) -> Tuple[bool, str]:
    if event_type not in ["POLITICAL_EVENT", "POLICY_EVENT", "REGULATORY_EVENT", "MACRO_EVENT", "EVENT"]:
        return False, f"Invalid root event type for policy transmission: '{event_type}'"

    if policy_type not in [EntityType.POLICY.value, EntityType.LAW.value, EntityType.REGULATION.value, EntityType.EVENT.value, "STATUTE", "DECREE"]:
        return False, f"Invalid policy intermediary: '{policy_type}' is not a policy/law/regulation"

    if implementer_type not in [EntityType.GOVERNMENT.value, EntityType.MINISTRY.value, EntityType.REGULATOR.value, EntityType.CENTRAL_BANK.value]:
        return False, f"Invalid policy implementer: '{implementer_type}' cannot implement statutory policy"

    try:
        EconomicChannel(economic_channel)
    except ValueError:
        return False, f"Invalid economic channel: '{economic_channel}' is not an authorized economic transmission channel"

    return True, "Policy transmission chain structurally valid"
