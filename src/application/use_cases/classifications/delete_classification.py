"""Use case para deletar classificação."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class DeleteClassificationUseCase:
    """Soft delete de classificação."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo

    async def execute(self, classification_id: int, user_id: int) -> bool:
        """Soft delete verificando ownership."""
        result = await self.classification_repo.soft_delete(
            classification_id=classification_id,
            user_id=user_id
        )

        logger.info(
            "Classification soft deleted",
            classification_id=classification_id,
            user_id=user_id
        )

        return result
