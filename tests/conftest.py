import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.services.user_service import pwd_context
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, Wallet, Transfer, PasswordResetToken

pwd_context.update(bcrypt__rounds=4)

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def registered_user(client):
    response = await client.post(
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
async def auth_client(client, registered_user):
    response = await client.post(
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
async def second_user(client, db_session):
    response = await client.post(
        "/users",
        json={"email": "Manoj@Test.com", "full_name": "Manoj", "password": "manoj"},
    )
    assert response.status_code == 201, "user registration failed in fixture"
    user_id = response.json()["id"]
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    assert wallet is not None, "wallet not created for second user"
    return {
        "id": user_id,
        "wallet_id": wallet.id
    }