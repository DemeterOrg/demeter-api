"""
Implementação concreta do repositório de Usuários usando SQLAlchemy.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import UserEntity
from src.infrastructure.models.user import User
from src.infrastructure.models.user_role import UserRole
from src.infrastructure.models.role import Role
from src.infrastructure.models.role_permission import RolePermission
from src.infrastructure.models.permission import Permission
from src.config.exceptions.custom_exceptions import (
    ConflictError,
    NotFoundError,
    DatabaseError,
)
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class UserRepositoryImpl(UserRepository):
    """
    Implementação do repositório de Usuários usando SQLAlchemy.

    Args:
        session: Sessão assíncrona do SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_entity(self, model: User) -> UserEntity:
        """Converte modelo SQLAlchemy para entidade de domínio."""
        return UserEntity(
            id=model.id,
            email=model.email,
            name=model.name,
            phone=model.phone,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
        )

    async def create(self, user: UserEntity) -> UserEntity:
        """Cria um novo usuário."""
        try:
            model = User(
                email=user.email,
                name=user.name,
                phone=user.phone,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_verified=user.is_verified,
            )

            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            logger.info("User created", user_id=model.id, email=model.email)
            return self._model_to_entity(model)

        except IntegrityError as e:
            await self.session.rollback()
            logger.warning("User creation failed - duplicate email", email=user.email)
            raise ConflictError(
                f"Usuário com email '{user.email}' já existe",
                details={"email": user.email},
            )
        except Exception as e:
            await self.session.rollback()
            logger.error("User creation failed", error=str(e), exc_info=True)
            raise DatabaseError(f"Erro ao criar usuário: {str(e)}")

    async def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Busca um usuário por ID."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error("Error fetching user by ID", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar usuário: {str(e)}")

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """Busca um usuário por email."""
        try:
            stmt = select(User).where(User.email == email)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_entity(model)
            return None

        except Exception as e:
            logger.error("Error fetching user by email", email=email, error=str(e))
            raise DatabaseError(f"Erro ao buscar usuário: {str(e)}")

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[UserEntity]:
        """Lista usuários com paginação e filtros opcionais."""
        try:
            stmt = select(User)

            if is_active is not None:
                stmt = stmt.where(User.is_active == is_active)

            stmt = stmt.offset(skip).limit(limit).order_by(User.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_entity(model) for model in models]

        except Exception as e:
            logger.error("Error listing users", error=str(e))
            raise DatabaseError(f"Erro ao listar usuários: {str(e)}")

    async def update(self, user: UserEntity) -> UserEntity:
        """Atualiza um usuário existente."""
        try:
            stmt = select(User).where(User.id == user.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                raise NotFoundError(f"Usuário com ID {user.id} não encontrado")

            model.name = user.name
            model.email = user.email
            model.phone = user.phone
            model.hashed_password = user.hashed_password
            model.is_active = user.is_active
            model.is_verified = user.is_verified

            await self.session.flush()
            await self.session.refresh(model)

            logger.info("User updated", user_id=model.id, email=model.email)
            return self._model_to_entity(model)

        except NotFoundError:
            raise
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError(f"Email '{user.email}' já está em uso")
        except Exception as e:
            await self.session.rollback()
            logger.error("User update failed", user_id=user.id, error=str(e))
            raise DatabaseError(f"Erro ao atualizar usuário: {str(e)}")

    async def delete(self, user_id: int) -> bool:
        """Deleta um usuário."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            await self.session.delete(model)
            await self.session.flush()

            logger.info("User deleted", user_id=user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("User deletion failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao deletar usuário: {str(e)}")

    async def exists_by_email(self, email: str) -> bool:
        """Verifica se existe um usuário com o email especificado."""
        try:
            stmt = select(User.id).where(User.email == email)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error("Error checking user existence", email=email, error=str(e))
            raise DatabaseError(f"Erro ao verificar usuário: {str(e)}")

    async def update_last_login(self, user_id: int, login_time: datetime) -> bool:
        """Atualiza a data do último login do usuário."""
        try:
            stmt = (
                sql_update(User)
                .where(User.id == user_id)
                .values(last_login=login_time)
                .execution_options(synchronize_session="fetch")
            )

            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            await self.session.flush()

            logger.debug("User last login updated", user_id=user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("Update last login failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao atualizar último login: {str(e)}")

    async def count_all(self, is_active: Optional[bool] = None) -> int:
        """Conta o número total de usuários."""
        try:
            from sqlalchemy import func

            stmt = select(func.count(User.id))

            if is_active is not None:
                stmt = stmt.where(User.is_active == is_active)

            result = await self.session.execute(stmt)
            return result.scalar_one()

        except Exception as e:
            logger.error("Error counting users", error=str(e))
            raise DatabaseError(f"Erro ao contar usuários: {str(e)}")

    async def activate(self, user_id: int) -> bool:
        """Ativa um usuário."""
        try:
            stmt = (
                sql_update(User)
                .where(User.id == user_id)
                .values(is_active=True)
                .execution_options(synchronize_session="fetch")
            )

            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            await self.session.flush()

            logger.info("User activated", user_id=user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("User activation failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao ativar usuário: {str(e)}")

    async def deactivate(self, user_id: int) -> bool:
        """Desativa um usuário."""
        try:
            stmt = (
                sql_update(User)
                .where(User.id == user_id)
                .values(is_active=False)
                .execution_options(synchronize_session="fetch")
            )

            result = await self.session.execute(stmt)

            if result.rowcount == 0:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            await self.session.flush()

            logger.info("User deactivated", user_id=user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("User deactivation failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao desativar usuário: {str(e)}")

    async def get_by_id_with_roles(self, user_id: int, include_deleted: bool = False) -> Optional[User]:
        """Busca usuário por ID com roles e permissions carregadas."""
        try:
            stmt = (
                select(User)
                .where(User.id == user_id)
                .options(
                    selectinload(User.user_roles).selectinload(UserRole.role).selectinload(Role.role_permissions).selectinload(RolePermission.permission)
                )
            )

            if not include_deleted:
                stmt = stmt.where(User.is_deleted == False)

            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error("Error fetching user with roles", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar usuário: {str(e)}")

    async def get_by_email_with_roles(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Busca usuário por email com roles e permissions carregadas."""
        try:
            stmt = (
                select(User)
                .where(User.email == email)
                .options(
                    selectinload(User.user_roles).selectinload(UserRole.role).selectinload(Role.role_permissions).selectinload(RolePermission.permission)
                )
            )

            if not include_deleted:
                stmt = stmt.where(User.is_deleted == False)

            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error("Error fetching user with roles by email", email=email, error=str(e))
            raise DatabaseError(f"Erro ao buscar usuário: {str(e)}")

    async def soft_delete(self, user_id: int, deleted_by_id: Optional[int] = None) -> bool:
        """Marca usuário como deletado (soft delete)."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            user.soft_delete(deleted_by_id)
            await self.session.flush()

            logger.info("User soft deleted", user_id=user_id, deleted_by=deleted_by_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("User soft delete failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao deletar usuário: {str(e)}")

    async def restore(self, user_id: int) -> bool:
        """Restaura usuário soft deleted."""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise NotFoundError(f"Usuário com ID {user_id} não encontrado")

            user.restore()
            await self.session.flush()

            logger.info("User restored", user_id=user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("User restore failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao restaurar usuário: {str(e)}")
