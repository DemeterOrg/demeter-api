"""
Router de gerenciamento de usuários.

Endpoints para operações CRUD de usuários.
"""

from fastapi import APIRouter, Depends, status

from src.config.db.dependencies import DbSessionDep
from src.config.dependencies.common import get_current_user_payload
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.repositories.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.application.use_cases.users.get_user import GetUserUseCase
from src.application.use_cases.users.update_user import UpdateUserUseCase
from src.application.use_cases.users.delete_user import DeleteUserUseCase
from src.application.schemas.user import UserUpdate, UserResponse
from src.application.schemas.auth import MessageResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter dados do usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado",
)
async def get_me(
    db: DbSessionDep,
    current_user: dict = Depends(get_current_user_payload),
) -> UserResponse:
    """
    Obter dados do próprio usuário.

    Retorna informações detalhadas do usuário autenticado.

    Requer autenticação via access token no header:
    `Authorization: Bearer <access_token>`
    """
    user_repo = UserRepositoryImpl(db)
    user_id = int(current_user["sub"])

    use_case = GetUserUseCase(user_repo)
    return await use_case.execute(user_id)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar dados do usuário autenticado",
    description="Atualiza informações do usuário atualmente autenticado",
)
async def update_me(
    update_data: UserUpdate,
    db: DbSessionDep,
    current_user: dict = Depends(get_current_user_payload),
) -> UserResponse:
    """
    Atualizar dados do próprio usuário.

    Campos atualizáveis:
    - **name**: Nome completo
    - **email**: Email (único)
    - **password**: Nova senha

    Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.

    Requer autenticação via access token no header:
    `Authorization: Bearer <access_token>`
    """
    user_repo = UserRepositoryImpl(db)
    user_id = int(current_user["sub"])

    use_case = UpdateUserUseCase(user_repo)
    return await use_case.execute(user_id, update_data)


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Deletar própria conta",
    description="Deleta permanentemente a conta do usuário autenticado",
)
async def delete_me(
    db: DbSessionDep,
    current_user: dict = Depends(get_current_user_payload),
) -> MessageResponse:
    """
    Deletar própria conta.

    **ATENÇÃO:** Esta ação é irreversível!

    Deleta permanentemente:
    - Dados do usuário
    - Todos os refresh tokens
    - Todas as classificações associadas (quando implementado)

    Requer autenticação via access token no header:
    `Authorization: Bearer <access_token>`
    """
    user_repo = UserRepositoryImpl(db)
    refresh_token_repo = RefreshTokenRepositoryImpl(db)
    user_id = int(current_user["sub"])

    use_case = DeleteUserUseCase(user_repo, refresh_token_repo)
    result = await use_case.execute(user_id)

    return MessageResponse(message=result["message"])
