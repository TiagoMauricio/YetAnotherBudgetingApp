import pytest
from fastapi.testclient import TestClient


def _get_bearer_headers(bearer_token: str):
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    return headers


def test_create_account(client: TestClient, token):
    """Test successful creation"""
    headers = _get_bearer_headers(token)
    payload = {
        "name": "My Test account",
        "currency_code": "EUR",
        "description": ""
    }
    response = client.post(url="/api/accounts", headers=headers, json=payload)
    assert response.status_code == 201


def test_create_account_error(client: TestClient, token):
    """Test error on account creation"""

    headers = _get_bearer_headers(token)
    payload = {
        "name": "Incorrect Payload Account",
        "description": ""
    }
    response = client.post(url="/api/accounts", headers=headers, json=payload)
    print(response.json())
    assert response.status_code == 422


def test_duplicate_account_name(client: TestClient, token):
    """Test duplicate account name"""
    headers = _get_bearer_headers(token)
    payload = {
        "name": "Duplicated test account",
        "currency_code": "EUR",
        "description": ""
    }
    response = client.post(url="/api/accounts", headers=headers, json=payload)
    assert response.status_code == 201

    response2 = client.post(url="/api/accounts", headers=headers, json=payload)
    assert response2.status_code == 400


def test_update_account(client: TestClient, token):
    """Test update account"""
    headers = _get_bearer_headers(token)

    # create test account
    payload_creation = {
        "name": "Create test account",
        "currency_code": "EUR",
        "description": "Some description"
    }
    response = client.post(url="/api/accounts", headers=headers, json=payload_creation)
    assert response.status_code == 201

    # update account
    payload_update = {
        "currency_code": "USD",
        "description": "Changed description"
    }
    response_update = client.patch(url="/api/accounts/1", headers=headers, json=payload_update)
    assert response_update.status_code == 200
    assert response_update.json()['description'] == payload_update['description']
    assert response_update.json()['currency_code'] == payload_update['currency_code']


def test_get_phorbiden_account(client: TestClient, token):
    """Attempt access of an account that the user is not an owner of"""
    headers = _get_bearer_headers(token)
    response = client.get("/api/accounts/1123123", headers=headers)

    assert response.status_code == 403
