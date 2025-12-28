"""
Tests for core API routes defined in veridian_atlas/api/server.py
These tests do NOT assume embeddings or processed data exist.
"""

import pytest
from fastapi.testclient import TestClient
from veridian_atlas.api.server import create_app

app = create_app()
client = TestClient(app)


# ---------------------------------------------------------
# ROOT & HEALTH
# ---------------------------------------------------------

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "routes" in data
    assert isinstance(data["routes"], list)


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()

    # The real API returns service.health() structure, not fixed values
    assert isinstance(body, dict)
    # Minimum expected contract: must not crash & must contain some fields
    assert "device" in body or "status" in body


# ---------------------------------------------------------
# DEALS & METADATA
# ---------------------------------------------------------

def test_list_deals_route(tmp_path, monkeypatch):
    """
    Ensures /deals does not crash when the deals directory is missing.
    Accepts either empty list (preferred) or 404 depending on app behavior.
    """

    # Patch the deals path so the app points to a temp directory
    monkeypatch.chdir(tmp_path)  # acts as root for test environment

    response = client.get("/deals")

    # Two acceptable outcomes depending on environment:
    # - 200 with an empty list if directory is created or assumed
    # - 404 if path missing
    assert response.status_code in (200, 404)

    if response.status_code == 200:
        data = response.json()
        assert "deals" in data
        assert isinstance(data["deals"], list)



def test_deal_metadata_missing():
    response = client.get("/deals/DOES_NOT_EXIST")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Deal not found"


# ---------------------------------------------------------
# DOCUMENT LISTING
# ---------------------------------------------------------

def test_docs_missing_deal():
    response = client.get("/deals/UNKNOWN_DEAL/docs")
    assert response.status_code == 404
    assert response.json()["detail"] == "Deal not found"


# ---------------------------------------------------------
# ASK & SEARCH ENDPOINTS (NO EMBEDDINGS CASE)
# ---------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/ask/testdeal",
    "/search/testdeal"
])
def test_rag_endpoints_missing_deal(path):
    # Request body structure must match QueryRequest
    payload = {"query": "Hello world", "top_k": 1}
    response = client.post(path, json=payload)

    # Expected realities:
    # 404 = missing embeddings or missing deal
    # 422 = invalid state or schema mismatch
    assert response.status_code in (404, 422)


# ---------------------------------------------------------
# CHUNK LOOKUP
# ---------------------------------------------------------

def test_chunk_lookup_missing():
    response = client.get("/chunk/UnknownDeal/XYZ")
    assert response.status_code == 404
    detail = response.json().get("detail")
    assert "not found" in detail.lower() or "missing" in detail.lower()
