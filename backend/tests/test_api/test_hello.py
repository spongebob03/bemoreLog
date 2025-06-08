from fastapi.testclient import TestClient
import pytest
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_hello_endpoint(client):
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI!"} 