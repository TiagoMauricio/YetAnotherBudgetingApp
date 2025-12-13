from fastapi.testclient import TestClient


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
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201

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
        assert isinstance(user["id"], int)
        assert "email" in user
        assert "created_at" in user
        assert "updated_at" in user
