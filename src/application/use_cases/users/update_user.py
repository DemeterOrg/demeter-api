"""
Use Case para atualização de dados de usuário.
"""

from datetime import datetime, timezone

from src.domain.repositories.user_repository import UserRepository
from src.application.schemas.user import UserUpdate, UserResponse
from src.config.security.password import get_password_hash
from src.config.exceptions.custom_exceptions import NotFoundError, ConflictError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class UpdateUserUseCase:
    """
    Use Case para atualização de usuário.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(
        self,
        user_id: int,
        update_data: UserUpdate,
    ) -> UserResponse:
        """
        Atualiza os dados de um usuário.
        """
        logger.info("Updating user", user_id=user_id)

        user = await self.user_repository.get_by_id(user_id)

        if not user:
            logger.warning("Update failed - user not found", user_id=user_id)
            raise NotFoundError(
                f"Usuário com ID {user_id} não encontrado",
                details={"user_id": user_id},
            )

        if update_data.email and update_data.email != user.email:
            email_exists = await self.user_repository.exists_by_email(update_data.email)
            if email_exists:
                logger.warning(
                    "Update failed - email already in use",
                    user_id=user_id,
                    email=update_data.email,
                )
                raise ConflictError(
                    f"Email '{update_data.email}' já está em uso",
                    details={"email": update_data.email},
                )

        if update_data.name is not None:
            user.name = update_data.name

        if update_data.email is not None:
            user.email = update_data.email

        if update_data.phone is not None:
            user.phone = update_data.phone

        if update_data.password is not None:
            user.hashed_password = get_password_hash(update_data.password)
            logger.info("User password updated", user_id=user_id)

        updated_user = await self.user_repository.update(user)

        logger.info("User updated successfully", user_id=user_id)

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name,
            phone=updated_user.phone,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            created_at=updated_user.created_at or datetime.now(timezone.utc),
            last_login=updated_user.last_login,
        )
