def test_forgot_password(client, registered_user):
    response = client.post("/auth/forgot-password", json={"email": registered_user["email"]})
    assert response.status_code == 200
    assert "token" in response.json()

# NOTE: token in response is a dev-mode stand-in for email delivery; in production, remove it from the response so both branches return identical bodies — currently the shape difference leaks account existence.

def test_forgot_password_unknown_email(client):
    response = client.post("/auth/forgot-password", json={"email": "test@gmail.com"})
    assert response.status_code == 200
    assert "token" not in response.json()

def test_reset_password_flow(client, registered_user):
    response = client.post("/auth/forgot-password", json={"email": registered_user["email"]})
    assert response.status_code == 200
    assert "token" in response.json()
    token = response.json()["token"]
    response = client.post("/auth/reset-password", json={"token": token, "new_password": "testing", "confirm_new_password": "testing"})
    assert response.status_code == 200
    response = client.post("/auth/token", data={"username": registered_user["email"], "password": "testing"})
    assert response.status_code == 200
    response = client.post("/auth/token", data={"username": registered_user["email"], "password": registered_user["password"]})
    assert response.status_code == 401

def test_reset_password_invalid_token(client):
    response = client.post("/auth/reset-password", json={"token": "1243865890hsfz72", "new_password": "testing", "confirm_new_password": "testing"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InvalidResetTokenError"

def test_reset_token_single_use(client, registered_user):
    response = client.post("/auth/forgot-password", json={"email": registered_user["email"]})
    assert response.status_code == 200
    assert "token" in response.json()
    token = response.json()["token"]
    response = client.post("/auth/reset-password", json={"token": token, "new_password": "testing", "confirm_new_password": "testing"})
    assert response.status_code == 200
    response = client.post("/auth/token", data={"username": registered_user["email"], "password": "testing"})
    assert response.status_code == 200
    response = client.post("/auth/reset-password", json={"token": token, "new_password": "testing", "confirm_new_password": "testing"})
    assert response.status_code == 400
    assert response.json()["error_type"] == "InvalidResetTokenError"
