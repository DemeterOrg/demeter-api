"""
Módulo de autenticação JWT (JSON Web Tokens).

Este módulo implementa a criação, verificação e decodificação de tokens JWT
para autenticação de usuários na API.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from src.config.settings import settings


def create_access_token(
    subject: str | int,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Cria um access token JWT.

    Args:
        subject: Identificador do usuário (user_id)
        additional_claims: Claims adicionais opcionais

    Returns:
        Token JWT assinado

    Example:
        >>> token = create_access_token(subject=123)
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def create_refresh_token(subject: str | int) -> str:
    """
    Cria um refresh token JWT.

    Refresh tokens têm validade maior e são usados para obter novos access tokens.

    Args:
        subject: Identificador do usuário (user_id)

    Returns:
        Refresh token JWT assinado

    Example:
        >>> token = create_refresh_token(subject=123)
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica um token JWT sem validar expiração.

    Útil para inspecionar o conteúdo do token.

    Args:
        token: Token JWT a ser decodificado

    Returns:
        Dicionário com os claims do token

    Raises:
        JWTError: Se o token for inválido ou malformado

    Example:
        >>> token = create_access_token(subject=123)
        >>> payload = decode_token(token)
        >>> print(payload["sub"])
        123
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},  # Não verifica expiração
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Token inválido: {str(e)}")


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verifica e decodifica um token JWT com validação completa.

    Valida:
    - Assinatura do token
    - Expiração
    - Tipo do token (access ou refresh)

    Args:
        token: Token JWT a ser verificado
        token_type: Tipo esperado do token ("access" ou "refresh")

    Returns:
        Dicionário com os claims do token

    Raises:
        ExpiredSignatureError: Se o token estiver expirado
        JWTError: Se o token for inválido
        ValueError: Se o tipo do token não corresponder

    Example:
        >>> token = create_access_token(subject=123)
        >>> payload = verify_token(token, token_type="access")
        >>> print(payload["sub"])
        123
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Verificar tipo do token
        if payload.get("type") != token_type:
            raise ValueError(
                f"Tipo de token inválido. Esperado: {token_type}, "
                f"Recebido: {payload.get('type')}"
            )

        return payload

    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token expirado")
    except JWTError as e:
        raise JWTError(f"Token inválido: {str(e)}")


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Retorna a data de expiração de um token.

    Args:
        token: Token JWT

    Returns:
        Data de expiração do token (timezone-aware) ou None se não houver

    Example:
        >>> token = create_access_token(subject=123)
        >>> expiration = get_token_expiration(token)
        >>> print(expiration)
        2025-10-23 15:30:00+00:00
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")

        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        return None
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """
    Verifica se um token está expirado.

    Args:
        token: Token JWT

    Returns:
        True se expirado, False caso contrário

    Example:
        >>> token = create_access_token(subject=123)
        >>> is_token_expired(token)
        False
    """
    expiration = get_token_expiration(token)

    if expiration is None:
        return True

    return datetime.now(timezone.utc) > expiration


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrai o user_id de um token JWT.

    Args:
        token: Token JWT

    Returns:
        ID do usuário ou None se não encontrado

    Example:
        >>> token = create_access_token(subject=123)
        >>> user_id = extract_user_id_from_token(token)
        >>> print(user_id)
        123
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except (JWTError, ValueError, TypeError):
        return None


