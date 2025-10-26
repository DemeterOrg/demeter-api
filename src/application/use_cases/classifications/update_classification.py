"""Use case para atualizar classificação."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.application.schemas.classification import ClassificationUpdate, ClassificationResponse
from src.config.exceptions.custom_exceptions import NotFoundError


class UpdateClassificationUseCase:
    """Atualiza notas da classificação."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo

    async def execute(
        self,
        classification_id: int,
        user_id: int,
        data: ClassificationUpdate
    ) -> ClassificationResponse:
        """Atualiza classificação do usuário."""
        classification = await self.classification_repo.get_by_id(
            classification_id=classification_id,
            user_id=user_id,
            include_deleted=False
        )

        if not classification:
            raise NotFoundError("Classificação não encontrada")

        if data.notes is not None:
            if classification.extra_data is None:
                classification.extra_data = {}
            classification.extra_data["notes"] = data.notes

        updated = await self.classification_repo.update(classification)

        return ClassificationResponse.model_validate(updated)
