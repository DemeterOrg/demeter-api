"""
Interfaces de repositórios (Abstract Base Classes).

Define contratos para acesso a dados.
"""

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.refresh_token_repository import RefreshTokenRepository

__all__ = [
    "UserRepository",
    "RefreshTokenRepository",
]
