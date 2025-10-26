"""
Use Case para obter dados de um usuário.
"""

from datetime import datetime, timezone

from src.domain.repositories.user_repository import UserRepository
from src.application.schemas.user import UserResponse
from src.config.exceptions.custom_exceptions import NotFoundError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class GetUserUseCase:
    """
    Use Case para obter dados de um usuário.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: int) -> UserResponse:
        """
        Obtém os dados de um usuário por ID.
        """
        logger.debug("Fetching user", user_id=user_id)

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning("User not found", user_id=user_id)
            raise NotFoundError(
                f"Usuário com ID {user_id} não encontrado",
                details={"user_id": user_id},
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at or datetime.now(timezone.utc),
            last_login=user.last_login,
        )
