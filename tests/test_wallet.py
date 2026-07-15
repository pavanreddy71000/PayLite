from decimal import Decimal

def test_get_my_wallet(auth_client):
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200   
    assert Decimal(response.json()["balance"]) == Decimal("0.00")   

def test_deposit(auth_client):
    response = auth_client.post("/wallets/me/deposit", json={"amount":"20.02"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("20.02")
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("20.02")

def test_withdraw(auth_client):
    response = auth_client.post("/wallets/me/deposit", json={"amount":"20.02"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("20.02")
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("20.02")
    response = auth_client.post("/wallets/me/withdraw", json={"amount":"10.01"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("10.01")
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("10.01")

def test_withdraw_insufficient_funds(auth_client):
    response = auth_client.post("/wallets/me/deposit", json={"amount":"20.02"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("20.02")
    response = auth_client.post("/wallets/me/withdraw", json={"amount":"30.00"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InsufficientFundsError"
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("20.02")