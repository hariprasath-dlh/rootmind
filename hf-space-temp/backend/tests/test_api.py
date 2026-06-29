"""
test_api.py - Integration tests for FastAPI endpoints

Validates REST routing structures, parameter input schema validations,
and error status responses for the API endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """
    Asserts the API health route returns a 200 OK and valid status dict.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "RootMind Backend"}


def test_list_incidents_endpoint() -> None:
    """
    Asserts incident list query yields proper status response.
    """
    response = client.get("/incidents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
