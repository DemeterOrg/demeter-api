"""
Módulo de segurança da aplicação.

Este módulo contém implementações relacionadas a:
- Autenticação (JWT)
- Hashing e verificação de senhas (Argon2id)
"""

from src.config.security.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
)
from src.config.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    "validate_password_strength",
]
