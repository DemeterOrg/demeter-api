"""
Interface do repositório de Usuários.

"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from src.domain.entities.user import UserEntity


class UserRepository(ABC):
    """
    Define as operações de persistência para entidades User.
    """

    @abstractmethod
    async def create(self, user: UserEntity) -> UserEntity:
        """
        Cria um novo usuário.
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        Busca um usuário por ID.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Busca um usuário por email.
        """
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[UserEntity]:
        """
        Lista usuários com paginação e filtros opcionais.
        """
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity:
        """
        Atualiza um usuário existente.
        """
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Deleta um usuário.
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica se existe um usuário com o email especificado.
        """
        pass

    @abstractmethod
    async def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        """
        Atualiza a data do último login do usuário.
        """
        pass

    @abstractmethod
    async def count_all(self, is_active: Optional[bool] = None) -> int:
        """
        Conta o número total de usuários.
        """
        pass

    @abstractmethod
    async def activate(self, user_id: int) -> bool:
        """
        Ativa um usuário.
        """
        pass

    @abstractmethod
    async def deactivate(self, user_id: int) -> bool:
        """
        Desativa um usuário.
        """
        pass
