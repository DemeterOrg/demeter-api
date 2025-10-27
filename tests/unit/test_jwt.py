import time
from datetime import datetime, timedelta, timezone

import pytest
from jose.exceptions import ExpiredSignatureError

from src.config.security.auth import (
    create_access_token,
    extract_user_id_from_token,
    verify_token,
)


@pytest.mark.unit
def test_create_access_token_valid():
    user_id = 123
    token = create_access_token(subject=user_id)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_decode_token_returns_user_id():
    user_id = 456
    token = create_access_token(subject=user_id)

    extracted_user_id = extract_user_id_from_token(token)

    assert extracted_user_id == user_id


@pytest.mark.unit
def test_decode_expired_token_raises_error():
    from jose import jwt
    from src.config.settings import settings

    expired_time = datetime.now(timezone.utc) - timedelta(minutes=10)

    payload = {
        "sub": "123",
        "exp": expired_time,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(ExpiredSignatureError):
        verify_token(expired_token, token_type="access")
