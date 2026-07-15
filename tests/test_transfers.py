from decimal import Decimal
from app.models.wallet import Wallet

def test_transfer_success(auth_client, second_user, db_session):
    response = auth_client.post("/wallets/me/deposit", json={"amount":"40.50"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("40.50") 
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("40.50")
    response = auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": second_user["wallet_id"], "amount": "10.25"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("10.25")
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200   
    assert Decimal(response.json()["balance"]) == Decimal("30.25") 
    wallet = db_session.query(Wallet).filter(Wallet.user_id == second_user["id"]).first()
    assert wallet.balance == Decimal("10.25")

def test_transfer_insufficient_funds(auth_client, second_user, db_session):
    response = auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": second_user["wallet_id"], "amount": "10.25"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InsufficientFundsError"
    response = auth_client.get("/wallets/me")
    assert response.status_code == 200   
    assert Decimal(response.json()["balance"]) == Decimal("0.00") 
    wallet = db_session.query(Wallet).filter(Wallet.user_id == second_user["id"]).first()
    assert wallet.balance == Decimal("0.00")

def test_transfer_to_self(auth_client, registered_user, db_session):
    wallet = db_session.query(Wallet).filter(Wallet.user_id == registered_user["id"]).first()
    response = auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": wallet.id, "amount": "10.25"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InvalidTransferError"

def test_transfer_to_nonexistent_wallet(auth_client):
    response = auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": 9999, "amount": "10.25"})
    assert response.status_code == 404
    assert response.json()["error_type"] == "WalletNotFoundError"