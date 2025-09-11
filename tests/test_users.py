import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User


def test_create_user_success(client: TestClient):
    """Test successful user creation"""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    
    response = client.post("/api/users", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data
    assert isinstance(data["id"], int)  # ID should be an integer
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data  # Password should not be in response
    assert "password_hash" not in data  # Password hash should not be in response


def test_create_user_duplicate_email(client: TestClient):
    """Test creating user with duplicate email fails"""
    user_data = {
        "email": "duplicate@example.com",
        "name": "First User",
        "password": "password123"
    }
    
    # Create first user
    response1 = client.post("/api/users", json=user_data)
    assert response1.status_code == 200
    
    # Try to create second user with same email
    user_data["name"] = "Second User"
    response2 = client.post("/api/users", json=user_data)
    
    assert response2.status_code == 400
    assert "User with this email already exists" in response2.json()["detail"]


def test_create_user_invalid_email(client: TestClient):
    """Test creating user with invalid email fails"""
    user_data = {
        "email": "invalid-email",
        "name": "Test User",
        "password": "password123"
    }
    
    response = client.post("/api/users", json=user_data)
    
    assert response.status_code == 422  # Validation error


def test_create_user_short_password(client: TestClient):
    """Test creating user with short password fails"""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "short"  # Less than 8 characters
    }
    
    response = client.post("/api/users", json=user_data)
    
    assert response.status_code == 422  # Validation error


def test_create_user_missing_required_fields(client: TestClient):
    """Test creating user with missing required fields fails"""
    # Missing email
    response1 = client.post("/api/users", json={
        "name": "Test User",
        "password": "password123"
    })
    assert response1.status_code == 422
    
    # Missing password
    response2 = client.post("/api/users", json={
        "email": "test@example.com",
        "name": "Test User"
    })
    assert response2.status_code == 422


def test_create_user_optional_name(client: TestClient):
    """Test creating user without name (optional field) succeeds"""
    user_data = {
        "email": "noname@example.com",
        "password": "password123"
    }
    
    response = client.post("/api/users", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] is None
    assert isinstance(data["id"], int)  # ID should be an integer


def test_get_all_users_empty(client: TestClient):
    """Test getting all users when database is empty"""
    response = client.get("/api/users")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_all_users_with_data(client: TestClient):
    """Test getting all users when users exist"""
    # Create test users
    users_data = [
        {"email": "user1@example.com", "name": "User One", "password": "password123"},
        {"email": "user2@example.com", "name": "User Two", "password": "password123"},
        {"email": "user3@example.com", "password": "password123"}  # No name
    ]
    
    # Create users
    for user_data in users_data:
        response = client.post("/api/users", json=user_data)
        assert response.status_code == 200
    
    # Get all users
    response = client.get("/api/users")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check that all users are returned with correct fields
    emails = [user["email"] for user in data]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails
    assert "user3@example.com" in emails
    
    # Verify no sensitive data is exposed
    for user in data:
        assert "password" not in user
        assert "password_hash" not in user
        assert "id" in user
        assert isinstance(user["id"], int)  # ID should be an integer
        assert "email" in user
        assert "created_at" in user
        assert "updated_at" in user


def test_user_password_is_hashed(client: TestClient, session: Session):
    """Test that user passwords are properly hashed in database"""
    user_data = {
        "email": "hash@example.com",
        "name": "Hash User",
        "password": "plainpassword123"
    }
    
    response = client.post("/api/users", json=user_data)
    assert response.status_code == 200
    
    # Get user from database directly
    user_id = response.json()["id"]
    assert isinstance(user_id, int)  # ID should be an integer
    db_user = session.get(User, user_id)
    
    assert db_user is not None
    assert db_user.password_hash != user_data["password"]  # Password should be hashed
    assert db_user.password_hash.startswith("$2b$")  # bcrypt hash format
