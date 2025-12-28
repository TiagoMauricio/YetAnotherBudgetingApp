from fastapi.testclient import TestClient

API_URL = "/api/transactions"


def test_get_transaction(helpers, client: TestClient, token):
    """Find transaction by id"""
    headers = helpers.get_bearer_headers(token)
    response = client.get(url=f"{API_URL}/1", headers=headers)
    assert response.status_code == 200


def test_create_transaction():
    """Successful transaction creation"""
    pass


def test_update_transaction():
    pass


def test_delete_transaction():
    pass


def test_get_account_transactions():
    pass
