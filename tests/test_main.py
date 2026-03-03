import pytest
from fastapi.testclient import TestClient
from lmstudio_claude_shim_proxy import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    """Test health check endpoint"""
    response = client.get("/_health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "upstream" in data
    assert "speculative_decoding" in data
