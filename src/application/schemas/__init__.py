"""
Define modelos de entrada e saída para validação de dados nas APIs.
"""

from src.application.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from src.application.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
]
