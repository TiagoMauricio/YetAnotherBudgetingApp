import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.utils.security import create_access_token


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
def userCreated(client: TestClient):

    test_password = "testpassword123"
    user_data = {
        "email": "user@fixture.com",
        "name": "Fixture User",
        "password": test_password
    }

    response = client.post("/api/auth/register", json=user_data)

    yield user_data


@pytest.fixture(scope="module", name="token")
def jwtToken(client: TestClient, user):

    token = create_access_token(data={'sub': user["email"]})
    yield token
