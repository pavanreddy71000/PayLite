from app.services.user_service import pwd_context
from app.services.auth_service import verify_password

def test_python_basics():
    assert 2 + 2 == 4


def test_password_hash_and_verify():
    # Arrange — set up the data we need
    password = "SuperSecret123"

    # Act — run the thing we're testing
    hashed = pwd_context.hash(password)

    # Assert — check the outcome
    assert hashed != password          # hashing must not store plaintext
    assert verify_password(password, hashed) is True


def test_wrong_password_fails():
    hashed = pwd_context.hash("correct-password")

    assert verify_password("wrong-password", hashed) is False