from fastapi.testclient import TestClient
from httpx import Response

from tests.conftest import Helpers

API_URL = "/api/transactions"


def test_get_create_transaction(helpers: type[Helpers], client: TestClient, token: str, account: dict[str,str]):
    """Find transaction by id"""
    headers: dict[str,str] = helpers.get_bearer_headers(token)
    response: Response = client.get(url=f"{API_URL}/1", headers=headers)
    assert response.status_code == 404

    payload: dict[str, str | int] = {
        "category_id": 1,
        "type": "income",
        "amount": 25,
        "description": "Test Income",
        "date": "2025-12-30",
        "account_id": 1,
    }
    response_create: Response = client.post(url=API_URL, headers=headers, json=payload)
    response_create_data = response_create.json()
    print(response_create_data)
    assert response_create.status_code == 201
    assert response_create_data["account_id"] == account["id"]
    assert response_create_data["amount"] == payload["amount"]
    assert response_create_data["category_id"] == payload["category_id"]
    assert response_create_data["date"] == payload["date"]
    assert response_create_data["type"] == payload["type"]
    assert response_create_data["description"] == payload["description"]

    response_get: Response = client.get(url=f"{API_URL}/{response_create_data["id"]}", headers=headers)
    print(f"{API_URL}/{response_create_data["id"]}")
    response_get_data = response_get.json()
    assert response_get.status_code == 200

    assert response_get_data["id"] == response_create_data["id"]
    assert response_get_data["account_id"] == account["id"]
    assert response_get_data["amount"] == payload["amount"]
    assert response_get_data["category_id"] == payload["category_id"]
    assert response_get_data["date"] == payload["date"]
    assert response_get_data["type"] == payload["type"]
    assert response_get_data["description"] == payload["description"]


def test_update_transaction():
    pass


def test_delete_transaction():
    pass

