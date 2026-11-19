"""
Integration tests for FastAPI endpoints using TestClient.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_metadata_endpoint():
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "total_articles" in data
    assert "total_events" in data
    assert "hybrid_weights" in data


def test_import_fixture_and_detect_events():
    # 1. Import fixture dataset
    import_resp = client.post("/api/articles/import-fixture")
    assert import_resp.status_code == 200
    import_data = import_resp.json()
    assert import_data["status"] == "success"
    assert import_data["inserted"] > 0 or import_data["skipped_duplicates"] > 0

    # 2. List articles
    list_resp = client.get("/api/articles?page=1&page_size=10")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] > 0
    assert len(list_data["items"]) > 0

    # 3. Trigger hybrid event detection
    detect_resp = client.post("/api/events/detect?alpha=0.55&beta=0.25&gamma=0.20&similarity_threshold=0.60")
    assert detect_resp.status_code == 200
    detect_data = detect_resp.json()
    assert detect_data["status"] == "success"
    assert detect_data["events_created"] > 0

    # 4. List detected events
    events_resp = client.get("/api/events")
    assert events_resp.status_code == 200
    events_data = events_resp.json()
    assert events_data["total"] > 0
    first_event = events_data["items"][0]
    first_evt_id = first_event["id"]

    # 5. Get event details and timeline
    detail_resp = client.get(f"/api/events/{first_evt_id}")
    assert detail_resp.status_code == 200
    timeline_resp = client.get(f"/api/events/{first_evt_id}/timeline")
    assert timeline_resp.status_code == 200
    assert len(timeline_resp.json()) > 0


def test_settings_update_validation():
    # Invalid sum of weights should be rejected
    invalid_resp = client.put("/api/settings", json={
        "default_embedding_model": "all-MiniLM-L6-v2",
        "alpha_semantic": 0.8,
        "beta_temporal": 0.5, # sum = 1.5 != 1.0
        "gamma_entity": 0.2,
        "similarity_threshold": 0.6,
        "temporal_decay_hours": 72.0,
        "newsapi_key": ""
    })
    assert invalid_resp.status_code == 400

    # Valid sum should succeed
    valid_resp = client.put("/api/settings", json={
        "default_embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "alpha_semantic": 0.5,
        "beta_temporal": 0.3,
        "gamma_entity": 0.2, # sum = 1.0
        "similarity_threshold": 0.62,
        "temporal_decay_hours": 48.0,
        "newsapi_key": ""
    })
    assert valid_resp.status_code == 200
    assert valid_resp.json()["weights_valid"] is True
