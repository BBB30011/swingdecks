import os
import json
import pytest
from unittest.mock import patch
import duckdb

from core.command_parser import CommandParser
from core.live_news_ingestion import LiveNewsIngestionEngine
from core.agent2_research_provider import Agent2ResearchProvider

@pytest.fixture
def test_db_path(tmp_path):
    db_file = str(tmp_path / "test_intelligence.duckdb")
    con = duckdb.connect(db_file)
    con.execute("""
        CREATE TABLE fact_event (
            event_id VARCHAR PRIMARY KEY,
            entity_id VARCHAR,
            event_type VARCHAR,
            event_subtype VARCHAR,
            event_timestamp TIMESTAMP,
            published_at TIMESTAMP,
            information_available_at TIMESTAMP,
            observed_at TIMESTAMP,
            retrieved_at TIMESTAMP,
            valid_from TIMESTAMP,
            valid_to TIMESTAMP,
            source_id VARCHAR,
            source_name VARCHAR,
            source_url VARCHAR,
            source_quality VARCHAR,
            source_type VARCHAR,
            raw_reference VARCHAR,
            provenance VARCHAR,
            information_state VARCHAR,
            information_delta VARCHAR,
            materiality VARCHAR,
            relevance VARCHAR,
            confidence FLOAT,
            is_pit_valid BOOLEAN,
            pit_reason VARCHAR,
            supersedes_event_id VARCHAR,
            contradicts_event_id VARCHAR,
            status VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE fact_information_impact (
            impact_id VARCHAR PRIMARY KEY,
            event_id VARCHAR,
            entity_id VARCHAR,
            exposure_id VARCHAR,
            expected_direction VARCHAR,
            expected_materiality VARCHAR,
            actual_direction VARCHAR,
            actual_magnitude FLOAT,
            peer_reaction FLOAT,
            specificity_status VARCHAR,
            evidence_id VARCHAR,
            confidence FLOAT,
            pit_status VARCHAR,
            provenance_id VARCHAR
        )
    """)
    con.execute("CREATE TABLE dim_entity (entity_id VARCHAR, primary_symbol VARCHAR, canonical_name VARCHAR, entity_type VARCHAR)")
    con.execute("INSERT INTO dim_entity VALUES ('ENT_BBCA', 'BBCA', 'Bank Central Asia', 'COMPANY')")
    con.execute("CREATE TABLE dim_entity_alias (alias_id VARCHAR, entity_id VARCHAR, alias_type VARCHAR, alias_value VARCHAR, valid_from TIMESTAMP, valid_to TIMESTAMP, source_id VARCHAR, pit_status VARCHAR)")
    con.execute("INSERT INTO dim_entity_alias VALUES ('AL1', 'ENT_BBCA', 'TICKER', 'BBCA', NULL, NULL, NULL, NULL)")
    con.close()
    return db_file

@pytest.fixture
def mock_research_result():
    return {
        "status": "SUCCESS",
        "command": "AGENT2 UPDATE NEWS BBCA",
        "symbol": "BBCA",
        "mode": "REAL_INTERNET_RESEARCH",
        "sources": [
            {
                "url": "https://idx.co.id/news/bbca",
                "title": "BBCA Klarifikasi",
                "content_hash": "abc"
            }
        ],
        "evidence": [],
        "knowledge_delta": {
            "ADDED": ["Company officially denied acquisition rumors by Haji Isam (Sept 26)."],
            "CONTRADICTED": ["Social media speculation regarding acquisition."],
            "UPDATED": []
        }
    }

def test_command_parser_validation(test_db_path, mock_research_result):
    parser = CommandParser(db_path=test_db_path)
    
    # Valid command, auto mode, no API key
    env_patch = {}
    if "GEMINI_API_KEY" in os.environ:
        env_patch["GEMINI_API_KEY"] = ""
    if "OPENAI_API_KEY" in os.environ:
        env_patch["OPENAI_API_KEY"] = ""
        
    with patch.dict(os.environ, env_patch):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        report = parser.execute_command("AGENT2 UPDATE NEWS BBCA")
        assert "SOURCE_ACCESS_FAILURE" in report
        assert "No AI Provider API capability found" in report
        
    # Invalid agent
    report = parser.execute_command("AGENT4 UPDATE NEWS BBCA")
    assert "REJECT: Unknown command" in report or "Invalid agent" in report
    
    # Invalid ticker
    report = parser.execute_command("AGENT2 UPDATE NEWS X")
    assert "REJECT: ENTITY_UNCERTAIN" in report
    
def test_dual_mode_routing():
    provider = Agent2ResearchProvider()
    
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}):
        with patch.object(provider, '_execute_api_mode', return_value={"status": "SUCCESS"}) as mock_api:
            # API mode forced
            res = provider.research("BBCA", "RECENT", "api")
            assert res["status"] == "SUCCESS"
            assert res["executed_mode"] == "API"
            mock_api.assert_called_once()
            
            # Auto mode should route to API when available
            mock_api.reset_mock()
            res = provider.research("BBCA", "RECENT", "auto")
            assert res["executed_mode"] == "API"
            mock_api.assert_called_once()
            
    env_patch = {}
    if "GEMINI_API_KEY" in os.environ:
        env_patch["GEMINI_API_KEY"] = ""
    if "OPENAI_API_KEY" in os.environ:
        env_patch["OPENAI_API_KEY"] = ""
        
    with patch.dict(os.environ, env_patch):
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
        # Web mode should fail gracefully without API key
        res = provider.research("BBCA", "RECENT", "web")
        assert res["status"] == "SOURCE_ACCESS_FAILURE"
        assert "WEB mode is an IDE-assisted capability" in res["reason"]
        
        # Auto mode should fail if no API key
        res = provider.research("BBCA", "RECENT", "auto")
        assert res["status"] == "SOURCE_ACCESS_FAILURE"

def test_command_parser_mode_flag_and_ingest(test_db_path, mock_research_result, tmp_path):
    parser = CommandParser(db_path=test_db_path)
    
    # Test passing --mode web
    report = parser.execute_command("AGENT2 UPDATE NEWS BBCA --mode web")
    assert "REJECT: WEB mode is an IDE-assisted mode" in report
    
    # Test INGEST NEWS (IDE Handoff)
    payload_path = tmp_path / "ide_payload.json"
    with open(payload_path, "w") as f:
        json.dump(mock_research_result, f)
        
    with patch.object(parser.news_engine, 'execute_ai_research_ingestion', return_value="INGEST SUCCESS"):
        report = parser.execute_command(f"AGENT2 INGEST NEWS BBCA {payload_path}")
        assert report == "INGEST SUCCESS"
