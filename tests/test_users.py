from app.models.wallet import Wallet

def test_register_user(client, db_session):
    response = client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    
    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "pavan@test.com"
    assert data["full_name"] == "Pavan"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

    assert db_session.query(Wallet).filter(Wallet.user_id == data["id"]).first() is not None

def test_register_duplicate_email(client):
    response = client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    assert response.status_code == 201
    response = client.post("/users", json={"email":"Pavan@Test.com", "full_name":"Pavan", "password":"password"})
    
    assert response.status_code == 409
    data = response.json()
    assert data["error_type"] == "DuplicateEmailError"

