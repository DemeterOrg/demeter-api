"""
Interface do repositório de Refresh Tokens.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class RefreshTokenRepository(ABC):
    """
    Interface abstrata para repositório de Refresh Tokens.
    """

    @abstractmethod
    async def create(
        self,
        token: str,
        user_id: int,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> int:
        """
        Cria um novo refresh token.
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[dict]:
        """
        Busca um refresh token pelo hash.
        """
        pass

    @abstractmethod
    async def get_by_id(self, token_id: int) -> Optional[dict]:
        """
        Busca um refresh token por ID.
        """
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        only_valid: bool = True,
    ) -> List[dict]:
        """
        Lista todos os refresh tokens de um usuário.
        """
        pass

    @abstractmethod
    async def revoke(self, token: str) -> bool:
        """
        Revoga um refresh token.
        """
        pass

    @abstractmethod
    async def revoke_all_by_user(self, user_id: int) -> int:
        """
        Revoga todos os refresh tokens de um usuário.
        """
        pass

    @abstractmethod
    async def delete_expired(self) -> int:
        """
        Deleta todos os tokens expirados do banco de dados.
        """
        pass

    @abstractmethod
    async def is_valid(self, token: str) -> bool:
        """
        Verifica se um token é válido (existe, não revogado, não expirado).
        """
        pass

    @abstractmethod
    async def exists(self, token: str) -> bool:
        """
        Verifica se um token existe no banco.
        """
        pass
