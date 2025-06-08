from fastapi.testclient import TestClient
import pytest
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_epic(client, test_db):
    epic_data = {
        "title": "Test Epic",
        "description": "Test Description",
        "status": "TODO"
    }
    response = client.post("/api/epic", json=epic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == epic_data["title"]
    assert data["description"] == epic_data["description"]
    assert data["status"] == epic_data["status"]
    assert "id" in data

def test_read_epics(client, test_db):
    # Create test epics
    epic1 = {"title": "Epic 1", "description": "Desc 1", "status": "TODO"}
    epic2 = {"title": "Epic 2", "description": "Desc 2", "status": "IN_PROGRESS"}
    
    client.post("/api/epic", json=epic1)
    client.post("/api/epic", json=epic2)
    
    response = client.get("/api/epic")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == epic1["title"]
    assert data[1]["title"] == epic2["title"]

def test_read_epic(client, test_db):
    # Create a test epic
    epic_data = {"title": "Test Epic", "description": "Test Description", "status": "TODO"}
    create_response = client.post("/api/epic", json=epic_data)
    epic_id = create_response.json()["id"]
    
    # Test reading the epic
    response = client.get(f"/api/epic/{epic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == epic_data["title"]
    assert data["description"] == epic_data["description"]
    assert data["status"] == epic_data["status"]
    
    # Test reading non-existent epic
    response = client.get("/api/epic/999")
    assert response.status_code == 404 