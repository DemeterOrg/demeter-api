"""
Router de autenticação.

Endpoints para registro, login, logout e renovação de tokens.
"""

from typing import Optional

from fastapi import APIRouter, Depends, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.db.dependencies import DbSessionDep
from src.config.dependencies.common import get_current_user_payload
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.repositories.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.application.use_cases.auth.login_user import LoginUserUseCase
from src.application.use_cases.auth.logout_user import LogoutUserUseCase
from src.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from src.application.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    MessageResponse,
)
from src.application.schemas.user import UserCreate, UserResponse

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário no sistema",
)
async def register(
    user_data: UserCreate,
    db: DbSessionDep,
) -> UserResponse:
    """
    Registrar um novo usuário.

    - **email**: Email único do usuário
    - **name**: Nome completo
    - **phone**: Telefone (10-11 dígitos)
    - **password**: Senha forte (mínimo 8 caracteres, com maiúscula, minúscula, número e especial)
    - **password_confirm**: Confirmação da senha
    """
    user_repo = UserRepositoryImpl(db)

    use_case = RegisterUserUseCase(user_repo, db)
    return await use_case.execute(user_data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer login",
    description="Autentica usuário e retorna tokens de acesso",
)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: DbSessionDep,
) -> LoginResponse:
    """
    Fazer login no sistema.

    - **email**: Email do usuário
    - **password**: Senha do usuário

    Retorna:
    - **access_token**: Token JWT com validade de 15 minutos
    - **refresh_token**: Token para renovação com validade de 7 dias
    - **user**: Dados do usuário autenticado
    """
    user_repo = UserRepositoryImpl(db)
    refresh_token_repo = RefreshTokenRepositoryImpl(db)
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    use_case = LoginUserUseCase(user_repo, refresh_token_repo)
    return await use_case.execute(login_data, user_agent, ip_address)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer logout",
    description="Revoga refresh token e invalida sessão",
)
async def logout(
    logout_data: LogoutRequest,
    db: DbSessionDep,
    current_user: dict = Depends(get_current_user_payload),
) -> MessageResponse:
    """
    Fazer logout do sistema.

    - **refresh_token**: Token a ser revogado (opcional)

    Se não fornecer refresh_token, apenas o access token atual será invalidado
    (no cliente).

    Requer autenticação via access token no header:
    `Authorization: Bearer <access_token>`
    """
    refresh_token_repo = RefreshTokenRepositoryImpl(db)
    user_id = int(current_user["sub"])

    use_case = LogoutUserUseCase(refresh_token_repo)
    result = await use_case.execute(
        user_id=user_id,
        refresh_token=logout_data.refresh_token,
        revoke_all=False,
    )

    return MessageResponse(message=result["message"])


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Fazer logout de todos os dispositivos",
    description="Revoga todos os refresh tokens do usuário",
)
async def logout_all(
    db: DbSessionDep,
    current_user: dict = Depends(get_current_user_payload),
) -> MessageResponse:
    """
    Fazer logout de todos os dispositivos.

    Revoga todos os refresh tokens do usuário, forçando login
    em todos os dispositivos/sessões.

    Requer autenticação via access token no header:
    `Authorization: Bearer <access_token>`
    """
    refresh_token_repo = RefreshTokenRepositoryImpl(db)
    user_id = int(current_user["sub"])

    use_case = LogoutUserUseCase(refresh_token_repo)
    result = await use_case.execute(
        user_id=user_id,
        refresh_token=None,
        revoke_all=True,
    )

    return MessageResponse(message=result["message"])


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token",
    description="Gera novo access token usando refresh token válido",
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: DbSessionDep,
) -> TokenResponse:
    """
    Renovar access token.

    - **refresh_token**: Refresh token válido

    Retorna novo access token com validade de 15 minutos.
    O refresh token permanece o mesmo.

    Use este endpoint quando o access token expirar para obter
    um novo sem necessidade de login.
    """
    user_repo = UserRepositoryImpl(db)
    refresh_token_repo = RefreshTokenRepositoryImpl(db)

    use_case = RefreshTokenUseCase(user_repo, refresh_token_repo)
    return await use_case.execute(refresh_data.refresh_token)
