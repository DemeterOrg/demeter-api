"""Use case para criar classificação."""

from fastapi import UploadFile
from decimal import Decimal

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.infrastructure.services.storage_service import StorageService
from src.infrastructure.services.mock_classifier_service import MockClassifierService
from src.infrastructure.services.demeter_ml_service import DemeterMLService
from src.application.schemas.classification import ClassificationResponse
from src.config.logging.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


class CreateClassificationUseCase:
    """Cria classificação com upload de imagem."""

    def __init__(self, classification_repo: ClassificationRepositoryImpl):
        self.classification_repo = classification_repo
        self.storage = StorageService()

        if settings.USE_REAL_ML_API:
            self.classifier = DemeterMLService()
            logger.info("Using DemeterMLService (real AI)")
        else:
            self.classifier = MockClassifierService()
            logger.info("Using MockClassifierService (simulated)")

    async def execute(
        self,
        user_id: int,
        image: UploadFile,
        notes: str | None = None
    ) -> ClassificationResponse:
        """Processa upload, classifica e salva."""
        image_path = await self.storage.save_image(user_id, image)

        result = await self.classifier.classify(image_path)

        if notes:
            result["extra_data"]["notes"] = notes

        classification = await self.classification_repo.create(
            user_id=user_id,
            image_path=image_path,
            grain_type=result["grain_type"],
            confidence_score=(
            result["confidence_score"]
            if result.get("confidence_score") is not None
            else Decimal("0.0")
            ),
            extra_data=result["extra_data"]
        )

        logger.info(
            "Classification created",
            classification_id=classification.id,
            user_id=user_id,
            grain_type=classification.grain_type,
            is_real_ml=result["extra_data"].get("mock") == False
        )

        return ClassificationResponse.model_validate(classification)
