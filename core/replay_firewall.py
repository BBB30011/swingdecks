from typing import Dict, Any, List, Optional

class ReplayFirewall:
    """
    Enforces the Replay Eligibility logic (READY, CONDITIONAL, LIMITED, BLOCKED),
    Four-Timestamp filtering, Current-State rejection, Outcome blindness, and Silent Fallback prevention.
    """
    
    TOP_20_TICKERS = {
        "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "UNTR", "ADRO", 
        "PTBA", "ANTM", "INCO", "ITMG", "ICBP", "INDF", "GOTO", "AMMN", 
        "BRPT", "TPIA", "CPIN", "KLBF"
    }

    PROHIBITED_OUTCOME_FIELDS = {
        "H1", "H3", "H5", "H10", "H20", "target_H1", "target_H3", "target_H5", "target_H10", "target_H20",
        "target_h1", "target_h3", "target_h5", "target_h10", "target_h20", "forward_return",
        "peer_H1", "peer_H3", "peer_H5", "peer_H10", "peer_H20", "excess_H1", "excess_H3", "excess_H5", "excess_H10", "excess_H20",
        "h1", "h3", "h5", "h10", "h20", "mfe", "mae", "mfe_h5", "mae_h5", "peer_h5", "excess_h5", "h5_peer_excess"
    }

    @classmethod
    def evaluate_eligibility(cls, ticker: str, date: str, domain: str) -> str:
        """
        Returns the eligibility state for a specific company-date-domain.
        States: READY, CONDITIONAL, LIMITED, BLOCKED.
        """
        try:
            year = int(date.split("-")[0])
        except Exception:
            return "BLOCKED"
        
        domain_upper = domain.upper()
        
        if domain_upper == "MARKET":
            if year < 2000:
                return "BLOCKED"
            return "READY"
            
        if domain_upper == "CORPORATE_ACTION":
            if year < 2016:
                return "LIMITED"
            return "READY"
            
        if domain_upper in ["OWNERSHIP", "RELATIONSHIP"]:
            if year < 2018:
                return "LIMITED"
            return "READY"
            
        if domain_upper == "NEWS":
            if year < 2016:
                return "LIMITED"
            if ticker in cls.TOP_20_TICKERS:
                return "READY"
            return "CONDITIONAL" # Top 20 coverage bias
            
        if domain_upper in ["EXPOSURE", "PEER"]:
            return "READY"
            
        if domain_upper in ["MACRO", "COMMODITY"]:
            if year < 2016:
                return "LIMITED"
            return "READY"
            
        # Default fallback for unknown domains
        if year <= 2017:
            return "LIMITED"
            
        return "READY"

    @classmethod
    def prevent_future_leak(cls, record: Dict[str, Any], decision_datetime: str) -> bool:
        """
        Hard block on any record whose publication or availability timestamp is in the future relative to T.
        """
        # Check published_at
        if "published_at" in record and record["published_at"]:
            if str(record["published_at"]) > decision_datetime:
                return False
                
        # Check available_at
        if "available_at" in record and record["available_at"]:
            if str(record["available_at"]) > decision_datetime:
                return False
                
        # Check generic time/timestamp
        if "time" in record and record["time"]:
            if str(record["time"]) > decision_datetime:
                return False
        if "timestamp" in record and record["timestamp"]:
            ts_clean = str(record["timestamp"]).split("+")[0]
            if ts_clean > decision_datetime:
                return False
                
        # Check observed_at
        if "observed_at" in record and record["observed_at"]:
            if str(record["observed_at"]) > decision_datetime:
                return False
                
        return True

    @classmethod
    def prevent_current_state_leak(cls, record: Dict[str, Any], decision_date: Optional[str] = None) -> bool:
        """
        Blocks any record designated as 'current_state' object or having valid_from in the future relative to T.
        """
        if record.get("is_current_state", False):
            return False
            
        if decision_date:
            if "valid_from" in record and record["valid_from"]:
                if str(record["valid_from"])[:10] > decision_date:
                    return False
            if "valid_to" in record and record["valid_to"]:
                if str(record["valid_to"])[:10] < decision_date:
                    return False
                    
        return True

    @classmethod
    def prevent_outcome_leak(cls, record_or_context: Dict[str, Any]) -> bool:
        """
        Hard block on any forward outcomes, holding returns, or future labels.
        """
        for key in record_or_context.keys():
            k_lower = key.lower()
            if k_lower in {
                "h1", "h3", "h5", "h10", "h20",
                "target_h1", "target_h3", "target_h5", "target_h10", "target_h20",
                "peer_h1", "peer_h3", "peer_h5", "peer_h10", "peer_h20",
                "excess_h1", "excess_h3", "excess_h5", "excess_h10", "excess_h20",
                "h5_peer_excess", "forward_return", "mfe", "mae", "mfe_h5", "mae_h5"
            } or any(x in k_lower for x in ["forward_return", "peer_excess", "h5_excess", "sentinel"]):
                return False
        return True

    @classmethod
    def enforce_peer_self_exclusion(cls, target_ticker: str, peer_list: List[str]) -> List[str]:
        """
        Enforces leave-one-out peer calculation: target is strictly excluded from its own peer set.
        """
        target_clean = target_ticker.upper()
        target_ent = f"ENT_{target_clean}"
        
        return [
            p for p in peer_list 
            if p.upper() != target_clean and p.upper() != target_ent
        ]
