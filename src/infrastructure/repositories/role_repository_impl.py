"""Implementação do repositório de Roles."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.models.role import Role
from src.infrastructure.models.user_role import UserRole
from src.config.exceptions.custom_exceptions import DatabaseError, NotFoundError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class RoleRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Busca role por nome."""
        try:
            stmt = select(Role).where(Role.name == name)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error fetching role by name", name=name, error=str(e))
            raise DatabaseError(f"Erro ao buscar role: {str(e)}")

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """Busca role por ID."""
        try:
            stmt = select(Role).where(Role.id == role_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error fetching role by ID", role_id=role_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar role: {str(e)}")

    async def get_with_permissions(self, role_id: int) -> Optional[Role]:
        """Busca role com suas permissões carregadas."""
        try:
            stmt = (
                select(Role)
                .where(Role.id == role_id)
                .options(selectinload(Role.role_permissions))
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error fetching role with permissions", role_id=role_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar role: {str(e)}")

    async def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None
    ) -> UserRole:
        """Atribui uma role a um usuário."""
        try:
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                assigned_by=assigned_by,
            )
            self.session.add(user_role)
            await self.session.flush()
            await self.session.refresh(user_role)

            logger.info("Role assigned to user", user_id=user_id, role_id=role_id)
            return user_role
        except Exception as e:
            await self.session.rollback()
            logger.error("Error assigning role to user", user_id=user_id, role_id=role_id, error=str(e))
            raise DatabaseError(f"Erro ao atribuir role: {str(e)}")

    async def revoke_role_from_user(self, user_id: int, role_id: int) -> bool:
        """Remove uma role de um usuário."""
        try:
            stmt = select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
            result = await self.session.execute(stmt)
            user_role = result.scalar_one_or_none()

            if not user_role:
                raise NotFoundError("Associação usuário-role não encontrada")

            await self.session.delete(user_role)
            await self.session.flush()

            logger.info("Role revoked from user", user_id=user_id, role_id=role_id)
            return True
        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("Error revoking role from user", user_id=user_id, role_id=role_id, error=str(e))
            raise DatabaseError(f"Erro ao remover role: {str(e)}")

    async def list_all(self) -> list[Role]:
        """Lista todas as roles."""
        try:
            stmt = select(Role).order_by(Role.name)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing roles", error=str(e))
            raise DatabaseError(f"Erro ao listar roles: {str(e)}")
