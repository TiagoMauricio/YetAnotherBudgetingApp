from fastapi.testclient import TestClient
from httpx import Response

from tests.conftest import Helpers

API_URL = "/api/categories"


def test_get_category_list_success(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test get list of categories"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)

    payload = helpers.category_payload()
    payload["name"] = "List Test Category 1"
    payload2 = helpers.category_payload()
    payload2["name"] = "List Test Category 2"
    _ = client.post(url=API_URL, headers=headers, json=payload)
    _ = client.post(url=API_URL, headers=headers, json=payload2)

    response: Response = client.get(url=API_URL, headers=headers)
    assert response.status_code == 200

    categories = response.json()
    assert len(categories) == 2

    first_category = categories[0]
    second_category = categories[1]

    assert first_category["id"] == 1
    assert first_category["name"] == payload["name"]

    assert second_category["id"] == 2
    assert second_category["name"] == payload2["name"]

def test_get_category_list_unauthenticated(client: TestClient):
    response: Response = client.get(url=API_URL)
    assert response.status_code == 401


def test_get_category_success(helpers: type[Helpers], client: TestClient, token: str):
    """Test category by id"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)

    payload = helpers.category_payload()
    payload["name"] = "Get Test Category"
    create_response = client.post(url=API_URL, headers=headers, json=payload)
    assert create_response.status_code == 201
    created_category = create_response.json()

    response: Response = client.get(
        url=f"{API_URL}/{created_category['id']}", headers=headers
    )
    assert response.status_code == 200

    category = response.json()
    assert category["id"] == created_category["id"]
    assert category["name"] == payload["name"]
    assert category["is_expense"] == payload["is_expense"]
    assert category["description"] == payload["description"]


def test_get_default_category_success(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test get default category"""
    # TODO:  unsure how to test this
    pass


def test_get_category_not_found(helpers: type[Helpers], client: TestClient, token: str):
    """Test get category that doesn't exist"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    response: Response = client.get(url=f"{API_URL}/69420", headers=headers)
    assert response.status_code == 404


def test_get_category_unauthenticated(client: TestClient):
    response: Response = client.get(url=f"{API_URL}/1")
    assert response.status_code == 401


def test_create_category_success(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test create category"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    payload = helpers.category_payload()
    payload["name"] = "Success Test Category"

    response: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response.status_code == 201

    category = response.json()
    assert category["name"] == payload["name"]
    assert category["is_expense"] == payload["is_expense"]
    assert category["description"] == payload["description"]
    assert "id" in category
    assert category["user_id"] == 1


def test_create_category_missing_fields(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test bad post payload"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)

    payload = {"is_expense": True}
    response: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response.status_code == 422

    payload = {"name": "Test Category"}
    response: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response.status_code == 422


def test_create_category_duplicate_name(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test duplicate category name"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    payload = helpers.category_payload()
    payload["name"] = "Duplicate Test Category"

    response1: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response1.status_code == 201

    response2: Response = client.post(url=API_URL, headers=headers, json=payload)
    assert response2.status_code == 400  # Should return conflict/error


def test_create_category_unauthenticated(client: TestClient):
    """Test creating a category without authentication"""
    payload = Helpers.category_payload()
    response: Response = client.post(url=API_URL, json=payload)
    assert response.status_code == 401


def test_update_category_success(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test update category"""
    headers: dict[str, str] = helpers.get_bearer_headers(token)

    create_payload = helpers.category_payload()
    create_payload["name"] = "Update Test Category"
    create_response = client.post(url=API_URL, headers=headers, json=create_payload)
    assert create_response.status_code == 201
    created_category = create_response.json()

    update_payload = {
        "name": "Updated Category Name",
        "is_expense": not create_payload["is_expense"],
        "description": "Updated description",
    }

    response: Response = client.patch(
        url=f"{API_URL}/{created_category['id']}", headers=headers, json=update_payload
    )
    assert response.status_code == 200

    updated_category = response.json()
    assert updated_category["id"] == created_category["id"]
    assert updated_category["name"] == update_payload["name"]
    assert updated_category["is_expense"] == update_payload["is_expense"]
    assert updated_category["description"] == update_payload["description"]


def test_update_category_not_found(
    helpers: type[Helpers], client: TestClient, token: str
):
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    payload = helpers.category_payload()

    response: Response = client.patch(
        url=f"{API_URL}/99999", headers=headers, json=payload
    )
    assert response.status_code == 404


def test_update_default_category_forbidden(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test that default categories cannot be updated"""
    # TODO: not sure how to do this
    pass

def test_update_category_unauthenticated(client: TestClient):
    payload = Helpers.category_payload()
    response: Response = client.patch(url=f"{API_URL}/1", json=payload)
    assert response.status_code == 401


def test_delete_category_success(
    helpers: type[Helpers], client: TestClient, token: str
):
    headers: dict[str, str] = helpers.get_bearer_headers(token)

    payload = helpers.category_payload()
    payload["name"] = "Delete Test Category"
    create_response = client.post(url=API_URL, headers=headers, json=payload)
    assert create_response.status_code == 201
    created_category = create_response.json()

    response: Response = client.delete(
        url=f"{API_URL}/{created_category['id']}", headers=headers
    )
    assert response.status_code == 204

    get_response: Response = client.get(
        url=f"{API_URL}/{created_category['id']}", headers=headers
    )
    assert get_response.status_code == 404


def test_delete_category_not_found(
    helpers: type[Helpers], client: TestClient, token: str
):
    headers: dict[str, str] = helpers.get_bearer_headers(token)
    response: Response = client.delete(url=f"{API_URL}/99999", headers=headers)
    assert response.status_code == 404


def test_delete_default_category_forbidden(
    helpers: type[Helpers], client: TestClient, token: str
):
    """Test that default categories cannot be deleted"""
    # TODO: not sure how to do this
    pass

def test_delete_category_unauthenticated(client: TestClient):
    response: Response = client.delete(url=f"{API_URL}/1")
    assert response.status_code == 401
