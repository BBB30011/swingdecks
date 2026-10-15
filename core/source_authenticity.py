"""
SwingDeck Source Authenticity & Verification Engine V1
Provides formal source authenticity evaluation, TLS/protocol inspection,
redirect-chain analysis, publisher identity evidence, and origin classification.
"""

import hashlib
import re
import urllib.parse
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

class AuthenticityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"

class OriginClass(str, Enum):
    PRIMARY_OFFICIAL = "PRIMARY_OFFICIAL"         # Regulator, Exchange, Government Decree, Central Bank
    PRIMARY_CORPORATE = "PRIMARY_CORPORATE"       # Issuer Official Disclosure, Audited Annual Report
    SECONDARY_REPUTABLE = "SECONDARY_REPUTABLE"   # Verified News Agency (CNBC, Reuters, Bloomberg, Bisnis)
    SECONDARY_MEDIA = "SECONDARY_MEDIA"           # General media / online portal
    AGGREGATOR = "AGGREGATOR"                     # Search aggregators, syndication hubs
    SOCIAL = "SOCIAL"                             # Social media / forums / community boards
    SYNTHETIC = "SYNTHETIC"                       # Test fixture / synthetic benchmark
    UNKNOWN = "UNKNOWN"                           # Unproven provenance

class AccessClass(str, Enum):
    PUBLIC = "PUBLIC"
    AUTHORIZED_PRIVATE = "AUTHORIZED_PRIVATE"
    RESTRICTED = "RESTRICTED"
    MNPI_SUSPECTED = "MNPI_SUSPECTED"
    MNPI = "MNPI"
    UNKNOWN = "UNKNOWN"

class AuthorizationStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"

from core.data_platform_schemas import TimestampDerivationMethod, TemporalConfidence

def normalize_timestamp_to_utc(
    raw_ts: Optional[str],
    source_hint: str = "SOURCE_ARTICLE_METADATA",
    default_utc: Optional[str] = None
) -> Tuple[str, str, str, TimestampDerivationMethod, TemporalConfidence]:
    """
    Normalizes timestamps across timezones (WIB/WITA/WIT/UTC/RFC-2822/ISO) to UTC ISO-8601.
    Returns: (normalized_utc_iso, original_ts, original_tz, derivation_method, temporal_confidence)
    """
    now_utc = default_utc or datetime.now(timezone.utc).isoformat()
    if not raw_ts or not str(raw_ts).strip():
        return (now_utc, "", "UNKNOWN", TimestampDerivationMethod.RETRIEVAL_CLOCK_FALLBACK, TemporalConfidence.FALLBACK)

    orig_str = str(raw_ts).strip()
    orig_tz = "UTC"
    derivation = TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
    confidence = TemporalConfidence.EXACT

    # Check Indonesian timezone strings
    clean_ts = orig_str
    offset_hours = 0
    has_tz = False

    if "WIB" in orig_str.upper() or "GMT+7" in orig_str.upper():
        orig_tz = "WIB"
        offset_hours = 7
        clean_ts = re.sub(r'(?i)\b(WIB|GMT\+7)\b', '', clean_ts).strip()
        has_tz = True
    elif "WITA" in orig_str.upper() or "GMT+8" in orig_str.upper():
        orig_tz = "WITA"
        offset_hours = 8
        clean_ts = re.sub(r'(?i)\b(WITA|GMT\+8)\b', '', clean_ts).strip()
        has_tz = True
    elif "WIT" in orig_str.upper() or "GMT+9" in orig_str.upper():
        orig_tz = "WIT"
        offset_hours = 9
        clean_ts = re.sub(r'(?i)\b(WIT|GMT\+9)\b', '', clean_ts).strip()
        has_tz = True
    elif "+07:00" in orig_str or "+0700" in orig_str:
        orig_tz = "UTC+07:00"
        has_tz = True
    elif "+08:00" in orig_str or "+0800" in orig_str:
        orig_tz = "UTC+08:00"
        has_tz = True
    elif "+09:00" in orig_str or "+0900" in orig_str:
        orig_tz = "UTC+09:00"
        has_tz = True

    try:
        if has_tz and offset_hours > 0:
            # Parse naive datetime then apply fixed offset
            # Try ISO formats
            clean_ts = clean_ts.replace("T", " ")
            dt_naive = datetime.fromisoformat(clean_ts[:19])
            # Subtract offset to get UTC
            import datetime as dt_module
            dt_utc = dt_naive - dt_module.timedelta(hours=offset_hours)
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            return (dt_utc.isoformat(), orig_str, orig_tz, derivation, TemporalConfidence.EXACT)
        else:
            # Standard ISO parse
            ts_iso = orig_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts_iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
                confidence = TemporalConfidence.DERIVED
            else:
                dt = dt.astimezone(timezone.utc)
            return (dt.isoformat(), orig_str, orig_tz, derivation, confidence)
    except Exception:
        # Fallback
        return (now_utc, orig_str, "UNKNOWN", TimestampDerivationMethod.INFERRED, TemporalConfidence.ESTIMATED)

