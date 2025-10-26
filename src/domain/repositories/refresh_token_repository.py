"""
Interface do repositório de Refresh Tokens.

Define o contrato para operações de persistência relacionadas a refresh tokens.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class RefreshTokenRepository(ABC):
    """
    Interface abstrata para repositório de Refresh Tokens.

    Define as operações de persistência para refresh tokens,
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

        Args:
            token: Hash do token
            user_id: ID do usuário proprietário
            expires_at: Data de expiração
            user_agent: User agent do cliente
            ip_address: IP do cliente

        Returns:
            ID do token criado

        Raises:
            DatabaseError: Em caso de erro no banco de dados
        """
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[dict]:
        """
        Busca um refresh token pelo hash.

        Args:
            token: Hash do token

        Returns:
            Dicionário com dados do token ou None se não encontrado
        """
        pass

    @abstractmethod
    async def get_by_id(self, token_id: int) -> Optional[dict]:
        """
        Busca um refresh token por ID.

        Args:
            token_id: ID do token

        Returns:
            Dicionário com dados do token ou None se não encontrado
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

        Args:
            user_id: ID do usuário
            only_valid: Se True, retorna apenas tokens válidos (não revogados e não expirados)

        Returns:
            Lista de dicionários com dados dos tokens
        """
        pass

    @abstractmethod
    async def revoke(self, token: str) -> bool:
        """
        Revoga um refresh token.

        Args:
            token: Hash do token a ser revogado

        Returns:
            True se revogado com sucesso

        Raises:
            NotFoundError: Se o token não existir
        """
        pass

    @abstractmethod
    async def revoke_all_by_user(self, user_id: int) -> int:
        """
        Revoga todos os refresh tokens de um usuário.

        Útil para logout global ou quando usuário trocar senha.

        Args:
            user_id: ID do usuário

        Returns:
            Número de tokens revogados
        """
        pass

    @abstractmethod
    async def delete_expired(self) -> int:
        """
        Deleta todos os tokens expirados do banco de dados.

        Esta operação deve ser executada periodicamente para limpeza.

        Returns:
            Número de tokens deletados
        """
        pass

    @abstractmethod
    async def is_valid(self, token: str) -> bool:
        """
        Verifica se um token é válido (existe, não revogado, não expirado).

        Args:
            token: Hash do token

        Returns:
            True se válido, False caso contrário
        """
        pass

    @abstractmethod
    async def exists(self, token: str) -> bool:
        """
        Verifica se um token existe no banco.

        Args:
            token: Hash do token

        Returns:
            True se existir, False caso contrário
        """
        pass
