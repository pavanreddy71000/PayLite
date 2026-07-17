from decimal import Decimal
from app.models.wallet import Wallet
from sqlalchemy import select

async def test_transfer_success(auth_client, second_user, db_session):
    response = await auth_client.post("/wallets/me/deposit", json={"amount":"40.50"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("40.50") 
    response = await auth_client.get("/wallets/me")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("40.50")
    response = await auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": second_user["wallet_id"], "amount": "10.25"})
    assert response.status_code == 201
    assert Decimal(response.json()["amount"]) == Decimal("10.25")
    response = await auth_client.get("/wallets/me")
    assert response.status_code == 200   
    assert Decimal(response.json()["balance"]) == Decimal("30.25") 
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == second_user["id"]))
    wallet = result.scalar_one_or_none()
    assert wallet.balance == Decimal("10.25")

async def test_transfer_insufficient_funds(auth_client, second_user, db_session):
    response = await auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": second_user["wallet_id"], "amount": "10.25"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InsufficientFundsError"
    response = await auth_client.get("/wallets/me")
    assert response.status_code == 200   
    assert Decimal(response.json()["balance"]) == Decimal("0.00") 
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == second_user["id"]))
    wallet = result.scalar_one_or_none()
    assert wallet.balance == Decimal("0.00")

async def test_transfer_to_self(auth_client, registered_user, db_session):
    result = await db_session.execute(select(Wallet).where(Wallet.user_id == registered_user["id"]))
    wallet = result.scalar_one_or_none()
    response = await auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": wallet.id, "amount": "10.25"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InvalidTransferError"

async def test_transfer_to_nonexistent_wallet(auth_client):
    response = await auth_client.post("/wallets/me/transfer", json={"receiver_wallet_id": 9999, "amount": "10.25"})
    assert response.status_code == 404
    assert response.json()["error_type"] == "WalletNotFoundError"