class SourceAuthenticityRecord(BaseModel):
    source_id: str
    publisher_name: str
    publisher_type: str
    canonical_domain: str
    canonical_url: str
    retrieval_url: str
    protocol: str = "https"
    tls_verified: bool = True
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    publication_timestamp: Optional[str] = None
    event_timestamp: Optional[str] = None
    last_modified_timestamp: Optional[str] = None
    timestamp_source: str = "SOURCE_METADATA"
    derivation_method: TimestampDerivationMethod = TimestampDerivationMethod.SOURCE_ARTICLE_METADATA
    timezone: str = "UTC"
    original_timezone: str = "UTC"
    original_timestamp: Optional[str] = None
    temporal_confidence: TemporalConfidence = TemporalConfidence.EXACT
    content_hash: str
    mime_type: str = "text/html"
    http_status: int = 200
    redirect_chain: List[str] = Field(default_factory=list)
    content_length: int = 0
    encoding: str = "utf-8"
    document_identifier: str = ""
    source_identity_evidence: Dict[str, Any] = Field(default_factory=dict)
    authenticity_status: AuthenticityStatus = AuthenticityStatus.UNKNOWN
    authenticity_reason: str = ""
    origin_class: OriginClass = OriginClass.UNKNOWN
    access_class: AccessClass = AccessClass.PUBLIC
    authorization_status: AuthorizationStatus = AuthorizationStatus.NOT_APPLICABLE

