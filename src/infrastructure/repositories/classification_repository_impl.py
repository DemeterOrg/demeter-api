"""Implementação do repositório de Classifications."""

from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.classification import Classification
from src.config.exceptions.custom_exceptions import DatabaseError, NotFoundError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class ClassificationRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        image_path: str,
        grain_type: str,
        confidence_score: Optional[float] = None,
        extra_data: Optional[dict] = None,
    ) -> Classification:
        """Cria uma nova classificação."""
        try:
            classification = Classification(
                user_id=user_id,
                image_path=image_path,
                grain_type=grain_type,
                confidence_score=confidence_score,
                extra_data=extra_data,
            )
            self.session.add(classification)
            await self.session.flush()
            await self.session.refresh(classification)

            logger.info("Classification created", classification_id=classification.id, user_id=user_id)
            return classification
        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating classification", user_id=user_id, error=str(e))
            raise DatabaseError(f"Erro ao criar classificação: {str(e)}")

    async def get_by_id(
        self,
        classification_id: int,
        user_id: Optional[int] = None,
        include_deleted: bool = False
    ) -> Optional[Classification]:
        """Busca classificação por ID, opcionalmente filtrando por usuário."""
        try:
            conditions = [Classification.id == classification_id]

            if user_id is not None:
                conditions.append(Classification.user_id == user_id)

            if not include_deleted:
                conditions.append(Classification.is_deleted == False)

            stmt = select(Classification).where(and_(*conditions))
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error fetching classification", classification_id=classification_id, error=str(e))
            raise DatabaseError(f"Erro ao buscar classificação: {str(e)}")

    async def list_all(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        grain_type: Optional[str] = None,
    ) -> list[Classification]:
        """Lista classificações com filtros opcionais."""
        try:
            conditions = []

            if user_id is not None:
                conditions.append(Classification.user_id == user_id)

            if not include_deleted:
                conditions.append(Classification.is_deleted == False)

            if grain_type:
                conditions.append(Classification.grain_type == grain_type)

            stmt = select(Classification)
            if conditions:
                stmt = stmt.where(and_(*conditions))

            stmt = stmt.order_by(Classification.created_at.desc()).offset(skip).limit(limit)

            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing classifications", error=str(e))
            raise DatabaseError(f"Erro ao listar classificações: {str(e)}")

    async def count(
        self,
        user_id: Optional[int] = None,
        include_deleted: bool = False,
        grain_type: Optional[str] = None,
    ) -> int:
        """Conta classificações com filtros opcionais."""
        try:
            conditions = []

            if user_id is not None:
                conditions.append(Classification.user_id == user_id)

            if not include_deleted:
                conditions.append(Classification.is_deleted == False)

            if grain_type:
                conditions.append(Classification.grain_type == grain_type)

            stmt = select(func.count(Classification.id))
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            logger.error("Error counting classifications", error=str(e))
            raise DatabaseError(f"Erro ao contar classificações: {str(e)}")

    async def update(self, classification: Classification) -> Classification:
        """Atualiza uma classificação."""
        try:
            await self.session.flush()
            await self.session.refresh(classification)
            logger.info("Classification updated", classification_id=classification.id)
            return classification
        except Exception as e:
            await self.session.rollback()
            logger.error("Error updating classification", classification_id=classification.id, error=str(e))
            raise DatabaseError(f"Erro ao atualizar classificação: {str(e)}")

    async def soft_delete(self, classification_id: int, user_id: Optional[int] = None) -> bool:
        """Soft delete de uma classificação."""
        classification = await self.get_by_id(classification_id, user_id=user_id)

        if not classification:
            raise NotFoundError("Classificação não encontrada")

        try:
            classification.soft_delete()
            await self.session.flush()
            logger.info("Classification soft deleted", classification_id=classification_id)
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error("Error soft deleting classification", classification_id=classification_id, error=str(e))
            raise DatabaseError(f"Erro ao deletar classificação: {str(e)}")

    async def hard_delete(self, classification_id: int) -> bool:
        """Hard delete de uma classificação (apenas admin)."""
        classification = await self.get_by_id(classification_id, include_deleted=True)

        if not classification:
            raise NotFoundError("Classificação não encontrada")

        try:
            await self.session.delete(classification)
            await self.session.flush()
            logger.info("Classification hard deleted", classification_id=classification_id)
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error("Error hard deleting classification", classification_id=classification_id, error=str(e))
            raise DatabaseError(f"Erro ao deletar classificação: {str(e)}")

    async def restore(self, classification_id: int) -> bool:
        """Restaura uma classificação soft deleted."""
        classification = await self.get_by_id(classification_id, include_deleted=True)

        if not classification:
            raise NotFoundError("Classificação não encontrada")

        if not classification.is_deleted:
            return True

        try:
            classification.restore()
            await self.session.flush()
            logger.info("Classification restored", classification_id=classification_id)
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error("Error restoring classification", classification_id=classification_id, error=str(e))
            raise DatabaseError(f"Erro ao restaurar classificação: {str(e)}")
