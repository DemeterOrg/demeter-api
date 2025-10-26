"""Use case admin para deletar classificação."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.infrastructure.repositories.audit_log_repository_impl import AuditLogRepositoryImpl
from src.infrastructure.services.storage_service import StorageService
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class DeleteClassificationAdminUseCase:
    """Hard ou soft delete de classificação (admin)."""

    def __init__(
        self,
        classification_repo: ClassificationRepositoryImpl,
        audit_repo: AuditLogRepositoryImpl
    ):
        self.classification_repo = classification_repo
        self.audit_repo = audit_repo
        self.storage = StorageService()

    async def execute(
        self,
        classification_id: int,
        admin_user_id: int,
        hard_delete: bool = False
    ) -> bool:
        """Deleta classificação (hard ou soft)."""
        classification = await self.classification_repo.get_by_id(
            classification_id=classification_id,
            include_deleted=True
        )

        if not classification:
            from src.config.exceptions.custom_exceptions import NotFoundError
            raise NotFoundError("Classificação não encontrada")

        if hard_delete:
            await self.audit_repo.create(
                user_id=admin_user_id,
                action="hard_delete_classification",
                resource_type="classifications",
                resource_id=classification_id,
                changes={
                    "grain_type": classification.grain_type,
                    "user_id": classification.user_id,
                    "image_path": classification.image_path
                }
            )

            self.storage.delete_image(classification.image_path)

            result = await self.classification_repo.hard_delete(classification_id)

            logger.info(
                "Classification hard deleted",
                classification_id=classification_id,
                admin_user_id=admin_user_id
            )
        else:
            result = await self.classification_repo.soft_delete(classification_id)

            logger.info(
                "Classification soft deleted by admin",
                classification_id=classification_id,
                admin_user_id=admin_user_id
            )

        return result
