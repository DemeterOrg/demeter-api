"""
Interface do repositório de Usuários.

Define o contrato para operações de persistência relacionadas a usuários.
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

        Args:
            user: Entidade User a ser criada

        Returns:
            Entidade User criada com ID preenchido

        Raises:
            ConflictError: Se já existir usuário com o mesmo email
            DatabaseError: Em caso de erro no banco de dados
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        Busca um usuário por ID.

        Args:
            user_id: ID do usuário

        Returns:
            Entidade User ou None se não encontrado
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        Busca um usuário por email.

        Args:
            email: Email do usuário

        Returns:
            Entidade User ou None se não encontrado
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

        Args:
            skip: Número de registros a pular (offset)
            limit: Número máximo de registros a retornar
            is_active: Filtrar por status ativo (None = todos)

        Returns:
            Lista de entidades User
        """
        pass

    @abstractmethod
    async def update(self, user: UserEntity) -> UserEntity:
        """
        Atualiza um usuário existente.

        Args:
            user: Entidade User com dados atualizados

        Returns:
            Entidade User atualizada

        Raises:
            NotFoundError: Se o usuário não existir
            ConflictError: Se tentar alterar para email já existente
            DatabaseError: Em caso de erro no banco de dados
        """
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Deleta um usuário.

        Args:
            user_id: ID do usuário a ser deletado

        Returns:
            True se deletado com sucesso

        Raises:
            NotFoundError: Se o usuário não existir
            DatabaseError: Em caso de erro no banco de dados
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica se existe um usuário com o email especificado.

        Args:
            email: Email a verificar

        Returns:
            True se existir, False caso contrário
        """
        pass

    @abstractmethod
    async def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        """
        Atualiza a data do último login do usuário.

        Args:
            user_id: ID do usuário
            login_time: Data/hora do login

        Returns:
            True se atualizado com sucesso

        Raises:
            NotFoundError: Se o usuário não existir
            DatabaseError: Em caso de erro no banco de dados
        """
        pass

    @abstractmethod
    async def count_all(self, is_active: Optional[bool] = None) -> int:
        """
        Conta o número total de usuários.

        Args:
            is_active: Filtrar por status ativo (None = todos)

        Returns:
            Número total de usuários
        """
        pass

    @abstractmethod
    async def activate(self, user_id: int) -> bool:
        """
        Ativa um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            True se ativado com sucesso

        Raises:
            NotFoundError: Se o usuário não existir
        """
        pass

    @abstractmethod
    async def deactivate(self, user_id: int) -> bool:
        """
        Desativa um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            True se desativado com sucesso

        Raises:
            NotFoundError: Se o usuário não existir
        """
        pass
