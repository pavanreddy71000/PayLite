def test_login_success(client, registered_user):
    response = client.post("/auth/token", data={"username": registered_user["email"], "password": registered_user["password"]})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/token", data={"username":"Pavan@Test.com", "password":"wrong"})
    assert response.status_code == 401
    data = response.json()
    assert data["error_type"] == "AuthenticationError"

def test_protected_endpoint_rejects_garbage_token(client):
    client.headers["Authorization"] = "Bearer not-a-real-jwt"
    response = client.get("/wallets/me")
    assert response.status_code == 401
    assert response.json()["error_type"] == "AuthenticationError"