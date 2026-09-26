from pydantic import BaseModel, ValidationError

def validate_model(model: BaseModel) -> bool:
    """
    Memvalidasi sebuah object Pydantic terhadap schema yang didefinisikan.
    Fungsi ini compatible untuk digunakan pada seluruh model standar seperti:
    - JobRequest
    - QuantResult
    - ResearchResult
    - RedTeamResult
    - DecisionResult
    - JobEnvelope
    - MarketBar
    - MarketSnapshot
    """
    try:
        model.__class__.model_validate(model.model_dump())
        return True
    except ValidationError as e:
        raise ValueError(f"Data tidak valid: {e}")
    except Exception as e:
        raise ValueError(f"Terjadi error saat memvalidasi model: {e}")
