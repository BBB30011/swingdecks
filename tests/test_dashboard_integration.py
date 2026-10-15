"""
SwingDeck — Dashboard Integration & Architectural Synchronization Tests
Verifies that dashboard backend and frontend interfaces remain strictly synchronized
with the core Temporal Market Intelligence platform (Gates 1-6) and 3-agent boundary.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure repo root is available
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.backend.main import app, store
from dashboard.app import load_data, get_platform_and_retrieval
from core.data_platform_schemas import (
    NoveltyClass, ThesisState, InvestigationTriggerType
)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_dashboard_backend_overview_endpoint(client):
    """Verifies that the overview endpoint returns complete intelligence metrics and system health."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "system_health" in data
    assert data["system_health"]["EXECUTION"] == "PAPER"
    assert data["system_health"]["AGENTS"] == "EXACTLY 3" or data["system_health"]["AGENT 1"] == "ACTIVE"
    assert "intelligence_metrics" in data
    assert data["intelligence_metrics"]["temporal_truth_hardened"] is True
    assert data["intelligence_metrics"]["pit_isolation"] == "ACTIVE"

def test_dashboard_backend_stock_detail_endpoint(client):
    """Verifies stock detail endpoint returns state, position, timeline, deltas, and clusters."""
    response = client.get("/api/stock/ADRO")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ADRO"
    assert "state" in data
    assert "timeline" in data
    assert "information_deltas" in data
    assert "event_clusters" in data

def test_dashboard_backend_propagated_exposures_endpoint(client):
    """Verifies multi-hop exposure propagation endpoint."""
    response = client.get("/api/intelligence/exposures/ADRO")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ADRO"
    assert data["entity_id"] == "ENT_ADRO"
    assert "exposures" in data

def test_dashboard_backend_information_deltas_endpoint(client):
    """Verifies state-transition information deltas endpoint."""
    response = client.get("/api/intelligence/deltas/ADRO")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ADRO"
    assert "deltas" in data

def test_dashboard_backend_reverse_investigation_endpoint(client):
    """Verifies Agent 1 -> Agent 2 reverse investigation dispatch endpoint."""
    response = client.get("/api/intelligence/investigations/ADRO?trigger=UNUSUAL_VOLUME")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ADRO"
    assert data["trigger"] == "UNUSUAL_VOLUME"
    assert "report" in data

def test_dashboard_backend_thesis_delta_endpoint(client):
    """Verifies dynamic post-entry thesis delta monitoring endpoint."""
    response = client.get("/api/intelligence/thesis_deltas/ADRO")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "ADRO"
    assert "thesis_delta" in data

def test_dashboard_backend_temporal_quality_endpoint(client):
    """Verifies temporal truth quality metrics and Indonesian timezone support."""
    response = client.get("/api/intelligence/temporal_quality")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["PASS", "FAIL"]
    assert "WIB" in data["timezones_supported"]
    assert "EXACT" in data["temporal_confidence_levels"]
    assert "EXCHANGE_METADATA" in data["derivation_methods"]

def test_dashboard_frontend_platform_retrieval_binding():
    """Verifies that the Streamlit frontend correctly instantiates the knowledge platform and retrieval engine."""
    kdp, retrieval = get_platform_and_retrieval()
    assert kdp is not None
    assert retrieval is not None
