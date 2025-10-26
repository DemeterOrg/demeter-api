"""Use case admin para restaurar classificação."""

from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.infrastructure.repositories.audit_log_repository_impl import AuditLogRepositoryImpl
from src.application.schemas.classification import ClassificationResponse
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class RestoreClassificationUseCase:
    """Restaura classificação soft deleted."""

    def __init__(
        self,
        classification_repo: ClassificationRepositoryImpl,
        audit_repo: AuditLogRepositoryImpl
    ):
        self.classification_repo = classification_repo
        self.audit_repo = audit_repo

    async def execute(
        self,
        classification_id: int,
        admin_user_id: int
    ) -> ClassificationResponse:
        """Restaura classificação deletada."""
        await self.classification_repo.restore(classification_id)

        await self.audit_repo.create(
            user_id=admin_user_id,
            action="restore_classification",
            resource_type="classifications",
            resource_id=classification_id
        )

        classification = await self.classification_repo.get_by_id(
            classification_id=classification_id,
            include_deleted=False
        )

        logger.info(
            "Classification restored",
            classification_id=classification_id,
            admin_user_id=admin_user_id
        )

        return ClassificationResponse.model_validate(classification)
