"""
Use Case para login de usuários.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.application.schemas.auth import LoginRequest, LoginResponse, TokenResponse
from src.application.schemas.user import UserResponse
from src.config.security.password import verify_password
from src.config.security.auth import create_access_token, create_refresh_token
from src.config.exceptions.custom_exceptions import AuthenticationError
from src.config.settings import settings
from src.config.logging.logger import get_logger, log_auth_event

logger = get_logger(__name__)


class LoginUserUseCase:
    """
    Use Case para login de usuários.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(
        self,
        login_data: LoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> LoginResponse:
        """
        Executa o login do usuário.
        """
        logger.info("Login attempt", email=login_data.email, ip=ip_address)

        user = await self.user_repository.get_by_email(login_data.email)

        if not user:
            log_auth_event(
                logger,
                event_type="login",
                email=login_data.email,
                success=False,
                reason="User not found",
                ip=ip_address,
            )
            raise AuthenticationError(
                "Email ou senha inválidos",
                details={"email": login_data.email},
            )

        if not verify_password(login_data.password, user.hashed_password):
            log_auth_event(
                logger,
                event_type="login",
                user_id=user.id,
                email=user.email,
                success=False,
                reason="Invalid password",
                ip=ip_address,
            )
            raise AuthenticationError(
                "Email ou senha inválidos",
                details={"email": login_data.email},
            )

        if not user.is_active:
            log_auth_event(
                logger,
                event_type="login",
                user_id=user.id,
                email=user.email,
                success=False,
                reason="User inactive",
                ip=ip_address,
            )
            raise AuthenticationError(
                "Usuário inativo. Entre em contato com o suporte.",
                details={"user_id": user.id},
            )

        access_token = create_access_token(subject=user.id)

        refresh_token = create_refresh_token(subject=user.id)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await self.refresh_token_repository.create(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        await self.user_repository.update_last_login(
            user_id=user.id,
            login_time=datetime.now(timezone.utc),
        )

        log_auth_event(
            logger,
            event_type="login",
            user_id=user.id,
            email=user.email,
            success=True,
            ip=ip_address,
        )

        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at or datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc),
        )

        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return LoginResponse(
            user=user_response.model_dump(),
            tokens=tokens,
        )
