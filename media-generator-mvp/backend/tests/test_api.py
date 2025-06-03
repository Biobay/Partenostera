import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_books():
    """Test get books endpoint"""
    response = client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    assert len(books) > 0

def test_create_project():
    """Test project creation"""
    project_data = {
        "title": "Test Project",
        "description": "Test Description",
        "userId": "test_user",
        "userMode": "tool"
    }
    response = client.post("/projects", json=project_data)
    assert response.status_code == 200
    project = response.json()
    assert project["title"] == "Test Project"
    assert project["userId"] == "test_user"

def test_get_user_projects():
    """Test get user projects"""
    response = client.get("/projects/test_user")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)

def test_file_upload():
    """Test file upload endpoint"""
    test_file_content = "Questo è un testo di prova per il test di upload."
    files = {"file": ("test.txt", test_file_content, "text/plain")}
    data = {
        "title": "Test Upload",
        "description": "Test upload description",
        "userId": "test_user",
        "userMode": "tool"
    }
    
    response = client.post("/generate/file", files=files, data=data)
    assert response.status_code == 200
    result = response.json()
    assert "projectId" in result
    assert result["status"] == "processing"
