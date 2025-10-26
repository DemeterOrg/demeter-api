"""
Use Case para renovação de access token usando refresh token.
"""

from datetime import datetime, timezone

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.application.schemas.auth import TokenResponse
from src.config.security.auth import (
    verify_token,
    create_access_token,
    extract_user_id_from_token,
)
from src.config.exceptions.custom_exceptions import AuthenticationError, TokenError
from src.config.settings import settings
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class RefreshTokenUseCase:
    """
    Use Case para renovação de access token.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, refresh_token: str) -> TokenResponse:
        """
        Executa a renovação do access token.
        """
        logger.info("Token refresh attempt")

        try:
            payload = verify_token(refresh_token, token_type="refresh")
            user_id = int(payload["sub"])
        except Exception as e:
            logger.warning("Token refresh failed - invalid token", error=str(e))
            raise TokenError(
                "Refresh token inválido ou expirado",
                details={"error": str(e)},
            )

        is_valid = await self.refresh_token_repository.is_valid(refresh_token)

        if not is_valid:
            logger.warning(
                "Token refresh failed - token revoked or expired",
                user_id=user_id,
            )
            raise TokenError(
                "Refresh token revogado ou expirado. Faça login novamente.",
                details={"user_id": user_id},
            )

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning("Token refresh failed - user not found", user_id=user_id)
            raise AuthenticationError(
                "Usuário não encontrado",
                details={"user_id": user_id},
            )

        if not user.is_active:
            logger.warning("Token refresh failed - user inactive", user_id=user_id)
            raise AuthenticationError(
                "Usuário inativo",
                details={"user_id": user_id},
            )

        new_access_token = create_access_token(
            subject=user.id,
        )

        logger.info("Token refreshed successfully", user_id=user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
