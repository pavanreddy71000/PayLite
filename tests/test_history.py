from decimal import Decimal


def test_transfer_history(auth_client, second_user):
    # Arrange: create a known history — 2 deposits and 1 outgoing transfer
    auth_client.post("/wallets/me/deposit", json={"amount": "50.00"})
    auth_client.post("/wallets/me/deposit", json={"amount": "5.00"})
    auth_client.post(
        "/wallets/me/transfer",
        json={"receiver_wallet_id": second_user["wallet_id"], "amount": "12.50"},
    )

    response = auth_client.get("/wallets/me/history")
    assert response.status_code == 200
    data = response.json()

    # pagination envelope
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["size"] == 20
    assert data["pages"] == 1
    assert len(data["items"]) == 3

    # all three operations present (created_at ties → row order not guaranteed)
    amounts = {Decimal(item["amount"]) for item in data["items"]}
    assert amounts == {Decimal("50.00"), Decimal("5.00"), Decimal("12.50")}

    # sorting verified via a column with no ties
    response = auth_client.get("/wallets/me/history", params={"sort": "-amount"})
    assert response.status_code == 200
    assert Decimal(response.json()["items"][0]["amount"]) == Decimal("50.00")


def test_transfer_history_filter_and_pagination(auth_client, second_user):
    auth_client.post("/wallets/me/deposit", json={"amount": "50.00"})
    auth_client.post("/wallets/me/deposit", json={"amount": "5.00"})
    auth_client.post(
        "/wallets/me/transfer",
        json={"receiver_wallet_id": second_user["wallet_id"], "amount": "12.50"},
    )

    # filter: only deposits
    response = auth_client.get("/wallets/me/history", params={"type": "deposit"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["sender_wallet_id"] is None for item in data["items"])

    # pagination: page size 1 → 3 pages, one item each
    response = auth_client.get("/wallets/me/history", params={"size": 1, "page": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["pages"] == 3
    assert len(data["items"]) == 1


def test_transfer_history_invalid_sort(auth_client):
    response = auth_client.get("/wallets/me/history", params={"sort": "hacker_field"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InvalidTransferError"