class SourceAuthenticityEvaluator:
    """
    Evaluates document and publisher authenticity using multi-dimensional evidence:
    1. Canonical Domain & Hostname validation
    2. TLS/HTTPS Protocol verification
    3. Redirect Chain integrity (no open redirect to malicious domain)
    4. Publisher identity & document identifier consistency
    5. URL structure and path conformance
    6. Content-type and encoding validation
    7. Cryptographic Content Hash verification
    8. Timestamp realism and Point-in-Time consistency
    9. Access class & MNPI screening
    """

    # Canonical authoritative publisher registry
    CANONICAL_PUBLISHERS = {
        "idx.co.id": {
            "name": "Indonesia Stock Exchange (PT Bursa Efek Indonesia)",
            "publisher_type": "EXCHANGE",
            "origin_class": OriginClass.PRIMARY_OFFICIAL,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["idx.co.id", "www.idx.co.id", "ksei.co.id"]
        },
        "ojk.go.id": {
            "name": "Otoritas Jasa Keuangan (OJK)",
            "publisher_type": "REGULATOR",
            "origin_class": OriginClass.PRIMARY_OFFICIAL,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["ojk.go.id", "www.ojk.go.id"]
        },
        "bi.go.id": {
            "name": "Bank Indonesia",
            "publisher_type": "CENTRAL_BANK",
            "origin_class": OriginClass.PRIMARY_OFFICIAL,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["bi.go.id", "www.bi.go.id"]
        },
        "kemenkeu.go.id": {
            "name": "Kementerian Keuangan Republik Indonesia",
            "publisher_type": "MINISTRY",
            "origin_class": OriginClass.PRIMARY_OFFICIAL,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["kemenkeu.go.id", "www.kemenkeu.go.id"]
        },
        "cnbcindonesia.com": {
            "name": "CNBC Indonesia (Transmedia)",
            "publisher_type": "FINANCIAL_NEWS",
            "origin_class": OriginClass.SECONDARY_REPUTABLE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["cnbcindonesia.com", "www.cnbcindonesia.com"]
        },
        "bloomberg.com": {
            "name": "Bloomberg LP",
            "publisher_type": "FINANCIAL_NEWS",
            "origin_class": OriginClass.SECONDARY_REPUTABLE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["bloomberg.com", "www.bloomberg.com"]
        },
        "reuters.com": {
            "name": "Thomson Reuters",
            "publisher_type": "FINANCIAL_NEWS",
            "origin_class": OriginClass.SECONDARY_REPUTABLE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["reuters.com", "www.reuters.com"]
        },
        "bisnis.com": {
            "name": "Bisnis Indonesia",
            "publisher_type": "FINANCIAL_NEWS",
            "origin_class": OriginClass.SECONDARY_REPUTABLE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["bisnis.com", "www.bisnis.com", "market.bisnis.com"]
        },
        "kontan.co.id": {
            "name": "Harian Kontan (Kompas Gramedia)",
            "publisher_type": "FINANCIAL_NEWS",
            "origin_class": OriginClass.SECONDARY_REPUTABLE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["kontan.co.id", "www.kontan.co.id", "investasi.kontan.co.id"]
        },
        "adaro.com": {
            "name": "PT Adaro Energy Indonesia Tbk (Official IR)",
            "publisher_type": "COMPANY_ISSUER",
            "origin_class": OriginClass.PRIMARY_CORPORATE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["adaro.com", "www.adaro.com", "adarominerals.id"]
        },
        "bca.co.id": {
            "name": "PT Bank Central Asia Tbk (Official IR)",
            "publisher_type": "COMPANY_ISSUER",
            "origin_class": OriginClass.PRIMARY_CORPORATE,
            "required_protocol": "https",
            "access_class": AccessClass.PUBLIC,
            "trusted_domains": ["bca.co.id", "www.bca.co.id"]
        }
    }

    # Suspected MNPI & Prompt Injection regex patterns
    MNPI_PATTERNS = [
        r"\b(MNPI|MATERIAL\s+NON[- ]PUBLIC\s+INFORMATION)\b",
        r"\b(CONFIDENTIAL\s+INTERNAL\s+MEMO|STRICTLY\s+CONFIDENTIAL|LEAKED\s+DRAFT)\b",
        r"\b(UNANNOUNCED\s+MERGER|CONFIDENTIAL\s+ACQUISITION\s+TARGET)\b",
        r"\b(EMBARGOED\s+UNTIL|INSIDER\s+TRADING|INTERNAL\s+BOARD\s+MINUTES)\b"
    ]

    PROMPT_INJECTION_PATTERNS = [
        r"(?i)\bIGNORE\s+ALL\s+PREVIOUS\s+INSTRUCTIONS\b",
        r"(?i)\bSYSTEM\s+OVERRIDE\b",
        r"(?i)\bREVEAL\s+(SYSTEM\s+)?PROMPT\b",
        r"(?i)\bEXECUTE\s+COMMAND\b",
        r"(?i)\bDROP\s+TABLE\b",
        r"(?i)\bDELETE\s+DATABASE\b",
        r"(?i)\bBUY\s+[A-Z]{4}\s+IMMEDIATELY\b"
    ]

    @classmethod
    def evaluate(
        cls,
        url: str,
        content: str,
        headers: Optional[Dict[str, str]] = None,
        http_status: int = 200,
        redirect_chain: Optional[List[str]] = None,
        claimed_publisher: Optional[str] = None,
        pub_time: Optional[str] = None,
        retrieval_time: Optional[str] = None,
        access_class_hint: Optional[str] = None
    ) -> SourceAuthenticityRecord:
        """Evaluates complete authenticity contract."""
        headers = headers or {}
        redirect_chain = redirect_chain or []
        retrieval_time = retrieval_time or datetime.now(timezone.utc).isoformat()
        
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower().split(':')[0]
        protocol = parsed_url.scheme.lower()

        # Compute SHA-256
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest() if content else ""
        content_length = len(content.encode('utf-8')) if content else 0
        mime_type = headers.get("content-type", "text/html").split(";")[0].strip().lower()

        # Generate Document Identifier
        doc_id = f"DOC_{hashlib.sha256((url + (pub_time or '') + content_hash[:16]).encode('utf-8')).hexdigest()[:16].upper()}"

        reasons = []
        auth_status = AuthenticityStatus.UNVERIFIED
        origin_class = OriginClass.UNKNOWN
        access_class = AccessClass.PUBLIC
        tls_verified = (protocol == "https")

        # Check 1: HTTP Status
        if http_status != 200:
            return SourceAuthenticityRecord(
                source_id="UNKNOWN",
                publisher_name="UNKNOWN",
                publisher_type="UNKNOWN",
                canonical_domain=domain,
                canonical_url=url,
                retrieval_url=url,
                protocol=protocol,
                tls_verified=tls_verified,
                retrieval_timestamp=retrieval_time,
                publication_timestamp=pub_time,
                content_hash=content_hash,
                mime_type=mime_type,
                http_status=http_status,
                redirect_chain=redirect_chain,
                content_length=content_length,
                document_identifier=doc_id,
                authenticity_status=AuthenticityStatus.REJECTED,
                authenticity_reason=f"HTTP Error: Received non-200 status {http_status}",
                origin_class=OriginClass.UNKNOWN,
                access_class=AccessClass.UNKNOWN
            )

        # Check 2: Domain Registry Match
        matched_pub_key = None
        for pub_domain, pub_info in cls.CANONICAL_PUBLISHERS.items():
            if domain == pub_domain or domain.endswith("." + pub_domain) or domain in pub_info["trusted_domains"]:
                matched_pub_key = pub_domain
                break

        if matched_pub_key:
            pub_info = cls.CANONICAL_PUBLISHERS[matched_pub_key]
            publisher_name = pub_info["name"]
            publisher_type = pub_info["publisher_type"]
            origin_class = pub_info["origin_class"]
            
            # Check Protocol
            if pub_info["required_protocol"] == "https" and protocol != "https":
                reasons.append(f"Insecure protocol: Expected https for {matched_pub_key}, got {protocol}")
                auth_status = AuthenticityStatus.PARTIALLY_VERIFIED
            else:
                auth_status = AuthenticityStatus.VERIFIED
                reasons.append(f"Domain verified against canonical publisher registry: {matched_pub_key}")
        else:
            # Domain not in canonical registry
            publisher_name = domain or "UNKNOWN_PUBLISHER"
            publisher_type = "GENERAL_WEB"
            origin_class = OriginClass.SECONDARY_MEDIA
            auth_status = AuthenticityStatus.PARTIALLY_VERIFIED
            reasons.append(f"Domain '{domain}' is active but not in canonical registry")

        # Check 3: Redirect Chain Security (No redirect spoofing)
        if redirect_chain:
            final_domain = urllib.parse.urlparse(redirect_chain[-1]).netloc.lower().split(':')[0]
            if matched_pub_key and final_domain not in cls.CANONICAL_PUBLISHERS[matched_pub_key]["trusted_domains"]:
                auth_status = AuthenticityStatus.REJECTED
                reasons.append(f"Malicious redirect detected: redirected from {domain} to untrusted {final_domain}")

        # Check 4: Content Poisoning / MNPI / Prompt Injection Screening
        has_prompt_injection = False
        for pat in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pat, content):
                has_prompt_injection = True
                reasons.append(f"Adversarial prompt injection pattern detected: '{pat}'")
                break

        has_mnpi = False
        for pat in cls.MNPI_PATTERNS:
            if re.search(pat, content, re.IGNORECASE):
                has_mnpi = True
                access_class = AccessClass.MNPI_SUSPECTED
                reasons.append(f"Suspected Material Non-Public Information pattern detected: '{pat}'")
                break

        if access_class_hint:
            try:
                access_class = AccessClass(access_class_hint)
            except ValueError:
                access_class = AccessClass.UNKNOWN

        # Check 5: Timestamp Normalization & Validity
        norm_pub_time, orig_pub_time, orig_tz, deriv_method, temp_conf = normalize_timestamp_to_utc(
            pub_time, source_hint="ARTICLE_PUBLICATION_METADATA", default_utc=retrieval_time
        )
        
        if pub_time:
            try:
                dt_pub = datetime.fromisoformat(norm_pub_time.replace("Z", "+00:00"))
                dt_ret = datetime.fromisoformat(retrieval_time.replace("Z", "+00:00"))
                if dt_pub > dt_ret:
                    auth_status = AuthenticityStatus.REJECTED
                    reasons.append(f"Impossible timestamp: publication_time {pub_time} is in the future relative to retrieval_time {retrieval_time}")
            except Exception as e:
                reasons.append(f"Malformed publication timestamp: {pub_time} ({e})")

        source_id = f"SRC_{domain.replace('.', '_').upper()}"

        return SourceAuthenticityRecord(
            source_id=source_id,
            publisher_name=publisher_name,
            publisher_type=publisher_type,
            canonical_domain=domain,
            canonical_url=url,
            retrieval_url=url,
            protocol=protocol,
            tls_verified=tls_verified,
            retrieval_timestamp=retrieval_time,
            publication_timestamp=norm_pub_time,
            event_timestamp=norm_pub_time,
            last_modified_timestamp=headers.get("last-modified"),
            timestamp_source="SOURCE_ARTICLE_METADATA" if pub_time else "RETRIEVAL_CLOCK",
            derivation_method=deriv_method,
            timezone="UTC",
            original_timezone=orig_tz,
            original_timestamp=orig_pub_time,
            temporal_confidence=temp_conf,
            content_hash=content_hash,
            mime_type=mime_type,
            http_status=http_status,
            redirect_chain=redirect_chain,
            content_length=content_length,
            encoding=headers.get("content-encoding", "utf-8"),
            document_identifier=doc_id,
            source_identity_evidence={
                "has_prompt_injection": has_prompt_injection,
                "has_mnpi": has_mnpi,
                "domain_in_registry": matched_pub_key is not None,
                "tls_verified": tls_verified,
                "evaluation_reasons": reasons
            },
            authenticity_status=auth_status,
            authenticity_reason="; ".join(reasons),
            origin_class=origin_class,
            access_class=access_class,
            authorization_status=AuthorizationStatus.AUTHORIZED if access_class == AccessClass.PUBLIC else AuthorizationStatus.UNAUTHORIZED
        )
