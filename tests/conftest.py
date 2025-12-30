import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.utils.security import create_access_token


# define helper class following this post:
# https://stackoverflow.com/questions/33508060/create-and-import-helper-functions-in-tests-without-creating-packages-in-test-di#comment108181817_42156088#answer-42156088
class Helpers:
    @staticmethod
    def get_bearer_headers(bearer_token: str):
        headers = {"Authorization": f"Bearer {bearer_token}"}
        return headers


@pytest.fixture
def helpers():
    return Helpers


### END helpers


@pytest.fixture(scope="module", name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module", name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module", name="user")
def user_created(client: TestClient):

    test_password = "testpassword123"
    user_data = {
        "email": "user@fixture.com",
        "name": "Fixture User",
        "password": test_password,
    }

    response = client.post("/api/auth/register", json=user_data)

    yield user_data


@pytest.fixture(scope="module", name="token")
def jwt_token(client: TestClient, user):

    token = create_access_token(data={"sub": user["email"]})
    yield token


@pytest.fixture(scope="module", name="account")
def create_account(client: TestClient, token: str):
    headers = Helpers.get_bearer_headers(token)
    payload = {"name": "string", "currency_code": "str", "description": "string"}
    account = client.post("api/accounts", headers=headers, json=payload)
    yield account.json()
