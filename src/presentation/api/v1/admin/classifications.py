"""Endpoints administrativos de classificações."""

from typing import Annotated

from fastapi import APIRouter, Depends, status, Query

from src.config.db.dependencies import DbSessionDep
from src.config.dependencies.common import require_permission
from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.infrastructure.repositories.audit_log_repository_impl import AuditLogRepositoryImpl
from src.application.schemas.classification import (
    ClassificationResponse,
    ClassificationListResponse
)
from src.application.schemas.auth import MessageResponse
from src.application.use_cases.admin.list_all_classifications import ListAllClassificationsUseCase
from src.application.use_cases.admin.delete_classification import DeleteClassificationAdminUseCase
from src.application.use_cases.admin.restore_classification import RestoreClassificationUseCase

router = APIRouter()


@router.get(
    "/admin/classifications",
    response_model=ClassificationListResponse,
    summary="[ADMIN] Listar todas classificações"
)
async def list_all_classifications(
    current_user: Annotated[dict, Depends(require_permission("classifications:read:all"))],
    db: DbSessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: int | None = Query(None),
    grain_type: str | None = Query(None),
    include_deleted: bool = Query(False)
):
    """Lista todas classificações de todos usuários."""
    repo = ClassificationRepositoryImpl(db)
    use_case = ListAllClassificationsUseCase(repo)

    return await use_case.execute(
        skip=skip,
        limit=limit,
        user_id=user_id,
        grain_type=grain_type,
        include_deleted=include_deleted
    )


@router.delete(
    "/admin/classifications/{classification_id}",
    response_model=MessageResponse,
    summary="[ADMIN] Deletar classificação"
)
async def delete_classification(
    classification_id: int,
    current_user: Annotated[dict, Depends(require_permission("classifications:delete:all"))],
    db: DbSessionDep,
    hard: bool = Query(False, description="True=hard delete, False=soft delete")
):
    """Deleta classificação (hard ou soft delete)."""
    classification_repo = ClassificationRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    use_case = DeleteClassificationAdminUseCase(classification_repo, audit_repo)

    await use_case.execute(
        classification_id=classification_id,
        admin_user_id=current_user["id"],
        hard_delete=hard
    )

    delete_type = "permanentemente" if hard else "temporariamente"
    return MessageResponse(message=f"Classificação removida {delete_type}")


@router.post(
    "/admin/classifications/{classification_id}/restore",
    response_model=ClassificationResponse,
    summary="[ADMIN] Restaurar classificação"
)
async def restore_classification(
    classification_id: int,
    current_user: Annotated[dict, Depends(require_permission("classifications:restore:all"))],
    db: DbSessionDep
):
    """Restaura classificação soft deleted."""
    classification_repo = ClassificationRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    use_case = RestoreClassificationUseCase(classification_repo, audit_repo)

    return await use_case.execute(
        classification_id=classification_id,
        admin_user_id=current_user["id"]
    )
