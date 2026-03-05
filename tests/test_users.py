from fastapi.testclient import TestClient

from app.utils.security import create_access_token


def test_get_me(helpers, client: TestClient, token, user):
    """GET /api/users/me returns current user profile"""
    headers = helpers.get_bearer_headers(token)
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user["email"]
    assert data["name"] == user["name"]
    assert "id" in data
    assert "created_at" in data
    assert "password_hash" not in data


def test_get_me_unauthenticated(client: TestClient):
    """GET /api/users/me returns 401 without token"""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_update_me_name(helpers, client: TestClient, token):
    """PATCH /api/users/me updates the user's name"""
    headers = helpers.get_bearer_headers(token)
    response = client.patch(
        "/api/users/me", headers=headers, json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_update_me_password(helpers, client: TestClient, token):
    """PATCH /api/users/me updates the user's password"""
    headers = helpers.get_bearer_headers(token)
    response = client.patch(
        "/api/users/me", headers=headers, json={"password": "newpassword123"}
    )
    assert response.status_code == 200


def test_update_me_short_password(helpers, client: TestClient, token):
    """PATCH /api/users/me rejects passwords shorter than 8 characters"""
    headers = helpers.get_bearer_headers(token)
    response = client.patch(
        "/api/users/me", headers=headers, json={"password": "short"}
    )
    assert response.status_code == 422


def test_update_me_empty_body(helpers, client: TestClient, token):
    """PATCH /api/users/me with no fields is a no-op and returns 200"""
    headers = helpers.get_bearer_headers(token)
    before = client.get("/api/users/me", headers=headers).json()
    response = client.patch("/api/users/me", headers=headers, json={})
    assert response.status_code == 200
    assert response.json()["name"] == before["name"]


def test_update_me_unauthenticated(client: TestClient):
    """PATCH /api/users/me returns 401 without token"""
    response = client.patch("/api/users/me", json={"name": "Hacker"})
    assert response.status_code == 401


def test_deactivate_me_unauthenticated(client: TestClient):
    """DELETE /api/users/me returns 401 without token"""
    response = client.delete("/api/users/me")
    assert response.status_code == 401


def test_deactivate_me(helpers, client: TestClient):
    """DELETE /api/users/me deactivates the account; subsequent auth fails"""
    # Register a throwaway user
    user_data = {
        "email": "todeactivate@fixture.com",
        "name": "To Deactivate",
        "password": "testpassword123",
    }
    client.post("/api/auth/register", json=user_data)
    token = create_access_token(data={"sub": user_data["email"]})
    headers = helpers.get_bearer_headers(token)

    response = client.delete("/api/users/me", headers=headers)
    assert response.status_code == 204

    # Deactivated user can no longer authenticate
    follow_up = client.get("/api/users/me", headers=headers)
    assert follow_up.status_code == 401
