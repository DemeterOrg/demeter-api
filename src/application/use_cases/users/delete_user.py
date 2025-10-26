"""
Use Case para deleção de usuário.
"""

from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.refresh_token_repository import RefreshTokenRepository
from src.config.exceptions.custom_exceptions import NotFoundError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class DeleteUserUseCase:
    """
    Use Case para deleção de usuário.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, user_id: int) -> dict:
        """
        Deleta um usuário.
        """
        logger.info("Deleting user", user_id=user_id)

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning("Deletion failed - user not found", user_id=user_id)
            raise NotFoundError(
                f"Usuário com ID {user_id} não encontrado",
                details={"user_id": user_id},
            )

        tokens_revoked = await self.refresh_token_repository.revoke_all_by_user(
            user_id=user_id
        )

        logger.info(
            "User tokens revoked before deletion",
            user_id=user_id,
            tokens_revoked=tokens_revoked,
        )

        await self.user_repository.delete(user_id)

        logger.info(
            "User deleted successfully",
            user_id=user_id,
            email=user.email,
        )

        return {
            "message": "Usuário deletado com sucesso",
            "user_id": user_id,
        }
