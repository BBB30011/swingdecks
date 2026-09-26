from core.orchestrator_schemas import FailureType

class RetryPolicy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def is_retryable(self, failure_type: FailureType) -> bool:
        return failure_type in [FailureType.TRANSIENT, FailureType.SYSTEM]

    def classify_error(self, error: Exception) -> FailureType:
        err_str = str(error).lower()
        if "validation" in err_str or "pydantic" in err_str:
            return FailureType.VALIDATION
        if "secret" in err_str or "credential" in err_str or "path traversal" in err_str:
            return FailureType.SECURITY
        if "ioerror" in err_str or "file" in err_str or "timeout" in err_str:
            return FailureType.TRANSIENT
        if "idempotency" in err_str or "conflict" in err_str:
            return FailureType.IDEMPOTENCY
        if "data" in err_str or "nan" in err_str:
            return FailureType.DATA
        if "business" in err_str or "gate" in err_str:
            return FailureType.BUSINESS_RULE
            
        return FailureType.UNKNOWN
