"""
Use Case para logout de usuários.
"""

from typing import Optional

from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.config.exceptions.custom_exceptions import NotFoundError, AuthenticationError
from src.config.logging.logger import get_logger, log_auth_event

logger = get_logger(__name__)


class LogoutUserUseCase:
    """
    Use Case para logout de usuários.
    """

    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def execute(
        self,
        user_id: int,
        refresh_token: Optional[str] = None,
        revoke_all: bool = False,
    ) -> dict:
        """
        Executa o logout do usuário.
        """
        logger.info("Logout attempt", user_id=user_id, revoke_all=revoke_all)

        tokens_revoked = 0

        if revoke_all:
            tokens_revoked = await self.refresh_token_repository.revoke_all_by_user(
                user_id=user_id
            )

            log_auth_event(
                logger,
                event_type="logout_all",
                user_id=user_id,
                success=True,
            )

            return {
                "message": "Logout realizado em todos os dispositivos",
                "tokens_revoked": tokens_revoked,
            }

        elif refresh_token:
            try:
                await self.refresh_token_repository.revoke(token=refresh_token)
                tokens_revoked = 1

                log_auth_event(
                    logger,
                    event_type="logout",
                    user_id=user_id,
                    success=True,
                )

                return {
                    "message": "Logout realizado com sucesso",
                    "tokens_revoked": tokens_revoked,
                }

            except NotFoundError:
                logger.warning("Logout failed - token not found", user_id=user_id)
                raise AuthenticationError(
                    "Refresh token inválido ou já revogado",
                    details={"user_id": user_id},
                )

        else:
            log_auth_event(
                logger,
                event_type="logout",
                user_id=user_id,
                success=True,
            )

            return {
                "message": "Logout realizado com sucesso (apenas access token invalidado)",
                "tokens_revoked": 0,
            }
