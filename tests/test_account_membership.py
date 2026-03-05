from fastapi.testclient import TestClient

from app.utils.security import create_access_token


def test_get_user_accounts_with_owner_field(
    helpers, client: TestClient, token, account
):
    """GET /api/users/{user_id}/accounts returns accounts with an owner field"""
    headers = helpers.get_bearer_headers(token)
    response = client.get(f"/api/users/{account['id']}/accounts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "owner" in data[0]


def test_owner_is_correct(helpers, client: TestClient, token, user, account):
    """The owner field matches the user who created the account"""
    # Register to get the user id from the response
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "owner_check@fixture.com",
            "name": "X",
            "password": "testpass123",
        },
    )
    owner_user = register_response.json()
    owner_token = create_access_token(data={"sub": owner_user["email"]})
    owner_headers = helpers.get_bearer_headers(owner_token)

    new_account = client.post(
        "/api/accounts",
        headers=owner_headers,
        json={"name": "Owner Check Account", "currency_code": "USD"},
    ).json()

    response = client.get(
        f"/api/users/{owner_user['id']}/accounts", headers=owner_headers
    )
    data = response.json()
    matched = next(a for a in data if a["id"] == new_account["id"])
    assert matched["owner"] == owner_user["id"]


def test_get_user_accounts_forbidden(helpers, client: TestClient, token, second_user):
    """GET /api/users/{other_id}/accounts returns 403 when accessing another user's accounts"""
    headers = helpers.get_bearer_headers(token)
    response = client.get(f"/api/users/{second_user['id']}/accounts", headers=headers)
    assert response.status_code == 403


def test_add_account_member(helpers, client: TestClient, token, account, second_user):
    """POST /api/accounts/{id}/members adds a member with role member"""
    headers = helpers.get_bearer_headers(token)
    payload = {"user_id": second_user["id"]}
    response = client.post(
        f"/api/accounts/{account['id']}/members", headers=headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == second_user["id"]
    assert data["role"] == "member"
    assert data["is_owner"] is False


def test_add_account_member_duplicate(
    helpers, client: TestClient, token, account, second_user
):
    """POST /api/accounts/{id}/members returns 400 when member already exists"""
    headers = helpers.get_bearer_headers(token)
    payload = {"user_id": second_user["id"]}
    response = client.post(
        f"/api/accounts/{account['id']}/members", headers=headers, json=payload
    )
    assert response.status_code == 400


def test_add_account_member_user_not_found(helpers, client: TestClient, token, account):
    """POST /api/accounts/{id}/members returns 404 for a nonexistent user"""
    headers = helpers.get_bearer_headers(token)
    response = client.post(
        f"/api/accounts/{account['id']}/members",
        headers=headers,
        json={"user_id": 9999},
    )
    assert response.status_code == 404


def test_add_account_member_not_owner(
    helpers, client: TestClient, second_token, account
):
    """POST /api/accounts/{id}/members returns 403 when caller is not the account owner"""
    headers = helpers.get_bearer_headers(second_token)
    response = client.post(
        f"/api/accounts/{account['id']}/members",
        headers=headers,
        json={"user_id": 9999},
    )
    assert response.status_code == 403


def test_get_account_members(helpers, client: TestClient, token, account, second_user):
    """GET /api/accounts/{id}/members returns all members including the new one"""
    headers = helpers.get_bearer_headers(token)
    response = client.get(f"/api/accounts/{account['id']}/members", headers=headers)
    assert response.status_code == 200
    user_ids = [m["user_id"] for m in response.json()]
    assert second_user["id"] in user_ids


def test_member_sees_account_in_list(
    helpers, client: TestClient, second_token, second_user, account
):
    """A member can see the shared account in their list, with the correct owner"""
    headers = helpers.get_bearer_headers(second_token)
    response = client.get(f"/api/users/{second_user['id']}/accounts", headers=headers)
    assert response.status_code == 200
    data = response.json()
    shared = next((a for a in data if a["id"] == account["id"]), None)
    assert shared is not None
    assert "owner" in shared


def test_remove_account_member(
    helpers, client: TestClient, token, account, second_user
):
    """DELETE /api/accounts/{id}/members/{user_id} removes a member"""
    headers = helpers.get_bearer_headers(token)
    response = client.delete(
        f"/api/accounts/{account['id']}/members/{second_user['id']}", headers=headers
    )
    assert response.status_code == 204

    # Verify member is no longer listed
    members_response = client.get(
        f"/api/accounts/{account['id']}/members", headers=headers
    )
    user_ids = [m["user_id"] for m in members_response.json()]
    assert second_user["id"] not in user_ids
