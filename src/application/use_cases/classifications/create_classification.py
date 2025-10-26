"""Use case para criar classificação."""

from fastapi import UploadFile

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.infrastructure.services.storage_service import StorageService
from src.infrastructure.services.mock_classifier_service import MockClassifierService
from src.application.schemas.classification import ClassificationResponse
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class CreateClassificationUseCase:
    """Cria classificação com upload de imagem."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo
        self.storage = StorageService()
        self.classifier = MockClassifierService()

    async def execute(
        self,
        user_id: int,
        image: UploadFile,
        notes: str | None = None
    ) -> ClassificationResponse:
        """Processa upload, classifica e salva."""
        image_path = await self.storage.save_image(user_id, image)

        result = self.classifier.classify(image_path)

        if notes:
            result["extra_data"]["notes"] = notes

        classification = await self.classification_repo.create(
            user_id=user_id,
            image_path=image_path,
            grain_type=result["grain_type"],
            confidence_score=float(result["confidence_score"]),
            extra_data=result["extra_data"]
        )

        logger.info(
            "Classification created",
            classification_id=classification.id,
            user_id=user_id,
            grain_type=classification.grain_type
        )

        return ClassificationResponse.model_validate(classification)
