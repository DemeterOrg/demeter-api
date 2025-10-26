"""
Implementação concreta do repositório de Refresh Tokens usando SQLAlchemy.
"""

from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.models.refresh_token import RefreshToken
from src.config.exceptions.custom_exceptions import (
    NotFoundError,
    DatabaseError,
)
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    """
    Implementação do repositório de Refresh Tokens usando SQLAlchemy.

    Args:
        session: Sessão assíncrona do SQLAlchemy
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _model_to_dict(self, model: RefreshToken) -> dict:
        """Converte modelo SQLAlchemy para dicionário."""
        return {
            "id": model.id,
            "token": model.token,
            "user_id": model.user_id,
            "expires_at": model.expires_at,
            "created_at": model.created_at,
            "revoked_at": model.revoked_at,
            "is_revoked": model.is_revoked,
            "user_agent": model.user_agent,
            "ip_address": model.ip_address,
            "is_expired": model.is_expired,
            "is_valid": model.is_valid,
        }

    async def create(
        self,
        token: str,
        user_id: int,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> int:
        """Cria um novo refresh token."""
        try:
            model = RefreshToken(
                token=token,
                user_id=user_id,
                expires_at=expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )

            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)

            logger.info(
                "Refresh token created",
                token_id=model.id,
                user_id=user_id,
            )
            return model.id

        except Exception as e:
            await self.session.rollback()
            logger.error("Refresh token creation failed", error=str(e), exc_info=True)
            raise DatabaseError(f"Erro ao criar refresh token: {str(e)}")

    async def get_by_token(self, token: str) -> Optional[dict]:
        """Busca um refresh token pelo hash."""
        try:
            stmt = select(RefreshToken).where(RefreshToken.token == token)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_dict(model)
            return None

        except Exception as e:
            logger.error("Error fetching refresh token", error=str(e))
            raise DatabaseError(f"Erro ao buscar refresh token: {str(e)}")

    async def get_by_id(self, token_id: int) -> Optional[dict]:
        """Busca um refresh token por ID."""
        try:
            stmt = select(RefreshToken).where(RefreshToken.id == token_id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                return self._model_to_dict(model)
            return None

        except Exception as e:
            logger.error("Error fetching refresh token by ID", token_id=token_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar refresh token: {str(e)}")

    async def list_by_user(
        self,
        user_id: int,
        only_valid: bool = True,
    ) -> List[dict]:
        """Lista todos os refresh tokens de um usuário."""
        try:
            stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)

            if only_valid:
                now = datetime.now(timezone.utc)
                stmt = stmt.where(
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > now,
                )

            stmt = stmt.order_by(RefreshToken.created_at.desc())

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            return [self._model_to_dict(model) for model in models]

        except Exception as e:
            logger.error("Error listing refresh tokens", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao listar refresh tokens: {str(e)}")

    async def revoke(self, token: str) -> bool:
        """Revoga um refresh token."""
        try:
            stmt = select(RefreshToken).where(RefreshToken.token == token)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()

            if not model:
                raise NotFoundError("Refresh token não encontrado")

            model.revoke()
            await self.session.flush()

            logger.info("Refresh token revoked", token_id=model.id, user_id=model.user_id)
            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error("Refresh token revocation failed", error=str(e))
            raise DatabaseError(f"Erro ao revogar refresh token: {str(e)}")

    async def revoke_all_by_user(self, user_id: int) -> int:
        """Revoga todos os refresh tokens de um usuário."""
        try:
            now = datetime.now(timezone.utc)

            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )

            result = await self.session.execute(stmt)
            models = result.scalars().all()

            count = 0
            for model in models:
                model.revoke()
                count += 1

            await self.session.flush()

            logger.info(
                "All refresh tokens revoked for user",
                user_id=user_id,
                count=count,
            )
            return count

        except Exception as e:
            await self.session.rollback()
            logger.error("Bulk revocation failed", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao revogar tokens: {str(e)}")

    async def delete_expired(self) -> int:
        """Deleta todos os tokens expirados do banco de dados."""
        try:
            now = datetime.now(timezone.utc)

            stmt = sql_delete(RefreshToken).where(
                RefreshToken.expires_at < now
            )

            result = await self.session.execute(stmt)
            count = result.rowcount

            await self.session.flush()

            logger.info("Expired refresh tokens deleted", count=count)
            return count

        except Exception as e:
            await self.session.rollback()
            logger.error("Expired token deletion failed", error=str(e))
            raise DatabaseError(f"Erro ao deletar tokens expirados: {str(e)}")

    async def is_valid(self, token: str) -> bool:
        """Verifica se um token é válido (existe, não revogado, não expirado)."""
        try:
            now = datetime.now(timezone.utc)

            stmt = select(RefreshToken.id).where(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now,
            )

            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error("Error checking token validity", error=str(e))
            raise DatabaseError(f"Erro ao verificar token: {str(e)}")

    async def exists(self, token: str) -> bool:
        """Verifica se um token existe no banco."""
        try:
            stmt = select(RefreshToken.id).where(RefreshToken.token == token)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error("Error checking token existence", error=str(e))
            raise DatabaseError(f"Erro ao verificar token: {str(e)}")
