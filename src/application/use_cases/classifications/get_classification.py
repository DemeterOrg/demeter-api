"""Use case para buscar classificação."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.application.schemas.classification import ClassificationResponse
from src.config.exceptions.custom_exceptions import NotFoundError


class GetClassificationUseCase:
    """Busca classificação verificando ownership."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo

    async def execute(
        self,
        classification_id: int,
        user_id: int
    ) -> ClassificationResponse:
        """Busca classificação do usuário."""
        classification = await self.classification_repo.get_by_id(
            classification_id=classification_id,
            user_id=user_id,
            include_deleted=False
        )

        if not classification:
            raise NotFoundError("Classificação não encontrada")

        return ClassificationResponse.model_validate(classification)
