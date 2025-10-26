"""Use case para listar classificações."""

from datetime import datetime

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.application.schemas.classification import ClassificationListResponse, ClassificationResponse


class ListClassificationsUseCase:
    """Lista classificações do usuário com filtros."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo

    async def execute(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        grain_type: str | None = None
    ) -> ClassificationListResponse:
        """Lista classificações do usuário."""
        classifications = await self.classification_repo.list_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            include_deleted=False,
            grain_type=grain_type
        )

        total = await self.classification_repo.count(
            user_id=user_id,
            include_deleted=False,
            grain_type=grain_type
        )

        items = [ClassificationResponse.model_validate(c) for c in classifications]

        return ClassificationListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
