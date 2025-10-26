"""Use case admin para listar todas classificações."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.application.schemas.classification import ClassificationListResponse, ClassificationResponse


class ListAllClassificationsUseCase:
    """Lista classificações de todos usuários (admin)."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        grain_type: str | None = None,
        include_deleted: bool = False
    ) -> ClassificationListResponse:
        """Lista todas classificações com filtros."""
        classifications = await self.classification_repo.list_all(
            user_id=user_id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
            grain_type=grain_type
        )

        total = await self.classification_repo.count(
            user_id=user_id,
            include_deleted=include_deleted,
            grain_type=grain_type
        )

        items = [ClassificationResponse.model_validate(c) for c in classifications]

        return ClassificationListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
