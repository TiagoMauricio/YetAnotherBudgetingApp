from fastapi.testclient import TestClient
from httpx import Response

from app.utils.messages import CATEGORY_NOT_FOUND

from tests.conftest import Helpers

API_URL = "/api/transactions"


def test_get_create_transaction(
    helpers: type[Helpers], client: TestClient, token: str, account: dict[str, str]
):
    """Find transaction by id"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    response: Response = client.get(url=f"{API_URL}/1", headers=headers)
    assert response.status_code == 404

    payload: dict[str, str | int] = helpers.transaction_payload()

    response_create: Response = client.post(url=API_URL, headers=headers, json=payload)
    response_create_data = response_create.json()
    assert response_create.status_code == 201
    assert response_create_data["account_id"] == account["id"]
    assert response_create_data["amount"] == payload["amount"]
    assert response_create_data["category_id"] == payload["category_id"]
    assert response_create_data["date"] == payload["date"]
    assert response_create_data["description"] == payload["description"]

    response_get: Response = client.get(
        url=f"{API_URL}/{response_create_data["id"]}", headers=headers
    )
    response_get_data = response_get.json()
    assert response_get.status_code == 200

    assert response_get_data["id"] == response_create_data["id"]
    assert response_get_data["account_id"] == account["id"]
    assert response_get_data["amount"] == payload["amount"]
    assert response_get_data["category_id"] == payload["category_id"]
    assert response_get_data["date"] == payload["date"]
    assert response_get_data["description"] == payload["description"]


def test_update_transaction(
    helpers: type[Helpers], client: TestClient, token: str, account: dict[str, str]
):
    """Test update transaction description, category and value"""

    headers: dict[str, str] = helpers.get_bearer_headers(token)
    payload: dict[str, str | int] = helpers.transaction_payload()

    response_create: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response_create.status_code == 201
    assert response_create.json()["account_id"] == account["id"]

    update_payload: dict[str, str | int | float] = {
        "category_id": 4,
        "description": "Updated description",
        "amount": 23.5,
    }
    update_response: Response = client.patch(
        url=f"{API_URL}/{response_create.json()["id"]}",
        headers=headers,
        json=update_payload,
    )
    update_data: dict[str, str] = update_response.json()
    assert update_response.status_code == 200
    assert update_data["id"] == response_create.json()["id"]
    assert update_data["category_id"] == update_payload["category_id"]
    assert update_data["description"] == update_payload["description"]
    assert update_data["amount"] == update_payload["amount"]

    update_payload_unkown: dict[str, str | int | float] = {
        "category_id": 123,
    }
    update_response_unknown: Response = client.patch(
        url=f"{API_URL}/{response_create.json()["id"]}",
        headers=headers,
        json=update_payload_unkown,
    )
    update_data_unknown: dict[str, str] = update_response_unknown.json()
    assert update_response_unknown.status_code == 404
    assert update_data_unknown["message"] == CATEGORY_NOT_FOUND


def test_delete_transaction(
    helpers: type[Helpers], client: TestClient, token: str, account: dict[str, str]
):

    headers: dict[str, str] = helpers.get_bearer_headers(token)
    payload: dict[str, str | int] = helpers.transaction_payload()

    response_create: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response_create.status_code == 201
    assert response_create.json()["account_id"] == account["id"]

    response_delete: Response = client.delete(
        url=f"{API_URL}/{response_create.json()["id"]}", headers=headers
    )
    assert response_delete.status_code == 204

    response_get: Response = client.get(
        url=f"{API_URL}/{response_create.json()["id"]}", headers=headers
    )
    assert response_get.status_code == 404
