import pytest
from pydantic import ValidationError
from core.schemas import JobEnvelope

def test_job_envelope_valid():
    # Test 1: JobEnvelope valid dapat dibuat.
    env = JobEnvelope(
        job_id="JOB-001", job_type="SCAN", created_at="2026",
        source="AGENT1", destination="QUEUE", payload={"symbol": "BBCA"}
    )
    assert env.job_id == "JOB-001"

def test_payload_dict_accepted():
    # Test 2: payload dictionary diterima.
    env = JobEnvelope(
        job_id="JOB-001", job_type="SCAN", created_at="2026",
        source="AGENT1", destination="QUEUE", payload={"key": "value"}
    )
    assert isinstance(env.payload, dict)

def test_payload_not_dict_rejected():
    # Test 3: payload bukan dictionary ditolak.
    with pytest.raises(ValidationError):
        JobEnvelope(
            job_id="JOB-001", job_type="SCAN", created_at="2026",
            source="AGENT1", destination="QUEUE", payload="not a dict" # type: ignore
        )

def test_job_id_empty_rejected():
    # Test 4: job_id kosong ditolak.
    with pytest.raises(ValidationError):
        JobEnvelope(
            job_id="", job_type="SCAN", created_at="2026",
            source="AGENT1", destination="QUEUE", payload={}
        )

def test_destination_empty_rejected():
    # Test 5: destination kosong ditolak.
    with pytest.raises(ValidationError):
        JobEnvelope(
            job_id="JOB-001", job_type="SCAN", created_at="2026",
            source="AGENT1", destination="", payload={}
        )

def test_default_schema_version():
    # Test 6: default schema_version adalah 1.0.
    env = JobEnvelope(
        job_id="JOB-001", job_type="SCAN", created_at="2026",
        source="AGENT1", destination="QUEUE", payload={}
    )
    assert env.schema_version == "1.0"

def test_model_to_dict():
    # Test 7: Model dapat diubah menjadi dictionary.
    env = JobEnvelope(
        job_id="JOB-001", job_type="SCAN", created_at="2026",
        source="A", destination="B", payload={}
    )
    d = env.model_dump()
    assert isinstance(d, dict)
    assert d["job_id"] == "JOB-001"

def test_model_to_json():
    # Test 8: Model dapat diubah menjadi JSON.
    env = JobEnvelope(
        job_id="JOB-001", job_type="SCAN", created_at="2026",
        source="A", destination="B", payload={}
    )
    j = env.model_dump_json()
    assert isinstance(j, str)
    assert '"JOB-001"' in j

def test_json_to_model():
    # Test 9: JSON valid dapat dikembalikan menjadi JobEnvelope.
    j = '{"job_id": "J1", "job_type": "TEST", "created_at": "2026", "source": "A", "destination": "B", "payload": {}, "schema_version": "1.0"}'
    env = JobEnvelope.model_validate_json(j)
    assert isinstance(env, JobEnvelope)
    assert env.job_id == "J1"

def test_json_invalid_rejected():
    # Test 10: JSON invalid ditolak.
    # Kasus: Field wajib hilang
    with pytest.raises(ValidationError):
        JobEnvelope.model_validate_json('{"job_id": "J1"}') 
    # Kasus: Format JSON rusak
    with pytest.raises(ValueError):
        JobEnvelope.model_validate_json('{corrupt_json: true')
