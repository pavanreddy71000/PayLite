from app.models.wallet import Wallet
from sqlalchemy import select

async def test_register_user(client, db_session):
    response = await client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    
    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "pavan@test.com"
    assert data["full_name"] == "Pavan"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == data["id"]))
    assert result.scalar_one_or_none() is not None

async def test_register_duplicate_email(client):
    response = await client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    assert response.status_code == 201
    response = await client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    assert response.status_code == 409
    data = response.json()
    assert data["error_type"] == "DuplicateEmailError"

