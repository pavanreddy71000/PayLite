import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.services.user_service import pwd_context
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, Wallet, Transfer, PasswordResetToken

pwd_context.update(bcrypt__rounds=4)

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)      # setup: fresh tables
    session = TestingSessionLocal()
    try:
        yield session                          # the test runs here
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)    # teardown: destroy everything


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    app.dependency_overrides.clear()           # teardown: remove the override

@pytest.fixture
def registered_user(client):
    response = client.post(
        "/users",
        json={"email": "Pavan@Test.com", "full_name": "Pavan", "password": "password"},
    )
    assert response.status_code == 201, "user registration failed in fixture"
    return {
        "email": "Pavan@Test.com",
        "password": "password",
        "id": response.json()["id"],
    }


@pytest.fixture
def auth_client(client, registered_user):
    response = client.post(
        "/auth/token",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200, "login failed in fixture"
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client

@pytest.fixture
def second_user(client, db_session):
    response = client.post(
        "/users",
        json={"email": "Manoj@Test.com", "full_name": "Manoj", "password": "manoj"},
    )
    assert response.status_code == 201, "user registration failed in fixture"
    user_id = response.json()["id"]
    wallet = db_session.query(Wallet).filter(Wallet.user_id == user_id).first()
    assert wallet is not None, "wallet not created for second user"
    return {
        "id": user_id,
        "wallet_id": wallet.id
    }