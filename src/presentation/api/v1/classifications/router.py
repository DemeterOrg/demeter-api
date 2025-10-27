"""Endpoints de classificações para usuários."""

from typing import Annotated

from fastapi import APIRouter, Depends, status, File, UploadFile, Form, Query

from src.config.db.dependencies import DbSessionDep
from src.config.dependencies.common import require_permission
from src.infrastructure.repositories.classification_repository_impl import ClassificationRepositoryImpl
from src.application.schemas.classification import (
    ClassificationResponse,
    ClassificationListResponse,
    ClassificationUpdate
)
from src.application.use_cases.classifications.create_classification import CreateClassificationUseCase
from src.application.use_cases.classifications.list_classifications import ListClassificationsUseCase
from src.application.use_cases.classifications.get_classification import GetClassificationUseCase
from src.application.use_cases.classifications.update_classification import UpdateClassificationUseCase
from src.application.use_cases.classifications.delete_classification import DeleteClassificationUseCase
from src.application.schemas.auth import MessageResponse

router = APIRouter()


@router.post(
    "/classifications",
    response_model=ClassificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar classificação de grão"
)
async def create_classification(
    image: Annotated[UploadFile, File(description="Imagem do grão")],
    current_user: Annotated[dict, Depends(require_permission("classifications:create:own"))],
    db: DbSessionDep,
    notes: Annotated[str | None, Form()] = None
):
    """Upload de imagem e classificação automática (mock)."""
    repo = ClassificationRepositoryImpl(db)
    use_case = CreateClassificationUseCase(repo)

    return await use_case.execute(
        user_id=current_user["id"],
        image=image,
        notes=notes
    )


@router.get(
    "/classifications",
    response_model=ClassificationListResponse,
    summary="Listar minhas classificações"
)
async def list_classifications(
    current_user: Annotated[dict, Depends(require_permission("classifications:read:own"))],
    db: DbSessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    grain_type: str | None = Query(None)
):
    """Lista classificações do usuário autenticado."""
    repo = ClassificationRepositoryImpl(db)
    use_case = ListClassificationsUseCase(repo)

    return await use_case.execute(
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        grain_type=grain_type
    )


@router.get(
    "/classifications/{classification_id}",
    response_model=ClassificationResponse,
    summary="Ver detalhes de classificação"
)
async def get_classification(
    classification_id: int,
    current_user: Annotated[dict, Depends(require_permission("classifications:read:own"))],
    db: DbSessionDep
):
    """Busca classificação por ID (apenas próprias)."""
    repo = ClassificationRepositoryImpl(db)
    use_case = GetClassificationUseCase(repo)

    return await use_case.execute(
        classification_id=classification_id,
        user_id=current_user["id"]
    )


@router.patch(
    "/classifications/{classification_id}",
    response_model=ClassificationResponse,
    summary="Atualizar classificação"
)
async def update_classification(
    classification_id: int,
    data: ClassificationUpdate,
    current_user: Annotated[dict, Depends(require_permission("classifications:update:own"))],
    db: DbSessionDep
):
    """Atualiza notas da classificação (apenas próprias)."""
    repo = ClassificationRepositoryImpl(db)
    use_case = UpdateClassificationUseCase(repo)

    return await use_case.execute(
        classification_id=classification_id,
        user_id=current_user["id"],
        data=data
    )


@router.delete(
    "/classifications/{classification_id}",
    response_model=MessageResponse,
    summary="Deletar classificação"
)
async def delete_classification(
    classification_id: int,
    current_user: Annotated[dict, Depends(require_permission("classifications:delete:own"))],
    db: DbSessionDep
):
    """Soft delete de classificação (apenas próprias)."""
    repo = ClassificationRepositoryImpl(db)
    use_case = DeleteClassificationUseCase(repo)

    await use_case.execute(
        classification_id=classification_id,
        user_id=current_user["id"]
    )

    return MessageResponse(message="Classificação removida com sucesso")
