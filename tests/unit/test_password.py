import pytest

from src.config.security.password import get_password_hash, verify_password


@pytest.mark.unit
def test_hash_password_creates_valid_hash():
    password = "MySecurePass123!"
    hashed = get_password_hash(password)

    assert hashed is not None
    assert hashed != password
    assert hashed.startswith("$argon2")


@pytest.mark.unit
def test_verify_password_correct_returns_true():
    password = "MySecurePass123!"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


@pytest.mark.unit
def test_verify_password_incorrect_returns_false():
    password = "MySecurePass123!"
    wrong_password = "WrongPassword456"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False
